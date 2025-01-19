import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
from gestion import GestionDB
from tkcalendar import DateEntry
from datetime import datetime

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión")
        self.root.geometry("1200x700")
        
        # Inicializar ruta_imagen
        self.ruta_imagen = None  # Asegúrate de que esta línea esté presente

        # Configurar el estilo general
        style = ttk.Style()
        style.theme_use('clam')  # Usar el tema 'clam' que es más moderno
        
        # Configurar colores y estilos
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Helvetica', 10))
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('Treeview', font=('Helvetica', 10))
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        
        self.db = GestionDB()
        self.app = self.db
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Crear pestañas
        self.tab_personas = ttk.Frame(self.notebook)
        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_transacciones = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_personas, text='Gestión de Personas')
        self.notebook.add(self.tab_inventario, text='Gestión de Inventario')
        self.notebook.add(self.tab_transacciones, text='Transacciones')
        
        # Vincular el evento de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Botón para abrir la ventana de transacciones
        ttk.Button(self.tab_transacciones, text="Registrar Transacción", 
                command=lambda: abrir_ventana_transacciones(self, self.db)).pack(pady=10)
        
        # Crear un marco para los botones
        frame_botones = ttk.Frame(self.tab_personas)
        frame_botones.pack(pady=10)

        # Configurar estilos personalizados para los botones
        style = ttk.Style()
        style.configure('Add.TButton', 
                       background='#77dd77',  # Verde pastel
                       foreground='black',
                       padding=10)
        style.configure('Edit.TButton', 
                       background='#007BFF',  # Azul
                       foreground='white',
                       padding=10)
        style.configure('Date.TButton', 
                       background='#FFC107',  # Amarillo
                       foreground='black',
                       padding=10)
        style.configure('Delete.TButton', 
                       background='#DC3545',  # Rojo
                       foreground='white',
                       padding=10)

        # Botón para agregar persona
        ttk.Button(frame_botones, text="Agregar Persona", 
                   command=self.abrir_ventana_agregar_persona,
                   style='Add.TButton').grid(row=0, column=0, padx=15, pady=5)

        # Botón para editar persona
        ttk.Button(frame_botones, text="Editar Persona", 
                   command=self.abrir_ventana_editar_persona,
                   style='Edit.TButton').grid(row=0, column=1, padx=15, pady=5)
        
        # Botón para establecer fecha de entrega
        ttk.Button(frame_botones, text="Establecer Fecha de Entrega", 
                   command=self.abrir_ventana_fecha_entrega,
                   style='Date.TButton').grid(row=0, column=2, padx=15, pady=5)
        
        # Botón para eliminar persona (separado con más padding)
        ttk.Button(frame_botones, text="Eliminar Persona", 
                   command=self.eliminar_persona,
                   style='Delete.TButton').grid(row=0, column=3, padx=(30, 15), pady=5, sticky='e')
        
        # Ocultar detalles de persona
        self.frame_formulario = ttk.LabelFrame(self.tab_personas, text="Detalles de Persona")
        self.frame_formulario.pack(fill='x', padx=5, pady=5)
        self.frame_formulario.pack_forget()  # Ocultar el frame inicialmente
        
        # Inicializar componentes
        self.setup_personas_tab()
        self.setup_inventario_tab()
        self.setup_transacciones_tab()
        
        # Variable para la casilla de verificación
        self.entregado_var = tk.BooleanVar()
        
        # Opciones de municipios
        self.municipios = ["Montemorelos", "Allende", "Rayones", "Linares", "Hualahuises", "Terán"]
        
        # Campos del formulario
        self.campos_persona = {}
        campos_normales = [
            ('Nombre:', 'nombre'), 
            ('Artículo:', 'articulo'),  
            ('Teléfono:', 'telefono'), 
            ('Dirección:', 'direccion'), 
            ('Municipio:', 'municipio')  # Cambiar a Combobox
        ]
        campos_fecha = [
            ('Fecha Petición:', 'fecha_peticion'),
            ('Fecha Entrega:', 'fecha_entrega')
        ]

        # Crear campos normales (Entry y Combobox)
        for i, (label, campo) in enumerate(campos_normales):
            ttk.Label(self.frame_formulario, text=label).grid(row=i, column=0, padx=5, pady=2)
            if campo == 'municipio':
                combobox = ttk.Combobox(self.frame_formulario, values=self.municipios)
                combobox.grid(row=i, column=1, padx=5, pady=2)
                self.campos_persona[campo] = combobox
            else:
                entry = ttk.Entry(self.frame_formulario)
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.campos_persona[campo] = entry

        # Crear campos de fecha (DateEntry)
        for i, (label, campo) in enumerate(campos_fecha, start=len(campos_normales)):
            ttk.Label(self.frame_formulario, text=label).grid(row=i, column=0, padx=5, pady=2)
            date_entry = DateEntry(self.frame_formulario, 
                                 width=20,
                                 background='darkblue',
                                 foreground='white',
                                 borderwidth=2,
                                 date_pattern='yyyy-mm-dd')
            date_entry.grid(row=i, column=1, padx=5, pady=2)
            self.campos_persona[campo] = date_entry

        # Casilla de verificación para "Entregado"
        ttk.Checkbutton(self.frame_formulario, text="Entregado", variable=self.entregado_var).grid(row=len(campos_normales) + len(campos_fecha), column=0, columnspan=2)

        # Botones
        frame_botones = ttk.Frame(self.frame_formulario)
        frame_botones.grid(row=len(campos_normales) + len(campos_fecha) + 1, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Agregar", 
                command=self.agregar_persona).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar", 
                command=self.actualizar_persona).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar", 
                command=self.limpiar_campos_persona).pack(side='left', padx=5)

        # Nuevo marco para el botón de eliminar
        frame_boton_eliminar = ttk.Frame(self.frame_formulario)
        frame_boton_eliminar.grid(row=len(campos_normales) + len(campos_fecha) + 2, column=0, columnspan=2, pady=10)

        ttk.Button(frame_boton_eliminar, text="Eliminar", 
                command=self.eliminar_persona).pack(side='left', padx=5)
        
        # Bind para selección en el TreeView
        self.tree_personas.bind('<<TreeviewSelect>>', self.seleccionar_persona)
        
        # Cargar datos iniciales
        self.actualizar_lista_personas()

        # Crear un marco para la búsqueda
        frame_busqueda = ttk.Frame(self.tab_personas)
        frame_busqueda.pack(pady=10)

        # Filtros de búsqueda
        ttk.Label(frame_busqueda, text="Buscar por Nombre:").pack(side='left', padx=5)
        self.combobox_nombre = ttk.Combobox(frame_busqueda)  # Cambiar de Entry a Combobox
        self.combobox_nombre.pack(side='left', padx=5)
        self.combobox_nombre.bind('<Return>', self.filtrar_personas)

        ttk.Label(frame_busqueda, text="Buscar por Artículo:").pack(side='left', padx=5)
        self.entry_buscar_articulo = ttk.Entry(frame_busqueda)  # Asegúrate de que esté definido
        self.entry_buscar_articulo.pack(side='left', padx=5)
        self.entry_buscar_articulo.bind('<Return>', self.filtrar_personas)

        ttk.Label(frame_busqueda, text="Buscar por Municipio:").pack(side='left', padx=5)
        self.combobox_municipio = ttk.Combobox(frame_busqueda, values=[''] + self.municipios)
        self.combobox_municipio.pack(side='left', padx=5)
        self.combobox_municipio.bind('<<ComboboxSelected>>', self.filtrar_personas)

        # Nuevo filtro de estado
        ttk.Label(frame_busqueda, text="Estado:").pack(side='left', padx=5)
        self.combo_estado = ttk.Combobox(frame_busqueda, 
                                       values=['Todos', 'Entregado', 'Pendiente'],
                                       width=10)
        self.combo_estado.set('Todos')
        self.combo_estado.pack(side='left', padx=5)
        self.combo_estado.bind('<<ComboboxSelected>>', self.filtrar_personas)

        # Botón para buscar
        ttk.Button(frame_busqueda, text="Buscar", 
                  command=lambda: self.filtrar_personas(None)).pack(side='left', padx=5)

        # Botón para exportar a Excel
        ttk.Button(frame_busqueda, text="Exportar a Excel", 
                  command=self.exportar_a_excel).pack(side='left', padx=5)

        # Cargar nombres y artículos en los comboboxes
        self.cargar_nombres_y_articulos()

        # Frame para los filtros de búsqueda
        frame_busqueda = ttk.Frame(self.tab_personas)
        frame_busqueda.pack(fill='x', padx=5, pady=5)

        # Configurar estilos personalizados
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 10), padding=5, background='#4CAF50', foreground='white')
        style.configure('Danger.TButton', font=('Helvetica', 10), padding=5, background='#f44336', foreground='white')

    def on_tab_changed(self, event):
        """Método llamado cuando se cambia de pestaña en el Notebook."""
        selected_tab = event.widget.tab('current')['text']
        if selected_tab == 'Gestión de Inventario':
            self.actualizar_lista_inventario()

    def cargar_nombres_y_articulos(self):
        # Obtener nombres y artículos de la base de datos
        nombres = self.db.obtener_nombres()  # Asegúrate de que este método exista
        articulos = self.db.obtener_articulos()  # Asegúrate de que este método exista

        # Llenar los comboboxes
        self.combobox_nombre['values'] = nombres
        self.combo_articulo['values'] = articulos  # Asegúrate de usar el nombre correcto

    def setup_inventario_tab(self):
        # Frame para búsqueda
        frame_busqueda = ttk.LabelFrame(self.tab_inventario, text="Búsqueda")
        frame_busqueda.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(frame_busqueda, text="Buscar:").pack(side='left', padx=5)
        self.entry_busqueda_inventario = ttk.Entry(frame_busqueda)
        self.entry_busqueda_inventario.pack(side='left', padx=5)

        # Vincular el evento de Enter a la función de búsqueda
        self.entry_busqueda_inventario.bind("<Return>", self.buscar_articulos)

        ttk.Button(frame_busqueda, text="Buscar", 
                   command=self.buscar_articulos).pack(side='left', padx=5)
        
        # Botón para agregar producto
        ttk.Button(frame_busqueda, text="Agregar Producto", 
                   command=self.abrir_ventana_agregar_producto, 
                   style='Add.TButton').pack(side='left', padx=5)
        
        # Frame principal dividido en dos
        frame_principal = ttk.PanedWindow(self.tab_inventario, orient=tk.HORIZONTAL)
        frame_principal.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Crear un marco para los detalles del artículo
        self.frame_detalles_articulo = ttk.LabelFrame(self.tab_inventario, text="Detalles del Artículo")
        self.frame_detalles_articulo.pack(fill='x', padx=5, pady=5)

        # Crear un marco para agrupar los campos
        frame_campos = ttk.Frame(self.frame_detalles_articulo)
        frame_campos.grid(row=0, column=0, padx=5, pady=5)

        # Campos del formulario
        self.campos_inventario = {}
        campos_normales = [
            ('Nombre del Artículo:', 'nombre_articulo'), 
            ('Descripción:', 'descripcion'), 
            ('Cantidad Disponible:', 'cantidad_disponible'),
            ('Fecha de Ingreso:', 'fecha_ingreso')
        ]

        # Crear campos normales (Entry y DateEntry)
        for i, (label, campo) in enumerate(campos_normales):
            ttk.Label(frame_campos, text=label).grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)  # Alinear a la izquierda
            if campo == 'fecha_ingreso':
                date_entry = DateEntry(frame_campos, 
                                       width=20,
                                       background='darkblue',
                                       foreground='white',
                                       borderwidth=2,
                                       date_pattern='yyyy-mm-dd')
                date_entry.grid(row=i, column=1, padx=5, pady=2)
                self.campos_inventario[campo] = date_entry
            else:
                entry = ttk.Entry(frame_campos)
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.campos_inventario[campo] = entry

        # Frame para la imagen
        frame_imagen = ttk.LabelFrame(self.frame_detalles_articulo, text="Imagen del Artículo", width=150, height=150)
        frame_imagen.grid(row=0, column=2, rowspan=len(campos_normales), padx=5, pady=5)

        # Label para mostrar la imagen
        self.label_imagen = ttk.Label(frame_imagen, text="No hay imagen", width=20)  # Texto por defecto
        self.label_imagen.pack(padx=5, pady=5)

        # Botones para la imagen
        ttk.Button(frame_imagen, text="Seleccionar Imagen", 
                command=self.seleccionar_imagen).pack(side='left', padx=5)
        ttk.Button(frame_imagen, text="Eliminar Imagen", 
                command=self.eliminar_imagen).pack(side='left', padx=5)

        # Botones de acción
        frame_botones = ttk.Frame(self.frame_detalles_articulo)
        frame_botones.grid(row=len(campos_normales), column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Actualizar", 
                command=self.actualizar_articulo).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar", 
                command=self.eliminar_articulo).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar", 
                command=self.limpiar_campos_inventario).pack(side='left', padx=5)
        
        # Crear Treeview
        self.tree_inventario = ttk.Treeview(frame_principal, columns=('ID', 'Nombre', 'Descripción', 'Cantidad', 'Imagen', 'Fecha de Ingreso'), show='headings')

        # Configurar columnas
        for col in self.tree_inventario['columns']:
            self.tree_inventario.heading(col, text=col)
            self.tree_inventario.column(col, width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(frame_principal, orient='vertical', command=self.tree_inventario.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_inventario.configure(yscrollcommand=scrollbar.set)
        self.tree_inventario.pack(fill='both', expand=True)
        
        # Bind para selección en el TreeView
        self.tree_inventario.bind('<<TreeviewSelect>>', self.seleccionar_articulo)
        
        # Cargar datos iniciales
        self.actualizar_lista_inventario()

        # Crear el menú contextual
        self.menu_contextual = tk.Menu(self.root, tearoff=0)
        self.menu_contextual.add_command(label="Editar", command=self.editar_articulo)
        self.menu_contextual.add_command(label="Eliminar", command=self.eliminar_articulo)
        self.menu_contextual.add_command(label="Cambiar Foto", command=self.seleccionar_imagen)

        # Bind para el clic derecho
        self.tree_inventario.bind("<Button-3>", self.mostrar_menu_contextual)

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual al hacer clic derecho"""
        # Obtener la posición del clic
        self.tree_inventario.selection_set(self.tree_inventario.identify_row(event.y))
        self.menu_contextual.post(event.x_root, event.y_root)

    def editar_articulo(self):
        """Abre la ventana de edición para el artículo seleccionado"""
        seleccion = self.tree_inventario.selection()  # Usar tree_inventario en lugar de tree
        if seleccion:
            item = self.tree_inventario.item(seleccion[0])
            # Obtener los valores del artículo seleccionado
            valores = item['values']
            
            # Crear la ventana de edición
            edit_window = tk.Toplevel(self.root)  # Usar self.root en lugar de self.master
            VentanaEditarArticulo(edit_window, self, valores)

    def eliminar_articulo(self):
        seleccion = self.tree_inventario.selection()
        if seleccion:
            item = self.tree_inventario.item(seleccion[0])
            # Aquí puedes implementar la lógica para eliminar el artículo
            print("Eliminar artículo:", item['values'])

    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if ruta:
            try:
                # Obtener el artículo seleccionado
                seleccion = self.tree_inventario.selection()
                if seleccion:
                    item = self.tree_inventario.item(seleccion[0])
                    id_articulo = item['values'][0]
                    
                    # Guardar la imagen en la carpeta de imágenes
                    nombre_archivo = f"imagenes/{os.path.basename(ruta)}"
                    os.makedirs("imagenes", exist_ok=True)
                    Image.open(ruta).save(nombre_archivo)
                    
                    # Mostrar la imagen en el label
                    imagen = Image.open(ruta)
                    imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(imagen)
                    self.label_imagen.configure(image=foto)
                    self.label_imagen.image = foto
                    
                    # Actualizar solo la imagen en la base de datos
                    if self.db.actualizar_imagen_articulo(id_articulo, nombre_archivo):
                        self.actualizar_lista_inventario()
                        messagebox.showinfo("Éxito", "Imagen actualizada correctamente")
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar la imagen")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar la imagen: {str(e)}")

    def setup_inventario_tab(self):
        # Limpiar cualquier widget existente en la pestaña
        for widget in self.tab_inventario.winfo_children():
            widget.destroy()

        # Frame principal para contener todo utilizando grid
        main_frame = ttk.Frame(self.tab_inventario)
        main_frame.pack(fill='both', expand=True)

        # Configurar las filas y columnas de main_frame
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # Solo la fila 1 (frame_tree) tendrá peso

        # Frame para búsqueda (fila 0)
        self.frame_busqueda = ttk.LabelFrame(main_frame, text="Búsqueda")
        self.frame_busqueda.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Configurar las columnas de frame_busqueda
        self.frame_busqueda.columnconfigure(1, weight=1)

        ttk.Label(self.frame_busqueda, text="Buscar:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_busqueda_inventario = ttk.Entry(self.frame_busqueda)
        self.entry_busqueda_inventario.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(self.frame_busqueda, text="Buscar", 
                   command=self.buscar_articulos).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(self.frame_busqueda, text="Agregar Producto", 
                   command=self.abrir_ventana_agregar_producto).grid(row=0, column=3, padx=5, pady=5)

        # Frame para el TreeView (fila 1)
        frame_tree = ttk.Frame(main_frame)
        frame_tree.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Configurar el TreeView
        self.tree_inventario = ttk.Treeview(frame_tree, columns=('ID', 'Nombre', 'Descripción', 'Cantidad', 'Imagen', 'Fecha de Ingreso'))
        
        # Configurar las columnas
        for col in ('ID', 'Nombre', 'Descripción', 'Cantidad', 'Imagen', 'Fecha de Ingreso'):
            self.tree_inventario.heading(col, text=col)
            self.tree_inventario.column(col, width=100, anchor='center')

        # Ocultar la columna vacía del TreeView
        self.tree_inventario['show'] = 'headings'

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_inventario.yview)
        self.tree_inventario.configure(yscrollcommand=scrollbar.set)

        # Empaquetar TreeView y scrollbar utilizando grid
        self.tree_inventario.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configurar el grid de frame_tree
        frame_tree.columnconfigure(0, weight=1)
        frame_tree.rowconfigure(0, weight=1)

        # Vincular la selección del TreeView
        self.tree_inventario.bind('<<TreeviewSelect>>', self.seleccionar_articulo)
        
        # Frame para detalles del artículo y la imagen (fila 2)
        frame_detalles_imagen = ttk.Frame(main_frame)
        frame_detalles_imagen.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        # Configurar las columnas de frame_detalles_imagen
        frame_detalles_imagen.columnconfigure(0, weight=1)
        frame_detalles_imagen.columnconfigure(1, weight=1)

        # Frame para detalles del artículo
        self.frame_detalles = ttk.LabelFrame(frame_detalles_imagen, text="Detalles del Artículo")
        self.frame_detalles.grid(row=0, column=0, sticky='ew', padx=(0, 5), pady=5)

        # Campos para detalles del artículo
        campos = [
            ('Nombre del Artículo:', 'nombre_articulo'),
            ('Descripción:', 'descripcion'),
            ('Cantidad Disponible:', 'cantidad'),
            ('Fecha de Ingreso:', 'fecha_ingreso')
        ]

        self.campos_inventario = {}
        for i, (label, campo) in enumerate(campos):
            ttk.Label(self.frame_detalles, text=label, width=20).grid(row=i, column=0, padx=5, pady=2, sticky='w')
            if campo == 'fecha_ingreso':
                widget = DateEntry(self.frame_detalles, width=30, background='darkblue', 
                                 foreground='white', borderwidth=2, 
                                 date_pattern='yyyy-mm-dd')
            else:
                widget = ttk.Entry(self.frame_detalles, width=30)
            widget.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
            self.campos_inventario[campo] = widget

        # Configurar las columnas de frame_detalles para expandirse
        self.frame_detalles.columnconfigure(1, weight=1)

        # Frame separado para la imagen
        self.frame_imagen = ttk.LabelFrame(frame_detalles_imagen, text="Imagen del Artículo")
        self.frame_imagen.grid(row=0, column=1, sticky='ew', padx=(5, 0), pady=5)

        # Contenedor para la imagen y botones
        frame_contenido_imagen = ttk.Frame(self.frame_imagen)
        frame_contenido_imagen.pack(padx=10, pady=10, fill='both', expand=True)

        # Label para mostrar la imagen
        self.label_imagen = ttk.Label(frame_contenido_imagen, text="No hay imagen")
        self.label_imagen.pack(pady=5, expand=True)

        # Frame para los botones de imagen
        frame_botones_imagen = ttk.Frame(frame_contenido_imagen)
        frame_botones_imagen.pack(pady=5)

        ttk.Button(frame_botones_imagen, text="Seleccionar Imagen",
                  command=self.seleccionar_imagen).pack(side='left', padx=5)
        ttk.Button(frame_botones_imagen, text="Eliminar Imagen",
                  command=self.eliminar_imagen).pack(side='left', padx=5)

        # Frame para botones de acción
        frame_botones = ttk.Frame(self.frame_detalles)
        frame_botones.grid(row=len(campos), column=0, columnspan=2, pady=10, sticky='e')

        ttk.Button(frame_botones, text="Actualizar",
                  command=self.actualizar_articulo).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar",
                  command=self.eliminar_articulo).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar",
                  command=self.limpiar_campos_inventario).pack(side='left', padx=5)

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual al hacer clic derecho"""
        # Obtener la posición del clic
        self.tree_inventario.selection_set(self.tree_inventario.identify_row(event.y))
        self.menu_contextual.post(event.x_root, event.y_root)

    def editar_articulo(self):
        """Abre la ventana de edición para el artículo seleccionado"""
        seleccion = self.tree_inventario.selection()  # Usar tree_inventario en lugar de tree
        if seleccion:
            item = self.tree_inventario.item(seleccion[0])
            # Obtener los valores del artículo seleccionado
            valores = item['values']
            
            # Crear la ventana de edición
            edit_window = tk.Toplevel(self.root)  # Usar self.root en lugar de self.master
            VentanaEditarArticulo(edit_window, self, valores)

    def eliminar_articulo(self):
        seleccion = self.tree_inventario.selection()
        if seleccion:
            item = self.tree_inventario.item(seleccion[0])
            # Aquí puedes implementar la lógica para eliminar el artículo
            print("Eliminar artículo:", item['values'])

    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if ruta:
            try:
                # Obtener el artículo seleccionado
                seleccion = self.tree_inventario.selection()
                if seleccion:
                    item = self.tree_inventario.item(seleccion[0])
                    id_articulo = item['values'][0]
                    
                    # Guardar la imagen en la carpeta de imágenes
                    nombre_archivo = f"imagenes/{os.path.basename(ruta)}"
                    os.makedirs("imagenes", exist_ok=True)
                    Image.open(ruta).save(nombre_archivo)
                    
                    # Mostrar la imagen en el label
                    imagen = Image.open(ruta)
                    imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(imagen)
                    self.label_imagen.configure(image=foto)
                    self.label_imagen.image = foto
                    
                    # Actualizar solo la imagen en la base de datos
                    if self.db.actualizar_imagen_articulo(id_articulo, nombre_archivo):
                        self.actualizar_lista_inventario()
                        messagebox.showinfo("Éxito", "Imagen actualizada correctamente")
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar la imagen")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar la imagen: {str(e)}")

    def setup_transacciones_tab(self):
        # Estilo para los frames
        style = ttk.Style()
        style.configure('Custom.TFrame', background='#f0f0f0')
        style.configure('Custom.TLabelframe', background='#f0f0f0')
        style.configure('Custom.TButton', padding=5)
        
        # Frame principal con padding y estilo
        main_frame = ttk.Frame(self.tab_transacciones, style='Custom.TFrame', padding="10")
        main_frame.pack(fill='both', expand=True)

        # Frame para filtros rápidos
        quick_filter_frame = ttk.LabelFrame(main_frame, text="Filtros Rápidos", style='Custom.TLabelframe', padding="5")
        quick_filter_frame.pack(fill='x', padx=5, pady=5)

        # Botones de filtro rápido
        ttk.Button(quick_filter_frame, text="Ver Todo", 
                   command=self.mostrar_todas_transacciones,
                   style='Custom.TButton').pack(side='left', padx=5)
        ttk.Button(quick_filter_frame, text="Solo Entradas", 
                   command=lambda: self.filtrar_por_tipo('entrada'),
                   style='Custom.TButton').pack(side='left', padx=5)
        ttk.Button(quick_filter_frame, text="Solo Salidas", 
                   command=lambda: self.filtrar_por_tipo('salida'),
                   style='Custom.TButton').pack(side='left', padx=5)

        # Frame para filtros avanzados
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros Avanzados", style='Custom.TLabelframe', padding="5")
        filter_frame.pack(fill='x', padx=5, pady=5)

        # Grid para los filtros
        ttk.Label(filter_frame, text="Tipo:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(filter_frame, values=["", "entrada", "salida"])
        self.combo_tipo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Artículo:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_articulo = ttk.Combobox(filter_frame)
        self.combo_articulo.grid(row=0, column=3, padx=5, pady=5)

        # Checkbox para todas las fechas
        self.filtrar_fecha_var = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Todas las fechas", 
                        variable=self.filtrar_fecha_var,
                        command=self.toggle_fecha).grid(row=1, column=0, columnspan=2)

        # Frame para fechas
        date_frame = ttk.Frame(filter_frame)
        date_frame.grid(row=2, column=0, columnspan=4, pady=5)

        ttk.Label(date_frame, text="Desde:").pack(side='left', padx=5)
        self.entry_fecha_desde = DateEntry(date_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2,
                                         date_pattern='yyyy-mm-dd')
        self.entry_fecha_desde.pack(side='left', padx=5)

        ttk.Label(date_frame, text="Hasta:").pack(side='left', padx=5)
        self.entry_fecha_hasta = DateEntry(date_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2,
                                         date_pattern='yyyy-mm-dd')
        self.entry_fecha_hasta.pack(side='left', padx=5)

        # Botón de filtrar
        ttk.Button(filter_frame, text="Aplicar Filtros", 
                   command=self.filtrar_transacciones,
                   style='Custom.TButton').grid(row=3, column=0, columnspan=4, pady=10)

        # TreeView con estilo mejorado
        style.configure("Treeview", background="#ffffff",
                       foreground="black",
                       rowheight=25,
                       fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        # Frame para el TreeView
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=5)

        # Crear TreeView
        self.tree_transacciones = ttk.Treeview(tree_frame, 
            columns=('ID', 'Artículo', 'Tipo', 'Cantidad', 'Stock sin Transacción', 
                    'Stock con Transacción', 'Fecha'),
            show='headings',
            style="Treeview")

        # Configurar columnas
        for col in self.tree_transacciones['columns']:
            self.tree_transacciones.heading(col, text=col)
            self.tree_transacciones.column(col, width=100)

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', 
                                 command=self.tree_transacciones.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_transacciones.configure(yscrollcommand=scrollbar.set)
        self.tree_transacciones.pack(fill='both', expand=True)

        # Cargar datos iniciales
        self.cargar_articulos_unicos()
        self.actualizar_lista_transacciones()




    def cargar_articulos_unicos(self):
        # Obtener artículos de la base de datos
        articulos = self.db.obtener_transacciones()  # Asegúrate de que este método devuelva las transacciones
        articulos_unicos = set(transaccion[1] for transaccion in articulos)  # Suponiendo que el artículo está en la segunda columna
        self.combo_articulo['values'] = list(articulos_unicos)  # Asignar los artículos únicos al combobox

    def toggle_fecha(self):
        estado = self.filtrar_fecha_var.get()
        if estado:
            # Si está marcada, deshabilitar los campos de fecha
            self.entry_fecha_desde.config(state='disabled')
            self.entry_fecha_hasta.config(state='disabled')
        else:
            # Si está desmarcada, habilitar los campos de fecha
            self.entry_fecha_desde.config(state='normal')
            self.entry_fecha_hasta.config(state='normal')

    def filtrar_transacciones(self, event=None):
        tipo = self.combo_tipo.get()
        articulo = self.combo_articulo.get()
        
        # Si la casilla está marcada, no usar fechas
        if self.filtrar_fecha_var.get():
            fecha_desde = None
            fecha_hasta = None
        else:
            fecha_desde = self.entry_fecha_desde.get()
            fecha_hasta = self.entry_fecha_hasta.get()

        # Verificar si al menos un campo tiene valor
        if not any([tipo, articulo, (fecha_desde and fecha_hasta)]):
            messagebox.showwarning("Advertencia", "Por favor, ingrese al menos un criterio de búsqueda.")
            return

        # Limpiar el TreeView
        for item in self.tree_transacciones.get_children():
            self.tree_transacciones.delete(item)

        # Obtener transacciones filtradas
        transacciones = self.app.obtener_transacciones_filtradas(tipo, fecha_desde, fecha_hasta, articulo)

        # Insertar las transacciones filtradas
        if transacciones:
            for transaccion in transacciones:
                fecha_formateada = transaccion[6].split(" ")[0]
                self.tree_transacciones.insert('', 'end', values=(
                    transaccion[0], transaccion[1], transaccion[2], 
                    transaccion[3], transaccion[4], transaccion[5], 
                    fecha_formateada))
        else:
            messagebox.showinfo("Información", "No se encontraron transacciones para los criterios seleccionados.")

    def exportar_transacciones(self):
        success, message = self.db.exportar_a_csv('transacciones')
        messagebox.showinfo("Exportar a CSV", message)

    def setup_personas_tab(self):
        # Crear TreeView para mostrar personas
        self.tree_personas = ttk.Treeview(self.tab_personas, columns=('ID', 'Nombre', 'Artículo', 'Teléfono', 'Dirección', 'Municipio', 'Fecha Petición', 'Fecha Entrega'), show='headings')
        self.tree_personas.pack(fill='both', expand=True, padx=5, pady=5)

        # Configurar columnas
        for col in self.tree_personas['columns']:
            self.tree_personas.heading(col, text=col)
            self.tree_personas.column(col, width=100)

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(self.tab_personas, orient='vertical', command=self.tree_personas.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_personas.configure(yscrollcommand=scrollbar.set)

        # Cargar datos iniciales
        self.actualizar_lista_personas()

    # Métodos para gestión de personas
    def actualizar_lista_personas(self):
        # Limpiar el TreeView
        for item in self.tree_personas.get_children():
            self.tree_personas.delete(item)
        
        # Obtener y mostrar las personas
        personas = self.db.obtener_personas()
        for persona in personas:
            # Convertir None o 'None' a 'Pendiente' para mostrar en el TreeView
            valores = list(persona)
            valores[-1] = 'Pendiente' if valores[-1] in [None, 'None', ''] else valores[-1]
            self.tree_personas.insert('', 'end', values=valores)

    def buscar_personas(self, event=None):
        nombre = self.combobox_nombre.get()
        articulo = self.combo_articulo.get()
        municipio = self.combobox_municipio.get()

        # Limpiar la lista actual
        for item in self.tree_personas.get_children():
            self.tree_personas.delete(item)

        # Obtener personas filtradas
        personas = self.db.obtener_personas(nombre, articulo, municipio)
        for persona in personas:
            self.tree_personas.insert('', 'end', values=persona)

    def agregar_persona(self):
        # Recoger los datos de los campos de entrada
        nombre = self.entry_nombre.get()
        articulo = self.entry_articulo.get()
        telefono = self.entry_telefono.get()
        direccion = self.entry_direccion.get()
        municipio = self.combobox_municipio.get()
        fecha_peticion = self.entry_fecha_peticion.get()
        fecha_entrega = self.entry_fecha_entrega.get() if not self.check_pendiente.get() else None

        # Crear un diccionario con los valores
        valores = {
            'nombre': nombre,
            'articulo': articulo,
            'telefono': telefono,
            'direccion': direccion,
            'municipio': municipio,
            'fecha_peticion': fecha_peticion,
            'fecha_entrega': fecha_entrega
        }

        # Llamar al método para agregar la persona
        if self.app.db.agregar_persona(**valores):
            messagebox.showinfo("Éxito", "Persona agregada correctamente")
            self.master.destroy()  # Cerrar la ventana
            self.app.actualizar_lista_personas()  # Actualizar la lista de personas
        else:
            messagebox.showerror("Error", "No se pudo agregar la persona. Verifique los datos.")

    def actualizar_persona(self):
        seleccion = self.tree_personas.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una persona para actualizar")
            return
        
        item = self.tree_personas.item(seleccion[0])
        id_persona = item['values'][0]
        valores = {campo: entry.get() for campo, entry in self.campos_persona.items()}
        
        # Solo asignar la fecha de entrega si la casilla está marcada
        if self.entregado_var.get():
            valores['fecha_entrega'] = self.campos_persona['fecha_entrega'].get()
        else:
            valores['fecha_entrega'] = None  # O puedes dejarlo vacío según tu lógica

        # Asegúrate de que los nombres de los argumentos coincidan con los de GestionDB
        if self.db.actualizar_persona(id_persona, 
                                       nombre=valores['nombre'], 
                                       telefono=valores['telefono'], 
                                       direccion=valores['direccion'], 
                                       municipio=valores['municipio'], 
                                       fecha_peticion=valores['fecha_peticion'], 
                                       fecha_entrega=valores['fecha_entrega']):
            messagebox.showinfo("Éxito", "Persona actualizada correctamente")
            self.limpiar_campos_persona()
            self.actualizar_lista_personas()
        else:
            messagebox.showerror("Error", "No se pudo actualizar la persona")

    def eliminar_persona(self):
        seleccion = self.tree_personas.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una persona para eliminar")
            return
        
        # Confirmar la eliminación
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta persona?"):
            item = self.tree_personas.item(seleccion[0])
            id_persona = item['values'][0]  # Asumiendo que el ID es el primer valor
            
            if self.db.eliminar_persona(id_persona):
                messagebox.showinfo("Éxito", "Persona eliminada correctamente")
                self.actualizar_lista_personas()  # Actualizar la lista de personas
            else:
                messagebox.showerror("Error", "No se pudo eliminar la persona")

    def seleccionar_persona(self, event):
        seleccion = self.tree_personas.selection()
        if seleccion:
            item = self.tree_personas.item(seleccion[0])
            valores = item['values']
            for i, (campo, entry) in enumerate(self.campos_persona.items()):
                if isinstance(entry, DateEntry):
                    try:
                        entry.set_date(valores[i + 1])
                    except:
                        entry.set_date(None)
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, valores[i + 1] if valores[i + 1] else '')

            # Establecer el estado de la casilla de verificación
            self.entregado_var.set(valores[6] is not None)  # Asumiendo que la fecha de entrega es el índice 6

    def limpiar_campos_persona(self):
        for campo, entry in self.campos_persona.items():
            if isinstance(entry, DateEntry):
                entry.set_date(None)  # Limpiar campos de fecha
            else:
                entry.delete(0, tk.END)  # Limpiar campos normales
        if self.tree_personas.selection():
            self.tree_personas.selection_remove(self.tree_personas.selection())


    def eliminar_imagen(self):
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un artículo para eliminar su imagen")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la imagen?"):
            try:
                item = self.tree_inventario.item(seleccion[0])
                id_articulo = item['values'][0]
                
                # Usar el método específico para actualizar solo la imagen
                if self.db.actualizar_imagen_articulo(id_articulo, None):
                    messagebox.showinfo("Éxito", "Imagen eliminada correctamente")
                    self.label_imagen.configure(text="No hay imagen", image='')  # Cambiado de image_label a label_imagen
                    self.label_imagen.image = None  # Limpiar la referencia de la imagen
                    self.actualizar_lista_inventario()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la imagen")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar la imagen: {str(e)}")

    def agregar_articulo(self):
        valores = {campo: entry.get() for campo, entry in self.campos_inventario.items()}
        
        # Validar campos numéricos
        try:
            valores['cantidad_disponible'] = int(valores['cantidad_disponible'])
        except ValueError:
            messagebox.showwarning("Error", "La cantidad debe ser un número")
            return
        
        # Manejar la imagen
        if self.ruta_imagen:
            nombre_archivo = f"imagenes/{os.path.basename(self.ruta_imagen)}"
            os.makedirs("imagenes", exist_ok=True)
            Image.open(self.ruta_imagen).save(nombre_archivo)
            valores['imagen'] = nombre_archivo
        else:
            valores['imagen'] = None
        
        # Asegúrate de incluir la fecha de ingreso
        fecha_ingreso = valores.pop('fecha_ingreso', None)  # Extraer la fecha de ingreso

        if self.db.agregar_articulo(**valores, fecha_ingreso=fecha_ingreso):
            messagebox.showinfo("Éxito", "Artículo agregado correctamente")
            self.limpiar_campos_inventario()
            self.actualizar_lista_inventario()
        else:
            messagebox.showerror("Error", "No se pudo agregar el artículo")

    def actualizar_lista_inventario(self):
        """Actualiza los datos mostrados en el TreeView de Inventario."""
        # Limpiar la lista actual
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)

        # Obtener los artículos de la base de datos
        articulos = self.db.obtener_articulos()  # Asegúrate de tener este método en GestionDB

        # Agregar los artículos a la lista
        for articulo in articulos:
            self.tree_inventario.insert('', 'end', values=articulo)

    def seleccionar_articulo(self, event):
        seleccion = self.tree_inventario.selection()
        if seleccion:
            item = self.tree_inventario.item(seleccion[0])
            valores = item['values']
            
            # Llenar campos
            for i, (campo, entry) in enumerate(self.campos_inventario.items()):
                entry.delete(0, tk.END)
                entry.insert(0, valores[i + 1])  # Asegúrate de que esto esté correcto
            
            # Cargar imagen si existe
            articulo = self.db.obtener_articulo(valores[0])
            if articulo and articulo[4]:  # Si hay ruta de imagen
                self.ruta_imagen = articulo[4]
                try:
                    imagen = Image.open(self.ruta_imagen)
                    imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(imagen)
                    self.label_imagen.configure(image=foto)
                    self.label_imagen.image = foto  # Mantener referencia
                except Exception as e:
                    print(f"Error al cargar la imagen: {e}")
                    self.ruta_imagen = None
                    self.label_imagen.configure(image='')  # Limpiar imagen si hay error
            else:
                # Limpiar el Label de la imagen si no hay imagen
                self.label_imagen.configure(image='')
                self.label_imagen.image = None  # Asegurarse de que la referencia se limpie
            
            # Establecer la fecha de ingreso en el DateEntry
            if isinstance(valores[5], str):  # Si es una cadena, intenta convertirla a fecha
                try:
                    fecha_peticion = datetime.strptime(valores[5], '%Y-%m-%d')  # Ajusta el formato según sea necesario
                    self.campos_inventario['fecha_ingreso'].set_date(fecha_peticion)
                except ValueError:
                    print(f"Error: {valores[5]} no es una fecha válida.")
            else:
                self.campos_inventario['fecha_ingreso'].set_date(valores[5])  # Si ya es un objeto datetime

    def buscar_articulos(self, event=None):
        """Filtra y muestra los artículos en inventario según el término de búsqueda."""
        filtro = self.entry_busqueda_inventario.get().lower()  # Obtener el término de búsqueda en minúsculas
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)  # Limpiar la tabla

        # Obtener los artículos filtrados de la base de datos
        articulos = self.db.obtener_inventario(filtro)  # Asegúrate de que este método exista y acepte un filtro

        # Insertar los artículos filtrados en la tabla
        for articulo in articulos:
            self.tree_inventario.insert('', 'end', values=articulo[:-1])  # Excluir la ruta de la imagen si es necesario

    def limpiar_campos_inventario(self):
        # Limpiar campos de texto
        for entry in self.campos_inventario.values():
            entry.delete(0, tk.END)
        
        # Limpiar imagen
        self.label_imagen.configure(image='')
        self.label_imagen.image = None
        self.ruta_imagen = None  # Importante: resetear la ruta de la imagen
        
        # Deseleccionar item en el TreeView si hay alguno seleccionado
        if self.tree_inventario.selection():
            self.tree_inventario.selection_remove(self.tree_inventario.selection())

    def eliminar_articulo(self):
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un artículo para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este artículo?"):
            item = self.tree_inventario.item(seleccion[0])
            id_articulo = item['values'][0]
            
            if self.db.eliminar_articulo(id_articulo):
                messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                self.limpiar_campos_inventario()
                self.actualizar_lista_inventario()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el artículo")

    def actualizar_articulo(self):
        """Actualiza los datos del artículo seleccionado"""
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un artículo para actualizar")
            return
        
        try:
            # Obtener el ID del artículo seleccionado
            item = self.tree_inventario.item(seleccion[0])
            id_articulo = item['values'][0]
            
            # Obtener los valores de los campos
            nombre = self.campos_inventario['nombre_articulo'].get()
            descripcion = self.campos_inventario['descripcion'].get()
            cantidad = self.campos_inventario['cantidad_disponible'].get()
            fecha = self.campos_inventario['fecha_ingreso'].get()
            
            # Validar campos obligatorios
            if not nombre or not cantidad:
                messagebox.showwarning("Error", "El nombre y la cantidad son obligatorios")
                return
            
            try:
                cantidad = int(cantidad)
            except ValueError:
                messagebox.showwarning("Error", "La cantidad debe ser un número entero")
                return
            
            # Obtener la imagen actual del artículo
            articulo_actual = self.db.obtener_articulo(id_articulo)
            imagen_actual = articulo_actual[4] if articulo_actual else None
            
            # Actualizar el artículo
            if self.db.actualizar_articulo(
                id_articulo=id_articulo,
                nombre_articulo=nombre,
                descripcion=descripcion,
                cantidad_disponible=cantidad,
                imagen=imagen_actual,  # Mantener la imagen actual
                fecha_ingreso=fecha
            ):
                messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
                self.limpiar_campos_inventario()
                self.actualizar_lista_inventario()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el artículo")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar el artículo: {str(e)}")

    def actualizar_lista_transacciones(self):
        # Limpiar el TreeView
        for item in self.tree_transacciones.get_children():
            self.tree_transacciones.delete(item)

        # Obtener y mostrar las transacciones
        transacciones = self.db.obtener_transacciones()  # Asegúrate de tener este método en tu clase GestionDB
        for transaccion in transacciones:
            # Formatear la fecha para mostrar solo el día (sin hora ni segundos)
            fecha_formateada = transaccion[6].split(" ")[0]  # Suponiendo que la fecha está en el índice 6
            self.tree_transacciones.insert('', 'end', values=(transaccion[0], transaccion[1], transaccion[2], transaccion[3], transaccion[4], transaccion[5], fecha_formateada))

    def abrir_ventana_agregar_persona(self):
        ventana = tk.Toplevel()
        VentanaAgregarPersona(ventana, self)

    def exportar_a_excel(self):
        success, message = self.db.exportar_a_csv('personas')
        messagebox.showinfo("Exportar a Excel", message)

    def abrir_ventana_agregar_producto(self):
        ventana = tk.Toplevel(self.root)
        VentanaAgregarProducto(ventana, self)

    def eliminar_transaccion(self):
        seleccion = self.tree_transacciones.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una transacción para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta transacción?"):
            item = self.tree_transacciones.item(seleccion[0])
            id_transaccion = item['values'][0]  # Asumiendo que el ID es el primer valor
            
            if self.db.eliminar_transaccion(id_transaccion):
                messagebox.showinfo("Éxito", "Transacción eliminada correctamente")
                self.actualizar_lista_transacciones()  # Actualizar la lista de transacciones
            else:
                messagebox.showerror("Error", "No se pudo eliminar la transacción")

    def abrir_ventana_editar_persona(self):
        seleccion = self.tree_personas.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una persona para editar")
            return

        item = self.tree_personas.item(seleccion[0])
        valores = item['values'][1:]  # Ignorar el primer elemento (ID)

        print("Valores seleccionados:", valores)  # Imprimir para depuración

        # Crear la ventana de edición
        ventana = tk.Toplevel()
        VentanaEditarPersona(ventana, self, valores)

    def abrir_ventana_fecha_entrega(self):
        seleccion = self.tree_personas.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una persona para establecer la fecha de entrega")
            return

        item = self.tree_personas.item(seleccion[0])
        valores = item['values']
        ventana = tk.Toplevel()
        VentanaFechaEntrega(ventana, self, valores[0])  # Pasar el ID de la persona

    def mostrar_todas_transacciones(self):
        """Muestra todas las transacciones sin filtros"""
        self.combo_tipo.set('')
        self.combo_articulo.set('')
        self.filtrar_fecha_var.set(True)
        self.actualizar_lista_transacciones()

    def filtrar_por_tipo(self, tipo):
        """Filtra las transacciones por tipo (entrada/salida)"""
        self.combo_tipo.set(tipo)
        self.combo_articulo.set('')
        self.filtrar_fecha_var.set(True)
        self.filtrar_transacciones()

    def filtrar_personas(self, event=None):
        # Obtener valores de búsqueda
        nombre = self.combobox_nombre.get().lower()  # Convertir a minúsculas
        articulo = self.entry_buscar_articulo.get().lower()  # Convertir a minúsculas
        municipio = self.combobox_municipio.get()  # Asegúrate de que esto esté definido
        estado = self.combo_estado.get()

        # Limpiar TreeView
        for item in self.tree_personas.get_children():
            self.tree_personas.delete(item)

        # Obtener todas las personas
        personas = self.db.obtener_personas()

        # Filtrar personas
        for persona in personas:
            # Convertir valores a minúsculas para comparación
            nombre_persona = str(persona[1]).lower()  # Convertir a minúsculas
            articulo_persona = str(persona[2]).lower()  # Convertir a minúsculas
            municipio_persona = str(persona[5])
            fecha_entrega = persona[7]

            # Determinar estado
            estado_persona = "Entregado" if fecha_entrega and fecha_entrega not in ['None', '', 'Pendiente'] else "Pendiente"

            # Aplicar filtros
            mostrar = True
            if nombre and not nombre_persona.startswith(nombre):  # Cambiado a startswith
                mostrar = False
            if articulo and articulo and not articulo_persona.startswith(articulo):  # Cambiado a startswith
                mostrar = False
            if municipio and municipio != municipio_persona:
                mostrar = False
            if estado != 'Todos' and estado != estado_persona:
                mostrar = False

            # Mostrar si pasa todos los filtros
            if mostrar:
                # Convertir None o '' a 'Pendiente' para la visualización
                valores = list(persona)
                valores[-1] = 'Pendiente' if not valores[-1] or valores[-1] in ['None', ''] else valores[-1]
                self.tree_personas.insert('', 'end', values=valores)

class VentanaTransacciones:
    def __init__(self, master, app, db):
        self.master = master
        self.app = app  # Guardar referencia a la instancia principal
        self.db = db
        self.master.title("Registrar Transacción")
        self.master.geometry("400x300")

        # Agregar un marco para el diseño
        frame = ttk.Frame(master, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Artículo
        tk.Label(frame, text="Seleccionar Artículo:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_articulos = ttk.Combobox(frame)
        self.combo_articulos.grid(row=0, column=1, padx=5, pady=5)
        self.cargar_articulos()  # Cargar artículos al inicializar

        # Tipo de transacción
        tk.Label(frame, text="Tipo de Transacción:").grid(row=1, column=0, padx=5, pady=5)
        self.tipo_transaccion = ttk.Combobox(frame, values=["entrada", "salida"])
        self.tipo_transaccion.grid(row=1, column=1, padx=5, pady=5)

        # Cantidad
        tk.Label(frame, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        self.campo_cantidad = tk.Entry(frame)
        self.campo_cantidad.grid(row=2, column=1, padx=5, pady=5)

        # Fecha
        tk.Label(frame, text="Fecha:").grid(row=3, column=0, padx=5, pady=5)
        self.campo_fecha = DateEntry(frame, width=17, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.campo_fecha.grid(row=3, column=1, padx=5, pady=5)

        # Descripción
        tk.Label(frame, text="Descripción (opcional):").grid(row=4, column=0, padx=5, pady=5)
        self.campo_descripcion = tk.Entry(frame)
        self.campo_descripcion.grid(row=4, column=1, padx=5, pady=5)

        # Botón para registrar transacción
        self.boton_registrar = tk.Button(frame, text="Registrar Transacción", command=self.registrar_transaccion)
        self.boton_registrar.grid(row=5, columnspan=2, pady=10)

    def cargar_articulos(self):
        articulos = self.db.obtener_inventario()  # Obtener artículos de la base de datos
        self.combo_articulos['values'] = [articulo[1] for articulo in articulos]  # Suponiendo que el nombre del artículo está en la segunda columna

    def registrar_transaccion(self):
        articulo_seleccionado = self.combo_articulos.get()
        tipo = self.tipo_transaccion.get()
        cantidad = self.campo_cantidad.get()

        # Obtener el ID del artículo seleccionado
        articulos = self.db.obtener_inventario()
        id_articulo = next((articulo[0] for articulo in articulos if articulo[1] == articulo_seleccionado), None)

        if id_articulo is not None:
            try:
                cantidad = int(cantidad)  # Asegúrate de que la cantidad sea un número
                # Lógica para registrar la transacción
                if self.db.registrar_transaccion(id_articulo, tipo, cantidad):
                    messagebox.showinfo("Transacción", "Transacción registrada con éxito.")
                    
                    # Actualizar la lista de transacciones
                    self.app.actualizar_lista_transacciones()  # Actualiza la lista de transacciones
                    
                    # Actualizar la lista de inventario
                    self.app.actualizar_lista_inventario()  # Actualiza la lista de inventario
                    
                else:
                    messagebox.showerror("Error", "No se pudo registrar la transacción.")
            except ValueError:
                messagebox.showwarning("Advertencia", "La cantidad debe ser un número válido.")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un artículo válido.")

class VentanaAgregarPersona:
    def __init__(self, master, app, persona=None):
        self.master = master
        self.app = app
        self.persona = persona  # Almacenar la persona si se está editando
        self.master.title("Agregar Persona" if persona is None else "Editar Persona")
        self.master.geometry("400x600")
        self.master.minsize(400, 600)

        # Configurar el estilo
        style = ttk.Style()
        style.configure('Custom.TFrame', background='#f0f0f0', padding=15)
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Field.TLabel', font=('Helvetica', 10))
        style.configure('Custom.TButton', font=('Helvetica', 10), padding=10)

        # Marco principal con padding y color de fondo
        main_frame = ttk.Frame(master, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Título de la ventana
        ttk.Label(main_frame, text="Registro de Nueva Persona", style='Header.TLabel').pack(pady=(0, 20))

        # Marco para los campos del formulario
        form_frame = ttk.LabelFrame(main_frame, text="Datos Personales", padding=15)
        form_frame.pack(fill='x', padx=10)

        # Campos del formulario con mejor espaciado y alineación
        campos = [
            ('Nombre:', 'entry_nombre'),
            ('Artículo:', 'entry_articulo'),
            ('Teléfono:', 'entry_telefono'),
            ('Dirección:', 'entry_direccion'),
            ('Municipio:', 'combobox_municipio')
        ]

        for i, (label, campo) in enumerate(campos):
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', pady=5)
            
            ttk.Label(frame, text=label, style='Field.TLabel', width=15).pack(side='left')
            
            if campo == 'combobox_municipio':
                widget = ttk.Combobox(frame, values=self.app.municipios, width=30)
            else:
                widget = ttk.Entry(frame, width=32)
            widget.pack(side='left', padx=(10, 0))
            setattr(self, campo, widget)

        # Marco para las fechas
        dates_frame = ttk.LabelFrame(main_frame, text="Fechas", padding=15)
        dates_frame.pack(fill='x', padx=10, pady=15)

        # Campo de fecha de petición
        fecha_pet_frame = ttk.Frame(dates_frame)
        fecha_pet_frame.pack(fill='x', pady=5)
        ttk.Label(fecha_pet_frame, text="Fecha Petición:", style='Field.TLabel', width=15).pack(side='left')
        self.entry_fecha_peticion = DateEntry(fecha_pet_frame, width=30,
                                            background='darkblue',
                                            foreground='white',
                                            borderwidth=2,
                                            date_pattern='yyyy-mm-dd')
        self.entry_fecha_peticion.pack(side='left', padx=(10, 0))

        # Campo de fecha de entrega
        fecha_ent_frame = ttk.Frame(dates_frame)
        fecha_ent_frame.pack(fill='x', pady=5)
        ttk.Label(fecha_ent_frame, text="Fecha Entrega:", style='Field.TLabel', width=15).pack(side='left')
        self.entry_fecha_entrega = DateEntry(fecha_ent_frame, width=30,
                                           background='darkblue',
                                           foreground='white',
                                           borderwidth=2,
                                           date_pattern='yyyy-mm-dd')
        self.entry_fecha_entrega.pack(side='left', padx=(10, 0))

        # Checkbutton para marcar la fecha de entrega como pendiente
        self.check_pendiente = tk.BooleanVar()
        ttk.Checkbutton(dates_frame, 
                       text="Fecha de Entrega Pendiente", 
                       variable=self.check_pendiente,
                       command=self.toggle_fecha_estado).pack(pady=10)

        # Marco para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)

        if self.persona:  # Si hay una persona, mostrar el botón de actualizar
            ttk.Button(button_frame, text="Actualizar", 
                      style='Custom.TButton',
                      command=self.actualizar_persona).pack(side='left', padx=10, expand=True)
        else:  # Si no, mostrar el botón de agregar
            ttk.Button(button_frame, text="Agregar", 
                      style='Custom.TButton',
                      command=self.agregar_persona).pack(side='left', padx=10, expand=True)

        ttk.Button(button_frame, text="Cancelar", 
                  style='Custom.TButton',
                  command=self.master.destroy).pack(side='right', padx=10, expand=True)

        if self.persona:  # Si se está editando, cargar los valores
            self.cargar_valores(self.persona)

    def cargar_valores(self, persona):
        # Cargar los valores de la persona en los campos
        self.entry_nombre.insert(0, persona[1])
        self.entry_articulo.insert(0, persona[2])
        self.entry_telefono.insert(0, persona[3])
        self.entry_direccion.insert(0, persona[4])
        self.combobox_municipio.set(persona[5])
        self.entry_fecha_peticion.set_date(persona[6])
        
        if persona[7] and persona[7] not in ['None', '', 'Pendiente']:
            self.entry_fecha_entrega.set_date(persona[7])
            self.check_pendiente.set(False)
            self.entry_fecha_entrega.config(state='normal')
        else:
            self.check_pendiente.set(True)
            self.entry_fecha_entrega.config(state='disabled')

    def agregar_persona(self):
        nombre = self.entry_nombre.get()
        articulo = self.entry_articulo.get()
        telefono = self.entry_telefono.get()
        direccion = self.entry_direccion.get()
        municipio = self.combobox_municipio.get()
        fecha_peticion = self.entry_fecha_peticion.get()
        fecha_entrega = self.entry_fecha_entrega.get() if not self.check_pendiente.get() else None

        # Crear un diccionario con los valores
        valores = {
            'nombre': nombre,
            'articulo': articulo,
            'telefono': telefono,
            'direccion': direccion,
            'municipio': municipio,
            'fecha_peticion': fecha_peticion,
            'fecha_entrega': fecha_entrega
        }

        # Llamar al método para agregar la persona
        if self.app.db.agregar_persona(**valores):
            messagebox.showinfo("Éxito", "Persona agregada correctamente")
            self.master.destroy()  # Cerrar la ventana
            self.app.actualizar_lista_personas()  # Actualizar la lista de personas
        else:
            messagebox.showerror("Error", "No se pudo agregar la persona. Verifique los datos.")

    def actualizar_persona(self):
        # Recoger los datos de los campos de entrada
        nombre = self.entry_nombre.get()
        articulo = self.entry_articulo.get()
        telefono = self.entry_telefono.get()
        direccion = self.entry_direccion.get()
        municipio = self.combobox_municipio.get()
        fecha_peticion = self.entry_fecha_peticion.get()
        fecha_entrega = self.entry_fecha_entrega.get() if not self.check_pendiente.get() else None

        # Crear un diccionario con los valores
        valores = {
            'nombre': nombre,
            'articulo': articulo,
            'telefono': telefono,
            'direccion': direccion,
            'municipio': municipio,
            'fecha_peticion': fecha_peticion,
            'fecha_entrega': fecha_entrega
        }

        # Llamar al método para actualizar la persona
        if self.app.db.actualizar_persona(self.persona[0], **valores):  # Usar el ID de la persona
            messagebox.showinfo("Éxito", "Persona actualizada correctamente")
            self.master.destroy()  # Cerrar la ventana
            self.app.actualizar_lista_personas()  # Actualizar la lista de personas
        else:
            messagebox.showerror("Error", "No se pudo actualizar la persona. Verifique los datos.")

    def toggle_fecha_estado(self):
        """Controla la visibilidad y estado del campo de fecha"""
        if self.check_pendiente.get():
            self.entry_fecha_entrega.config(state='disabled')
        else:
            self.entry_fecha_entrega.config(state='normal')

class VentanaAgregarProducto:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.master.title("Agregar Producto")
        self.master.geometry("400x400")  # Ajustar el tamaño de la ventana

        # Estilo
        style = ttk.Style()
        style.configure('Custom.TFrame', background='#f0f0f0', padding=15)
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Field.TLabel', font=('Helvetica', 10))
        style.configure('Custom.TButton', font=('Helvetica', 10), padding=10)

        # Marco principal
        main_frame = ttk.Frame(master, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True)

        # Título de la ventana
        ttk.Label(main_frame, text="Agregar Nuevo Producto", style='Header.TLabel').pack(pady=(0, 20))

        # Marco para los campos del formulario
        form_frame = ttk.LabelFrame(main_frame, text="Detalles del Producto", padding=15)
        form_frame.pack(fill='x', padx=10)

        # Campos del formulario
        campos = [
            ('Nombre del Artículo:', 'entry_nombre_articulo'),
            ('Descripción:', 'entry_descripcion'),
            ('Cantidad Disponible:', 'entry_cantidad'),
            ('Fecha de Ingreso:', 'entry_fecha_ingreso')
        ]

        for label, campo in campos:
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', pady=5)

            ttk.Label(frame, text=label, style='Field.TLabel', width=20).pack(side='left')
            if campo == 'entry_fecha_ingreso':
                widget = DateEntry(frame, width=30, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            else:
                widget = ttk.Entry(frame, width=30)
            widget.pack(side='left', padx=(10, 0))
            setattr(self, campo, widget)

        # Marco para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)

        # Botones
        ttk.Button(button_frame, text="Agregar", style='Custom.TButton', command=self.agregar_producto).pack(side='left', padx=10, expand=True)
        ttk.Button(button_frame, text="Cancelar", style='Custom.TButton', command=self.master.destroy).pack(side='right', padx=10, expand=True)

    def agregar_producto(self):
        nombre_articulo = self.entry_nombre_articulo.get()
        descripcion = self.entry_descripcion.get()
        cantidad_disponible = self.entry_cantidad.get()
        fecha_ingreso = self.entry_fecha_ingreso.get()

        # Validar campos obligatorios
        if not nombre_articulo or not cantidad_disponible:
            messagebox.showwarning("Advertencia", "Nombre del artículo y cantidad son obligatorios.")
            return

        try:
            cantidad_disponible = int(cantidad_disponible)  # Convertir a entero
        except ValueError:
            messagebox.showwarning("Error", "La cantidad debe ser un número.")
            return

        # Agregar el producto a la base de datos
        if self.app.db.agregar_articulo(nombre_articulo, descripcion, cantidad_disponible, None, fecha_ingreso):
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            self.master.destroy()  # Cerrar la ventana
            self.app.actualizar_lista_inventario()  # Actualizar la lista de inventario
        else:
            messagebox.showerror("Error", "No se pudo agregar el producto. Verifique los datos.")

class VentanaEditarPersona:
    def __init__(self, master, app, valores):
        self.master = master
        self.app = app
        self.master.title("Editar Persona")
        self.master.geometry("400x600")  # Aumentar la altura para acomodar todos los elementos
        self.master.minsize(400, 600)  # Establecer un tamaño mínimo

        # Configurar el estilo
        style = ttk.Style()
        style.configure('Custom.TFrame', background='#f0f0f0', padding=15)
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Field.TLabel', font=('Helvetica', 10))
        style.configure('Custom.TButton', font=('Helvetica', 10), padding=10)

        # Marco principal con padding y color de fondo
        main_frame = ttk.Frame(master, style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Título de la ventana
        ttk.Label(main_frame, text="Editar Persona", style='Header.TLabel').pack(pady=(0, 20))

        # Marco para los campos del formulario
        form_frame = ttk.LabelFrame(main_frame, text="Datos Personales", padding=15)
        form_frame.pack(fill='x', padx=10)

        # Asignar valores a los campos
        campos = [
            ('Nombre:', 'entry_nombre'),
            ('Artículo:', 'entry_articulo'),
            ('Teléfono:', 'entry_telefono'),
            ('Dirección:', 'entry_direccion'),
            ('Municipio:', 'combobox_municipio')
        ]

        for i, (label, campo) in enumerate(campos):
            frame = ttk.Frame(form_frame)
            frame.pack(fill='x', pady=5)
            
            ttk.Label(frame, text=label, style='Field.TLabel', width=15).pack(side='left')
            widget = ttk.Entry(frame, width=32) if campo != 'combobox_municipio' else ttk.Combobox(frame, values=self.app.municipios, width=30)
            widget.pack(side='left', padx=(10, 0))
            setattr(self, campo, widget)

        # Marco para las fechas
        dates_frame = ttk.LabelFrame(main_frame, text="Fechas", padding=15)
        dates_frame.pack(fill='x', padx=10, pady=15)

        # Campo de fecha de petición
        fecha_pet_frame = ttk.Frame(dates_frame)
        fecha_pet_frame.pack(fill='x', pady=5)
        ttk.Label(fecha_pet_frame, text="Fecha Petición:", style='Field.TLabel', width=15).pack(side='left')
        self.entry_fecha_peticion = DateEntry(fecha_pet_frame, width=30,
                                            background='darkblue',
                                            foreground='white',
                                            borderwidth=2,
                                            date_pattern='yyyy-mm-dd')
        self.entry_fecha_peticion.pack(side='left', padx=(10, 0))

        # Campo de fecha de entrega
        fecha_ent_frame = ttk.Frame(dates_frame)
        fecha_ent_frame.pack(fill='x', pady=5)
        ttk.Label(fecha_ent_frame, text="Fecha Entrega:", style='Field.TLabel', width=15).pack(side='left')
        self.entry_fecha_entrega = DateEntry(fecha_ent_frame, width=30,
                                           background='darkblue',
                                           foreground='white',
                                           borderwidth=2,
                                           date_pattern='yyyy-mm-dd')
        self.entry_fecha_entrega.pack(side='left', padx=(10, 0))

        # Checkbutton para marcar la fecha de entrega como pendiente
        self.check_pendiente = tk.BooleanVar()
        ttk.Checkbutton(dates_frame, 
                       text="Fecha de Entrega Pendiente", 
                       variable=self.check_pendiente,
                       command=self.toggle_fecha_estado).pack(pady=10)

        # Marco para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)

        # Botones con mejor estilo y espaciado
        ttk.Button(button_frame, text="Actualizar", 
                  style='Custom.TButton',
                  command=self.actualizar_persona).pack(side='left', padx=10, expand=True)
        ttk.Button(button_frame, text="Cancelar", 
                  style='Custom.TButton',
                  command=self.master.destroy).pack(side='right', padx=10, expand=True)

        # Asignar valores iniciales a los campos
        self.cargar_valores(valores)

    def toggle_fecha_estado(self):
        """Controla la visibilidad y estado del campo de fecha"""
        if self.check_pendiente.get():
            self.entry_fecha_entrega.config(state='disabled')
        else:
            self.entry_fecha_entrega.config(state='normal')

    def actualizar_persona(self):
        # Obtener valores básicos
        nombre = self.entry_nombre.get()
        articulo = self.entry_articulo.get()
        telefono = self.entry_telefono.get()
        direccion = self.entry_direccion.get()
        municipio = self.combobox_municipio.get()
        fecha_peticion = self.entry_fecha_peticion.get()
        
        # Determinar fecha de entrega
        fecha_entrega = None if self.check_pendiente.get() else self.entry_fecha_entrega.get()

        # Validar campos obligatorios
        if not nombre or not telefono:
            messagebox.showwarning("Advertencia", "Nombre y Teléfono son obligatorios.")
            return

        # Obtener ID de la persona seleccionada
        seleccion = self.app.tree_personas.selection()
        if not seleccion:
            messagebox.showwarning("Error", "No hay persona seleccionada")
            return
            
        item = self.app.tree_personas.item(seleccion[0])
        id_persona = item['values'][0]

        # Actualizar en la base de datos
        if self.app.db.actualizar_persona(
            id_persona,
            nombre=nombre,
            articulo=articulo,
            telefono=telefono,
            direccion=direccion,
            municipio=municipio,
            fecha_peticion=fecha_peticion,
            fecha_entrega=fecha_entrega
        ):
            messagebox.showinfo("Éxito", "Persona actualizada correctamente")
            self.master.destroy()
            self.app.actualizar_lista_personas()
        else:
            messagebox.showerror("Error", "No se pudo actualizar la persona")

class VentanaFechaEntrega:
    def __init__(self, master, app, id_persona):
        self.master = master
        self.app = app
        self.id_persona = id_persona
        self.master.title("Establecer Fecha de Entrega")
        self.master.geometry("300x200")

        # Crear un marco para el diseño
        frame = ttk.Frame(master, padding="20")
        frame.pack(fill='both', expand=True)

        # Campo para seleccionar la fecha
        ttk.Label(frame, text="Fecha de Entrega:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        self.entry_fecha_entrega = DateEntry(frame, width=17, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_fecha_entrega.grid(row=0, column=1, padx=5, pady=5)

        # Estilo para el botón de cancelar
        style = ttk.Style()
        style.configure('Red.TButton', background='#FF6F61', foreground='white')  # Rojo pastel

        # Botones para confirmar y cancelar
        ttk.Button(frame, text="Confirmar Entrega", command=self.confirmar_entrega, style='Accent.TButton').grid(row=1, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=self.master.destroy, style='Red.TButton').grid(row=1, column=1, pady=10)

    def confirmar_entrega(self):
        fecha_entrega = self.entry_fecha_entrega.get()
        
        # Actualizar solo la fecha de entrega
        if self.app.db.actualizar_persona(self.id_persona, fecha_entrega=fecha_entrega):
            messagebox.showinfo("Éxito", "Fecha de entrega actualizada correctamente")
            self.master.destroy()
            self.app.actualizar_lista_personas()  # Actualizar la lista de personas
        else:
            messagebox.showerror("Error", "No se pudo actualizar la fecha de entrega")

class VentanaEditarArticulo:
    def __init__(self, master, app, articulo):
        self.master = master
        self.app = app
        self.articulo = articulo
        
        # Configurar ventana
        self.master.title("Editar Artículo")
        self.master.geometry("600x500")
        
        # Estilo personalizado
        style = ttk.Style()
        style.configure('Heading.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Custom.TButton', padding=6, font=('Helvetica', 9))
        style.configure('Danger.TButton', padding=6)
        style.configure('Success.TButton', padding=6)
        
        # Frame principal con padding
        main_frame = ttk.Frame(master, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(main_frame, text="Editar Artículo", style='Heading.TLabel').pack(pady=(0, 20))
        
        # Frame para el contenido
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Frame izquierdo para los campos
        left_frame = ttk.LabelFrame(content_frame, text="Detalles del Artículo", padding="10")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Campos del formulario
        self.campos = {}
        campos_config = [
            ('Nombre del Artículo:', 'nombre'),
            ('Descripción:', 'descripcion'),
            ('Cantidad Disponible:', 'cantidad'),
            ('Fecha de Ingreso:', 'fecha')
        ]
        
        for i, (label_text, campo_name) in enumerate(campos_config):
            frame = ttk.Frame(left_frame)
            frame.pack(fill='x', pady=5)
            
            ttk.Label(frame, text=label_text, width=15).pack(side='left')
            
            if campo_name == 'fecha':
                widget = DateEntry(frame, width=25,
                                 background='darkblue',
                                 foreground='white',
                                 borderwidth=2,
                                 date_pattern='yyyy-mm-dd')
            else:
                widget = ttk.Entry(frame, width=25)
            widget.pack(side='left', padx=5, fill='x', expand=True)
            self.campos[campo_name] = widget
        
        # Frame derecho para la imagen
        right_frame = ttk.LabelFrame(content_frame, text="Imagen del Artículo", padding="10")
        right_frame.pack(side='right', fill='both', padx=(10, 0))
        
        # Label para la imagen
        self.image_label = ttk.Label(right_frame, text="No hay imagen")
        self.image_label.pack(pady=10)
        
        # Frame para los botones de imagen
        image_buttons_frame = ttk.Frame(right_frame)
        image_buttons_frame.pack(pady=10)
        
        # Botones para la imagen
        ttk.Button(image_buttons_frame, text="Seleccionar Imagen",
                  command=self.seleccionar_imagen,
                  style='Custom.TButton').pack(side='left', padx=5)
        
        ttk.Button(image_buttons_frame, text="Eliminar Imagen",
                  command=self.eliminar_imagen,
                  style='Custom.TButton').pack(side='left', padx=5)
        
        # Frame para los botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Botones de acción
        ttk.Button(button_frame, text="Actualizar",
                  command=self.actualizar_articulo,
                  style='Success.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Cancelar",
                  command=self.master.destroy,
                  style='Danger.TButton').pack(side='right', padx=5)
        
        # Cargar datos del artículo
        self.cargar_datos_articulo()
    
    def cargar_datos_articulo(self):
        """Carga los datos del artículo en los campos"""
        self.campos['nombre'].insert(0, self.articulo[1])
        self.campos['descripcion'].insert(0, self.articulo[2])
        self.campos['cantidad'].insert(0, str(self.articulo[3]))
        self.campos['fecha'].set_date(self.articulo[5])
        
        # Cargar imagen si existe
        if self.articulo[4] and self.articulo[4] != 'None':
            self.mostrar_imagen(self.articulo[4])
    
    def actualizar_articulo(self):
        """Actualiza el artículo con los nuevos datos"""
        try:
            # Obtener valores de los campos
            nombre = self.campos['nombre'].get()
            descripcion = self.campos['descripcion'].get()
            cantidad = self.campos['cantidad'].get()
            fecha = self.campos['fecha'].get()
            
            # Validaciones
            if not nombre or not cantidad:
                messagebox.showwarning("Advertencia", "Nombre y cantidad son campos obligatorios.")
                return
            
            try:
                cantidad = int(cantidad)
            except ValueError:
                messagebox.showwarning("Error", "La cantidad debe ser un número entero.")
                return
            
            # Actualizar en la base de datos
            if self.app.db.actualizar_articulo(
                self.articulo[0],  # ID
                nombre,
                descripcion,
                cantidad,
                self.articulo[4],  # Imagen actual
                fecha
            ):
                messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
                self.app.actualizar_lista_inventario()  # Actualizar la lista en la ventana principal
                self.master.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el artículo")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def seleccionar_imagen(self):
        """Permite seleccionar una nueva imagen para el artículo"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            try:
                if self.app.db.actualizar_articulo(
                    self.articulo[0],
                    self.campos['nombre'].get(),
                    self.campos['descripcion'].get(),
                    int(self.campos['cantidad'].get()),
                    file_path,
                    self.campos['fecha'].get()
                ):
                    messagebox.showinfo("Éxito", "Imagen actualizada correctamente")
                    self.mostrar_imagen(file_path)
                    self.articulo = list(self.articulo)
                    self.articulo[4] = file_path
                    self.app.actualizar_lista_inventario()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la imagen")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar la imagen: {str(e)}")
    
    def eliminar_imagen(self):
        """Elimina la imagen del artículo"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la imagen?"):
            try:
                if self.app.db.actualizar_articulo(
                    self.articulo[0],
                    self.campos['nombre'].get(),
                    self.campos['descripcion'].get(),
                    int(self.campos['cantidad'].get()),
                    None,
                    self.campos['fecha'].get()
                ):
                    messagebox.showinfo("Éxito", "Imagen eliminada correctamente")
                    self.image_label.configure(text="No hay imagen")
                    self.articulo = list(self.articulo)
                    self.articulo[4] = None
                    self.app.actualizar_lista_inventario()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la imagen")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar la imagen: {str(e)}")
    
    def mostrar_imagen(self, ruta_imagen):
        """Muestra la imagen en el label de imagen"""
        try:
            imagen = Image.open(ruta_imagen)
            imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)
            foto = ImageTk.PhotoImage(imagen)
            self.image_label.configure(image=foto)
            self.image_label.image = foto
        except Exception as e:
            self.image_label.configure(text="Error al cargar la imagen")
            print(f"Error al cargar la imagen: {str(e)}")

# Para abrir la ventana de transacciones
def abrir_ventana_transacciones(app, db):
    ventana = tk.Toplevel()
    VentanaTransacciones(ventana, app, db)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()