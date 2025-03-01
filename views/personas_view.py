import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from controllers.personas_controller import PersonasController
from views.Personas_dialogs.add_personas_dialog import AddPersonaDialog
from views.Personas_dialogs.edit_persona_dialog import EditPersonaDialog
from views.Personas_dialogs.confirmar_entrega_dialog import ConfirmarEntregaDialog
import pandas as pd
from tkinter import filedialog
from openpyxl.worksheet.table import Table, TableStyleInfo
import tkinter.font
from PIL import Image, ImageTk  # Asegúrate de importar estas bibliotecas
import os

# --- Implementación Personalizada de Tooltip ---
class Tooltip:
    """
    Clase para crear tooltips (textos emergentes) para widgets.

    Muestra un mensaje de texto cuando el cursor del ratón se sitúa sobre el widget
    y lo oculta cuando el cursor se aleja.
    """
    def __init__(self, widget, text):
        """
        Inicializa el Tooltip.

        Args:
            widget: El widget al que se asociará el tooltip.
            text: El texto que se mostrará en el tooltip.
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self._show_tooltip)
        self.widget.bind("<Leave>", self._hide_tooltip)

    def _show_tooltip(self, event=None):
        """Muestra el tooltip."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Elimina el borde de la ventana
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief='solid', borderwidth=1,
                         font=('Arial', '8', 'normal'))
        label.pack(ipadx=1, ipady=1)

    def _hide_tooltip(self, event=None):
        """Oculta el tooltip si está visible."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class FilterPanel(ttk.Frame):
    """Panel de filtros para la vista de personas."""
    def __init__(self, parent, personas_view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.personas_view = personas_view
        self.color_palette = personas_view.color_palette

        # Variables para los filtros
        self.nombre_var = tk.StringVar()
        self.articulo_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        self.municipio_var = tk.StringVar(value='Todos')
        self.estado_var = tk.StringVar(value='Todos')

        # Contenedor principal para todos los filtros
        filter_container = ttk.Frame(self, style='Filter.TFrame', padding=15)
        filter_container.pack(fill='both', expand=True)

        # Título del panel de filtros con borde
        title_frame = ttk.Frame(filter_container, style='Filter.TFrame')
        title_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(
            title_frame, 
            text="🔍 Filtros de Búsqueda", 
            style='CustomFilterTitle.TLabel'
        ).pack(anchor='center', fill='x', padx=5, pady=5)

        # Separador horizontal después del título
        ttk.Separator(filter_container, orient='horizontal').pack(fill='x', pady=(0, 15))

        # Filtros
        self._create_filter_widgets(filter_container)

        # Botones de acción
        self._create_action_buttons(filter_container)
        
    def _create_filter_widgets(self, container):
        """Crea y configura los widgets de filtro para cada variable."""
        filters_config = [
            ('Nombre:', 'nombre_var', '👤'),
            ('Artículo:', 'articulo_var', '📦'),
            ('Dirección:', 'direccion_var', '🏠'),
            ('Municipio:', 'municipio_var', '🌆'),
            ('Estado:', 'estado_var', '🔔')
        ]

        for i, (label_text, var_name, icon) in enumerate(filters_config):
            filter_frame = ttk.Frame(container, style='FilterRow.TFrame')
            filter_frame.pack(fill='x', pady=(0, 10))

            # Etiqueta del filtro con icono
            label = ttk.Label(filter_frame, text=f"{icon} {label_text}", style='FilterLabel.TLabel')
            label.pack(side='left', padx=(0, 5))

            # Campo de entrada o Combobox para el filtro
            if var_name in ['municipio_var', 'estado_var']:
                values = ["Todos", "Allende", "Hualahuises", "Linares", "Montemorelos", "Rayones", "Terán"] if var_name == 'municipio_var' else ['Todos', 'Pendiente', 'Entregado', 'Cancelado']
                combo = ttk.Combobox(
                    filter_frame,
                    textvariable=getattr(self, var_name),
                    values=values,
                    state='readonly',
                    style='Filter.TCombobox',
                    width=25
                )
                combo.pack(side='left', fill='x', expand=True)
            else:
                entry = ttk.Entry(
                    filter_frame,
                    textvariable=getattr(self, var_name),
                    style='Filter.TEntry'
                )
                entry.pack(side='left', fill='x', expand=True)

            # Separador
            ttk.Separator(container, orient='horizontal').pack(fill='x', pady=(10, 10))

    def _create_action_buttons(self, container):
        """Crea y configura los botones de acción."""
        action_frame = ttk.Frame(container, style='ButtonPanel.TFrame')
        action_frame.pack(fill='x', pady=(10, 0))

        # Botón Limpiar Filtros
        limpiar_btn = tk.Button(
            action_frame, 
            text="Limpiar Filtros", 
            command=self.personas_view.clear_filters,
            bg=self.color_palette['surface'],
            fg=self.color_palette['text'],
            relief=tk.FLAT,
            borderwidth=1,
            font=('Segoe UI', 11),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        limpiar_btn.pack(side='left', padx=(0, 5))

        # Botón Aplicar Filtros
        aplicar_btn = tk.Button(
            action_frame, 
            text="Aplicar Filtros", 
            command=self.update_filters,
            bg=self.color_palette['primary'],
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            font=('Segoe UI', 11, 'bold'),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        aplicar_btn.pack(side='left', padx=(0, 5))

        # Botón Exportar a Excel
        export_btn = tk.Button(
            action_frame, 
            text="Exportar a Excel", 
            command=self.personas_view.export_to_excel,
            bg=self.color_palette['info'],
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            font=('Segoe UI', 11, 'bold'),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        export_btn.pack(side='left', padx=(0, 5))

    def _on_frame_configure(self, event=None):
        """Ajusta el tamaño del canvas cuando el panel cambia de tamaño."""
        # Actualizar el ancho del canvas y la ventana interna
        canvas_width = event.width - self.scrollbar.winfo_width() - 5  # 5 píxeles de margen
        canvas_height = event.height - 5  # 5 píxeles de margen para altura
        
        self.canvas.configure(width=canvas_width, height=canvas_height)
        
        # Ajustar el tamaño de la ventana del scrollable_frame dentro del canvas
        self.canvas.itemconfig(1, width=canvas_width, height=canvas_height)

    def _setup_styles(self):
        """Configura los estilos visuales para la aplicación usando ttk styles."""
        style = ttk.Style()
        colors = self.color_palette

        # Estilo personalizado para el título del panel de filtros
        style.configure('CustomFilterTitle.TLabel',
                        background=colors['surface'],
                        foreground=colors['primary'],
                        font=('Segoe UI', 18, 'bold'),
                        padding=10,
                        borderwidth=2,
                        relief="groove")

        # Estilo personalizado para el título del panel principal
        style.configure('MainPanelTitle.TLabel',
                        background=colors['surface'],
                        foreground=colors['primary'],
                        font=('Segoe UI', 20, 'bold'),
                        padding=10,
                        borderwidth=2,
                        relief="ridge")
                        
        # Estilo personalizado para el título del panel de detalles
        style.configure('DetailPanelTitle.TLabel',
                        background=colors['background'],
                        foreground=colors['primary'],
                        font=('Segoe UI', 16, 'bold'),
                        padding=10,
                        borderwidth=2,
                        relief="groove")

        # Definición de fuentes con tamaños ajustados
        fonts = {
            'heading': ('Segoe UI', 28, 'bold'),
            'subheading': ('Segoe UI', 18, 'bold'),
            'body': ('Segoe UI', 12),
            'button': ('Segoe UI', 11, 'bold'),
            'caption': ('Segoe UI', 10)
        }

        # Estilos para filtros
        style.configure('Filter.TFrame', 
                      background=colors['background'],
                      relief='flat')
        
        style.configure('FilterPanel.TFrame', 
                      background=colors['surface'],
                      relief='ridge',
                      borderwidth=1)
                      
        style.configure('Filter.TLabel', 
                      background=colors['background'],
                      foreground=colors['text'],
                      font=fonts['body'])
                      
        style.configure('FilterLabel.TLabel', 
                      background=colors['background'],
                      foreground=colors['primary'],
                      font=('Segoe UI', 11, 'bold'))
                      
        style.configure('Filter.TEntry', 
                      foreground=colors['text'],
                      fieldbackground=colors['surface'],
                      insertcolor=colors['primary'],
                      font=fonts['body'])
                      
        style.configure('Filter.TCombobox', 
                      foreground=colors['text'],
                      fieldbackground=colors['surface'],
                      font=fonts['body'])
                      
        # Configurar el desplegable del combobox
        style.map('Filter.TCombobox', 
                fieldbackground=[('readonly', colors['surface'])],
                selectbackground=[('readonly', colors['primary'])],
                selectforeground=[('readonly', 'white')])
                
        # Estilos para el Treeview (tabla de datos)
        style.configure('Custom.Treeview',
                    background='#FFF0E0',  # Color de fondo más claro
                    fieldbackground='#FFF0E0',  # Color de fondo más claro
                    foreground='#3D3D3D',  # Gris oscuro para texto
                    rowheight=40,
                    font=('Segoe UI', 12))

        style.configure('Custom.Treeview.Heading',
                    background='#FF8C00',  # Color de encabezado
                    foreground='white',
                    font=('Segoe UI', 12, 'bold'),
                    relief='flat',
                    borderwidth=0,
                    padding=10)

        # Estilo para la selección en el Treeview
        style.map('Custom.Treeview',
                background=[('selected', colors['selected'])],
                foreground=[('selected', colors['text'])])

        # Estilos base para frames
        style.configure('App.TFrame',
                    background=colors['background'])

        style.configure('Card.TFrame',
                    background=colors['surface'],
                    relief='solid',
                    borderwidth=1)

        # Estilos para etiquetas
        style.configure('Header.TLabel',
                    font=fonts['heading'],
                    background=colors['surface'],
                    foreground=colors['text_header'])

        style.configure('Subheading.TLabel',
                    font=fonts['subheading'],
                    background=colors['surface'],
                    foreground=colors['text'])

        # Estilos para botones
        button_styles = {
            'Primary.TButton': (colors['primary'], colors['primary_dark'], 'white'),
            'Success.TButton': (colors['success'], colors['primary_dark'], 'white'),
            'Warning.TButton': (colors['warning'], colors['primary_dark'], colors['text']),
            'Error.TButton': (colors['error'], colors['primary_dark'], 'white'),
            'Info.TButton': (colors['info'], colors['primary_dark'], colors['text']),
            'Secondary.TButton': (colors['secondary'], colors['primary_dark'], colors['text'])
        }

        for style_name, (bg, active_bg, fg) in button_styles.items():
            style.configure(style_name,
                        font=fonts['button'],
                        background=bg,
                        foreground=fg,
                        borderwidth=1,
                        bordercolor=colors['border'],
                        relief='solid',
                        focuscolor=active_bg,
                        padding=(20, 10))

            style.map(style_name,
                    background=[('active', active_bg),
                            ('disabled', colors['disabled'])],
                    foreground=[('disabled', '#FFFFF0')])

        # Estilo para separadores visuales
        style.configure('TSeparator',
                    background=colors['divider'])

        # Estilo para el panel de filtros
        style.configure('Surface.TFrame',
                    background=colors['surface'],
                    relief='solid',
                    borderwidth=1)

        # Estilo para etiquetas dentro del panel de filtros
        style.configure('Filter.TLabel',
                    font=fonts['body'],
                    background=colors['surface'],
                    foreground=colors['text_filter_label'],
                    padding=5)

        # Estilo para campos de entrada y comboboxes
        style.configure('Modern.TEntry',
                    font=fonts['body'],
                    padding=8,
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'])

        style.configure('Modern.TCombobox',
                    font=fonts['body'],
                    padding=8,
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'])

        # Estilos para el panel de detalles
        style.configure('Detail.TFrame',
                    background=colors['background'],
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'])

        style.configure('Detail.TLabelframe',
                    background=colors['background'],
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'],
                    padding=10,
                    labelmargins=8,
                    font=('Segoe UI', 12, 'bold'),
                    foreground=colors['text_section_header'])

        style.configure('Detail.TLabelframe.Label',
                    font=('Segoe UI', 12, 'bold'),
                    foreground=colors['text_section_header'],
                    background=colors['background'])

        style.configure('Section.TLabel',
                    font=('Segoe UI', 16, 'bold'),
                    foreground=colors['text_header'],
                    background=colors['background'],
                    padding=(0, 10))

        style.configure('Field.TLabel',
                    font=('Segoe UI', 11, 'bold'),
                    foreground=colors['text_secondary'],
                    background=colors['background'],
                    padding=(2, 0))

        style.configure('Value.TLabel',
                    font=('Segoe UI', 12),
                    foreground=colors['text_value_label'],
                    background=colors['background'],
                    padding=(2, 5))

        # Estilos para scrollbars
        style.configure('Vertical.TScrollbar',
                    background=colors['primary_light'],
                    troughcolor=colors['background'],
                    bordercolor=colors['border'],
                    arrowcolor=colors['primary'])

        style.configure('Horizontal.TScrollbar',
                    background=colors['primary_light'],
                    troughcolor=colors['background'],
                    bordercolor=colors['border'],
                    arrowcolor=colors['primary'])

        # Estilo para la barra de estado
        style.configure('Statusbar.TLabel',
                    font=fonts['caption'],
                    background=colors['surface'],
                    foreground=colors['text_secondary'])

            # Guardar la paleta de colores configurada para uso posterior
        self.color_palette = colors
        
    def _bind_mouse_wheel(self):
        """Vincula el evento de la rueda del ratón al scroll del canvas."""
        def _on_mousewheel(event):
            """Función interna para manejar el evento de la rueda del ratón."""
            if self.scrollbar.get() != (0.0, 1.0):  # Solo hacer scroll si hay contenido que se pueda scrollear
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

    def update_filters(self, event=None):
        """
        Actualiza los filtros en la vista principal de personas.
        """
        self.personas_view.update_filters_from_panel(
            nombre_filter=self.nombre_var.get(),
            articulo_filter=self.articulo_var.get(),
            direccion_filter=self.direccion_var.get(),
            municipio_filter=self.municipio_var.get(),
            estado_filter=self.estado_var.get()
        )


class PersonasView:
    """
    Vista principal para la gestión de personas.
    """
    def __init__(self, parent, style=None):
        """
        Inicializa la vista de Personas.
        """
        self.parent = parent
        self.style = style
        self.controller = PersonasController()

        self.color_palette = {
            'primary': '#f2a900',  # Naranja Principal (más suave)
            'primary_light': '#ffcc66',  # Naranja Secundario Claro (más suave)
            'primary_dark': '#d89f00',  # Naranja Secundario Oscuro (más suave)
            'secondary': '#f2b600',  # Naranja Secundario (más suave)
            'background': '#FFF8F0',  # Fondo blanco
            'surface': '#ffdb99',  # Superficie (más suave)
            'error': '#f2a3a3',  # Color de error (más suave)
            'success': '#a3d6a3',  # Color de éxito (más suave)
            'warning': '#f2d66e',  # Color de advertencia (más suave)
            'info': '#f2c58a',  # Color de información (más suave)
            'text': '#424242',  # Gris Cálido / Neutro para Texto
            'text_secondary': '#76849a',  # Texto secundario
            'text_section_header': '#f2a900',  # Naranja Principal para encabezados (más suave)
            'text_filter_label': '#424242',  # Gris Cálido para etiquetas de filtro
            'text_value_label': '#424242',  # Gris Cálido para etiquetas de valor
            'text_header': '#f2a900',  # Naranja Principal para encabezados (más suave)
            'divider': '#d9d9d9',  # Gris claro para divisores
            'toolbar': '#ffffff',  # Fondo blanco para la barra de herramientas
            'status_bar': '#ffffff',  # Fondo blanco para la barra de estado
            'card': '#ffffff',  # Fondo blanco para tarjetas
            'hover': '#ffcc99',  # Naranja suave para hover
            'selected': '#ffcc99',  # Naranja suave para selección
            'disabled': '#d9d9d9',  # Color para elementos deshabilitados
            'input': '#ffffff',  # Fondo blanco para entradas
            'border': '#d9b300',  # Color de borde (más suave)
            'border_light': '#d9d9d9',  # Borde claro
            'border_dark': '#b3b3b3',  # Borde oscuro
            'bordercolor': '#d9b300',  # Color de borde (más suave)
            'panel': '#ffffff'  # Fondo blanco para paneles
        }

        # Cargar todos los íconos antes de configurar la interfaz
        self._load_all_icons()

        # Vincular teclas de método abreviado para zoom de fuente
        self.parent.bind('<Control-plus>', lambda event: self.aumentar_fuente())
        self.parent.bind('<Control-minus>', lambda event: self.disminuir_fuente())

        # Configurar estilos de la interfaz
        self._setup_styles()
        # Configurar la interfaz de usuario (widgets y layout)
        self._setup_ui()
        # Cargar datos iniciales en la tabla
        self.load_data()

        # Cargar icono específico de confirmar (asegurar que el archivo existe)
        self.confirmar_icon = self._load_and_resize_icon("confirmar.png")

    def show_context_menu(self, event):
        """Muestra el menú contextual al hacer clic derecho en la tabla."""
        # Obtener el item (fila) sobre el que se hizo clic
        item = self.tree.identify_row(event.y)

        # Seleccionar el item si existe
        if item:
            self.tree.selection_set(item)

        # Crear el menú contextual
        context_menu = tk.Menu(
            self.parent,
            tearoff=0,
            bg=self.color_palette['surface'],
            fg=self.color_palette['text'],
            activebackground=self.color_palette['primary_light'],
            activeforeground=self.color_palette['primary'],
            font=('Segoe UI', 10),
            relief='flat',
            bd=1
        )

        # Definir las opciones del menú contextual
        menu_options = [
            {
                'label': '  Agregar Persona',
                'icon': self.agregar_icon,
                'command': self.add_persona,
                'state': 'normal'
            },
            {
                'label': '  Editar Persona',
                'icon': self.editar_icon,
                'command': self.edit_persona,
                'state': 'normal' if item else 'disabled'
            },
            None,  # Separador
            {
                'label': '  Eliminar Persona',
                'icon': self.eliminar_icon,
                'command': self.delete_persona,
                'state': 'normal' if item else 'disabled'
            },
            None,  # Separador
            {
                'label': '  Confirmar Entrega',
                'icon': self.confirmar_icon,
                'command': self.confirmar_entrega_command,
                'state': 'normal' if item else 'disabled'
            },
            {
                'label': '  Cancelar Pedido',
                'icon': self.cancelar_icon,
                'command': self.cancelar_pedido_command,
                'state': 'normal' if item else 'disabled'
            },
            {
                'label': '  Marcar como Pendiente',
                'icon': self.pendiente_icon,
                'command': self.mark_as_pending_command,
                'state': 'normal' if item else 'disabled'
            }
        ]

        # Agregar comandos al menú contextual
        for option in menu_options:
            if option is None:
                context_menu.add_separator()
            else:
                context_menu.add_command(
                    label=option['label'],
                    image=option['icon'],
                    compound='left',
                    command=option['command'],
                    state=option['state']
                )

        # Mostrar el menú en la posición del clic del ratón
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _load_all_icons(self):
        """Carga todos los íconos necesarios para la interfaz de usuario."""
        # Tamaño estándar para todos los íconos
        icon_size = (20, 20)

        # Mapeo de nombres de archivo de íconos a atributos de clase
        icon_mapping = {
            'agregar': ('agregar.png', 'agregar_icon'),
            'editar': ('editar.png', 'editar_icon'),
            'eliminar': ('eliminar.png', 'eliminar_icon'),
            'confirmar': ('confirmar.png', 'confirmar_icon'),
            'cancelar': ('cancelar.png', 'cancelar_icon'),
            'pendiente': ('pendiente.png', 'pendiente_icon'),
            'salida': ('salida.png', 'salida_icon'),
            'recibe': ('recibe.png', 'recibe_icon'),
            'user': ('user.png', 'user_icon'),
            'articulo': ('articulo.png', 'articulo_icon'),
            'telefono': ('telefono.png', 'telefono_icon'),
            'localizacion': ('localizacion.png', 'localizacion_icon'),
            'calendar': ('calendar.png', 'calendar_icon'),
            'excel': ('excel.png', 'export_icon'),
            'limpiar': ('limpiar.png', 'limpiar_icon'),
            'aplicar': ('aplicar.png', 'aplicar_icon'),
            'eliminar1': ('eliminar1.png', 'eliminar1_icon'),
            'undo': ('undo.png', 'undo_icon'),
            'redo': ('redo.png', 'redo_icon')
        }

        # Obtener directorios para buscar los íconos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(current_dir, 'icons')  # Íconos están en views/icons

        # Cargar cada ícono y asignarlo como atributo de la clase
        for icon_key, (filename, attr_name) in icon_mapping.items():
            icon_path = os.path.join(icons_dir, filename)
            try:
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    image = image.resize(icon_size, Image.LANCZOS)
                    icon = ImageTk.PhotoImage(image)
                    setattr(self, attr_name, icon)
                else:
                    print(f"Warning: Icon file not found: {filename} at {icon_path}")
                    setattr(self, attr_name, None)
            except Exception as e:
                print(f"Error loading icon {filename}: {str(e)}")
                setattr(self, attr_name, None)

    def _setup_styles(self):
        """Configura los estilos visuales para la aplicación usando ttk styles."""
        style = ttk.Style()

        # Usar la paleta de colores definida
        colors = self.color_palette

        # Definición de fuentes con tamaños ajustados
        fonts = {
            'heading': ('Segoe UI', 28, 'bold'),
            'subheading': ('Segoe UI', 18, 'bold'),
            'body': ('Segoe UI', 12),
            'button': ('Segoe UI', 11, 'bold'),
            'caption': ('Segoe UI', 10)
        }

        # Estilos para filtros
        style.configure('Filter.TFrame', 
                      background=colors['background'],
                      relief='flat')
        
        style.configure('FilterPanel.TFrame', 
                      background=colors['surface'],
                      relief='ridge',
                      borderwidth=1)
                      
        style.configure('Filter.TLabel', 
                      background=colors['background'],
                      foreground=colors['text'],
                      font=fonts['body'])
                      
        style.configure('FilterLabel.TLabel', 
                      background=colors['surface'],
                      foreground=colors['primary'],
                      font=('Segoe UI', 11, 'bold'))
                      
        style.configure('FilterTitle.TLabel', 
                      background=colors['background'],
                      foreground=colors['primary'],
                      font=('Segoe UI', 14, 'bold'))
                      
        style.configure('Filter.TEntry', 
                      foreground=colors['text'],
                      fieldbackground=colors['surface'],
                      insertcolor=colors['primary'],
                      font=fonts['body'])
                      
        style.configure('Filter.TCombobox', 
                      foreground=colors['text'],
                      fieldbackground=colors['surface'],
                      font=fonts['body'])
                      
        # Configurar el desplegable del combobox
        style.map('Filter.TCombobox', 
                fieldbackground=[('readonly', colors['surface'])],
                selectbackground=[('readonly', colors['primary'])],
                selectforeground=[('readonly', 'white')])
                
        # Estilos para el Treeview (tabla de datos)
        style.configure('Custom.Treeview',
                    background=colors['surface'],
                    fieldbackground=colors['surface'],
                    foreground=colors['text'],
                    rowheight=40,
                    font=fonts['body'])

        style.configure('Custom.Treeview.Heading',
                    background=colors['primary'],
                    foreground='white',
                    font=('Segoe UI', 12, 'bold'),
                    relief='flat',
                    borderwidth=0,
                    padding=10)

        # Estilo para la selección en el Treeview
        style.map('Custom.Treeview',
                background=[('selected', colors['selected'])],
                foreground=[('selected', colors['text'])])

        # Estilos base para frames
        style.configure('App.TFrame',
                    background=colors['background'])

        style.configure('Card.TFrame',
                    background=colors['surface'],
                    relief='solid',
                    borderwidth=1)

        # Estilos para etiquetas
        style.configure('Header.TLabel',
                    font=fonts['heading'],
                    background=colors['surface'],
                    foreground=colors['text_header'])

        style.configure('Subheading.TLabel',
                    font=fonts['subheading'],
                    background=colors['surface'],
                    foreground=colors['text'])

        # Estilos para botones
        button_styles = {
            'Primary.TButton': (colors['primary'], colors['primary_dark'], 'white'),
            'Success.TButton': (colors['success'], colors['primary_dark'], 'white'),
            'Warning.TButton': (colors['warning'], colors['primary_dark'], colors['text']),
            'Error.TButton': (colors['error'], colors['primary_dark'], 'white'),
            'Info.TButton': (colors['info'], colors['primary_dark'], colors['text']),
            'Secondary.TButton': (colors['secondary'], colors['primary_dark'], colors['text'])
        }

        for style_name, (bg, active_bg, fg) in button_styles.items():
            style.configure(style_name,
                        font=fonts['button'],
                        background=bg,
                        foreground=fg,
                        borderwidth=1,
                        bordercolor=colors['border'],
                        relief='solid',
                        focuscolor=active_bg,
                        padding=(20, 10))

            style.map(style_name,
                    background=[('active', active_bg),
                            ('disabled', colors['disabled'])],
                    foreground=[('disabled', '#FFFFFF')])

        # Estilo para separadores visuales
        style.configure('TSeparator',
                    background=colors['divider'])

        # Estilo para el panel de filtros
        style.configure('Surface.TFrame',
                    background=colors['surface'],
                    relief='solid',
                    borderwidth=1)

        # Estilo para etiquetas dentro del panel de filtros
        style.configure('Filter.TLabel',
                    font=fonts['body'],
                    background=colors['surface'],
                    foreground=colors['text_filter_label'],
                    padding=5)

        # Estilo para campos de entrada y comboboxes
        style.configure('Modern.TEntry',
                    font=fonts['body'],
                    padding=8,
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'])

        style.configure('Modern.TCombobox',
                    font=fonts['body'],
                    padding=8,
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'])

        # Estilos para el panel de detalles
        style.configure('Detail.TFrame',
                    background=colors['background'],
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'])

        style.configure('Detail.TLabelframe',
                    background=colors['background'],
                    relief='solid',
                    borderwidth=1,
                    bordercolor=colors['border'],
                    padding=10,
                    labelmargins=8,
                    font=('Segoe UI', 12, 'bold'),
                    foreground=colors['text_section_header'])

        style.configure('Detail.TLabelframe.Label',
                    font=('Segoe UI', 12, 'bold'),
                    foreground=colors['text_section_header'],
                    background=colors['background'])

        style.configure('Section.TLabel',
                    font=('Segoe UI', 16, 'bold'),
                    foreground=colors['text_header'],
                    background=colors['background'],
                    padding=(0, 10))

        style.configure('Field.TLabel',
                    font=('Segoe UI', 11, 'bold'),
                    foreground=colors['text_secondary'],
                    background=colors['background'],
                    padding=(2, 0))

        style.configure('Value.TLabel',
                    font=('Segoe UI', 12),
                    foreground=colors['text_value_label'],
                    background=colors['background'],
                    padding=(2, 5))

        # Estilos para scrollbars
        style.configure('Vertical.TScrollbar',
                    background=colors['primary_light'],
                    troughcolor=colors['background'],
                    bordercolor=colors['border'],
                    arrowcolor=colors['primary'])

        style.configure('Horizontal.TScrollbar',
                    background=colors['primary_light'],
                    troughcolor=colors['background'],
                    bordercolor=colors['border'],
                    arrowcolor=colors['primary'])

        # Estilo para la barra de estado
        style.configure('Statusbar.TLabel',
                    font=fonts['caption'],
                    background=colors['surface'],
                    foreground=colors['text_secondary'])

        # Estilo personalizado para etiquetas de filtro
        style.configure('CustomFilterLabel.TLabel',
                        
                        foreground=colors['primary'],
                        font=('Segoe UI', 11, 'bold'),
                        padding=5)

        # Guardar la paleta de colores configurada para uso posterior
        self.color_palette = colors

    def _setup_ui(self):
        """Configura la interfaz de usuario principal, incluyendo paneles y widgets."""
        # Configurar el grid principal para que la ventana sea responsiva
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Frame principal que contiene toda la interfaz
        self.main_frame = ttk.Frame(self.parent, style='Background.TFrame')
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

        # Configurar columnas del grid principal con pesos y tamaños mínimos
        self.main_frame.grid_columnconfigure(0, weight=2, minsize=300)  # Panel izquierdo (filtros)
        self.main_frame.grid_columnconfigure(1, weight=6, minsize=600)  # Panel central (tabla)
        self.main_frame.grid_columnconfigure(2, weight=2, minsize=300)  # Panel derecho (detalles)

        # Configurar fila del grid principal para que se expanda verticalmente
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Establecer tamaño mínimo de la ventana principal
        if isinstance(self.parent, tk.Tk):
            self.parent.minsize(1200, 800)

        # Crear y colocar el panel de filtros a la izquierda
        self.filter_panel = FilterPanel(self.main_frame, self)
        self.filter_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        # Asegurar que el panel de filtros ocupe toda la columna verticalmente
        self.filter_panel.grid_rowconfigure(0, weight=1)
        self.filter_panel.grid_columnconfigure(0, weight=1)
        
        # Evitar que el panel se redimensione incorrectamente pero permitir expansión vertical
        self.filter_panel.configure(width=300)
        self.filter_panel.grid_propagate(False)  # Mantener el ancho fijo pero permitir expansión vertical

        # Configurar el panel central (tabla de personas)
        self._setup_center_panel()
        # Configurar el panel derecho (detalles de la persona)
        self._setup_right_panel()

        # Inicializar el panel de detalles con un mensaje predeterminado
        self.update_details()

    def _setup_center_panel(self):
        """Configura el panel central que contiene la tabla de datos de personas."""
        # Frame para el panel central
        center_panel = ttk.Frame(self.main_frame, style='Surface.TFrame')
        center_panel.grid(row=0, column=1, sticky='nsew', padx=10)
        center_panel.configure(style='Card.TFrame') # Aplicar estilo de tarjeta

        # Configurar grid del panel central para que sea responsivo
        center_panel.grid_columnconfigure(0, weight=1)
        for i in range(5):
            center_panel.grid_rowconfigure(i, weight=0)
        center_panel.grid_rowconfigure(3, weight=1)  # Fila de la tabla debe expandirse

        # Header del panel central
        header_frame = ttk.Frame(center_panel, style='Surface.TFrame')
        header_frame.grid(row=0, column=0, sticky='new', padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Contenedor para el título con icono
        title_container = ttk.Frame(header_frame, style='Surface.TFrame')
        title_container.grid(row=0, column=0, sticky='ew')
        title_container.grid_columnconfigure(1, weight=1)

        # Icono del título (personas)
        icon_label = ttk.Label(
            title_container,
            text="👥",
            font=('Segoe UI', int(self._get_relative_font_size(32)))
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0,20))

        # Título principal del panel con borde
        title_text = ttk.Label(
            title_container,
            text="Gestión de Personas",
            style='MainPanelTitle.TLabel'
        )
        title_text.grid(row=0, column=1, sticky='sw')

        # Subtítulo del panel
        subtitle_text = ttk.Label(
            title_container,
            text="Administración de clientes y pedidos",
            font=('Segoe UI', 11),
            foreground=self.color_palette['text_secondary']
        )
        subtitle_text.grid(row=1, column=1, sticky='nw', pady=(2,5))

        # Separador horizontal debajo del header
        separator = ttk.Separator(center_panel, orient='horizontal')
        separator.grid(row=1, column=0, sticky='ew', padx=20, pady=(10,15))

        # Configurar la toolbar (botones de acción sobre la tabla)
        self._setup_toolbar(center_panel)

        # Configurar el contenedor de la tabla (Treeview)
        self._setup_table_container(center_panel)

    def _get_relative_font_size(self, base_size):
        """Calcula el tamaño de fuente relativo basado en la resolución de la pantalla."""
        screen_width = self.parent.winfo_screenwidth()
        scale_factor = screen_width / 1920
        return max(int(base_size * scale_factor), 8)

    def _setup_toolbar(self, parent):
        """Configura la toolbar con botones para acciones sobre la tabla."""
        toolbar_frame = ttk.Frame(parent, style='Toolbar.TFrame')
        toolbar_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=(0,15))
        toolbar_frame.grid_columnconfigure(2, weight=1)

        # Frame para agrupar botones principales (izquierda de la toolbar)
        main_buttons_frame = ttk.Frame(toolbar_frame, style='Surface.TFrame')
        main_buttons_frame.grid(row=0, column=0, sticky='w', padx=(0,15))

        # Configuración de los botones principales: (texto, icono, comando, color)
        buttons_config = [
            ('Agregar', self.agregar_icon, self.add_persona, '#4CAF50'),
            ('Editar', self.editar_icon, self.edit_persona, '#2196F3'),
            ('Eliminar', self.eliminar_icon, self.delete_persona, '#F44336')
        ]

        for i, (text, icon, command, color) in enumerate(buttons_config):
            btn = tk.Button(
                main_buttons_frame,
                text=text,
                image=icon,
                compound='left',
                command=command,
                bg="SystemButtonFace",
                relief=tk.RAISED,
                borderwidth=2,
                font=('Segoe UI', 10),
                padx=10,
                pady=5
            )
            btn.grid(row=0, column=i, padx=3)
            btn.bind('<Configure>', lambda e, b=btn: self._adjust_button_size(e, b))

        # Separador vertical en la toolbar
        ttk.Separator(toolbar_frame, orient='vertical').grid(row=0, column=1, sticky='ns', padx=10, pady=5)

        # Frame para botones de historial (deshacer/rehacer, derecha de la toolbar)
        history_buttons_frame = ttk.Frame(toolbar_frame, style='Surface.TFrame')
        history_buttons_frame.grid(row=0, column=2, sticky='e')

        # Configuración de botones de historial: (texto, icono, comando, tooltip)
        history_buttons = [
            ('Deshacer', self.undo_icon, self.undo_last_change, 'Deshacer último cambio (Ctrl+Z)'),
            ('Rehacer', self.redo_icon, self.redo_last_change, 'Rehacer último cambio (Ctrl+Y)')
        ]

        for i, (text, icon, command, tooltip) in enumerate(history_buttons):
            btn = tk.Button(
                history_buttons_frame,
                text=text,
                image=icon,
                compound='left',
                command=command,
                state='disabled',
                bg="SystemButtonFace",
                relief=tk.RAISED,
                borderwidth=2,
                font=('Segoe UI', 10),
                padx=10,
                pady=5
            )
            btn.grid(row=0, column=i, padx=3)
            btn.bind('<Configure>', lambda e, b=btn: self._adjust_button_size(e, b))

            # Agregar tooltip para cada botón
            Tooltip(btn, tooltip)

            # Guardar referencia a los botones de deshacer/rehacer para actualizar su estado
            if text == 'Deshacer':
                self.undo_button = btn
            else:
                self.redo_button = btn

        # Vincular atajos de teclado para deshacer/rehacer
        self.parent.bind('<Control-z>', lambda e: self.undo_last_change())
        self.parent.bind('<Control-y>', lambda e: self.redo_last_change())

    def _adjust_button_size(self, event, button):
        """Ajusta el padding de los botones de la toolbar proporcionalmente al ancho de la ventana."""
        window_width = self.parent.winfo_width()
        padding_x = max(int(window_width * 0.01), 5)
        padding_y = max(int(window_width * 0.005), 3)

        # Verificar si el botón es ttk.Button (admite padding) o tk.Button (no admite padding)
        if isinstance(button, ttk.Button):
            button.configure(padding=(padding_x, padding_y))
        else:
            # Para tk.Button usamos padx y pady
            button.configure(padx=padding_x, pady=padding_y)

    def _setup_table_container(self, parent):
        """Configura el contenedor para la tabla (Treeview) y las scrollbars."""
        table_container = ttk.Frame(parent, style='Card.TFrame')
        table_container.grid(row=3, column=0, sticky='nsew', padx=15, pady=(5,5))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        # Estilos para las scrollbars (vertical y horizontal)
        scrollbar_style = {
            'background': self.color_palette['background'],
            'arrowcolor': self.color_palette['primary'],
            'troughcolor': self.color_palette['background'],
            'width': max(int(self.parent.winfo_screenwidth() / 192), 8)
        }

        # Scrollbar vertical para la tabla
        y_scroll = ttk.Scrollbar(
            table_container,
            orient='vertical',
            style='Vertical.TScrollbar'
        )
        y_scroll.grid(row=0, column=1, sticky='ns')

        # Scrollbar horizontal para la tabla
        x_scroll = ttk.Scrollbar(
            table_container,
            orient='horizontal',
            style='Horizontal.TScrollbar'
        )
        x_scroll.grid(row=1, column=0, sticky='ew')

        # Configurar la tabla (Treeview) en sí
        self._setup_treeview(table_container, x_scroll, y_scroll)
    def _setup_right_panel(self):
        """Configura el panel derecho que muestra los detalles de la persona seleccionada."""
        # Crear estilos específicos para el panel de detalles
        self._create_detail_panel_styles()
        
        # Panel derecho principal con estilo único
        right_panel = ttk.Frame(self.main_frame, style='DetailPanel.TFrame')
        right_panel.grid(row=0, column=2, sticky='nsew', padx=(10, 0))

        # Configurar grid para expansión vertical
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(2, weight=1)

        # Header del panel de detalles con diseño mejorado
        header_frame = ttk.Frame(right_panel, style='DetailHeader.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=12)
        header_frame.grid_columnconfigure(1, weight=1)

        # Icono del header con tamaño aumentado
        ttk.Label(
            header_frame,
            text="👤",
            font=('Segoe UI', 20),
            style='DetailIcon.TLabel'
        ).grid(row=0, column=0, padx=(0, 10))

        # Título del panel de detalles con borde y estilo mejorado
        ttk.Label(
            header_frame,
            text="Detalles del Cliente",
            style='DetailTitle.TLabel'
        ).grid(row=0, column=1, sticky='w')

        # Separador horizontal decorativo debajo del header
        separator = ttk.Separator(right_panel, orient='horizontal', style='DetailSeparator.TSeparator')
        separator.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

        # Canvas para permitir el scroll en el panel de detalles
        canvas = tk.Canvas(
            right_panel,
            highlightthickness=0,
            bg=self.color_palette['background'],
            bd=0
        )
        
        # Scrollbar personalizada
        scrollbar = ttk.Scrollbar(
            right_panel,
            orient="vertical",
            command=canvas.yview,
            style='DetailScroll.Vertical.TScrollbar'
        )

        # Frame interno para el contenido del scrollable panel de detalles
        content_frame = ttk.Frame(canvas, style='DetailContent.TFrame')
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Configurar canvas para el scroll con ancho ajustado
        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=270)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Layout del canvas y scrollbar en el panel derecho
        canvas.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
        scrollbar.grid(row=2, column=1, sticky='ns', pady=5)

        self.detail_labels = {}

        # Configuración de las secciones de detalle
        detail_sections_config = [
            {
                'title': 'Información Personal',
                'icon': '👤',
                'fields': [
                    {'name': 'Nombre', 'icon': '📝'},
                    {'name': 'Teléfono', 'icon': '📱'}
                ]
            },
            {
                'title': 'Detalles del Pedido',
                'icon': '📦',
                'fields': [
                    {'name': 'Artículo', 'icon': '🏷️'},
                    {'name': 'Estado', 'icon': '🔔'}
                ]
            },
            {
                'title': 'Fechas',
                'icon': '📅',
                'fields': [
                    {'name': 'Fecha Pedido', 'icon': '📥'},
                    {'name': 'Fecha Entrega', 'icon': '📤'}
                ]
            },
            {
                'title': 'Ubicación',
                'icon': '📍',
                'fields': [
                    {'name': 'Dirección', 'icon': '🏠'},
                    {'name': 'Municipio', 'icon': '🌆'}
                ]
            }
        ]

        # Crear secciones de detalle con mejor espaciado
        for i, section in enumerate(detail_sections_config):
            # Frame para cada sección con estilo único
            section_frame = ttk.LabelFrame(
                content_frame,
                text=f"{section['icon']} {section['title']}",
                style='DetailSection.TLabelframe',
                padding=8
            )
            section_frame.pack(fill='x', padx=8, pady=(12, 5) if i == 0 else (10, 5))

            # Separador decorativo después del título
            ttk.Separator(
                section_frame,
                orient='horizontal',
                style='DetailSectionSep.TSeparator'
            ).pack(fill='x', pady=(0, 8))

            # Crear campos dentro de cada sección con mejor espaciado
            for field in section['fields']:
                field_frame = ttk.Frame(section_frame, style='DetailField.TFrame')
                field_frame.pack(fill='x', padx=5, pady=(5, 5))

                # Etiqueta del campo con icono y mejor estilo
                ttk.Label(
                    field_frame,
                    text=f"{field['icon']} {field['name']}:",
                    style='DetailFieldLabel.TLabel'
                ).pack(anchor='center')

                # Separador sutil para mejorar la distinción visual
                ttk.Separator(
                    field_frame,
                    orient='horizontal',
                    style='DetailFieldSep.TSeparator'
                ).pack(fill='x', pady=(2, 4))

                # Etiqueta para mostrar el valor con mejor estilo
                self.detail_labels[field['name']] = ttk.Label(
                    field_frame,
                    text="",
                    style='DetailValue.TLabel',
                    wraplength=230,
                    anchor='center'
                )
                self.detail_labels[field['name']].pack(anchor='center', fill='x', pady=(0, 2))

        # Frame para la sección de acciones con mejor estilo
        action_frame = ttk.LabelFrame(
            right_panel,
            text="⚙️ Acciones",
            style='DetailActions.TLabelframe',
            padding=10
        )
        action_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(10, 10))
        action_frame.columnconfigure(0, weight=1)

        # Configuración de botones de acción
        action_buttons_config = [
            {
                'text': "Confirmar Entrega",
                'command': self.confirmar_entrega_command,
                'icon': self.confirmar_icon,
                'bg': '#a3d6a3'  # Verde suave
            },
            {
                'text': "Cancelar Pedido",
                'command': self.cancelar_pedido_command,
                'icon': self.cancelar_icon,
                'bg': '#f2a3a3'  # Rojo suave
            },
            {
                'text': "Marcar Pendiente",
                'command': self.mark_as_pending_command,
                'icon': self.pendiente_icon,
                'bg': '#f2d66e'  # Amarillo suave
            }
        ]

        # Crear botones de acción con estilo mejorado
        for action in action_buttons_config:
            btn = tk.Button(
                action_frame,
                text=action['text'],
                command=action['command'],
                image=action['icon'],
                compound='left',
                bg=action['bg'],
                fg="#424242",
                relief=tk.FLAT,
                borderwidth=1,
                font=('Segoe UI', 10, 'bold'),
                padx=15,
                pady=8,
                cursor="hand2"
            )
            btn.pack(fill='x', pady=3)
            
            # Efecto hover para los botones
            btn.bind("<Enter>", lambda e, b=btn: b.config(relief=tk.RAISED))
            btn.bind("<Leave>", lambda e, b=btn: b.config(relief=tk.FLAT))

    def _create_detail_panel_styles(self):
        """Crea estilos específicos para el panel de detalles."""
        style = ttk.Style()
        colors = self.color_palette

        # Colores específicos para el panel de detalles
        detail_colors = {
            'background': '#FFFAF0',  # Un fondo más cálido y suave
            'header_bg': '#ffe7ba',   # Color para encabezados
            'section_bg': '#FFF8F0',  # Color para secciones
            'field_bg': '#FFF8F0',    # Color para campos
            'separator': '#f2a900',   # Color para separadores
            'title': '#d88c00',       # Color para títulos
            'label': '#885400',       # Color para etiquetas
            'value': '#333333',       # Color para valores
            'border': '#ffcc99',      # Color para bordes
        }

        # Estilos generales del panel
        style.configure('DetailPanel.TFrame',
                      background=detail_colors['background'],
                      relief='ridge',
                      borderwidth=1,
                      bordercolor=detail_colors['border'])

        # Estilo para el encabezado
        style.configure('DetailHeader.TFrame',
                      background=detail_colors['header_bg'],
                      relief='flat')

        style.configure('DetailIcon.TLabel',
                      background=detail_colors['header_bg'],
                      foreground=detail_colors['title'])

        style.configure('DetailTitle.TLabel',
                      font=('Segoe UI', 16, 'bold'),
                      background=detail_colors['header_bg'],
                      foreground=detail_colors['title'],
                      padding=(0, 5))

        # Estilo para separadores
        style.configure('DetailSeparator.TSeparator',
                      background=detail_colors['separator'])

        # Estilo para el contenido scrollable
        style.configure('DetailContent.TFrame',
                      background=detail_colors['background'])

        # Estilo para secciones
        style.configure('DetailSection.TLabelframe',
                      background=detail_colors['section_bg'],
                      relief='groove',
                      borderwidth=1,
                      bordercolor=detail_colors['border'],
                      padding=8,
                      labelmargins=5)

        style.configure('DetailSection.TLabelframe.Label',
                      font=('Segoe UI', 12, 'bold'),
                      background=detail_colors['section_bg'],
                      foreground=detail_colors['title'])

        # Estilo para separadores de sección
        style.configure('DetailSectionSep.TSeparator',
                      background=detail_colors['separator'])

        # Estilos para campos
        style.configure('DetailField.TFrame',
                      background=detail_colors['field_bg'],
                      relief='flat',
                      padding=3)

        style.configure('DetailFieldLabel.TLabel',
                      font=('Segoe UI', 11, 'bold'),
                      background=detail_colors['field_bg'],
                      foreground=detail_colors['label'],
                      padding=(2, 2))

        style.configure('DetailFieldSep.TSeparator',
                      background='#ffdb99')

        style.configure('DetailValue.TLabel',
                      font=('Segoe UI', 12),
                      background=detail_colors['field_bg'],
                      foreground=detail_colors['value'],
                      padding=(2, 5))

        # Estilo para el panel de acciones
        style.configure('DetailActions.TLabelframe',
                      background=detail_colors['header_bg'],
                      relief='groove',
                      borderwidth=1,
                      bordercolor=detail_colors['border'],
                      padding=8,
                      labelmargins=5)

        style.configure('DetailActions.TLabelframe.Label',
                      font=('Segoe UI', 12, 'bold'),
                      background=detail_colors['header_bg'],
                      foreground=detail_colors['title'])

        # Estilo para scrollbar
        style.configure('DetailScroll.Vertical.TScrollbar',
                      background=detail_colors['header_bg'],
                      troughcolor=detail_colors['background'],
                      arrowcolor=detail_colors['title'])

    def update_status_indicator(self, estado):
        """Actualiza el color del indicador de estado en la barra de estado."""
        color_map = {
            'Pendiente': self.color_palette['warning'],
            'Entregado': self.color_palette['success'],
            'Cancelado': self.color_palette['error']
        }
        self.status_label.configure(foreground=color_map.get(estado, self.color_palette['text_filter_label']))

    def apply_filters_button(self):
        """Función llamada cuando se presiona el botón 'Aplicar' en el panel de filtros."""
        self.update_filters()

    def update_filters_from_panel(self, nombre_filter, articulo_filter, direccion_filter, municipio_filter, estado_filter):
        """
        Actualiza las variables de filtro con los valores del panel de filtros.
        """
        self.nombre_var_filter = nombre_filter.lower() if nombre_filter else ""
        self.articulo_var_filter = articulo_filter.lower() if articulo_filter else ""
        self.direccion_var_filter = direccion_filter.lower() if direccion_filter else ""
        self.municipio_var_filter = municipio_filter
        self.estado_var_filter = estado_filter

        self.filter_treeview()

    def filter_treeview(self):
        """Aplica los filtros configurados a la tabla Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        personas = self.controller.get_personas()

        for persona in personas:
            nombre = str(persona[1]).lower()
            articulo = str(persona[2]).lower()
            direccion = str(persona[4]).lower()
            municipio = str(persona[5])
            estado = str(persona[8])

            if all([
                (not self.nombre_var_filter or nombre.startswith(self.nombre_var_filter)),
                (not self.articulo_var_filter or articulo.startswith(self.articulo_var_filter)),
                (not self.direccion_var_filter or direccion.startswith(self.direccion_var_filter)),
                (self.municipio_var_filter == "Todos" or self.municipio_var_filter == municipio),
                (self.estado_var_filter == "Todos" or self.estado_var_filter == estado)
            ]):
                self.tree.insert('', 'end', values=persona, tags=('filtered',))

        total_registros = len(self.tree.get_children())
        self.status_label.configure(text=f"{total_registros} registros encontrados")

    def on_tree_select(self, event):
        """Maneja el evento de selección de un item en el Treeview (tabla)."""
        if (selected := self.tree.selection()):
            item_data = self.tree.item(selected[0])
            current_tags = item_data['tags']

            if self.color_states_var.get():
                estado = item_data['values'][6]
                if estado in ['Pendiente', 'Entregado', 'Cancelado']:
                    if not current_tags or estado not in current_tags:
                        self.tree.item(selected[0], tags=(estado,))

            persona = item_data['values']
            self.update_details(persona)

            if len(persona) > 8:
                self.update_status_indicator(persona[8])
        else:
            self.update_details(None)
            self.update_status_indicator('')

    def add_persona(self):
        """Abre el diálogo para agregar una nueva persona."""
        dialog = AddPersonaDialog(self.parent, "Agregar Persona")
        self.parent.wait_window(dialog)

        if dialog.result:
            self.load_data()
            self.update_undo_redo_buttons()

    def edit_persona(self):
        """Abre el diálogo para editar la persona seleccionada en la tabla."""
        if (selected := self.tree.selection()):
            persona_id = self.tree.item(selected[0])['values'][0]
            persona_data = next((p for p in self.controller.get_personas() if p[0] == persona_id), None)
            if persona_data:
                # Crear el diálogo de edición
                dialog = EditPersonaDialog(self.parent, "Editar Persona", persona_data)
                
                # Esperar a que el diálogo se cierre
                self.parent.wait_window(dialog)
                
                # Actualizar la interfaz si se guardaron cambios
                if dialog.result:
                    self.load_data()
                    self.update_undo_redo_buttons()
        else:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una persona para editar.")

    def delete_persona(self):
        """Elimina la(s) persona(s) seleccionada(s) de la tabla y la base de datos."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia",
                                 "Por favor, seleccione al menos una persona para eliminar.")
            return

        if messagebox.askyesno("Confirmar Eliminación",
                              "¿Está seguro de que desea eliminar los registros seleccionados?"):
            try:
                for item in selected_items:
                    persona_id = self.tree.item(item)['values'][0]
                    self.controller.delete_persona(persona_id)

                self.load_data()
                self.update_undo_redo_buttons()
                messagebox.showinfo("Éxito", "Registros eliminados correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def reorder_ids(self):
        """Reordena los IDs de las personas en la tabla para que sean secuenciales."""
        for index, item in enumerate(self.tree.get_children()):
            values = list(self.tree.item(item)['values'])
            values[0] = index + 1
            self.tree.item(item, values=values)

    def export_to_excel(self):
        """Exporta los datos de la tabla a un archivo Excel."""
        try:
            personas = self.controller.get_personas()

            df = pd.DataFrame(personas, columns=['ID', 'Nombre', 'Artículo', 'Teléfono', 'Dirección', 'Municipio', 'Fecha Pedido', 'Fecha Entrega', 'Estado'])

            if (file_path := filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[("Excel files", "*.xlsx")]
            )):
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Datos', index=False)

                    workbook = writer.book
                    worksheet = writer.sheets['Datos']

                    table = Table(displayName='PersonasTable', ref=worksheet.dimensions)

                    style = TableStyleInfo(
                        name="TableStyleMedium9",
                        showFirstColumn=False,
                        showLastColumn=False,
                        showRowStripes=True,
                        showColumnStripes=True
                    )

                    table.tableStyleInfo = style
                    worksheet.add_table(table)

                messagebox.showinfo("Éxito", "Datos exportados correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def confirmar_entrega_command(self):
        """Abre el diálogo para confirmar la entrega de un pedido seleccionado."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un pedido para confirmar.")
            return

        persona = self.tree.item(selected[0])['values']

        dialog = ConfirmarEntregaDialog(self.parent, "Confirmar Entrega", persona)
        self.parent.wait_window(dialog)

        if dialog.result:
            self.load_data()

    def update_details(self, persona=None):
        """Actualiza el panel de detalles con la información de la persona proporcionada."""
        fields = ['Nombre', 'Artículo', 'Teléfono', 'Dirección', 'Municipio',
                 'Fecha Pedido', 'Fecha Entrega', 'Estado']

        if persona:
            for i, field in enumerate(fields):
                value = persona[i+1]
                if field == 'Teléfono':
                    if isinstance(value, str) and value.startswith('no contacto:'):
                        explanation = value.split(':', 1)[1].strip()
                        self.detail_labels[field].config(
                            text=f"No contacto\nDetalles: {explanation}",
                            wraplength=200
                        )
                    else:
                        self.detail_labels[field].config(text=str(value))
                else:
                    self.detail_labels[field].config(text=str(value))

    def clear_filters(self):
        """Limpia todos los filtros y restablece la tabla a su estado original."""
        self.nombre_var_filter = ""
        self.articulo_var_filter = ""
        self.direccion_var_filter = ""
        self.municipio_var_filter = "Todos"
        self.estado_var_filter = "Todos"

        self.filter_panel.nombre_var.set('')
        self.filter_panel.articulo_var.set('')
        self.filter_panel.direccion_var.set('')
        self.filter_panel.municipio_var.set('Todos')
        self.filter_panel.estado_var.set('Todos')

        self.load_data()

    def load_data(self):
        """Carga los datos de personas desde el controlador y los muestra en la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        personas = self.controller.get_personas()
        if personas:
            for persona in personas:
                values = [
                    persona[0],  # ID
                    persona[1],  # Nombre
                    persona[2],  # Artículo
                    persona[3],  # Teléfono
                    persona[4],  # Dirección
                    persona[5],  # Municipio
                    persona[8],  # Estado
                    persona[6],  # Fecha Pedido
                    persona[7],  # Fecha Entrega
                ]

                if self.color_states_var.get():
                    self.tree.insert('', 'end', values=values, tags=(persona[8],))
                else:
                    self.tree.insert('', 'end', values=values)

        self.update_undo_redo_buttons()

    def update_table(self):
        """Recarga los datos de la tabla, manteniendo la selección actual."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        personas = self.controller.get_personas()
        for persona in personas:
            values = list(persona)
            self.tree.insert('', 'end', values=values)

        selected_items = self.tree.selection()
        if selected_items:
            self.on_tree_select(None)

    def cancelar_pedido_command(self):
        """Cancela el pedido de la persona seleccionada en la tabla."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia",
                                    "Por favor, seleccione un pedido para cancelar.")
            return

        persona = self.tree.item(selected[0])['values']

        if persona[8] == 'Cancelado':
            messagebox.showwarning("Advertencia", "El pedido ya está cancelado.")
            return

        if messagebox.askyesno("Confirmar Cancelación",
                                "¿Está seguro de que desea cancelar este pedido?"):
            try:
                self.controller.update_persona(
                    persona[0],
                    estado='Cancelado',
                    fecha_entrega=None
                )

                self.load_data()
                messagebox.showinfo("Éxito", "Pedido cancelado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cancelar el pedido: {str(e)}")

    def mark_as_pending_command(self):
        """Marca el pedido de la persona seleccionada como 'Pendiente'."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia",
                                    "Por favor, seleccione un pedido para marcar como pendiente.")
            return

        persona = self.tree.item(selected[0])['values']

        if messagebox.askyesno("Confirmar Acción",
                                "¿Está seguro de que desea marcar este pedido como pendiente?"):
            try:
                self.controller.update_persona(
                    persona[0],
                    estado="Pendiente",
                    fecha_entrega=None
                )
                self.load_data()
                messagebox.showinfo("Éxito", "Pedido marcado como pendiente correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al marcar como pendiente: {str(e)}")

    def update_undo_redo_buttons(self):
        """Actualiza el estado (habilitado/deshabilitado) de los botones de deshacer y rehacer."""
        if hasattr(self, 'undo_button'):
            can_undo = self.controller.can_undo()
            self.undo_button.configure(state='normal' if can_undo else 'disabled')
            if can_undo:
                description = self.controller.get_undo_description()
                Tooltip(self.undo_button, f"Deshacer: {description}")
            else:
                Tooltip(self.undo_button, "No hay acciones para deshacer")

        if hasattr(self, 'redo_button'):
            can_redo = self.controller.can_redo()
            self.redo_button.configure(state='normal' if can_redo else 'disabled')
            if can_redo:
                description = self.controller.get_redo_description()
                Tooltip(self.redo_button, f"Rehacer: {description}")
            else:
                Tooltip(self.redo_button, "No hay acciones para rehacer")

    def undo_last_change(self):
        """Deshace la última acción realizada a través del controlador."""
        if self.controller.can_undo():
            description = self.controller.get_undo_description()
            if messagebox.askyesno("Confirmar Deshacer",
                                 f"¿Desea deshacer la siguiente acción?\n{description}"):
                if self.controller.undo_last_change():
                    self.load_data()
                    self.update_undo_redo_buttons()
                    messagebox.showinfo("Éxito", "Se ha deshecho el último cambio.")
                else:
                    messagebox.showerror("Error", "No se pudo deshacer el cambio.")
        else:
            messagebox.showinfo("Información", "No hay cambios para deshacer.")

    def redo_last_change(self):
        """Rehace la última acción que fue deshecha a través del controlador."""
        if self.controller.can_redo():
            description = self.controller.get_redo_description()
            if messagebox.askyesno("Confirmar Rehacer",
                                 f"¿Desea rehacer la siguiente acción?\n{description}"):
                if self.controller.redo_last_change():
                    self.load_data()
                    self.update_undo_redo_buttons()
                    messagebox.showinfo("Éxito", "Se ha rehecho el cambio.")
                else:
                    messagebox.showerror("Error", "No se pudo rehacer el cambio.")
        else:
            messagebox.showinfo("Información", "No hay cambios para rehacer.")

    def _load_and_resize_icon(self, filename, size=(20, 20)):
        """Carga un icono desde el sistema de archivos y lo redimensiona."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, 'icons', filename)

            if not os.path.exists(icon_path):
                root_dir = os.path.dirname(current_dir)
                icon_path = os.path.join(root_dir, 'icons', filename)

            if not os.path.exists(icon_path):
                print(f"Warning: Icon {filename} not found")
                return None

            image = Image.open(icon_path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Warning: Could not load icon {filename}: {e}")
            return None

    def calculate_column_widths(self, columns, data):
        """Calcula el ancho dinámico de las columnas de la tabla basado en el contenido."""
        column_widths = {}
        font = tkinter.font.Font(family='Segoe UI', size=12)

        for col_index, col_name in enumerate(columns):
            max_width = font.measure(col_name)
            for row in data:
                cell_value = str(row[col_index])
                cell_width = font.measure(cell_value)
                max_width = max(max_width, cell_width)
            column_widths[col_name] = max_width + 20

        min_widths = {
            'ID': 60,
            'Nombre': 250,
            'Artículo': 200,
            'Teléfono': 150,
            'Dirección': 300,
            'Municipio': 150,
            'Fecha Pedido': 150,
            'Fecha Entrega': 150,
            'Estado': 100
        }

        for col in min_widths:
            if col in column_widths:
                column_widths[col] = max(column_widths[col], min_widths[col])

        return column_widths

    def cambiar_tamano_fuente(self):
        """Permite al usuario cambiar el tamaño de la fuente de la interfaz a través de un diálogo."""
        new_size = simpledialog.askinteger("Cambiar Tamaño de Fuente", "Ingrese el nuevo tamaño de fuente:", minvalue=8, maxvalue=72)
        if new_size:
            style = ttk.Style()
            font = style.lookup('Treeview', 'font')
            if not font:
                font_family = "TkDefaultFont"
                current_size = 10
            else:
                font_obj = tkinter.font.Font(font=font)
                font_family = font_obj.actual()['family']
                current_size = font_obj.actual()['size']

            style.configure('Treeview', font=(font_family, new_size))
            style.configure('Treeview.Heading', font=(font_family, new_size))
            style.configure('Section.TLabel',
                          font=('Arial Black', 13),
                          foreground="#333333",
                          background=self.color_palette['surface'])
            style.configure('SectionSubtitle.TLabel',
                          font=('Segoe UI', 10+2, 'italic'),
                          foreground=self.color_palette['text_section_header'],
                          background=self.color_palette['surface'])
            style.configure('Field.TLabel',
                          font=('Segoe UI', 10+2),
                          foreground=self.color_palette['text_filter_label'],
                          background=self.color_palette['surface'])
            style.configure('Value.TLabel',
                          font=('Segoe UI', 11+2, 'semibold'),
                          foreground=self.color_palette['text_value_label'],
                          background=self.color_palette['surface'])
            style.configure('Header.TLabel',
                          font=('Segoe UI', 18+2, 'bold'),
                          foreground=self.color_palette['text_header'],
                          background=self.color_palette['surface'])
            style.configure('Modern.TEntry',
                          font=('Arial', 10+2),
                          padding=8,
                          borderwidth=1,
                          relief='solid',
                          highlightthickness=0,
                          bordercolor='#ccc')
            style.configure('Modern.TCombobox',
                          font=('Arial', 10+2),
                          padding=8,
                          borderwidth=1,
                          relief='solid',
                          highlightthickness=0,
                          bordercolor='#ccc')
            style.configure('Filter.TLabel',
                          font=('Arial', 10+2),
                          foreground='#555')

            self._adjust_column_widths()

    def update_theme(self, new_color_palette):
        """Actualiza la paleta de colores del tema de la interfaz."""
        self.color_palette = new_color_palette
        self._setup_styles()
        self._setup_right_panel_styles()
        self._update_widget_colors()

    def _update_widget_colors(self):
        """Actualiza los colores de widgets específicos usando la paleta de colores actual."""
        style = ttk.Style()

        # Actualizar colores del Treeview
        style.configure('Treeview',
                       background=self.color_palette['surface'],
                       fieldbackground=self.color_palette['surface'],
                       foreground=self.color_palette['text'])

        style.configure('Treeview.Heading',
                       background=self.color_palette['primary'],
                       foreground=self.color_palette['text'],
                       padding=8)

        style.map('Treeview',
                 background=[('selected', self.color_palette['selected'])],
                 foreground=[('selected', self.color_palette['text'])])

    def _setup_treeview(self, container, x_scroll, y_scroll):
        """Configura el Treeview (tabla) con estilos, scrollbars y eventos."""
        style = ttk.Style()
        base_font_size = 10
        header_font_size = 10
        row_height = 30

        # Configurar estilos para el Treeview
        style.configure('Custom.Treeview',
                       background=self.color_palette['surface'],
                       fieldbackground=self.color_palette['surface'],
                       foreground=self.color_palette['text'],
                       rowheight=row_height,
                       font=('Segoe UI', base_font_size))

        # Configurar el color de selección en el Treeview
        style.map('Custom.Treeview',
                 background=[('selected', '#E8E8E8')],
                 foreground=[('selected', self.color_palette['text'])])

        # Configurar estilos para los encabezados del Treeview
        style.configure('Custom.Treeview.Heading',
                       background=self.color_palette['primary'],
                       foreground=self.color_palette['text'],
                       font=('Segoe UI', header_font_size, 'bold'),
                       padding=5)

        # Crear el Treeview con las columnas definidas
        self.tree = ttk.Treeview(
            container,
            columns=('ID', 'Nombre', 'Artículo', 'Teléfono', 'Dirección',
                    'Municipio', 'Estado', 'Fecha Pedido', 'Fecha Entrega'),
            show='headings',
            selectmode='browse',
            style='Custom.Treeview',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Configurar el ancho dinámico de las columnas
        self._setup_dynamic_columns()

        # Configurar las scrollbars para controlar el Treeview
        y_scroll.configure(command=lambda *args: self.tree.yview(*args))
        x_scroll.configure(command=lambda *args: self.tree.xview(*args))

        # Vincular eventos del Treeview
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Configure>', self.on_treeview_configure)

        # Configurar tags para diferentes estados (Pendiente, Entregado, Cancelado) inicialmente sin colores
        self.tree.tag_configure('Pendiente', background='', foreground='')
        self.tree.tag_configure('Entregado', background='', foreground='')
        self.tree.tag_configure('Cancelado', background='', foreground='')

        # Configurar la barra de estado en la parte inferior del contenedor de la tabla
        self._setup_status_bar(container)

    def _setup_dynamic_columns(self):
        """Configura el ancho de las columnas del Treeview de manera dinámica y proporcional."""
        total_width = self.parent.winfo_width()

        column_ratios = {
            'ID': 0.05,
            'Nombre': 0.15,
            'Artículo': 0.15,
            'Teléfono': 0.1,
            'Dirección': 0.15,
            'Municipio': 0.1,
            'Estado': 0.1,
            'Fecha Pedido': 0.1,
            'Fecha Entrega': 0.1
        }

        for col, ratio in column_ratios.items():
            width = int(total_width * ratio)
            stretch = ratio > 0.1
            anchor = 'center' if col in ['ID', 'Estado', 'Fecha Pedido', 'Fecha Entrega'] else 'w'

            self.tree.column(col,
                            width=width,
                            minwidth=int(width * 0.5),
                            stretch=stretch,
                            anchor=anchor)
            self.tree.heading(col, text=col, anchor=anchor)

    def on_treeview_configure(self, event):
        """Maneja el evento de redimensionamiento del Treeview para reajustar el ancho de las columnas."""
        if event.width != getattr(self, '_last_tree_width', None):
            self._last_tree_width = event.width
            self._setup_dynamic_columns()

    def _setup_status_bar(self, parent):
        """Configura la barra de estado en la parte inferior de la tabla."""
        status_frame = ttk.Frame(parent, style='Card.TFrame')
        status_frame.grid(row=4, column=0, sticky='ew', padx=15, pady=(0,10))
        status_frame.columnconfigure(1, weight=1)

        # Frame para el contador de registros (lado izquierdo de la barra de estado)
        count_frame = ttk.Frame(status_frame)
        count_frame.pack(side='left', padx=10, pady=5)

        ttk.Label(
            count_frame,
            text="📊",
            font=('Segoe UI', self._get_relative_font_size(12))
        ).pack(side='left', padx=(0,5))

        self.status_label = ttk.Label(
            count_frame,
            text="0 registros",
            font=('Segoe UI', self._get_relative_font_size(10)),
            foreground=self.color_palette['text_secondary']
        )
        self.status_label.pack(side='left')

        # Frame para el switch de colores de estado (lado derecho de la barra de estado)
        color_frame = ttk.Frame(status_frame)
        color_frame.pack(side='right', padx=10, pady=5)

        ttk.Label(
            color_frame,
            text="Colorear estados",
            font=('Segoe UI', self._get_relative_font_size(9)),
            foreground=self.color_palette['text_secondary']
        ).pack(side='left', padx=(0,8))

        self.color_states_var = tk.BooleanVar(value=False)

        self.switch_button = ttk.Checkbutton(
            color_frame,
            variable=self.color_states_var,
            style='Switch.TCheckbutton',
            command=self.toggle_state_colors
        )
        self.switch_button.pack(side='left')

        style = ttk.Style()
        style.configure('Switch.TCheckbutton',
                       background=self.color_palette['surface'],
                       width=8,
                       padding=4)

        self.apply_state_colors()

    def toggle_state_colors(self):
        """Alterna la visualización de colores de estado en la tabla al cambiar el switch."""
        self.apply_state_colors()

    def apply_state_colors(self):
        """Aplica o remueve los colores de estado en las filas de la tabla según el estado del switch."""
        if self.color_states_var.get():
            self.tree.tag_configure('Pendiente', background='#fff8e1', foreground='#ff8f00')
            self.tree.tag_configure('Entregado', background='#e8f5e9', foreground='#2e7d32')
            self.tree.tag_configure('Cancelado', background='#ffebee', foreground='#c62828')
        else:
            self.tree.tag_configure('Pendiente', background='', foreground='')
            self.tree.tag_configure('Entregado', background='', foreground='')
            self.tree.tag_configure('Cancelado', background='', foreground='')

        selected = self.tree.selection()
        self.load_data()
        if selected:
            self.tree.selection_set(selected)

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Crea un rectángulo con esquinas redondeadas en un canvas."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    tk.Canvas.create_rounded_rectangle = create_rounded_rectangle