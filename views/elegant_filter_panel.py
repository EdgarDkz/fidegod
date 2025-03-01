import tkinter as tk
from tkinter import ttk
from styles.elegant_widgets import ElegantWidgets

class ElegantFilterPanel(ttk.Frame):
    """
    Panel de filtros elegante para la aplicación FIDEGOD.
    Utiliza widgets personalizados para una apariencia más refinada.
    """
    
    def __init__(self, parent, theme_manager, personas_view, *args, **kwargs):
        """
        Inicializa el panel de filtros elegante.
        
        Args:
            parent: Widget padre
            theme_manager: Gestor de temas
            personas_view: Vista de personas para aplicar los filtros
            *args, **kwargs: Argumentos adicionales para el Frame
        """
        super().__init__(parent, *args, **kwargs)
        
        self.personas_view = personas_view
        self.theme_manager = theme_manager
        self.colors = theme_manager.get_color_palette()
        self.fonts = theme_manager.get_fonts()
        
        # Crear widgets elegantes
        self.elegant_widgets = ElegantWidgets(theme_manager)
        
        # Variables para los filtros
        self.nombre_var = tk.StringVar()
        self.articulo_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        self.municipio_var = tk.StringVar(value='Todos')
        self.estado_var = tk.StringVar(value='Todos')
        
        # Configurar el panel
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del panel de filtros."""
        # Contenedor principal con scroll
        self.setup_scrollable_container()
        
        # Título del panel
        title_label = self.elegant_widgets.create_elegant_label(
            self.scrollable_frame,
            text="🔍 Filtros de Búsqueda",
            font_style='h5',
            color=self.colors['primary'],
            padding=(10, 10),
            height=40
        )
        title_label.pack(fill='x', pady=(0, 15))
        
        # Crear filtros
        self.create_filter_widgets()
        
        # Crear botones de acción
        self.create_action_buttons()
    
    def setup_scrollable_container(self):
        """Configura un contenedor con scroll para los filtros."""
        # Canvas para scroll
        self.canvas = tk.Canvas(
            self,
            bg=self.colors['surface'],
            highlightthickness=0
        )
        
        # Scrollbar vertical
        self.scrollbar = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.canvas.yview
        )
        
        # Frame dentro del canvas para los filtros
        self.scrollable_frame = ttk.Frame(
            self.canvas,
            style='Filter.TFrame'
        )
        
        # Configurar scroll
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        
        # Crear ventana en el canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor='nw'
        )
        
        # Empaquetar widgets
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        # Configurar canvas para usar scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Vincular eventos de redimensionamiento
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Vincular eventos de rueda del ratón
        self.bind_mouse_wheel()
    
    def on_canvas_configure(self, event):
        """Ajusta el ancho del frame interno cuando el canvas cambia de tamaño."""
        # Ajustar el ancho del frame interno al ancho del canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def bind_mouse_wheel(self):
        """Vincula el evento de la rueda del ratón al scroll del canvas."""
        def _on_mousewheel(event):
            """Función interna para manejar el evento de la rueda del ratón."""
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            """Función interna para vincular el scroll de la rueda del ratón al canvas."""
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            """Función interna para desvincular el scroll de la rueda del ratón del canvas."""
            self.canvas.unbind_all("<MouseWheel>")
        
        # Vincular eventos cuando el ratón entra y sale del canvas
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def create_filter_widgets(self):
        """Crea los widgets para los filtros."""
        # Configuración de filtros: (etiqueta, variable, icono)
        filters_config = [
            ('Nombre:', self.nombre_var, '👤'),
            ('Artículo:', self.articulo_var, '📦'),
            ('Dirección:', self.direccion_var, '🏠'),
            ('Municipio:', self.municipio_var, '🌆', 'combobox', ["Todos", "Allende", "Hualahuises", "Linares", "Montemorelos", "Rayones", "Terán"]),
            ('Estado:', self.estado_var, '🔔', 'combobox', ['Todos', 'Pendiente', 'Entregado', 'Cancelado'])
        ]
        
        for config in filters_config:
            # Crear frame para el filtro
            filter_frame = ttk.Frame(self.scrollable_frame, style='TFrame')
            filter_frame.pack(fill='x', pady=(0, 5), padx=10)
            
            # Etiqueta con icono
            label_text = f"{config[2]} {config[0]}"
            label = self.elegant_widgets.create_elegant_label(
                filter_frame,
                text=label_text,
                font_style='subtitle2',
                color=self.colors['text'],
                padding=(0, 5),
                height=30
            )
            label.pack(fill='x', pady=(0, 5))
            
            # Widget de entrada según el tipo
            if len(config) > 4 and config[3] == 'combobox':
                # Combobox para selección
                combo = ttk.Combobox(
                    filter_frame,
                    textvariable=config[1],
                    values=config[4],
                    state='readonly',
                    style='TCombobox'
                )
                combo.pack(fill='x', pady=(0, 10))
            else:
                # Entry para texto
                entry = ttk.Entry(
                    filter_frame,
                    textvariable=config[1],
                    style='TEntry'
                )
                entry.pack(fill='x', pady=(0, 10))
            
            # Separador
            separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
            separator.pack(fill='x', pady=(0, 10), padx=5)
    
    def create_action_buttons(self):
        """Crea los botones de acción para el panel de filtros."""
        # Frame para los botones
        button_frame = ttk.Frame(self.scrollable_frame, style='TFrame')
        button_frame.pack(fill='x', pady=(10, 5), padx=10)
        
        # Botón para limpiar filtros
        clear_btn = self.elegant_widgets.create_elegant_button(
            button_frame,
            text="Limpiar Filtros",
            command=self.clear_filters,
            style_type='secondary',
            width=150,
            height=40
        )
        clear_btn.pack(side='left', padx=(0, 10))
        
        # Botón para aplicar filtros
        apply_btn = self.elegant_widgets.create_elegant_button(
            button_frame,
            text="Aplicar Filtros",
            command=self.apply_filters,
            style_type='primary',
            width=150,
            height=40
        )
        apply_btn.pack(side='left')
        
        # Botón para exportar a Excel
        export_btn = self.elegant_widgets.create_elegant_button(
            button_frame,
            text="Exportar a Excel",
            command=self.personas_view.export_to_excel,
            style_type='info',
            width=150,
            height=40
        )
        export_btn.pack(side='left', padx=(10, 0))
    
    def clear_filters(self):
        """Limpia todos los filtros."""
        self.nombre_var.set('')
        self.articulo_var.set('')
        self.direccion_var.set('')
        self.municipio_var.set('Todos')
        self.estado_var.set('Todos')
        
        # Limpiar filtros en la vista de personas
        self.personas_view.clear_filters()
    
    def apply_filters(self):
        """Aplica los filtros a la vista de personas."""
        self.personas_view.update_filters_from_panel(
            nombre_filter=self.nombre_var.get(),
            articulo_filter=self.articulo_var.get(),
            direccion_filter=self.direccion_var.get(),
            municipio_filter=self.municipio_var.get(),
            estado_filter=self.estado_var.get()
        ) 