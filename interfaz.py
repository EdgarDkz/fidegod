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
        
        # Botón para abrir la ventana de transacciones
        ttk.Button(self.tab_transacciones, text="Registrar Transacción", 
                command=lambda: abrir_ventana_transacciones(self, self.db)).pack(pady=10)
        
        # Crear un marco para los botones
        frame_botones = ttk.Frame(self.tab_personas)
        frame_botones.pack(pady=10)

        # Botón para agregar persona
        ttk.Button(frame_botones, text="Agregar Persona", 
                command=self.abrir_ventana_agregar_persona).grid(row=0, column=0, padx=5)

        # Botón para editar persona
        ttk.Button(frame_botones, text="Editar Persona", 
                command=self.abrir_ventana_editar_persona).grid(row=0, column=1, padx=5)
        
        # Botón para eliminar persona
        ttk.Button(frame_botones, text="Eliminar Persona", 
                command=self.eliminar_persona).grid(row=0, column=2, padx=5)
        
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
        ttk.Button(frame_botones, text="Eliminar", 
                command=self.eliminar_persona).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar", 
                command=self.limpiar_campos_persona).pack(side='left', padx=5)

        # Bind para selección en el TreeView
        self.tree_personas.bind('<<TreeviewSelect>>', self.seleccionar_persona)
        
        # Cargar datos iniciales
        self.actualizar_lista_personas()

        # Crear un marco para la búsqueda
        frame_busqueda = ttk.Frame(self.tab_personas)
        frame_busqueda.pack(pady=10)

        ttk.Label(frame_busqueda, text="Buscar por Nombre:").pack(side='left', padx=5)
        self.combobox_nombre = ttk.Combobox(frame_busqueda)
        self.combobox_nombre.pack(side='left', padx=5)
        self.combobox_nombre.bind("<<ComboboxSelected>>", self.buscar_personas)

        ttk.Label(frame_busqueda, text="Buscar por Artículo:").pack(side='left', padx=5)
        self.combobox_articulo = ttk.Combobox(frame_busqueda)
        self.combobox_articulo.pack(side='left', padx=5)
        self.combobox_articulo.bind("<<ComboboxSelected>>", self.buscar_personas)

        ttk.Label(frame_busqueda, text="Buscar por Municipio:").pack(side='left', padx=5)
        self.combobox_municipio = ttk.Combobox(frame_busqueda, values=self.municipios)
        self.combobox_municipio.pack(side='left', padx=5)
        self.combobox_municipio.bind("<<ComboboxSelected>>", self.buscar_personas)

        # Botón para buscar
        ttk.Button(frame_busqueda, text="Buscar", command=self.buscar_personas).pack(side='left', padx=5)

        # Botón para exportar a Excel
        ttk.Button(frame_busqueda, text="Exportar a Excel", command=self.exportar_a_excel).pack(side='left', padx=5)

        # Cargar nombres y artículos en los comboboxes
        self.cargar_nombres_y_articulos()

        

    def cargar_nombres_y_articulos(self):
        # Obtener nombres y artículos de la base de datos
        nombres = self.db.obtener_nombres()
        articulos = self.db.obtener_articulos()

        # Llenar los comboboxes
        self.combobox_nombre['values'] = nombres
        self.combobox_articulo['values'] = articulos

    def setup_inventario_tab(self):
        # Frame para búsqueda
        frame_busqueda = ttk.LabelFrame(self.tab_inventario, text="Búsqueda")
        frame_busqueda.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(frame_busqueda, text="Buscar:").pack(side='left', padx=5)
        self.entry_busqueda_inventario = ttk.Entry(frame_busqueda)
        self.entry_busqueda_inventario.pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text="Buscar", 
                command=self.buscar_articulos).pack(side='left', padx=5)
        
        # Botón para agregar producto
        ttk.Button(frame_busqueda, text="Agregar Producto", command=self.abrir_ventana_agregar_producto).pack(side='left', padx=5)
        
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
        frame_imagen = ttk.LabelFrame(self.frame_detalles_articulo, text="Imagen del Artículo")
        frame_imagen.grid(row=0, column=2, rowspan=len(campos_normales), padx=5, pady=5)

        # Label para mostrar la imagen
        self.label_imagen = ttk.Label(frame_imagen)
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

    def setup_transacciones_tab(self):
        # Crear marco para filtrado
        frame_filtro = ttk.LabelFrame(self.tab_transacciones, text="Filtrar Transacciones")
        frame_filtro.pack(fill='x', padx=5, pady=5)

        # Tipo de transacción
        ttk.Label(frame_filtro, text="Tipo:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_tipo = ttk.Combobox(frame_filtro, values=["entrada", "salida"])
        self.combo_tipo.grid(row=0, column=1, padx=5, pady=5)

        # Checkbox para activar/desactivar filtrado por fecha
        self.filtrar_fecha_var = tk.BooleanVar()
        ttk.Checkbutton(frame_filtro, text="Todas las fechas", variable=self.filtrar_fecha_var, command=self.toggle_fecha).grid(row=0, column=2, padx=5, pady=5)

        # Campos de fecha
        ttk.Label(frame_filtro, text="Desde:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_fecha_desde = DateEntry(frame_filtro, width=10, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_fecha_desde.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_filtro, text="Hasta:").grid(row=1, column=2, padx=5, pady=5)
        self.entry_fecha_hasta = DateEntry(frame_filtro, width=10, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_fecha_hasta.grid(row=1, column=3, padx=5, pady=5)

        # Filtro por artículo
        ttk.Label(frame_filtro, text="Artículo:").grid(row=0, column=3, padx=5, pady=5)
        self.combo_articulo = ttk.Combobox(frame_filtro)
        self.combo_articulo.grid(row=0, column=4, padx=5, pady=5)
        self.cargar_articulos()  # Método para cargar artículos en el combobox

        # Botón para filtrar
        ttk.Button(frame_filtro, text="Filtrar", command=self.filtrar_transacciones).grid(row=2, columnspan=5, pady=10)

        # Crear TreeView para mostrar transacciones
        self.tree_transacciones = ttk.Treeview(self.tab_transacciones, columns=('ID', 'Artículo', 'Tipo', 'Cantidad', 'Stock sin Transacción', 'Stock con Transacción', 'Fecha'), show='headings')
        self.tree_transacciones.pack(fill='both', expand=True, padx=5, pady=5)

        # Configurar columnas
        for col in self.tree_transacciones['columns']:
            self.tree_transacciones.heading(col, text=col)
            self.tree_transacciones.column(col, width=100)

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(self.tab_transacciones, orient='vertical', command=self.tree_transacciones.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_transacciones.configure(yscrollcommand=scrollbar.set)

        # Cargar datos iniciales
        self.actualizar_lista_transacciones()

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

    def cargar_articulos(self):
        articulos = self.db.obtener_inventario()  # Obtener artículos de la base de datos
        self.combo_articulo['values'] = [articulo[1] for articulo in articulos]  # Suponiendo que el nombre del artículo está en la segunda columna

    def filtrar_transacciones(self):
        tipo = self.combo_tipo.get()
        fecha_desde = self.entry_fecha_desde.get()
        fecha_hasta = self.entry_fecha_hasta.get()

        # Verificar si se seleccionó un tipo
        if not tipo:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un tipo de transacción.")
            return

        # Si la casilla está marcada, ignorar las fechas y tomar todas
        if self.filtrar_fecha_var.get():
            transacciones = self.app.obtener_transacciones_filtradas(tipo, None, None)
        else:
            # Si no se filtra por fecha, usar las fechas ingresadas
            if not fecha_desde or not fecha_hasta:
                messagebox.showwarning("Advertencia", "Por favor, ingrese un rango de fechas.")
                return
            transacciones = self.app.obtener_transacciones_filtradas(tipo, fecha_desde, fecha_hasta)

        # Limpiar el TreeView
        for item in self.tree_transacciones.get_children():
            self.tree_transacciones.delete(item)

        # Insertar las transacciones filtradas
        if transacciones:
            for transaccion in transacciones:
                # Formatear la fecha para mostrar solo el día (sin hora ni segundos)
                fecha_formateada = transaccion[6].split(" ")[0]  # Suponiendo que la fecha está en el índice 6
                self.tree_transacciones.insert('', 'end', values=(transaccion[0], transaccion[1], transaccion[2], transaccion[3], transaccion[4], transaccion[5], fecha_formateada))
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
        for item in self.tree_personas.get_children():
            self.tree_personas.delete(item)
        personas = self.db.obtener_personas()
        for persona in personas:
            self.tree_personas.insert('', 'end', values=persona)

    def buscar_personas(self, event=None):
        nombre = self.combobox_nombre.get()
        articulo = self.combobox_articulo.get()
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


    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if ruta:
            self.ruta_imagen = ruta
            # Mostrar la imagen en el label
            imagen = Image.open(ruta)
            imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)  # Redimensionar
            foto = ImageTk.PhotoImage(imagen)
            self.label_imagen.configure(image=foto)
            self.label_imagen.image = foto  # Mantener referencia

    def eliminar_imagen(self):
        try:
            # Verificar si hay un artículo seleccionado
            seleccion = self.tree_inventario.selection()
            if not seleccion:
                messagebox.showwarning("Aviso", "Por favor, seleccione un artículo primero.")
                return
            
            item = seleccion[0]
            item_id = self.tree_inventario.item(item)['values'][0]
            
            # Obtener el artículo actual
            articulo = self.db.obtener_articulo(item_id)
            if not articulo or not articulo[4]:  # Si no hay artículo o no tiene imagen
                messagebox.showinfo("Información", "Este artículo no tiene una imagen para eliminar.")
                return
            
            # Confirmar la eliminación
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la imagen de este artículo?"):
                # Actualizar el artículo manteniendo todos los datos excepto la imagen
                if self.db.actualizar_articulo(
                    id=item_id,
                    nombre_articulo=articulo[1],  # Mantener el nombre del artículo
                    descripcion=articulo[2],        # Mantener la descripción
                    cantidad_disponible=articulo[3],  # Mantener la cantidad
                    imagen=None,  # Eliminar la imagen
                    fecha_ingreso=articulo[5]  # Asegúrate de pasar la fecha de ingreso
                ):
                    # Limpiar la imagen en la interfaz
                    self.label_imagen.configure(image='')
                    self.label_imagen.image = None
                    self.ruta_imagen = None
                    
                    # Actualizar la lista de inventario
                    self.actualizar_lista_inventario()
                    messagebox.showinfo("Éxito", "Imagen eliminada correctamente.")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la imagen.")
                
        except Exception as e:
            print(f"Error al eliminar imagen: {e}")
            messagebox.showerror("Error", "Ocurrió un error al intentar eliminar la imagen.")

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
        # Limpiar el TreeView
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        
        # Obtener y mostrar los artículos
        articulos = self.db.obtener_inventario()
        for articulo in articulos:
            # Preparar la miniatura de la imagen si existe
            imagen_texto = "🖼️"  # Emoji por defecto para indicar que hay imagen
            if articulo[4]:  # Si existe la imagen
                imagen_texto = "Ver"  # Texto para indicar que hay una imagen
            else:
                imagen_texto = ""  # Texto si no hay imagen

            # Asegúrate de que el índice para la fecha de ingreso sea correcto
            valores = (
                articulo[0],  # ID
                articulo[1],  # Nombre
                articulo[2],  # Descripción
                articulo[3],  # Cantidad
                imagen_texto,  # Texto para la imagen
                articulo[5]    # Fecha de Ingreso (asegúrate de que este índice sea correcto)
            )
            self.tree_inventario.insert('', 'end', values=valores)

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

    def buscar_articulos(self):
        filtro = self.entry_busqueda_inventario.get()
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        articulos = self.db.obtener_inventario(filtro)
        for articulo in articulos:
            self.tree_inventario.insert('', 'end', values=articulo[:-1])  # Excluir la ruta de la imagen

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
            
            # Eliminar la imagen si existe
            articulo = self.db.obtener_articulo(id_articulo)
            if articulo and articulo[4]:  # Si hay imagen
                try:
                    os.remove(articulo[4])
                except:
                    pass
            
            if self.db.eliminar_articulo(id_articulo):
                messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                self.limpiar_campos_inventario()
                self.actualizar_lista_inventario()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el artículo")

    def actualizar_articulo(self):
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un artículo para actualizar")
            return
        
        item = self.tree_inventario.item(seleccion[0])
        id_articulo = item['values'][0]
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
            if self.ruta_imagen != nombre_archivo:
                Image.open(self.ruta_imagen).save(nombre_archivo)
            valores['imagen'] = nombre_archivo
        else:
            articulo = self.db.obtener_articulo(id_articulo)
            valores['imagen'] = articulo[4] if articulo else None
        
        # Asegúrate de incluir la fecha de ingreso
        fecha_ingreso = valores.pop('fecha_ingreso', None)  # Extraer la fecha de ingreso

        if self.db.actualizar_articulo(id_articulo, **valores, fecha_ingreso=fecha_ingreso):
            messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
            self.limpiar_campos_inventario()
            self.actualizar_lista_inventario()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el artículo")

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
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.master.title("Agregar Persona")
        self.master.geometry("300x400")

        # Crear un marco para el diseño
        frame = ttk.Frame(master, padding="10")
        frame.pack(fill='both', expand=True)

        # Campos para ingresar datos
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_nombre = ttk.Entry(frame)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Artículo:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_articulo = ttk.Entry(frame)
        self.entry_articulo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_telefono = ttk.Entry(frame)
        self.entry_telefono.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Dirección:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_direccion = ttk.Entry(frame)
        self.entry_direccion.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Municipio:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.combobox_municipio = ttk.Combobox(frame, values=self.app.municipios)
        self.combobox_municipio.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Fecha Petición:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_fecha_peticion = DateEntry(frame, width=17, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_fecha_peticion.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Fecha Entrega:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_fecha_entrega = DateEntry(frame, width=17, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_fecha_entrega.grid(row=6, column=1, padx=5, pady=5)

        # Checkbutton para marcar la fecha de entrega como pendiente
        self.check_pendiente = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Fecha de Entrega Pendiente", variable=self.check_pendiente, command=self.toggle_fecha_entrega).grid(row=7, columnspan=2, pady=5)

        # Botón para agregar persona
        ttk.Button(frame, text="Agregar", command=self.agregar_persona).grid(row=8, columnspan=2, pady=10)

    def toggle_fecha_entrega(self):
        if self.check_pendiente.get():
            self.entry_fecha_entrega.config(state='disabled')  # Deshabilitar el campo
            self.entry_fecha_entrega.delete(0, tk.END)  # Limpiar el campo
        else:
            self.entry_fecha_entrega.config(state='normal')  # Habilitar el campo

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

class VentanaAgregarProducto:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.master.title("Agregar Producto")
        self.master.geometry("300x400")

        # Campos para ingresar datos
        ttk.Label(master, text="Nombre del Artículo:").pack(pady=5)
        self.entry_nombre_articulo = ttk.Entry(master)
        self.entry_nombre_articulo.pack(pady=5)

        ttk.Label(master, text="Descripción:").pack(pady=5)
        self.entry_descripcion = ttk.Entry(master)
        self.entry_descripcion.pack(pady=5)

        ttk.Label(master, text="Cantidad Disponible:").pack(pady=5)
        self.entry_cantidad = ttk.Entry(master)
        self.entry_cantidad.pack(pady=5)

        ttk.Label(master, text="Fecha de Ingreso:").pack(pady=5)
        self.entry_fecha_ingreso = DateEntry(master, width=17, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_fecha_ingreso.pack(pady=5)

        # Botón para agregar producto
        ttk.Button(master, text="Agregar", command=self.agregar_producto).pack(pady=10)

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
        self.master.geometry("300x400")

        # Crear un marco para el diseño
        frame = ttk.Frame(master, padding="10")
        frame.pack(fill='both', expand=True)

        # Asignar valores a los campos
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_nombre = ttk.Entry(frame)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        self.entry_nombre.insert(0, valores[0])  # Cargar el nombre

        ttk.Label(frame, text="Artículo:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_articulo = ttk.Entry(frame)
        self.entry_articulo.grid(row=1, column=1, padx=5, pady=5)
        self.entry_articulo.insert(0, valores[1])  # Cargar el artículo

        ttk.Label(frame, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_telefono = ttk.Entry(frame)
        self.entry_telefono.grid(row=2, column=1, padx=5, pady=5)
        self.entry_telefono.insert(0, valores[2])  # Cargar el teléfono

        ttk.Label(frame, text="Dirección:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_direccion = ttk.Entry(frame)
        self.entry_direccion.grid(row=3, column=1, padx=5, pady=5)
        self.entry_direccion.insert(0, valores[3])  # Cargar la dirección

        ttk.Label(frame, text="Municipio:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.combobox_municipio = ttk.Combobox(frame, values=self.app.municipios)
        self.combobox_municipio.grid(row=4, column=1, padx=5, pady=5)
        self.combobox_municipio.set(valores[4])  # Cargar el municipio

        ttk.Label(frame, text="Fecha Petición:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_fecha_peticion = DateEntry(frame, width=17, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.entry_fecha_peticion.grid(row=5, column=1, padx=5, pady=5)
        self.entry_fecha_peticion.set_date(valores[5])  # Cargar la fecha de petición

        # Verificar si la fecha de entrega es None
        if valores[6] == 'None':
            # No mostrar el campo de fecha de entrega
            ttk.Label(frame, text="Fecha de Entrega:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Label(frame, text="No hay fecha de entrega").grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
            self.check_pendiente = tk.BooleanVar(value=True)  # Marcar como pendiente
        else:
            ttk.Label(frame, text="Fecha Entrega:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
            self.entry_fecha_entrega = DateEntry(frame, width=17, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            self.entry_fecha_entrega.grid(row=6, column=1, padx=5, pady=5)
            self.entry_fecha_entrega.set_date(valores[6])  # Cargar la fecha de entrega
            self.check_pendiente = tk.BooleanVar(value=False)  # No está pendiente

        # Checkbutton para marcar la fecha de entrega como pendiente
        ttk.Checkbutton(frame, text="Fecha de Entrega Pendiente", variable=self.check_pendiente).grid(row=7, columnspan=2, pady=5)

        # Botones para actualizar y cancelar
        ttk.Button(frame, text="Actualizar", command=self.actualizar_persona).grid(row=8, column=0, pady=10)
        ttk.Button(frame, text="Cancelar", command=self.master.destroy).grid(row=8, column=1, pady=10)

    def actualizar_persona(self):
        nombre = self.entry_nombre.get()
        articulo = self.entry_articulo.get()
        telefono = self.entry_telefono.get()
        direccion = self.entry_direccion.get()
        municipio = self.combobox_municipio.get()
        fecha_peticion = self.entry_fecha_peticion.get()
        fecha_entrega = None if self.check_pendiente.get() else self.entry_fecha_entrega.get()

        # Validar campos obligatorios
        if not nombre or not telefono:
            messagebox.showwarning("Advertencia", "Nombre y Teléfono son obligatorios.")
            return

        # Obtener el ID de la persona seleccionada
        seleccion = self.app.tree_personas.selection()
        item = self.app.tree_personas.item(seleccion[0])
        id_persona = item['values'][0]  # Obtener el ID

        # Actualizar la persona en la base de datos
        if self.app.db.actualizar_persona(id_persona, nombre, articulo, telefono, direccion, municipio, fecha_peticion, fecha_entrega):
            messagebox.showinfo("Éxito", "Persona actualizada correctamente")
            self.master.destroy()  # Cerrar la ventana
            self.app.actualizar_lista_personas()  # Actualizar la lista de personas
        else:
            messagebox.showerror("Error", "No se pudo actualizar la persona. Verifique los datos.")

# Para abrir la ventana de transacciones
def abrir_ventana_transacciones(app, db):
    ventana = tk.Toplevel()
    VentanaTransacciones(ventana, app, db)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()