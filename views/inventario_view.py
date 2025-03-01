import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
from controllers.inventario_controller import InventarioController
from views.Inventario_dialogs.add_producto_dialog import AddProductoDialog
from views.Inventario_dialogs.edit_producto_dialog import EditProductoDialog
from tkcalendar import DateEntry
from datetime import datetime
import pandas as pd  # Import pandas for excel export
import time  # Import time for delay

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief='solid', borderwidth=1,
                         font=('Arial', '8', 'normal'))
        label.pack(ipadx=1, ipady=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class FilterPanel(ttk.Frame):
    def __init__(self, parent, inventario_view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.inventario_view = inventario_view

        # Variables para los filtros
        self.nombre_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        self.stock_min_var = tk.StringVar()
        self.stock_max_var = tk.StringVar()
        self.fecha_inicio_var = tk.StringVar()
        self.fecha_fin_var = tk.StringVar()

        # Panel de búsqueda rápida
        search_frame = ttk.LabelFrame(self, text="Búsqueda Rápida", padding=(10, 5))
        search_frame.pack(fill='x', pady=(0, 10))

        # Campo de entrada para la búsqueda por nombre
        ttk.Label(search_frame, text="Buscar por Nombre:").pack(side='left', padx=(0, 5))
        self.busqueda_entry = ttk.Entry(search_frame, textvariable=self.nombre_var)
        self.busqueda_entry.pack(side='left', fill='x', expand=True)

        # Botones de acción
        btn_frame = ttk.Frame(search_frame)
        btn_frame.pack(side='right', padx=(5, 0))

        ttk.Button(btn_frame, text="Limpiar", command=self.clear_filters).pack(side='left', padx=(0, 5))
        ttk.Button(btn_frame, text="Buscar", command=self.apply_filters).pack(side='left')

        # Filtros avanzados
        advanced_frame = ttk.LabelFrame(self, text="Filtros Avanzados", padding=(10, 5))
        advanced_frame.pack(fill='x', pady=(10, 0))

        # Categoría
        ttk.Label(advanced_frame, text="Categoría:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Combobox(advanced_frame, textvariable=self.categoria_var, values=["Todos", "Herramientas", "Electrónicos", "Muebles", "Oficina", "Otros"], state='readonly').grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        # Rango de Stock
        ttk.Label(advanced_frame, text="Rango de Stock:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        stock_frame = ttk.Frame(advanced_frame)
        stock_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        ttk.Entry(stock_frame, textvariable=self.stock_min_var, width=5).pack(side='left', padx=(0, 5))
        ttk.Label(stock_frame, text="a").pack(side='left', padx=(0, 5))
        ttk.Entry(stock_frame, textvariable=self.stock_max_var, width=5).pack(side='left')

        # Rango de Fechas
        ttk.Label(advanced_frame, text="Desde:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(advanced_frame, textvariable=self.fecha_inicio_var).grid(row=2, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(advanced_frame, text="Hasta:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(advanced_frame, textvariable=self.fecha_fin_var).grid(row=3, column=1, sticky='ew', padx=5, pady=5)

        # Botones de acción para filtros avanzados
        action_frame = ttk.Frame(advanced_frame)
        action_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(action_frame, text="Aplicar", command=self.apply_filters).pack(side='left', padx=(0, 5))
        ttk.Button(action_frame, text="Limpiar", command=self.clear_filters).pack(side='left')

    def apply_filters(self, event=None):
        """Aplica los filtros basados en la entrada del usuario."""
        search_term = self.nombre_var.get().lower()
        # Lógica de búsqueda por nombre
        filtered_items = [item for item in self.inventario_view.articulos if item[1].lower().startswith(search_term)]

        # Aquí puedes agregar lógica para aplicar otros filtros (categoría, stock, fechas)

        # Actualizar la tabla con los elementos filtrados
        self.update_table(filtered_items)

    def clear_filters(self):
        """Limpia todos los filtros aplicados."""
        self.nombre_var.set('')
        self.categoria_var.set('Todos')
        self.stock_min_var.set('')
        self.stock_max_var.set('')
        self.fecha_inicio_var.set('')
        self.fecha_fin_var.set('')
        self.apply_filters()  # Mostrar todos los artículos

    def update_table(self, items):
        """Actualiza la tabla con los elementos filtrados."""
        # Limpiar la tabla actual
        for item in self.inventario_view.tree.get_children():
            self.inventario_view.tree.delete(item)

        # Insertar los elementos filtrados en la tabla
        for item in items:
            self.inventario_view.tree.insert('', 'end', values=item)

class InventarioView:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.image_size = (300, 300)
        self.current_image = None
        self.items_acciones_buttons = {}
        self.search_debounce_id = None
        self.current_filters = {}

        # Paleta de colores por defecto
        self.colors = {
            'primary': '#fb8404',           # Naranja principal
            'primary_light': '#fcad58',     # Naranja más claro
            'primary_dark': '#cb6304',      # Naranja oscuro
            'secondary': '#76849a',         # Gris medio
            'background': '#f4efdf',        # Beige claro
            'surface': '#FFFFFF',           # Blanco
            'error': '#dc3545',            # Rojo error
            'success': '#28a745',          # Verde éxito
            'warning': '#fbb333',          # Naranja claro
            'info': '#17a2b8',            # Azul información
            'text': '#181d22',            # Gris oscuro/negro
            'text_secondary': '#76849a',   # Gris medio
            'divider': '#fcc56e',         # Naranja muy claro
            'toolbar': '#f4efdf',         # Beige claro
            'status_bar': '#f4efdf',      # Beige claro
            'card': '#FFFFFF',            # Blanco
            'hover': '#fcad58',           # Naranja más claro
            'selected': '#fcc56e',        # Naranja muy claro
            'disabled': '#e0e0e0',        # Gris claro
            'input': '#FFFFFF',           # Blanco
            'border': '#fbb333',          # Naranja claro
            'text_header': '#181d22'      # Gris oscuro/negro
        }

        self.setup_variables()
        self.setup_styles()
        self.setup_main_layout()

    def setup_variables(self):
        """Inicializa las variables de la interfaz"""
        # Variables para detalles del producto
        self.nombre_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.cantidad_var = tk.StringVar()
        self.fecha_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        self.ubicacion_var = tk.StringVar()
        self.stock_minimo_var = tk.StringVar()

        # Variables para búsqueda y filtros
        self.search_var = tk.StringVar()
        self.filter_column = tk.StringVar(value='Nombre')
        self.is_filters_expanded = tk.BooleanVar(value=False)

        # Variables para filtros avanzados
        self.categoria_filter_var = tk.StringVar()
        self.stock_min_filter_var = tk.StringVar()
        self.stock_max_filter_var = tk.StringVar()
        self.fecha_inicio_filter_var = tk.StringVar()
        self.fecha_fin_filter_var = tk.StringVar()

        # Variable para mensajes de estado
        self.status_message = tk.StringVar()

        # Configurar observadores para búsqueda en tiempo real
        self.search_var.trace_add('write', self.on_search_change)
        self.filter_column.trace_add('write', self.on_search_change)

    def setup_styles(self):
        """Configuración de estilos para la vista"""
        style = ttk.Style()
        
        # Asegurarse de que no hay estilos previos
        style.theme_use('clam')
        
        # Paleta de colores
        colors = self.colors
        
        # Estilos básicos
        style.configure('App.TFrame', background=colors['surface'])
        style.configure('Toolbar.TFrame', background=colors['toolbar'])
        style.configure('Card.TFrame', background=colors['card'], relief='solid', borderwidth=1)
        
        # Etiquetas
        style.configure('TLabel', 
                       font=('Segoe UI', 10),
                       background=colors['surface'],
                       foreground=colors['text'])
        
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'),
                       background=colors['surface'],
                       foreground=colors['text_header'])
        
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 14, 'bold'),
                       background=colors['surface'],
                       foreground=colors['primary'])
        
        style.configure('Field.TLabel', 
                       font=('Segoe UI', 9),
                       background=colors['surface'],
                       foreground=colors['text_secondary'])
        
        # Entry
        style.configure('TEntry', 
                       padding=5,
                       font=('Segoe UI', 10),
                       fieldbackground=colors['input'])
        
        # Estilo de Entry con borde naranja al enfocar
        style.map('TEntry',
                bordercolor=[('focus', colors['primary'])])
        
        # Estilo especial para el campo de búsqueda
        style.configure('Search.TEntry', 
                       padding=8,
                       font=('Segoe UI', 10),
                       fieldbackground=colors['input'])
        
        style.map('Search.TEntry',
                bordercolor=[('focus', colors['primary'])],
                foreground=[('focus', colors['text'])])
                
        # Estilo para botones
        style.configure('TButton', 
                       font=('Segoe UI', 10),
                       padding=5)
        
        # Botones con colores específicos
        style.configure('Primary.TButton',
                      background=colors['primary'],
                      foreground='white',
                      font=('Segoe UI', 10, 'bold'))
        
        style.map('Primary.TButton',
                background=[('active', colors['primary_dark']),
                           ('pressed', colors['primary_dark'])],
                foreground=[('active', 'white'),
                           ('pressed', 'white')])
        
        style.configure('Secondary.TButton',
                      background=colors['secondary'],
                      foreground='white')
        
        style.map('Secondary.TButton',
                background=[('active', '#5a6579'),
                           ('pressed', '#5a6579')],
                foreground=[('active', 'white'),
                           ('pressed', 'white')])
        
        # Estilo para botones de opciones (radio buttons) para campos de búsqueda
        style.configure('Field.TRadiobutton',
                      font=('Segoe UI', 9),
                      background=colors['surface'],
                      foreground=colors['text'])
        
        style.map('Field.TRadiobutton',
                  background=[('active', colors['primary_light']),
                             ('selected', colors['primary_light'])])
        
        # Estilo para TreeView
        style.configure('Treeview',
            background=colors['surface'],
            fieldbackground=colors['surface'],
            rowheight=30,
            font=('Segoe UI', 9)
        )
        
        style.configure('Treeview.Heading',
            font=('Segoe UI', 9, 'bold'),
            background=colors['background'],
            foreground=colors['text'],
            relief='flat',
            padding=(5, 5)
        )
        
        style.map('Treeview',
                 background=[('selected', colors['primary'])],
                 foreground=[('selected', 'white')])

        # Estilo para Toolbar
        style.configure('Toolbar.TFrame', 
                       background=colors['background'],
                       relief='flat',
                       padding=5)
        
        style.configure('Toolbar.TButton',
                       font=('Segoe UI', 9),
                       padding=(10, 5))

        # Estilo para Combobox
        style.configure('TCombobox',
                       font=('Segoe UI', 9),
                       background=colors['background'],
                       fieldbackground=colors['background'],
                       selectbackground=colors['primary'],
                       selectforeground='white',
                       padding=(5, 2))

        # Estilo para Spinbox
        style.configure('TSpinbox',
                       font=('Segoe UI', 9),
                       background=colors['background'],
                       fieldbackground=colors['background'],
                       selectbackground=colors['primary'],
                       selectforeground='white',
                       padding=(5, 2))

        # Estilo para Scrollbar
        style.configure('TScrollbar',
                       background=colors['background'],
                       troughcolor=colors['surface'],
                       width=12,
                       arrowsize=13)

        # Estilos para filtros
        style.configure('Filter.TFrame',
                       background=colors['background'],
                       relief='flat',
                       padding=10)

        style.configure('Filter.TLabel',
                       font=('Segoe UI', 9),
                       background=colors['surface'],
                       foreground=colors['text_secondary'])

        style.configure('FilterHeader.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       background=colors['surface'],
                       foreground=colors['text'])

        # Estilos para notificaciones
        style.configure('Notification.TFrame',
                       background=colors['surface'],
                       relief='solid',
                       borderwidth=1)

        style.configure('Notification.TLabel',
                       font=('Segoe UI', 9),
                       background=colors['surface'],
                       foreground=colors['text'])

        # Estilos para indicadores
        style.configure('Counter.TLabel',
                       font=('Segoe UI', 9),
                       foreground=colors['primary'])

        style.configure('ActiveFilter.TLabel',
                       font=('Segoe UI', 9),
                       foreground=colors['success'])

    def setup_main_layout(self):
        """Configura el layout principal de la aplicación"""
        try:
            # Frame principal
            self.main_frame = ttk.Frame(self.parent)
            self.main_frame.grid(row=0, column=0, sticky='nsew')
            
            # Configurar grid weights del parent
            self.parent.grid_rowconfigure(0, weight=1)
            self.parent.grid_columnconfigure(0, weight=1)

            # Configurar grid weights del main_frame
            self.main_frame.grid_rowconfigure(1, weight=1)  # Cambiado a 1 para dejar espacio para la toolbar
            self.main_frame.grid_columnconfigure(1, weight=1)

            # Agregar barra de herramientas
            self.setup_toolbar()

            # Frame izquierdo (filtros)
            self.left_frame = ttk.Frame(self.main_frame)
            self.left_frame.grid(row=1, column=0, sticky='ns', padx=5, pady=5)

            # Frame central (tabla)
            self.center_frame = ttk.Frame(self.main_frame)
            self.center_frame.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
            self.center_frame.grid_rowconfigure(0, weight=1)
            self.center_frame.grid_columnconfigure(0, weight=1)

            # Frame derecho (detalles)
            self.details_frame = ttk.Frame(self.main_frame)
            self.details_frame.grid(row=1, column=2, sticky='nsew', padx=5, pady=5)
            self.details_frame.configure(width=350)  # Ancho fijo para el panel de detalles
            self.details_frame.grid_propagate(False)  # Evitar que el frame se encoja
            self.details_frame.pack_propagate(False)  # Evitar que el frame se encoja con pack

            # Configurar frames específicos en el orden correcto
            self.setup_tree()        # Primero configurar el TreeView
            self.setup_left_panel()  # Luego el panel izquierdo
            self.setup_details_frame()  # Finalmente el panel derecho

        except Exception as e:
            messagebox.showerror("Error", f"Error al configurar el layout: {str(e)}")

    def setup_toolbar(self):
        """Configura la barra de herramientas con botones de acción"""
        # Frame para la barra de herramientas
        self.toolbar_frame = ttk.Frame(self.main_frame, style='Toolbar.TFrame')
        self.toolbar_frame.grid(row=0, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

        # Botón Agregar
        self.btn_agregar = ttk.Button(
            self.toolbar_frame,
            text="Agregar",
            command=lambda: self.abrir_dialogo_agregar()
        )
        self.btn_agregar.grid(row=0, column=0, padx=2)

        # Botón Editar
        self.btn_editar = ttk.Button(
            self.toolbar_frame,
            text="Editar",
            command=lambda: self.editar_seleccionado()
        )
        self.btn_editar.grid(row=0, column=1, padx=2)
        self.btn_editar.state(['disabled'])

        # Botón Eliminar
        self.btn_eliminar = ttk.Button(
            self.toolbar_frame,
            text="Eliminar",
            command=lambda: self.eliminar_seleccionado()
        )
        self.btn_eliminar.grid(row=0, column=2, padx=2)
        self.btn_eliminar.state(['disabled'])

        # Separador
        ttk.Separator(self.toolbar_frame, orient='vertical').grid(row=0, column=3, padx=5, sticky='ns')

        # Botón Exportar
        self.btn_exportar = ttk.Button(
            self.toolbar_frame,
            text="Exportar",
            command=self.exportar_a_excel
        )
        self.btn_exportar.grid(row=0, column=4, padx=2)

    def abrir_dialogo_agregar(self):
        """Abre el diálogo para agregar un nuevo artículo"""
        dialog = AddProductoDialog(self.parent, self.controller, on_save=self.cargar_datos)
        self.parent.wait_window(dialog)

    def editar_seleccionado(self):
        """Edita el artículo seleccionado"""
        selected_items = self.tree.selection()
        if selected_items:
            item_id = selected_items[0]
            articulo_id = self.tree.item(item_id)['values'][0]  # Asumiendo que el ID está en la primera columna
            self.editar_articulo(articulo_id)

    def eliminar_seleccionado(self):
        """Elimina el artículo seleccionado"""
        selected_items = self.tree.selection()
        if selected_items:
            item_id = selected_items[0]
            articulo_id = self.tree.item(item_id)['values'][0]  # Asumiendo que el ID está en la primera columna
            if messagebox.askyesno("Confirmar eliminación",
                                 "¿Está seguro de que desea eliminar este artículo?"):
                if self.controller.eliminar_articulo(articulo_id):
                    self.cargar_datos()
                    self.limpiar_campos()
                    messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                    self.btn_editar.state(['disabled'])
                    self.btn_eliminar.state(['disabled'])

    def on_select(self, event):
        """Maneja la selección de un artículo en el TreeView"""
        selected_items = self.tree.selection()
        if selected_items:
            self.btn_editar.state(['!disabled'])  # Habilitar botón de editar
            self.btn_eliminar.state(['!disabled'])  # Habilitar botón de eliminar

            # Obtener datos del artículo seleccionado
            item = self.tree.item(selected_items[0])
            articulo_id = item['values'][0]

            # Obtener datos completos del artículo
            articulo = self.controller.get_articulo_by_id(articulo_id)
            if articulo:
                # Actualizar campos de detalle
                self.nombre_var.set(articulo[1])
                if 'Descripción' in self.detail_entries:
                    if isinstance(self.detail_entries['Descripción'], tk.Text):
                        self.detail_entries['Descripción'].delete('1.0', tk.END)
                        self.detail_entries['Descripción'].insert('1.0', articulo[2] or '')
                    else:
                        self.descripcion_var.set(articulo[2] or '')
                self.cantidad_var.set(str(articulo[3]))
                
                # Actualizar fecha usando la fecha exacta de la tabla
                if 'Fecha de Ingreso' in self.detail_entries:
                    try:
                        # Usar la fecha directamente de los valores de la tabla
                        fecha_tabla = item['values'][6]  # La fecha está en la posición 6 de los valores
                        fecha_obj = datetime.strptime(fecha_tabla, '%Y-%m-%d')
                        self.detail_entries['Fecha de Ingreso'].set_date(fecha_obj)
                    except (ValueError, TypeError, IndexError):
                        # Si hay algún error, usar la fecha del artículo o la fecha actual
                        fecha_default = datetime.strptime(articulo[4], '%Y-%m-%d') if articulo[4] else datetime.now()
                        self.detail_entries['Fecha de Ingreso'].set_date(fecha_default)
                
                self.categoria_var.set(articulo[5] if articulo[5] else '')
                self.ubicacion_var.set(articulo[6] if articulo[6] else '')
                self.stock_minimo_var.set(str(articulo[7]) if articulo[7] is not None else '')

                # Cargar imagen del artículo
                self.cargar_imagen_articulo(articulo_id)
        else:
            self.btn_editar.state(['disabled'])
            self.btn_eliminar.state(['disabled'])
            self.limpiar_campos()

    def setup_left_panel(self):
        """Configura el panel izquierdo con filtros"""
        # Frame de filtros
        self.filters_frame = ttk.Frame(self.left_frame)
        self.filters_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.filters_frame.grid_columnconfigure(0, weight=1)

        # Configurar filtros
        self.setup_search_filters()
        self.setup_advanced_filters()

    def setup_tree(self):
        """Configura el TreeView con estilos mejorados"""
        # Frame para la tabla
        table_frame = ttk.Frame(self.center_frame)
        table_frame.grid(row=0, column=0, sticky='nsew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient='vertical')
        y_scroll.grid(row=0, column=1, sticky='ns')

        x_scroll = ttk.Scrollbar(table_frame, orient='horizontal')
        x_scroll.grid(row=1, column=0, sticky='ew')

        # TreeView
        self.tree = ttk.Treeview(
            table_frame,
            columns=('ID', 'Nombre', 'Descripción', 'Cantidad', 'Stock Mínimo', 'Ubicación', 'Fecha', 'Categoría', 'Estado'),
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Configurar columnas
        columns_config = {
            'ID': {'width': 60, 'anchor': 'center'},
            'Nombre': {'width': 200, 'anchor': 'w'},
            'Descripción': {'width': 300, 'anchor': 'w'},
            'Cantidad': {'width': 80, 'anchor': 'center'},
            'Stock Mínimo': {'width': 100, 'anchor': 'center'},
            'Ubicación': {'width': 150, 'anchor': 'w'},
            'Fecha': {'width': 100, 'anchor': 'center'},
            'Categoría': {'width': 120, 'anchor': 'w'},
            'Estado': {'width': 80, 'anchor': 'center'}
        }

        for col, config in columns_config.items():
            self.tree.column(col, width=config['width'], anchor=config['anchor'])
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_columna(c))

        # Configurar scrollbars
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        # Configurar eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.open_context_menu)
        self.tree.bind('<Return>', lambda e: self.editar_articulo())
        self.tree.bind('<Delete>', lambda e: self.eliminar_articulo())

        # Configurar tags para estilos de fila
        self.tree.tag_configure('oddrow', background='#f5f5f5')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('match', background='#e3f2fd')
        self.tree.tag_configure('stock_critico', foreground='#d32f2f')
        self.tree.tag_configure('stock_bajo', foreground='#f57c00')
        self.tree.tag_configure('stock_ok', foreground='#388e3c')

        # Cargar datos iniciales
        self.cargar_datos()

    def setup_details_frame(self):
        """Configura el panel de detalles del artículo con diseño profesional y espaciado adecuado"""
        # Frame principal de detalles con estilo mejorado
        self.details_frame.configure(width=350)  # Ancho fijo inicial para el panel de detalles
        self.details_frame.grid_propagate(False)  # Evitar que el frame se encoja
        self.details_frame.pack_propagate(False)  # Evitar que el frame se encoja con pack
        
        # Esquema de colores con tonos naranja (temporales, actualizaremos en la siguiente parte)
        details_colors = {
            'background': '#FFF8F0',      # Fondo beige muy claro
            'panel_bg': '#FFFFFF',        # Blanco puro para paneles
            'border': '#FFE0BD',          # Borde naranja muy claro
            'header_bg': '#FFF0E0',       # Fondo para headers (naranja muy claro)
            'accent': '#FF8C00',          # Naranja como color de acento
            'accent_light': '#FFD8B0',    # Naranja claro para fondos de acento
            'text': '#3D3D3D',            # Gris oscuro para texto principal
            'text_secondary': '#666666',  # Gris medio para texto secundario
            'success': '#8BC34A',         # Verde para estados positivos
            'warning': '#FFC107',         # Amarillo/naranja para advertencias
            'danger': '#FF5722'           # Naranja rojizo para alertas
        }
        
        # Frame contenedor principal con borde
        details_container = ttk.Frame(
            self.details_frame,
            style='DetailContainer.TFrame',
            padding=(8, 5, 8, 5)
        )
        details_container.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Aplicar estilo al contenedor principal
        style = ttk.Style()
        style.configure(
            'DetailContainer.TFrame',
            background=details_colors['background'],
            borderwidth=1,
            relief='solid',
            bordercolor=details_colors['border']
        )
        
        # Canvas para scroll con bordes invisibles
        canvas = tk.Canvas(
            details_container,
            highlightthickness=0,
            background=details_colors['background']
        )
        
        # Scrollbar más delgada y discreta
        scrollbar = ttk.Scrollbar(
            details_container,
            orient="vertical",
            command=canvas.yview,
            style='Detail.Vertical.TScrollbar'
        )
        
        # Estilo para scrollbar
        style.configure(
            'Detail.Vertical.TScrollbar',
            background=details_colors['accent'],
            troughcolor=details_colors['background'],
            borderwidth=0,
            arrowcolor=details_colors['panel_bg'],
            relief='flat',
            width=6
        )
        
        # Frame interno scrollable
        scrollable_frame = ttk.Frame(
            canvas,
            style='DetailScroll.TFrame',
            padding=(5, 3, 5, 3)
        )
        
        # Configurar scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Asegurar que el ancho del canvas se ajuste al contenedor
        def adjust_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(frame_id, width=canvas_width - 2)
            
        canvas.bind('<Configure>', adjust_canvas_width)
        
        # Crear ventana del canvas - ajustable al ancho
        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side='left', fill='both', expand=True)
        
        # Configurar scroll del canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Eventos para mostrar/ocultar scrollbar automáticamente
        def on_enter(event):
            if canvas.winfo_height() < scrollable_frame.winfo_reqheight():
                scrollbar.pack(side='right', fill='y')
                
        def on_leave(event):
            # Verifica si el cursor está fuera del área del canvas
            if not (canvas.winfo_rootx() <= event.x_root <= canvas.winfo_rootx() + canvas.winfo_width()):
                scrollbar.pack_forget()
        
        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Motion>', on_enter)  # También activar al mover dentro del canvas
        
        # Habilitar scroll con el ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Header con título centralizado e icono
        header_frame = ttk.Frame(scrollable_frame, style='DetailHeader.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Estilo para el header
        style.configure(
            'DetailHeader.TFrame',
            background=details_colors['header_bg'],
            borderwidth=1,
            relief='solid',
            bordercolor=details_colors['border']
        )
        
        # Etiqueta de título con icono incorporado
        title_label = ttk.Label(
            header_frame,
            text="📋 Detalles del Artículo",
            style='DetailHeader.TLabel',
            font=('Segoe UI', 11, 'bold'),
            padding=(10, 8)
        )
        title_label.pack(fill='x')
        title_label.configure(anchor='center')  # Centrar el título
        
        # Estilo para el encabezado
        style.configure(
            'DetailHeader.TLabel',
            background=details_colors['header_bg'],
            foreground=details_colors['accent']
        )
        
        # Contenedor principal - Cambiamos a single-column layout para más espacio
        main_content = ttk.Frame(scrollable_frame, style='DetailContent.TFrame')
        main_content.pack(fill='x', pady=3)
        
        style.configure(
            'DetailContent.TFrame',
            background=details_colors['background']
        )
        
        # Creamos primero la sección de información básica
        info_frame = ttk.LabelFrame(
            main_content, 
            text="Información",
            style='Detail.TLabelframe'
        )
        info_frame.pack(fill='x', padx=5, pady=5)
        
        # Estilo para labelframes
        style.configure(
            'Detail.TLabelframe',
            background=details_colors['panel_bg'],
            borderwidth=1,
            relief='solid',
            bordercolor=details_colors['border']
        )
        
        style.configure(
            'Detail.TLabelframe.Label',
            background=details_colors['header_bg'],
            foreground=details_colors['accent'],
            font=('Segoe UI', 10, 'bold')
        )
        
        # Estilo para etiquetas de campo
        style.configure(
            'DetailField.TLabel',
            background=details_colors['panel_bg'],
            foreground=details_colors['text_secondary'],
            font=('Segoe UI', 10)  # Incrementamos tamaño de fuente
        )
        
        # Estilos para widgets de entrada
        style.configure(
            'Detail.TEntry',
            font=('Segoe UI', 10),
            fieldbackground=details_colors['panel_bg'],
            foreground=details_colors['text']
        )
        
        style.configure(
            'Detail.TSpinbox',
            font=('Segoe UI', 10),
            fieldbackground=details_colors['panel_bg'],
            foreground=details_colors['text']
        )
        
        style.configure(
            'Detail.TCombobox',
            font=('Segoe UI', 10),
            fieldbackground=details_colors['panel_bg'],
            foreground=details_colors['text']
        )
        
        # Datos para cada campo en la sección de información
        info_fields = [
            ('Nombre', 'entry', self.nombre_var, "Nombre del artículo"),
            ('Cantidad', 'spinbox', self.cantidad_var, "Cantidad en inventario"),
            ('Stock Mínimo', 'spinbox', self.stock_minimo_var, "Cantidad mínima antes de reordenar")
        ]
        
        self.detail_entries = {}
        
        # Crear cada campo con espacio adecuado
        for i, (field_name, field_type, field_var, tooltip) in enumerate(info_fields):
            # Contenedor para cada campo (más respiro vertical)
            field_container = ttk.Frame(info_frame, style='DetailField.TFrame')
            field_container.pack(fill='x', padx=8, pady=5)
            field_container.columnconfigure(0, weight=1)
            
            # Etiqueta del campo
            ttk.Label(
                field_container,
                text=f"{field_name}:",
                style='DetailField.TLabel'
            ).pack(anchor='w', pady=(0, 3))
            
            # Widget específico según el tipo
            if field_type == 'entry':
                widget = ttk.Entry(
                    field_container,
                    textvariable=field_var,
                    style='Detail.TEntry',
                    width=25,  # Ancho incrementado
                    justify='center'
                )
            elif field_type == 'spinbox':
                widget = ttk.Spinbox(
                    field_container,
                    textvariable=field_var,
                    from_=0,
                    to=99999,
                    style='Detail.TSpinbox',
                    width=20,  # Ancho incrementado
                    justify='center'
                )
            
            # Añadimos el widget al contenedor
            widget.pack(fill='x', ipady=3)  # Más alto
            self.detail_entries[field_name] = widget
            Tooltip(widget, tooltip)
        
        # Ahora la sección de clasificación
        clasif_frame = ttk.LabelFrame(
            main_content, 
            text="Clasificación",
            style='Detail.TLabelframe'
        )
        clasif_frame.pack(fill='x', padx=5, pady=5)
        
        # Datos para campos de clasificación
        clasif_fields = [
            ('Categoría', 'combobox', self.categoria_var, "Categoría del artículo"),
            ('Ubicación', 'entry', self.ubicacion_var, "Ubicación física del artículo"),
            ('Fecha', 'date', self.fecha_var, "Fecha de ingreso al inventario")
        ]
        
        # Crear campos de clasificación
        for i, (field_name, field_type, field_var, tooltip) in enumerate(clasif_fields):
            field_container = ttk.Frame(clasif_frame, style='DetailField.TFrame')
            field_container.pack(fill='x', padx=8, pady=5)
            field_container.columnconfigure(0, weight=1)
            
            ttk.Label(
                field_container,
                text=f"{field_name}:",
                style='DetailField.TLabel'
            ).pack(anchor='w', pady=(0, 3))
            
            if field_type == 'entry':
                widget = ttk.Entry(
                    field_container,
                    textvariable=field_var,
                    style='Detail.TEntry',
                    width=25,
                    justify='center'
                )
            elif field_type == 'combobox':
                widget = ttk.Combobox(
                    field_container,
                    textvariable=field_var,
                    values=["Herramientas", "Electrónicos", "Muebles", "Otros"],
                    state='readonly',
                    style='Detail.TCombobox',
                    width=25,  # Ancho incrementado
                    justify='center'
                )
            elif field_type == 'date':
                widget = DateEntry(
                    field_container,
                    textvariable=field_var,
                    width=20,  # Ancho incrementado
                    background=details_colors['header_bg'],
                    foreground=details_colors['text'],
                    bordercolor=details_colors['border'],
                    date_pattern='yyyy-mm-dd',
                    justify='center'
                )
            
            widget.pack(fill='x', ipady=3)
            self.detail_entries[field_name] = widget
            Tooltip(widget, tooltip)
        
        # Sección de descripción
        description_frame = ttk.LabelFrame(
            main_content, 
            text="Descripción",
            style='Detail.TLabelframe'
        )
        description_frame.pack(fill='x', padx=5, pady=5)
        
        # Campo de texto para descripción
        text_widget = tk.Text(
            description_frame,
            height=4,
            wrap='word',
            font=('Segoe UI', 10),  # Texto más grande
            bg=details_colors['panel_bg'],
            fg=details_colors['text']
        )
        text_widget.pack(fill='x', padx=8, pady=8)
        self.detail_entries['Descripción'] = text_widget
        
        # Panel de botones para acciones
        actions_frame = ttk.LabelFrame(
            main_content,
            text="Acciones",
            style='Detail.TLabelframe'
        )
        actions_frame.pack(fill='x', padx=5, pady=5)
        
        # Contenedor para botones 
        buttons_container = ttk.Frame(actions_frame, style='DetailButtons.TFrame')
        buttons_container.pack(fill='x', padx=8, pady=8)
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)
        buttons_container.columnconfigure(2, weight=1)
        
        # Estilo para botones
        style.configure(
            'Detail.TButton',
            font=('Segoe UI', 10, 'bold'),  # Texto más grande
            background=details_colors['panel_bg'],
            foreground=details_colors['text']
        )
        
        style.map('Detail.TButton',
            background=[('active', details_colors['accent'])],
            foreground=[('active', 'white')]
        )
        
        # Botones de acción
        ttk.Button(
            buttons_container,
            text="💾 Guardar",
            command=self.guardar_detalles,
            style='Detail.TButton'
        ).grid(row=0, column=0, padx=3, pady=3, sticky='ew')
        
        ttk.Button(
            buttons_container,
            text="🧹 Limpiar",
            command=self.limpiar_campos,
            style='Detail.TButton'
        ).grid(row=0, column=1, padx=3, pady=3, sticky='ew')
        
        ttk.Button(
            buttons_container,
            text="🗑️ Eliminar",
            command=self.eliminar_articulo,
            style='Detail.TButton'
        ).grid(row=0, column=2, padx=3, pady=3, sticky='ew')
        
        # Sección de imagen
        image_frame = ttk.LabelFrame(
            main_content,
            text="Imagen",
            style='Detail.TLabelframe'
        )
        image_frame.pack(fill='x', padx=5, pady=5)
        
        # Tamaño de imagen adecuado
        self.image_size = (200, 150)
        blank_image = Image.new('RGB', self.image_size, details_colors['panel_bg'])
        self.blank_photo = ImageTk.PhotoImage(blank_image)
        
        # Contenedor para la imagen
        image_container = ttk.Frame(image_frame, style='DetailImage.TFrame')
        image_container.pack(padx=8, pady=8, fill='x')
        
        # Centrar la imagen horizontalmente
        image_container.columnconfigure(0, weight=1)
        
        # Estilo para el marco de la imagen
        style.configure(
            'DetailImage.TFrame',
            background=details_colors['panel_bg']
        )
        
        # Label para la imagen en un contenedor centrado
        center_container = ttk.Frame(image_container, style='DetailImage.TFrame')
        center_container.grid(row=0, column=0)
        
        self.image_label = ttk.Label(
            center_container,
            image=self.blank_photo,
            style='DetailImage.TLabel'
        )
        self.image_label.pack(pady=5)
        
        # Botones para gestionar la imagen
        img_buttons_container = ttk.Frame(image_frame, style='DetailButtons.TFrame')
        img_buttons_container.pack(fill='x', padx=8, pady=(0, 8))
        img_buttons_container.columnconfigure(0, weight=1)
        img_buttons_container.columnconfigure(1, weight=1)
        
        ttk.Button(
            img_buttons_container,
            text="📸 Seleccionar",
            command=self.seleccionar_imagen,
            style='Detail.TButton'
        ).grid(row=0, column=0, padx=3, sticky='ew')
        
        ttk.Button(
            img_buttons_container,
            text="❌ Eliminar",
            command=self.eliminar_imagen,
            style='Detail.TButton'
        ).grid(row=0, column=1, padx=3, sticky='ew')

    def guardar_detalles(self):
        """Guarda los cambios del artículo en la base de datos"""
        try:
            # Obtener el ID del artículo seleccionado
            selected = self.tree.selection()
            if not selected:
                self.show_notification("Seleccione un artículo para guardar", type_='warning')
                return

            articulo_id = self.tree.item(selected[0])['values'][0]

            # Validar campos requeridos
            if not self.nombre_var.get().strip():
                self.show_notification("El nombre es obligatorio", type_='error')
                return

            try:
                cantidad = int(self.cantidad_var.get())
                if cantidad < 0:
                    raise ValueError("La cantidad debe ser positiva")
            except ValueError as e:
                self.show_notification(f"Error en cantidad: {str(e)}", type_='error')
                return

            try:
                stock_minimo = int(self.stock_minimo_var.get()) if self.stock_minimo_var.get() else None
                if stock_minimo is not None and stock_minimo < 0:
                    raise ValueError("El stock mínimo debe ser positivo")
            except ValueError as e:
                self.show_notification(f"Error en stock mínimo: {str(e)}", type_='error')
                return

            # Obtener descripción del widget Text
            descripcion = self.detail_entries['Descripción'].get('1.0', 'end-1c')

            # Actualizar en la base de datos
            if self.controller.actualizar_articulo(
                articulo_id,
                self.nombre_var.get().strip(),
                descripcion,
                cantidad,
                self.categoria_var.get(),
                self.ubicacion_var.get().strip(),
                stock_minimo
            ):
                # Actualizar la tabla
                self.cargar_datos()
                
                # Actualizar la fila seleccionada
                for item in self.tree.get_children():
                    if self.tree.item(item)['values'][0] == articulo_id:
                        self.tree.selection_set(item)
                        self.tree.see(item)
                        break

                self.show_notification("Artículo actualizado correctamente", type_='success')
            else:
                self.show_notification("Error al actualizar el artículo", type_='error')

        except Exception as e:
            self.show_notification(f"Error al guardar: {str(e)}", type_='error')

    def show_status_message(self, message):
        self.status_message.set(message)

    def cargar_datos(self, filtros=None):
        """Carga los datos en el Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        articulos = self.controller.get_articulos(filtros=filtros)
        for i, articulo in enumerate(articulos):
            estado, estado_color_tag = self.determinar_estado_stock(articulo)
            tags = ('oddrow',) if i % 2 != 0 else ('evenrow',)
            if estado_color_tag:
                tags = tags + (f'stock_{estado_color_tag}',)

            self.tree.insert('', 'end', values=(
                articulo[0],  # ID
                articulo[1],  # Nombre
                articulo[2],  # Descripción
                articulo[3],  # Cantidad
                articulo[7],  # Stock Mínimo
                articulo[6],  # Ubicación
                articulo[4],  # Fecha
                articulo[5],  # Categoría
                estado        # Estado
            ), tags=tags)

    def determinar_estado_stock(self, articulo):
        """Determina el estado del stock basado en la cantidad y el stock mínimo"""
        cantidad = articulo[3]
        stock_minimo = articulo[7]
        if stock_minimo is not None:
            if cantidad <= 0:
                return "Crítico", "critico"
            elif cantidad <= stock_minimo:
                return "Bajo", "bajo"
            else:
                return "OK", "ok"
        else:
            return "OK", "ok"

    def on_search_change(self, *args):
        """Maneja los cambios en el campo de búsqueda"""
        if self.search_debounce_id:
            self.parent.after_cancel(self.search_debounce_id)
        self.search_debounce_id = self.parent.after(300, self.buscar_articulo)

    def buscar_articulo(self, event=None):
        """Filtra los artículos en el Treeview según la entrada de búsqueda"""
        search_term = self.search_var.get().strip().lower()
        selected_column = self.filter_column.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        articulos = self.controller.buscar_articulos(search_term)
        for i, articulo in enumerate(articulos):
            estado, estado_color_tag = self.determinar_estado_stock(articulo)
            tags = ('oddrow',) if i % 2 != 0 else ('evenrow',)
            if estado_color_tag:
                tags = tags + (f'stock_{estado_color_tag}',)

            self.tree.insert('', 'end', values=(
                articulo[0],  # ID
                articulo[1],  # Nombre
                articulo[2],  # Descripción
                articulo[3],  # Cantidad
                articulo[7],  # Stock Mínimo
                articulo[6],  # Ubicación
                articulo[4],  # Fecha
                articulo[5],  # Categoría
                estado        # Estado
            ), tags=tags)

    def aplicar_filtros(self):
        """Aplica los filtros avanzados"""
        categoria_filter = self.categoria_filter_var.get()
        stock_min_filter = self.stock_min_filter_var.get()
        stock_max_filter = self.stock_max_filter_var.get()
        fecha_inicio_filter_str = self.fecha_inicio_filter_var.get()
        fecha_fin_filter_str = self.fecha_fin_filter_var.get()

        try:
            fecha_inicio_filter = datetime.strptime(fecha_inicio_filter_str, '%Y-%m-%d').date() if fecha_inicio_filter_str else None
            fecha_fin_filter = datetime.strptime(fecha_fin_filter_str, '%Y-%m-%d').date() if fecha_fin_filter_str else None
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido")
            return

        try:
            stock_min_filter = int(stock_min_filter) if stock_min_filter else None
            stock_max_filter = int(stock_max_filter) if stock_max_filter else None
            if (stock_min_filter is not None and stock_min_filter < 0) or \
               (stock_max_filter is not None and stock_max_filter < 0):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Los valores de stock deben ser números enteros no negativos")
            return

        filtros = {
            'categoria': categoria_filter if categoria_filter != 'Todos' else None,
            'min_stock': stock_min_filter,
            'max_stock': stock_max_filter,
            'fecha_inicio': fecha_inicio_filter,
            'fecha_fin': fecha_fin_filter
        }

        self.cargar_datos(filtros=filtros)

    def limpiar_filtros(self):
        """Limpia todos los filtros aplicados"""
        # Restablecer el campo de búsqueda con placeholder
        self.search_var.set("")
        if hasattr(self, 'search_entry'):
            self.search_entry.configure(foreground=self.colors['text_secondary'])
        
        # Restablecer el campo de búsqueda seleccionado (ID por defecto)
        self.filter_column.set("id")
        
        # Actualizar estado de los botones de campo
        if hasattr(self, 'field_buttons') and len(self.field_buttons) > 0:
            self.field_buttons[0].invoke()
        
        # Restablecer filtros avanzados
        self.limpiar_filtros_avanzados()
        
        # Cargar datos sin filtros
        self.cargar_datos()
        
        # Mostrar mensaje
        self.show_status_message("Filtros eliminados")

    def limpiar_filtros_avanzados(self):
        """Limpia los filtros avanzados"""
        self.categoria_filter_var.set('')
        self.stock_min_filter_var.set('')
        self.stock_max_filter_var.set('')
        self.fecha_inicio_filter_var.set('')
        self.fecha_fin_filter_var.set('')
        self.cargar_datos()

    def toggle_filters(self):
        """Alterna la visibilidad del frame de filtros avanzados"""
        if self.is_filters_expanded.get():
            self.advanced_filters.grid_remove()
            self.filter_toggle_btn.config(text="▼ Filtros Avanzados")
            self.is_filters_expanded.set(False)
        else:
            self.advanced_filters.grid()
            self.filter_toggle_btn.config(text="▲ Filtros Avanzados")
            self.is_filters_expanded.set(True)

    def on_double_click(self, event):
        """Maneja el doble clic en un artículo para editarlo"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            articulo_id = self.tree.item(item)['values'][0]
            self.editar_articulo(articulo_id)

    def open_context_menu(self, event):
        """Abre el menú contextual al hacer clic derecho"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu = tk.Menu(self.parent, tearoff=0)
            self.context_menu.add_command(label="Editar ✏️", command=lambda: self.editar_articulo(self.tree.item(item)['values'][0]))
            self.context_menu.add_command(label="Eliminar 🗑️", command=self.eliminar_articulo)
            self.context_menu.post(event.x_root, event.y_root)

    def editar_articulo(self, articulo_id):
        """Abre el diálogo de edición para un artículo"""
        articulo = self.controller.get_articulo_by_id(articulo_id)
        if articulo:
            dialog = EditProductoDialog(self.parent, "Editar Producto", articulo)
            self.parent.wait_window(dialog)
            if dialog.result:
                if self.controller.actualizar_articulo(
                    dialog.result['id'],
                    dialog.result['nombre'],
                    dialog.result['descripcion'],
                    dialog.result['cantidad'],
                    dialog.result['categoria'],
                    dialog.result['ubicacion'],
                    dialog.result['stock_minimo']
                ):
                    self.cargar_datos()
                    self.show_status_message("Artículo actualizado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el artículo")

    def limpiar_campos(self):
        """Limpia todos los campos del formulario"""
        self.nombre_var.set('')
        self.descripcion_var.set('')
        self.cantidad_var.set('')
        self.fecha_var.set('')
        self.categoria_var.set('')
        self.ubicacion_var.set('')
        self.stock_minimo_var.set('')

        # Limpiar campo de texto de descripción si existe
        if 'Descripción' in self.detail_entries and isinstance(self.detail_entries['Descripción'], tk.Text):
            self.detail_entries['Descripción'].delete('1.0', tk.END)

        # Limpiar imagen
        self.image_label.config(image=self.blank_photo)
        self.image_label.image = self.blank_photo
        self.current_image = None

    def eliminar_articulo(self):
        """Elimina el artículo seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para eliminar")
            return

        articulo_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este artículo?"):
            if self.controller.eliminar_articulo(articulo_id):
                self.show_status_message("Artículo eliminado correctamente")
                self.cargar_datos()
                self.limpiar_campos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el artículo")

    def seleccionar_imagen(self):
        """Permite seleccionar una imagen para el artículo"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                image = image.resize(self.image_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                self.image_label.config(image=photo)
                self.image_label.image = photo
                self.current_image = file_path

                # Guardar imagen si hay un artículo seleccionado
                selected = self.tree.selection()
                if selected:
                    articulo_id = self.tree.item(selected[0])['values'][0]
                    if self.controller.guardar_imagen(articulo_id, file_path):
                        self.show_status_message("Imagen guardada correctamente")
                    else:
                        messagebox.showerror("Error", "No se pudo guardar la imagen")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")

    def eliminar_imagen(self):
        """Elimina la imagen del artículo seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para eliminar su imagen")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar la imagen?"):
            articulo_id = self.tree.item(selected[0])['values'][0]
            if self.controller.eliminar_imagen(articulo_id):
                self.image_label.config(image=self.blank_photo)
                self.image_label.image = self.blank_photo
                self.current_image = None
                self.show_status_message("Imagen eliminada correctamente")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la imagen")

    def cargar_imagen_articulo(self, articulo_id):
        """Carga y muestra la imagen de un artículo"""
        imagen_path = self.controller.get_imagen_articulo(articulo_id)

        try:
            if imagen_path and os.path.exists(imagen_path):
                # Abrir y procesar la imagen
                image = Image.open(imagen_path)

                # Calcular el ratio de aspecto para mantener las proporciones
                width, height = image.size
                ratio = min(self.image_size[0]/width, self.image_size[1]/height)
                new_size = (int(width * ratio), int(height * ratio))

                # Redimensionar la imagen manteniendo la proporción
                image = image.resize(new_size, Image.Resampling.LANCZOS)

                # Crear una imagen en blanco del tamaño del contenedor
                background = Image.new('RGB', self.image_size, 'white')

                # Calcular la posición para centrar la imagen
                x = (self.image_size[0] - new_size[0]) // 2
                y = (self.image_size[1] - new_size[1]) // 2

                # Pegar la imagen redimensionada en el centro
                background.paste(image, (x, y))

                # Convertir a PhotoImage
                photo = ImageTk.PhotoImage(background)

                # Actualizar la etiqueta con la nueva imagen
                if hasattr(self, 'image_label'):
                    self.image_label.config(image=photo)
                    self.image_label.image = photo  # Mantener referencia
                    self.current_image = imagen_path

                self.show_status_message("Imagen cargada correctamente")
            else:
                if hasattr(self, 'image_label'):
                    self.image_label.config(image=self.blank_photo)
                    self.image_label.image = self.blank_photo
                    self.current_image = None
                self.show_status_message("No hay imagen disponible para este artículo")

        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            if hasattr(self, 'image_label'):
                self.image_label.config(image=self.blank_photo)
                self.image_label.image = self.blank_photo
                self.current_image = None
            self.show_status_message("Error al cargar la imagen del artículo")

    def show_column_tooltip(self, event, column):
        """Muestra el tooltip de una columna"""
        x, y, _, _ = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 25
        y += event.widget.winfo_rooty() + 20

        # Crear ventana de tooltip
        self.tooltip_window = tw = tk.Toplevel(event.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Obtener texto del tooltip según la columna
        tooltips = {
            'ID': 'Identificador único del artículo',
            'Nombre': 'Nombre del artículo',
            'Descripción': 'Descripción detallada del artículo',
            'Cantidad': 'Cantidad actual en inventario',
            'Stock Mínimo': 'Cantidad mínima antes de reordenar',
            'Ubicación': 'Ubicación física del artículo',
            'Fecha': 'Fecha de última actualización',
            'Categoría': 'Categoría del artículo',
            'Estado': 'Estado actual del stock'
        }

        label = tk.Label(
            tw,
            text=tooltips.get(column, ''),
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            font=("Arial", "8", "normal")
        )
        label.pack(ipadx=1)

    def hide_column_tooltip(self, event=None):
        """Oculta el tooltip de una columna"""
        if hasattr(self, 'tooltip_window') and self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def ordenar_columna(self, col):
        """Ordena el TreeView por una columna"""
        if not hasattr(self, 'sort_reverse'):
            self.sort_reverse = {}
        self.sort_reverse[col] = not self.sort_reverse.get(col, False)

        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]

        # Convertir valores para ordenamiento correcto
        def convert_value(value, column):
            if column in ['ID', 'Cantidad', 'Stock Mínimo']:
                try:
                    return int(value)
                except ValueError:
                    return 0
            elif column == 'Fecha':
                try:
                    return datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    return datetime.min
            return value.lower()

        items.sort(key=lambda x: convert_value(x[0], col), reverse=self.sort_reverse[col])

        # Reordenar items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)

        # Actualizar encabezado para mostrar dirección de ordenamiento
        for header in self.tree['columns']:
            if header == col:
                self.tree.heading(header, text=f"{header} {'↓' if self.sort_reverse[col] else '↑'}")
            else:
                self.tree.heading(header, text=header)

    def _get_field_icon(self, field):
        """Obtiene el icono para un campo específico"""
        icons = {
            'Nombre': '📛',
            'Descripción': '📝',
            'Cantidad': '🔢',
            'Fecha': '📅',
            'Categoría': '🏷️',
            'Ubicación': '📍',
            'Stock Mínimo': '⚠️'
        }
        return icons.get(field, '•')

    def setup_search_filters(self):
        """Configura los filtros de búsqueda rápida con enfoque en facilidad de uso"""
        # Frame de búsqueda con diseño mejorado
        search_frame = ttk.LabelFrame(self.filters_frame, text="🔍 Búsqueda Rápida", padding=10)
        search_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        search_frame.grid_columnconfigure(0, weight=1)

        # Campo unificado de búsqueda con icono
        search_container = ttk.Frame(search_frame)
        search_container.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        search_container.grid_columnconfigure(1, weight=1)

        # Icono de búsqueda
        ttk.Label(
            search_container, 
            text="🔍", 
            font=('Segoe UI', 12)
        ).grid(row=0, column=0, padx=(0, 5))

        # Entry principal de búsqueda con placeholder
        self.search_entry = ttk.Entry(
            search_container,
            textvariable=self.search_var,
            style='Search.TEntry',
            font=('Segoe UI', 10),
            width=30
        )
        self.search_entry.grid(row=0, column=1, sticky='ew')
        
        # Configurar placeholder
        self.search_var.set("")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_placeholder)
        self.search_entry.bind("<Return>", self.aplicar_filtros)

        # Selector de campo de búsqueda con diseño claro
        field_frame = ttk.Frame(search_frame)
        field_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        field_frame.grid_columnconfigure(0, weight=1)


        # Botones de acción
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=2, column=0, sticky='ew')
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ttk.Button(
            button_frame,
            text="Limpiar",
            command=self.limpiar_filtros,
            style='Secondary.TButton',
            width=12
        ).grid(row=0, column=0, sticky='w', padx=2)

        ttk.Button(
            button_frame,
            text="Buscar",
            command=self.aplicar_filtros,
            style='Primary.TButton', 
            width=12
        ).grid(row=0, column=1, sticky='e', padx=2)

    def setup_advanced_filters(self):
        """Configura los filtros avanzados"""
        # Botón para mostrar/ocultar filtros avanzados
        self.filter_toggle_btn = ttk.Button(
            self.filters_frame,
            text="▼ Filtros Avanzados",
            command=self.toggle_filters,
            style='Link.TButton'
        )
        self.filter_toggle_btn.grid(row=1, column=0, sticky='ew', padx=5, pady=5)

        # Frame de filtros avanzados
        self.advanced_filters = ttk.LabelFrame(self.filters_frame, text="⚙️ Filtros Avanzados", padding=10)
        self.advanced_filters.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        self.advanced_filters.grid_columnconfigure(0, weight=1)

        current_row = 0

        # Categoría
        ttk.Label(self.advanced_filters, text="Categoría:", style='Field.TLabel').grid(row=current_row, column=0, sticky='w', pady=(0, 5))
        current_row += 1

        self.categoria_filter_combo = ttk.Combobox(
            self.advanced_filters,
            textvariable=self.categoria_filter_var,
            values=["Todos", "Herramientas", "Electrónicos", "Muebles", "Otros"],
            state='readonly',
            style='FilterEntry.TCombobox'
        )
        self.categoria_filter_combo.grid(row=current_row, column=0, sticky='ew', pady=(0, 10))
        current_row += 1

        # Stock
        ttk.Label(self.advanced_filters, text="Rango de Stock:", style='Field.TLabel').grid(row=current_row, column=0, sticky='w', pady=(0, 5))
        current_row += 1

        stock_frame = ttk.Frame(self.advanced_filters)
        stock_frame.grid(row=current_row, column=0, sticky='ew', pady=(0, 10))
        stock_frame.grid_columnconfigure((0, 2), weight=1)
        current_row += 1

        self.stock_min_filter_spin = ttk.Spinbox(
            stock_frame,
            textvariable=self.stock_min_filter_var,
            from_=0,
            to=99999,
            width=10,
            style='FilterEntry.TSpinbox'
        )
        self.stock_min_filter_spin.grid(row=0, column=0, sticky='w')

        ttk.Label(stock_frame, text="a", style='Field.TLabel').grid(row=0, column=1, padx=5)

        self.stock_max_filter_spin = ttk.Spinbox(
            stock_frame,
            textvariable=self.stock_max_filter_var,
            from_=0,
            to=99999,
            width=10,
            style='FilterEntry.TSpinbox'
        )
        self.stock_max_filter_spin.grid(row=0, column=2, sticky='e')

        # Fecha
        ttk.Label(self.advanced_filters, text="Rango de Fechas:", style='Field.TLabel').grid(row=current_row, column=0, sticky='w', pady=(0, 5))
        current_row += 1

        # Fecha inicio
        ttk.Label(self.advanced_filters, text="Desde:", style='Field.TLabel').grid(row=current_row, column=0, sticky='w', pady=(0, 5))
        current_row += 1

        self.fecha_inicio_filter_date = DateEntry(
            self.advanced_filters,
            textvariable=self.fecha_inicio_filter_var,
            date_pattern='yyyy-mm-dd',
            style='FilterEntry.TEntry'
        )
        self.fecha_inicio_filter_date.grid(row=current_row, column=0, sticky='ew', pady=(0, 5))
        current_row += 1

        # Fecha fin
        ttk.Label(self.advanced_filters, text="Hasta:", style='Field.TLabel').grid(row=current_row, column=0, sticky='w', pady=(0, 5))
        current_row += 1

        self.fecha_fin_filter_date = DateEntry(
            self.advanced_filters,
            textvariable=self.fecha_fin_filter_var,
            date_pattern='yyyy-mm-dd',
            style='FilterEntry.TEntry'
        )
        self.fecha_fin_filter_date.grid(row=current_row, column=0, sticky='ew', pady=(0, 10))
        current_row += 1

        # Botones de filtro
        button_frame = ttk.Frame(self.advanced_filters)
        button_frame.grid(row=current_row, column=0, sticky='ew')
        button_frame.grid_columnconfigure((0, 1), weight=1)
        current_row += 1

        ttk.Button(
            button_frame,
            text="Aplicar 🔍",
            command=self.aplicar_filtros
        ).grid(row=0, column=0, sticky='ew', padx=2)

        ttk.Button(
            button_frame,
            text="Limpiar 🧹",
            command=self.limpiar_filtros_avanzados
        ).grid(row=0, column=1, sticky='ew', padx=2)

        # Exportar a Excel
        ttk.Button(
            self.advanced_filters,
            text="Exportar a Excel 📊",
            command=self.exportar_a_excel
        ).grid(row=current_row, column=0, sticky='ew', pady=(10, 0))

    def exportar_a_excel(self):
        """Exporta los datos del inventario a un archivo Excel"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx")]
            )
            if filepath:
                data_export = self.controller.get_inventario_for_export()
                df = pd.DataFrame(
                    data_export,
                    columns=['ID', 'Nombre', 'Descripción', 'Cantidad', 'Stock Mínimo', 'Ubicación', 'Fecha de Ingreso', 'Categoría']
                )
                df.to_excel(filepath, index=False, sheet_name='Inventario')
                messagebox.showinfo("Éxito", f"Inventario exportado a:\n{filepath}")
        except ImportError:
            messagebox.showerror("Error", "Para exportar a Excel, necesitas tener instalado 'pandas'.\nInstálalo con: pip install pandas")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {e}")

    def update_filters_from_panel(self, nombre_filter, categoria_filter, ubicacion_filter, stock_filter, fecha_filter):
        """Actualiza los filtros y la visualización de los resultados con optimización para búsqueda en tiempo real"""
        # Guardar filtros actuales
        self.current_filters = {
            'nombre': nombre_filter,
            'categoria': categoria_filter,
            'ubicacion': ubicacion_filter,
            'stock': stock_filter,
            'fecha': fecha_filter
        }

        # Si es una actualización muy rápida, evitamos mostrar el indicador de carga
        # para que la interfaz no parpadee constantemente
        show_loading = not (hasattr(self, '_last_filter_time') and 
                         time.time() - self._last_filter_time < 0.3)
        
        self._last_filter_time = time.time()
        
        if show_loading:
            self.show_loading("Aplicando filtros...", delay=100)  # Retrasar un poco para evitar parpadeos

        try:
            # Obtener datos filtrados sin limpiar la tabla primero para evitar parpadeos
            articulos = self.controller.get_articulos()
            filtered_articulos = []

            # Aplicar filtros
            for articulo in articulos:
                if self.matches_filters(articulo):
                    filtered_articulos.append(articulo)

            # Actualizar tabla con animación suave solo si hay cambios significativos
            current_ids = set(self.tree.item(item)['values'][0] for item in self.tree.get_children())
            new_ids = set(articulo[0] for articulo in filtered_articulos)
            
            # Si hay cambios significativos o la cantidad es diferente, actualizar con animación
            significant_change = len(current_ids.symmetric_difference(new_ids)) > 3 or len(current_ids) != len(new_ids)
            
            if significant_change:
                # Para cambios grandes, actualizamos con animación
                self.after(100, lambda: self.update_table_with_animation(filtered_articulos))
            else:
                # Para cambios menores, actualizamos inmediatamente para mejor respuesta
                self._update_table_immediate(filtered_articulos)

            # Actualizar resumen de resultados
            self.update_results_summary(filtered_articulos)

        except Exception as e:
            self.show_notification(f"Error al aplicar filtros: {str(e)}", type_='error')
        finally:
            if show_loading:
                self.hide_loading()
            else:
                # Actualizar el estado aunque no mostremos el loading
                self.status_message.configure(text="")

    def _update_table_immediate(self, articulos):
        """Actualiza la tabla inmediatamente sin animación para mejor respuesta en tiempo real"""
        # Guardar el item seleccionado actualmente para restaurarlo después
        selected_items = self.tree.selection()
        selected_id = None
        if selected_items:
            selected_id = self.tree.item(selected_items[0])['values'][0]
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Añadir artículos
        for i, articulo in enumerate(articulos):
            id_, nombre, descripcion, cantidad, fecha, categoria, ubicacion, stock_minimo = articulo[:8]
            
            values = (id_, nombre, descripcion, cantidad, fecha, categoria, ubicacion, stock_minimo)
            estado = self.determinar_estado_stock(articulo)
            
            # Alternar colores de fila
            row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tags = (row_tag, estado)
            
            # Añadir item
            item_id = self.tree.insert('', 'end', values=values, tags=tags)
            
            # Restaurar selección si corresponde
            if selected_id and id_ == selected_id:
                self.tree.selection_set(item_id)
                self.tree.see(item_id)

    def matches_filters(self, articulo):
        """Verifica si un artículo cumple con los filtros actuales usando búsqueda por prefijo"""
        # Desempaquetar valores del artículo
        id_, nombre, descripcion, cantidad, fecha, categoria, ubicacion, stock_minimo = articulo[:8]

        # Filtro por búsqueda rápida - usa búsqueda por prefijo según el campo seleccionado
        if self.current_filters['nombre'] and self.current_filters['nombre'] != "":
            search_term = self.current_filters['nombre'].lower()
            
            # Mapear el campo seleccionado con la columna correspondiente
            search_column = self.filter_column.get()
            
            if search_column == 'id':
                # Para ID, usamos coincidencia exacta
                if not str(id_).startswith(search_term):
                    return False
            elif search_column == 'nombre':
                # Para nombre, usamos coincidencia por prefijo
                if not nombre.lower().startswith(search_term):
                    return False
            elif search_column == 'descripcion':
                # Para descripción, usamos coincidencia por prefijo
                if not descripcion.lower().startswith(search_term):
                    return False
            elif search_column == 'categoria':
                # Para categoría, usamos coincidencia por prefijo
                if not categoria.lower().startswith(search_term):
                    return False
            elif search_column == 'ubicacion':
                # Para ubicación, usamos coincidencia por prefijo
                if not ubicacion.lower().startswith(search_term):
                    return False
            else:
                # Si no hay campo específico, buscamos en todos
                if not (nombre.lower().startswith(search_term) or 
                       descripcion.lower().startswith(search_term) or 
                       str(id_).startswith(search_term) or
                       categoria.lower().startswith(search_term) or
                       ubicacion.lower().startswith(search_term)):
                    return False

        # Filtro por categoría
        if self.current_filters['categoria'] != 'Todos' and categoria != self.current_filters['categoria']:
            return False

        # Filtro por ubicación - búsqueda más flexible
        if self.current_filters['ubicacion']:
            if not ubicacion.lower().startswith(self.current_filters['ubicacion'].lower()):
                return False

        # Filtro por stock
        if self.current_filters['stock'] != 'Todos':
            estado_actual = self.determinar_estado_stock(articulo)
            stock_filter_mapping = {
                'Crítico': 'stock_critico',
                'Bajo': 'stock_bajo',
                'Normal': 'stock_ok',
                'Alto': 'stock_ok'  # Para "Alto" usamos la misma tag que "Normal"
            }
            
            if estado_actual != stock_filter_mapping.get(self.current_filters['stock']):
                return False

        # Filtro por fecha
        if self.current_filters['fecha']:
            try:
                # Permitir comparaciones de fecha (mayor, menor, igual)
                fecha_input = self.current_filters['fecha']
                fecha_articulo = datetime.strptime(fecha, '%Y-%m-%d').date()
                
                if fecha_input.startswith('>'):
                    # Fecha posterior a
                    target_date = datetime.strptime(fecha_input[1:].strip(), '%Y-%m-%d').date()
                    if fecha_articulo <= target_date:
                        return False
                elif fecha_input.startswith('<'):
                    # Fecha anterior a
                    target_date = datetime.strptime(fecha_input[1:].strip(), '%Y-%m-%d').date()
                    if fecha_articulo >= target_date:
                        return False
                elif fecha_input.startswith('=') or not any(c in '><' for c in fecha_input[:1]):
                    # Fecha exacta (con o sin =)
                    clean_input = fecha_input[1:].strip() if fecha_input.startswith('=') else fecha_input
                    target_date = datetime.strptime(clean_input, '%Y-%m-%d').date()
                    if fecha_articulo != target_date:
                        return False
            except (ValueError, TypeError):
                pass

        return True

    def update_table_with_animation(self, articulos):
        """Actualiza la tabla con una animación suave"""
        def insert_row(index):
            if index < len(articulos):
                articulo = articulos[index]
                estado, estado_color_tag = self.determinar_estado_stock(articulo)
                
                # Determinar tags para la fila
                tags = ('oddrow',) if index % 2 != 0 else ('evenrow',)
                if estado_color_tag:
                    tags = tags + (f'stock_{estado_color_tag}',)
                if any(str(articulo[i]).lower().startswith(self.current_filters.get('nombre', '').lower()) for i in [1, 2]):
                    tags = tags + ('match',)

                # Insertar fila con efecto de fade in
                self.tree.insert('', 'end', values=(
                    articulo[0],  # ID
                    articulo[1],  # Nombre
                    articulo[2],  # Descripción
                    articulo[3],  # Cantidad
                    articulo[7],  # Stock Mínimo
                    articulo[6],  # Ubicación
                    articulo[4],  # Fecha
                    articulo[5],  # Categoría
                    estado        # Estado
                ), tags=tags)

                # Programar la siguiente inserción
                self.after(20, lambda: insert_row(index + 1))
            else:
                # Mostrar notificación al terminar
                total = len(articulos)
                if total == 0:
                    self.show_notification("No se encontraron resultados", type_='warning')
                else:
                    self.show_notification(
                        f"Se encontraron {total} resultado{'s' if total != 1 else ''}",
                        type_='success'
                    )

        # Iniciar animación
        insert_row(0)

    def update_results_summary(self, articulos):
        """Actualiza el resumen de resultados"""
        total = len(articulos)
        
        # Calcular estadísticas
        stats = {
            'total': total,
            'sin_stock': len([a for a in articulos if a[3] <= 0]),
            'bajo_stock': len([a for a in articulos if 0 < a[3] <= a[7] if a[7] is not None]),
            'stock_normal': len([a for a in articulos if a[3] > a[7] if a[7] is not None])
        }
        
        # Actualizar etiquetas de estadísticas
        for key, value in stats.items():
            if hasattr(self, f'{key}_label'):
                getattr(self, f'{key}_label').configure(text=str(value))

        # Actualizar gráfico si existe
        if hasattr(self, 'update_stock_chart'):
            self.update_stock_chart(stats)

    def update_theme(self, new_color_palette):
        """Actualiza el tema de la vista con la nueva paleta de colores"""
        self.colors = new_color_palette
        self.setup_styles()
        
        # Actualizar colores de los widgets existentes
        self.update_widget_colors()

    def update_widget_colors(self):
        """Actualiza los colores de los widgets existentes"""
        style = ttk.Style()
        
        # Actualizar colores del Treeview
        style.configure('Treeview',
                       background=self.colors['surface'],
                       fieldbackground=self.colors['surface'],
                       foreground=self.colors['text'])
        
        style.configure('Treeview.Heading',
                       background=self.colors['background'],
                       foreground=self.colors['text'])
        
        style.map('Treeview',
                 background=[('selected', self.colors['primary_light'])],
                 foreground=[('selected', self.colors['primary_dark'])])

        # Actualizar colores de los frames
        for widget in self.parent.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.configure(style='App.TFrame')

    def _clear_placeholder(self, event):
        """Limpia el placeholder cuando el usuario hace clic en el campo de búsqueda"""
        if self.search_var.get() == "":
            self.search_var.set("")
            self.search_entry.configure(foreground=self.colors['text'])

    def _restore_placeholder(self, event):
        """Restaura el placeholder si el usuario deja el campo vacío"""
        if not self.search_var.get():
            self.search_var.set("")
            self.search_entry.configure(foreground=self.colors['text_secondary'])