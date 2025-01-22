import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from gestion import GestionDB
from tkcalendar import DateEntry
from datetime import datetime
import shutil
import time

class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, 
                         justify='left',
                         background="#ffffe0", 
                         relief='solid', 
                         borderwidth=1)
        label.pack()

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# Asegúrate de que esta clase esté definida antes de usarla en tu aplicación

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Inventario")
        
        # Inicializar la base de datos con el nombre correcto
        self.db = GestionDB('gestion_inventario.db')
        
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
                       background='#A8D5BA',  # Verde pastel mate
                       foreground='black',
                       padding=(10, 2))  # Reducir el padding vertical
        style.configure('Edit.TButton', 
                       background='#A0C4FF',  # Azul pastel mate
                       foreground='black',
                       padding=(10, 2))  # Reducir el padding vertical
        style.configure('Date.TButton', 
                       background='#FFD6A5',  # Amarillo pastel mate
                       foreground='black',
                       padding=(10, 2))  # Reducir el padding vertical
        style.configure('Delete.TButton', 
                       background='#FFADAD',  # Rojo pastel mate
                       foreground='black',
                       padding=(10, 2))  # Reducir el padding vertical

        # Botón para agregar persona
        ttk.Button(frame_botones, text="Agregar Persona", 
                   command=self.abrir_ventana_agregar_persona,
                   style='Add.TButton').grid(row=0, column=0, padx=15, pady=5, sticky='w')

        # Botón para editar persona
        ttk.Button(frame_botones, text="Editar Persona", 
                   command=self.abrir_ventana_editar_persona,
                   style='Edit.TButton').grid(row=0, column=1, padx=15, pady=5, sticky='w')
        
        # Botón para establecer fecha de entrega
        ttk.Button(frame_botones, text="Establecer Fecha de Entrega", 
                   command=self.abrir_ventana_fecha_entrega,
                   style='Date.TButton').grid(row=0, column=2, padx=15, pady=5, sticky='w')
        
        # Botón para eliminar persona (separado con más padding)
        ttk.Button(frame_botones, text="Eliminar Persona", 
                   command=self.eliminar_persona,
                   style='Delete.TButton').grid(row=0, column=3, padx=(30, 15), pady=5, sticky='w')
        
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
        """Configura la pestaña de inventario con un diseño más profesional"""
        # Frame principal usando grid
        main_frame = ttk.Frame(self.tab_inventario)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        main_frame.grid_columnconfigure(0, weight=3)  # Columna izquierda más ancha
        main_frame.grid_columnconfigure(1, weight=2)  # Columna derecha más estrecha

        # Panel izquierdo (búsqueda y lista)
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Frame para búsqueda con estilo
        search_frame = ttk.LabelFrame(left_panel, text="Búsqueda de Artículos", padding=10)
        search_frame.pack(fill='x', pady=(0, 5))
        
        # Barra de búsqueda con icono
        ttk.Label(search_frame, text="Buscar:").pack(side='left', padx=5)
        self.entry_busqueda = ttk.Entry(search_frame)
        self.entry_busqueda.pack(side='left', fill='x', expand=True, padx=5)
        
        # Botones con estilo
        style = ttk.Style()
        style.configure('Accent.TButton', background='#4CAF50')
        
        ttk.Button(search_frame, text="Buscar", 
                   command=self.buscar_articulos,
                   style='Accent.TButton').pack(side='left', padx=5)
        
        ttk.Button(search_frame, text="Agregar Producto", 
                   command=self.abrir_ventana_agregar_producto,
                   style='Accent.TButton').pack(side='left', padx=5)

        # TreeView con estilo
        tree_frame = ttk.Frame(left_panel)
        tree_frame.pack(fill='both', expand=True)
        
        self.tree_inventario = ttk.Treeview(tree_frame, 
                                           columns=('ID', 'Nombre', 'Descripción', 'Cantidad', 'Imagen', 'Fecha'),
                                           show='headings',
                                           style='Custom.Treeview')
        
        # Configurar columnas
        self.tree_inventario.heading('ID', text='ID')
        self.tree_inventario.heading('Nombre', text='Nombre del Artículo')
        self.tree_inventario.heading('Descripción', text='Descripción')
        self.tree_inventario.heading('Cantidad', text='Cantidad')
        self.tree_inventario.heading('Imagen', text='Imagen')
        self.tree_inventario.heading('Fecha', text='Fecha de Ingreso')
        
        # Ajustar anchos de columna
        self.tree_inventario.column('ID', width=50)
        self.tree_inventario.column('Nombre', width=200)
        self.tree_inventario.column('Descripción', width=200)
        self.tree_inventario.column('Cantidad', width=100)
        self.tree_inventario.column('Imagen', width=150)
        self.tree_inventario.column('Fecha', width=100)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_inventario.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_inventario.xview)
        self.tree_inventario.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid del TreeView y scrollbars
        self.tree_inventario.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Panel derecho (detalles y imagen)
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        # Frame para detalles con estilo minimalista
        details_frame = ttk.LabelFrame(right_panel, text="Detalles del Artículo", padding=15)
        details_frame.pack(fill='x', pady=(0, 10))

        # Definir los campos de entrada
        self.campos_inventario = {}

        # Configurar estilo minimalista
        style = ttk.Style()
        style.configure('Minimal.TLabel', font=('Helvetica', 10))
        style.configure('Minimal.TEntry', padding=5)
        style.configure('Minimal.DateEntry', padding=5)
        style.configure('Minimal.TButton', 
                       font=('Helvetica', 9),
                       padding=8)

        # Crear campos con sus etiquetas
        campos = [
            ('Nombre:', 'entry_nombre'),
            ('Descripción:', 'entry_descripcion'),
            ('Cantidad:', 'entry_cantidad'), 
            ('Fecha de Ingreso:', 'entry_fecha')
        ]

        for i, (label, campo) in enumerate(campos):
            # Frame para cada campo para mejor alineación
            field_frame = ttk.Frame(details_frame)
            field_frame.grid(row=i, column=0, sticky='ew', pady=3)
            field_frame.grid_columnconfigure(1, weight=1)
            
            ttk.Label(field_frame, text=label, style='Minimal.TLabel').grid(row=0, column=0, padx=(0,10), sticky='e')
            
            if campo == 'entry_fecha':
                widget = DateEntry(field_frame, 
                                 width=25,
                                 background='white',
                                 foreground='black',
                                 borderwidth=1,
                                 date_pattern='yyyy-mm-dd',
                                 style='Minimal.DateEntry')
            else:
                widget = ttk.Entry(field_frame, width=30, style='Minimal.TEntry')
            widget.grid(row=0, column=1, sticky='ew')
            self.campos_inventario[campo] = widget

        # Frame para la imagen con estilo minimalista
        self.image_frame = ttk.LabelFrame(right_panel, text="Imagen del Artículo", padding=15)
        self.image_frame.pack(fill='both', expand=True, pady=10)

        # Label para mostrar la imagen
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(pady=15)

        # Frame para botones de imagen
        image_buttons_frame = ttk.Frame(self.image_frame)
        image_buttons_frame.pack(pady=10)

        # Botones con estilo minimalista
        ttk.Button(image_buttons_frame, 
                  text="Seleccionar Imagen",
                  style='Minimal.TButton',
                  command=self.seleccionar_imagen).pack(side='left', padx=8)
        ttk.Button(image_buttons_frame, 
                  text="Eliminar Imagen",
                  style='Minimal.TButton',
                  command=self.eliminar_imagen).pack(side='left', padx=8)

        # Frame para los botones de acción
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=5, column=0, sticky='ew', pady=10)

        # Estilo para los botones
        style = ttk.Style()
        style.configure('Success.TButton', background='#28a745')
        style.configure('Danger.TButton', background='#dc3545')
        style.configure('Warning.TButton', background='#ffc107')

        # Crear un subframe para cada botón para mejor organización
        update_frame = ttk.Frame(button_frame)
        update_frame.grid(row=0, column=0, padx=5)

        delete_frame = ttk.Frame(button_frame)
        delete_frame.grid(row=0, column=1, padx=5)

        clear_frame = ttk.Frame(button_frame)
        clear_frame.grid(row=0, column=2, padx=5)

        # Botón Actualizar con ícono y estilo verde
        self.btn_actualizar = ttk.Button(
            update_frame,
            text="✓ Actualizar",
            style='Success.TButton',
            command=self.actualizar_articulo
        )
        self.btn_actualizar.grid()

        # Botón Eliminar con ícono y estilo rojo
        self.btn_eliminar = ttk.Button(
            delete_frame,
            text="✗ Eliminar",
            style='Danger.TButton',
            command=self.eliminar_articulo
        )
        self.btn_eliminar.grid()

        # Botón Limpiar con ícono y estilo amarillo
        self.btn_limpiar = ttk.Button(
            clear_frame,
            text="↺ Limpiar",
            style='Warning.TButton',
            command=self.limpiar_campos_inventario
        )
        self.btn_limpiar.grid()

        # Tooltips para los botones
        ToolTip(self.btn_actualizar, "Guardar cambios en el artículo seleccionado")
        ToolTip(self.btn_eliminar, "Eliminar el artículo seleccionado")
        ToolTip(self.btn_limpiar, "Limpiar todos los campos")

        # Deshabilitar botones inicialmente
        self.btn_actualizar.config(state='disabled')
        self.btn_eliminar.config(state='disabled')

        # Vincular la selección del TreeView para habilitar/deshabilitar botones
        self.tree_inventario.bind('<<TreeviewSelect>>', self.cargar_detalles_articulo)

        # Mostrar imagen por defecto inicialmente
        self.mostrar_imagen_por_defecto()

        # Frame para el filtro de búsqueda
        filtro_frame = ttk.Frame(self.tab_inventario)
        filtro_frame.pack(fill='x', padx=10, pady=5)

        # Etiqueta y campo de entrada para la búsqueda
        tk.Label(filtro_frame, text="Buscardasasd:").pack(side='left', padx=5)
        self.entry_busqueda_inventario = tk.Entry(filtro_frame)
        self.entry_busqueda_inventario.pack(side='left', fill='x', expand=True, padx=5)

        # Botón de búsqueda
        ttk.Button(filtro_frame, text="Buscar", command=self.buscar_articulos).pack(side='left', padx=5)

        # Vincular la tecla Enter al campo de búsqueda
        self.entry_busqueda_inventario.bind('<Return>', self.buscar_articulos)

    def cargar_detalles_articulo(self, event=None):
        """Carga los detalles del artículo seleccionado en los campos"""
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            return

        # Obtener los valores del artículo seleccionado
        item = self.tree_inventario.item(seleccion[0])
        valores = item['values']

        try:
            # Limpiar campos actuales
            for campo in self.campos_inventario.values():
                if isinstance(campo, ttk.Entry):
                    campo.delete(0, tk.END)
                elif isinstance(campo, DateEntry):
                    campo.set_date(datetime.now())

            # Mapear los valores a los campos correspondientes
            self.campos_inventario['entry_nombre'].insert(0, valores[1])  # Nombre
            self.campos_inventario['entry_descripcion'].insert(0, valores[2])  # Descripción
            self.campos_inventario['entry_cantidad'].insert(0, valores[3])  # Cantidad
            
            # Manejar la fecha
            if valores[5]:  # Fecha de ingreso
                try:
                    fecha = datetime.strptime(valores[5], '%Y-%m-%d')
                    self.campos_inventario['entry_fecha'].set_date(fecha)
                except (ValueError, TypeError):
                    self.campos_inventario['entry_fecha'].set_date(datetime.now())

            # Manejar la imagen
            ruta_imagen = valores[4]  # Asumiendo que la ruta de la imagen está en el índice 4
            if ruta_imagen and ruta_imagen != 'None' and os.path.exists(ruta_imagen):
                self.mostrar_imagen(ruta_imagen)
                self.ruta_imagen = ruta_imagen  # Guardar la ruta actual
            else:
                self.mostrar_imagen_por_defecto()
                self.ruta_imagen = None

            # Habilitar botones de edición
            self.btn_actualizar.config(state='normal')
            self.btn_eliminar.config(state='normal')

        except Exception as e:
            print(f"Error al cargar detalles del artículo: {e}")
            messagebox.showerror("Error", "No se pudieron cargar los detalles del artículo")

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
        """Permite seleccionar una nueva imagen"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            # Crear directorio de imágenes si no existe
            os.makedirs("imagenes", exist_ok=True)
            
            # Crear nombre de archivo único
            extension = os.path.splitext(file_path)[1]
            nuevo_nombre = f"imagenes/img_{int(time.time())}{extension}"
            
            # Copiar imagen al directorio de imágenes
            shutil.copy2(file_path, nuevo_nombre)
            
            self.ruta_imagen = nuevo_nombre
            self.mostrar_imagen(nuevo_nombre)

    def eliminar_imagen(self):
        """Elimina la imagen del artículo seleccionado"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la imagen?"):
            self.ruta_imagen = None
            self.mostrar_imagen_por_defecto()

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

        # Configurar las columnas del TreeView de transacciones
        self.tree_transacciones = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Articulo', 'Tipo', 'Cantidad', 'Stock sin Transaccion', 'Stock con Transaccion', 'Fecha'),
            show='headings'
        )

        # Configurar los encabezados y anchos de columna
        self.tree_transacciones.heading('ID', text='ID')
        self.tree_transacciones.heading('Articulo', text='Artículo')
        self.tree_transacciones.heading('Tipo', text='Tipo')
        self.tree_transacciones.heading('Cantidad', text='Cantidad')
        self.tree_transacciones.heading('Stock sin Transaccion', text='Stock sin Transacción')
        self.tree_transacciones.heading('Stock con Transaccion', text='Stock con Transacción')
        self.tree_transacciones.heading('Fecha', text='Fecha')

        # Configurar anchos de columna
        self.tree_transacciones.column('ID', width=50)
        self.tree_transacciones.column('Articulo', width=150)
        self.tree_transacciones.column('Tipo', width=100)
        self.tree_transacciones.column('Cantidad', width=100)
        self.tree_transacciones.column('Stock sin Transaccion', width=150)
        self.tree_transacciones.column('Stock con Transaccion', width=150)
        self.tree_transacciones.column('Fecha', width=150)

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

    def filtrar_transacciones(self):
        """Filtra las transacciones según los criterios seleccionados"""
        tipo = self.combo_tipo.get() if self.combo_tipo.get() != 'Todos' else None
        articulo = self.combo_articulo.get() if self.combo_articulo.get() != 'Todos' else None
        
        fecha_desde = None
        fecha_hasta = None
        if not self.filtrar_fecha_var.get():
            fecha_desde = self.entry_fecha_desde.get_date().strftime('%Y-%m-%d')
            fecha_hasta = self.entry_fecha_hasta.get_date().strftime('%Y-%m-%d')

        # Limpiar TreeView
        for item in self.tree_transacciones.get_children():
            self.tree_transacciones.delete(item)

        # Obtener transacciones filtradas
        transacciones = self.db.obtener_transacciones_filtradas(
            tipo=tipo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            articulo=articulo
        )

        # Insertar transacciones filtradas
        for transaccion in transacciones:
            fecha = datetime.strptime(transaccion[6], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            valores = (
                transaccion[0],  # ID
                transaccion[1],  # Nombre del artículo
                transaccion[2],  # Tipo
                transaccion[3],  # Cantidad
                transaccion[4],  # Stock sin transacción
                transaccion[5],  # Stock con transacción
                fecha           # Fecha formateada
            )
            self.tree_transacciones.insert('', 'end', values=valores)

    def exportar_transacciones(self):
        success, message = self.db.exportar_a_csv('transacciones')
        messagebox.showinfo("Exportar a CSV", message)

    def setup_personas_tab(self):
        # Crear TreeView para mostrar personas
        self.tree_personas = ttk.Treeview(self.tab_personas, columns=('ID', 'Nombre', 'Artículo', 'Teléfono', 'Dirección', 'Municipio', 'Fecha Petición', 'Fecha Entrega'), show='headings')
        self.tree_personas.pack(fill='both', expand=True, padx=5, pady=5)

        # Configurar el menú contextual
        self.menu_contextual = tk.Menu(self.root, tearoff=0)
        
        # Configurar estilo del menú
        self.menu_contextual.configure(
            font=('Helvetica', 10),
            bg='#ffffff',
            fg='#333333',
            activebackground='#e1f5fe',
            activeforeground='#000000',
            relief='flat',
            bd=1
        )
        
        # Agregar opciones al menú
        self.menu_contextual.add_command(
            label="✨ Agregar Persona",
            command=self.abrir_ventana_agregar_persona,
            font=('Helvetica', 10)
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="✏️ Editar Persona",
            command=self.abrir_ventana_editar_persona,
            font=('Helvetica', 10)
        )
        self.menu_contextual.add_command(
            label="📅 Establecer Fecha de Entrega",
            command=self.abrir_ventana_fecha_entrega,
            font=('Helvetica', 10)
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="🗑️ Eliminar Persona",
            command=self.eliminar_persona,
            font=('Helvetica', 10),
            foreground='#dc3545'
        )

        # Vincular el clic derecho al TreeView
        self.tree_personas.bind("<Button-3>", self.mostrar_menu_contextual)

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


    def limpiar_campos_inventario(self):
        # Limpiar campos de texto
        for entry in self.campos_inventario.values():
            entry.delete(0, tk.END)
        
        # Limpiar imagen
        self.image_label.configure(image='')
        self.image_label.image = None
        self.ruta_imagen = None  # Importante: resetear la ruta de la imagen
        
        # Deseleccionar item en el TreeView si hay alguno seleccionado
        if self.tree_inventario.selection():
            self.tree_inventario.selection_remove(self.tree_inventario.selection())

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
        """Actualiza la lista de artículos en el TreeView"""
        # Limpiar TreeView
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)

        # Obtener artículos actualizados
        articulos = self.db.obtener_inventario()

        # Insertar artículos en el TreeView
        for articulo in articulos:
            # Reorganizar los valores para mostrar la imagen entre cantidad y fecha
            valores = (
                articulo[0],  # ID
                articulo[1],  # Nombre
                articulo[2],  # Descripción
                articulo[3],  # Cantidad
                articulo[4],  # Imagen
                articulo[5]   # Fecha
            )
            self.tree_inventario.insert('', 'end', values=valores)

    def seleccionar_articulo(self, event=None):
        """Maneja la selección de un artículo en el TreeView"""
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            return

        # Obtener los valores del artículo seleccionado
        item = self.tree_inventario.item(seleccion[0])
        valores = item['values']

        if valores:
            # Limpiar campos actuales
            for campo in self.campos_inventario.values():
                if isinstance(campo, ttk.Entry):
                    campo.delete(0, tk.END)
                elif isinstance(campo, DateEntry):
                    campo.set_date(datetime.now())

            # Mapear los valores a los campos correspondientes
            mapeo_campos = {
                'nombre': valores[1],       # Nombre del artículo
                'descripcion': valores[2],  # Descripción
                'cantidad': valores[3],     # Cantidad
                'fecha': valores[5]         # Fecha de ingreso
            }

            # Llenar los campos con los valores del artículo
            for campo, valor in mapeo_campos.items():
                if campo in self.campos_inventario:
                    if isinstance(self.campos_inventario[campo], DateEntry):
                        try:
                            fecha = datetime.strptime(valor, '%Y-%m-%d')
                            self.campos_inventario[campo].set_date(fecha)
                        except (ValueError, TypeError):
                            self.campos_inventario[campo].set_date(datetime.now())
                    else:
                        self.campos_inventario[campo].delete(0, tk.END)
                        self.campos_inventario[campo].insert(0, str(valor))

            # Mostrar imagen si existe
            ruta_imagen = valores[4]  # Ruta de la imagen
            if ruta_imagen and ruta_imagen != 'None' and os.path.exists(ruta_imagen):
                self.mostrar_imagen(ruta_imagen)
            else:
                self.mostrar_imagen_por_defecto()

    def mostrar_imagen_por_defecto(self):
        """Muestra una imagen por defecto cuando no hay imagen disponible"""
        try:
            # Crear imagen en blanco
            imagen = Image.new('RGB', (300, 300), '#f0f0f0')
            draw = ImageDraw.Draw(imagen)
            
            # Texto para mostrar
            texto = "No hay imagen\ndisponible"
            try:
                fuente = ImageFont.truetype("arial.ttf", 24)
            except:
                fuente = ImageFont.load_default()
            
            # Centrar texto
            bbox = draw.textbbox((0, 0), texto, font=fuente)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (300 - w) / 2
            y = (300 - h) / 2
            
            # Dibujar texto
            draw.text((x, y), texto, fill='#666666', font=fuente)
            
            # Mostrar imagen
            foto = ImageTk.PhotoImage(imagen)
            self.image_label.configure(image=foto)
            self.image_label.image = foto  # Mantener referencia
        except Exception as e:
            print(f"Error al mostrar imagen por defecto: {e}")
            self.image_label.configure(text="No hay imagen disponible")

    def mostrar_imagen(self, ruta_imagen):
        """Muestra la imagen en el label de imagen"""
        try:
            imagen = Image.open(ruta_imagen)
            
            # Dimensiones máximas para la imagen
            ancho_max = 300
            alto_max = 300
            
            # Mantener proporción de aspecto
            ratio = min(ancho_max/imagen.width, alto_max/imagen.height)
            nuevo_ancho = int(imagen.width * ratio)
            nuevo_alto = int(imagen.height * ratio)
            
            imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
            # Crear fondo blanco del tamaño máximo
            imagen_fondo = Image.new('RGB', (ancho_max, alto_max), 'white')
            x = (ancho_max - nuevo_ancho) // 2
            y = (alto_max - nuevo_alto) // 2
            
            # Pegar la imagen centrada
            imagen_fondo.paste(imagen, (x, y))
            
            # Convertir y mostrar
            foto = ImageTk.PhotoImage(imagen_fondo)
            self.image_label.configure(image=foto)
            self.image_label.image = foto  # Mantener referencia
        except Exception as e:
            print(f"Error al mostrar imagen: {e}")
            self.mostrar_imagen_por_defecto()

    def buscar_articulos(self, event=None):
        """Filtra y muestra los artículos en inventario según el término de búsqueda."""
        filtro = self.entry_busqueda_inventario.get().strip().lower()
        
        # Limpiar la tabla
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)

        # Obtener los artículos filtrados
        articulos = self.db.obtener_inventario(filtro)

        # Insertar los artículos filtrados
        for articulo in articulos:
            self.tree_inventario.insert('', 'end', values=articulo)

    def limpiar_campos_inventario(self):
        # Limpiar campos de texto
        for entry in self.campos_inventario.values():
            entry.delete(0, tk.END)
        
        # Limpiar imagen
        self.image_label.configure(image='')
        self.image_label.image = None
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
            nombre = self.campos_inventario['entry_nombre'].get()
            descripcion = self.campos_inventario['entry_descripcion'].get()
            cantidad = self.campos_inventario['entry_cantidad'].get()
            fecha = self.campos_inventario['entry_fecha'].get()
            
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
        """Actualiza la lista de transacciones en el TreeView"""
        # Limpiar el TreeView
        for item in self.tree_transacciones.get_children():
            self.tree_transacciones.delete(item)

        # Obtener las transacciones
        transacciones = self.db.obtener_transacciones_filtradas()

        # Insertar las transacciones en el TreeView
        for transaccion in transacciones:
            # Formatear la fecha para mejor visualización
            fecha = datetime.strptime(transaccion[6], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            
            valores = (
                transaccion[0],  # ID
                transaccion[1],  # Nombre del artículo
                transaccion[2],  # Tipo
                transaccion[3],  # Cantidad
                transaccion[4],  # Stock sin transacción
                transaccion[5],  # Stock con transacción
                fecha           # Fecha formateada
            )
            self.tree_transacciones.insert('', 'end', values=valores)

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

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual en la posición del clic"""
        # Seleccionar el item bajo el cursor
        item = self.tree_personas.identify_row(event.y)
        if item:
            # Seleccionar el item
            self.tree_personas.selection_set(item)
            # Mostrar el menú contextual
            try:
                self.menu_contextual.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu_contextual.grab_release()

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
        
        # Validar campos
        if not nombre_articulo or not cantidad_disponible:
            messagebox.showwarning("Advertencia", "Nombre y cantidad son obligatorios")
            return
        
        try:
            cantidad_disponible = int(cantidad_disponible)
            # Llamar al método con los argumentos correctos
            if self.app.db.agregar_articulo(nombre_articulo, descripcion, cantidad_disponible, None, fecha_ingreso):
                messagebox.showinfo("Éxito", "Artículo agregado correctamente")
                self.app.actualizar_lista_inventario()
                self.master.destroy()
            else:
                messagebox.showerror("Error", "No se pudo agregar el artículo")
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")

class VentanaEditarPersona:
    def __init__(self, master, app, valores):
        self.master = master
        self.app = app
        self.master.title("Editar Persona")
        self.master.geometry("400x500")

        # Frame para datos personales
        frame_datos = ttk.LabelFrame(master, text="Datos Personales", padding="10")
        frame_datos.pack(fill='x', padx=10, pady=5)

        # Crear campos
        self.campos = {}
        campos_info = [
            ("Nombre:", "nombre"),
            ("Artículo:", "articulo"),
            ("Teléfono:", "telefono"),
            ("Dirección:", "direccion")
        ]

        for i, (label_text, campo_name) in enumerate(campos_info):
            ttk.Label(frame_datos, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(frame_datos, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.campos[campo_name] = entry

        # Municipio (Combobox)
        ttk.Label(frame_datos, text="Municipio:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.campos['municipio'] = ttk.Combobox(frame_datos, 
                                              values=["Montemorelos", "Allende", "Rayones", "Linares", "Hualahuises", "Terán"],
                                              width=27)
        self.campos['municipio'].grid(row=4, column=1, padx=5, pady=5)

        # Frame para fechas
        frame_fechas = ttk.LabelFrame(master, text="Fechas", padding="10")
        frame_fechas.pack(fill='x', padx=10, pady=5)

        # Fecha de Petición
        ttk.Label(frame_fechas, text="Fecha Petición:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.campos['fecha_peticion'] = DateEntry(frame_fechas, width=27,
                                                background='darkblue',
                                                foreground='white',
                                                borderwidth=2,
                                                date_pattern='yyyy-mm-dd')
        self.campos['fecha_peticion'].grid(row=0, column=1, padx=5, pady=5)

        # Fecha de Entrega
        ttk.Label(frame_fechas, text="Fecha Entrega:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.campos['fecha_entrega'] = DateEntry(frame_fechas, width=27,
                                               background='darkblue',
                                               foreground='white',
                                               borderwidth=2,
                                               date_pattern='yyyy-mm-dd')
        self.campos['fecha_entrega'].grid(row=1, column=1, padx=5, pady=5)

        # Frame para botones
        frame_botones = ttk.Frame(master)
        frame_botones.pack(pady=20)

        # Botones
        ttk.Button(frame_botones, text="Guardar", 
                  command=self.guardar_cambios).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Cancelar", 
                  command=self.master.destroy).pack(side='left', padx=5)

        # Cargar los valores existentes
        self.cargar_valores(valores)

    def cargar_valores(self, valores):
        """Carga los valores existentes en los campos del formulario"""
        # Mapear los valores a los campos correspondientes
        campos_orden = ['nombre', 'articulo', 'telefono', 'direccion', 'municipio']
        
        # Cargar valores en los campos de texto y combobox
        for i, campo in enumerate(campos_orden):
            if campo in self.campos:
                if isinstance(self.campos[campo], ttk.Combobox):
                    self.campos[campo].set(valores[i])
                else:
                    self.campos[campo].delete(0, tk.END)
                    self.campos[campo].insert(0, valores[i])

        # Cargar fechas
        try:
            fecha_peticion = datetime.strptime(valores[5], '%Y-%m-%d')
            self.campos['fecha_peticion'].set_date(fecha_peticion)
        except (ValueError, TypeError):
            print(f"Error al cargar fecha de petición: {valores[5]}")

        try:
            if valores[6] and valores[6] != 'Pendiente':
                fecha_entrega = datetime.strptime(valores[6], '%Y-%m-%d')
                self.campos['fecha_entrega'].set_date(fecha_entrega)
        except (ValueError, TypeError):
            print(f"Error al cargar fecha de entrega: {valores[6]}")

    def guardar_cambios(self):
        """Guarda los cambios realizados en la persona"""
        # Obtener los valores actualizados
        valores_actualizados = {
            'nombre': self.campos['nombre'].get(),
            'articulo': self.campos['articulo'].get(),
            'telefono': self.campos['telefono'].get(),
            'direccion': self.campos['direccion'].get(),
            'municipio': self.campos['municipio'].get(),
            'fecha_peticion': self.campos['fecha_peticion'].get(),
            'fecha_entrega': self.campos['fecha_entrega'].get()
        }

        # Obtener el ID de la persona seleccionada
        seleccion = self.app.tree_personas.selection()
        if seleccion:
            item = self.app.tree_personas.item(seleccion[0])
            id_persona = item['values'][0]

            # Actualizar en la base de datos
            if self.app.db.actualizar_persona(id_persona, **valores_actualizados):
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
        self.ruta_imagen = articulo[4] if articulo[4] != 'None' else None
        
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
        try:
            # Cargar datos en los campos
            self.campos['nombre'].delete(0, tk.END)
            self.campos['nombre'].insert(0, self.articulo[1])  # Nombre
            
            self.campos['descripcion'].delete(0, tk.END)
            self.campos['descripcion'].insert(0, self.articulo[2])  # Descripción
            
            self.campos['cantidad'].delete(0, tk.END)
            self.campos['cantidad'].insert(0, str(self.articulo[3]))  # Cantidad
            
            # Cargar fecha
            if self.articulo[5]:  # Fecha de ingreso
                try:
                    fecha = datetime.strptime(self.articulo[5], '%Y-%m-%d')
                    self.campos['fecha'].set_date(fecha)
                except (ValueError, TypeError):
                    self.campos['fecha'].set_date(datetime.now())
            
            # Cargar imagen
            if self.ruta_imagen and os.path.exists(self.ruta_imagen):
                self.mostrar_imagen(self.ruta_imagen)
            else:
                self.mostrar_imagen_por_defecto()
                
        except Exception as e:
            print(f"Error al cargar datos del artículo: {e}")
            messagebox.showerror("Error", "No se pudieron cargar los datos del artículo")

    def actualizar_articulo(self):
        """Actualiza el artículo con los nuevos datos"""
        try:
            nombre = self.campos['nombre'].get()
            descripcion = self.campos['descripcion'].get()
            cantidad = self.campos['cantidad'].get()
            fecha = self.campos['fecha'].get()
            
            if not nombre or not cantidad:
                messagebox.showwarning("Advertencia", "Nombre y cantidad son campos obligatorios.")
                return
            
            try:
                cantidad = int(cantidad)
            except ValueError:
                messagebox.showwarning("Error", "La cantidad debe ser un número entero.")
                return
            
            if self.app.db.actualizar_articulo(
                self.articulo[0],
                nombre,
                descripcion,
                cantidad,
                self.ruta_imagen,
                fecha
            ):
                messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
                self.app.actualizar_lista_inventario()
                self.master.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el artículo")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def seleccionar_imagen(self):
        """Permite seleccionar una nueva imagen"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.ruta_imagen = file_path
            self.mostrar_imagen(file_path)

    def eliminar_imagen(self):
        """Elimina la imagen seleccionada"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la imagen?"):
            self.ruta_imagen = None
            self.mostrar_imagen_por_defecto()

    def mostrar_imagen_por_defecto(self):
        """Muestra una imagen por defecto cuando no hay imagen disponible"""
        try:
            # Crear imagen en blanco
            imagen = Image.new('RGB', (300, 300), '#f0f0f0')
            draw = ImageDraw.Draw(imagen)
            
            # Texto para mostrar
            texto = "No hay imagen\ndisponible"
            try:
                fuente = ImageFont.truetype("arial.ttf", 24)
            except:
                fuente = ImageFont.load_default()
            
            # Centrar texto
            bbox = draw.textbbox((0, 0), texto, font=fuente)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (300 - w) / 2
            y = (300 - h) / 2
            
            # Dibujar texto
            draw.text((x, y), texto, fill='#666666', font=fuente)
            
            # Mostrar imagen
            foto = ImageTk.PhotoImage(imagen)
            self.image_label.configure(image=foto)
            self.image_label.image = foto  # Mantener referencia
        except Exception as e:
            print(f"Error al mostrar imagen por defecto: {e}")
            self.image_label.configure(text="No hay imagen disponible")

    def mostrar_imagen(self, ruta_imagen):
        """Muestra la imagen en el label de imagen"""
        try:
            imagen = Image.open(ruta_imagen)
            
            # Dimensiones máximas para la imagen
            ancho_max = 300
            alto_max = 300
            
            # Mantener proporción de aspecto
            ratio = min(ancho_max/imagen.width, alto_max/imagen.height)
            nuevo_ancho = int(imagen.width * ratio)
            nuevo_alto = int(imagen.height * ratio)
            
            imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
            # Crear fondo blanco del tamaño máximo
            imagen_fondo = Image.new('RGB', (ancho_max, alto_max), 'white')
            x = (ancho_max - nuevo_ancho) // 2
            y = (alto_max - nuevo_alto) // 2
            
            # Pegar la imagen centrada
            imagen_fondo.paste(imagen, (x, y))
            
            # Convertir y mostrar
            foto = ImageTk.PhotoImage(imagen_fondo)
            self.image_label.configure(image=foto)
            self.image_label.image = foto  # Mantener referencia
        except Exception as e:
            print(f"Error al mostrar imagen: {e}")
            self.mostrar_imagen_por_defecto()

    def limpiar_campos_inventario(self):
        # Limpiar campos de texto
        for entry in self.campos_inventario.values():
            entry.delete(0, tk.END)
        
        # Limpiar imagen
        self.image_label.configure(image='')
        self.image_label.image = None
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

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual en la posición del clic"""
        # Seleccionar el item bajo el cursor
        item = self.tree_personas.identify_row(event.y)
        if item:
            # Seleccionar el item
            self.tree_personas.selection_set(item)
            # Mostrar el menú contextual
            try:
                self.menu_contextual.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu_contextual.grab_release()

# Para abrir la ventana de transacciones
def abrir_ventana_transacciones(app, db):
    ventana = tk.Toplevel()
    VentanaTransacciones(ventana, app, db)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()