"""
Módulo de estilos elegantes para la aplicación FIDEGOD.
Proporciona estilos modernos y profesionales para los widgets de Tkinter.
"""

import tkinter as tk
from tkinter import ttk
import platform

class ElegantStyles:
    """
    Clase para aplicar estilos elegantes a los widgets de Tkinter.
    Proporciona métodos para configurar estilos modernos y profesionales.
    """
    
    def __init__(self, root, theme_manager=None):
        """
        Inicializa los estilos elegantes.
        
        Args:
            root: La ventana raíz de Tkinter
            theme_manager: Gestor de temas opcional
        """
        self.root = root
        self.theme_manager = theme_manager
        self.style = ttk.Style()
        
        # Detectar sistema operativo para seleccionar fuentes adecuadas
        self.system = platform.system()
        
        # Obtener colores del theme_manager si está disponible
        if theme_manager:
            self.colors = theme_manager.get_color_palette()
        else:
            # Paleta de colores elegante por defecto
            self.colors = {
                # Colores principales
                'primary': '#E67E22',          # Naranja cálido
                'primary_light': '#F39C12',    # Naranja ámbar
                'primary_dark': '#D35400',     # Naranja oscuro
                
                # Colores neutros
                'background': '#F9F9F9',       # Fondo claro
                'surface': '#FFFFFF',          # Superficie blanca
                'card': '#FFFFFF',             # Tarjetas blancas
                
                # Colores de texto
                'text': '#2C3E50',             # Texto principal (azul oscuro)
                'text_secondary': '#7F8C8D',   # Texto secundario (gris)
                'text_tertiary': '#BDC3C7',    # Texto terciario (gris claro)
                'text_on_primary': '#FFFFFF',  # Texto sobre color primario
                
                # Colores de acento
                'accent': '#3498DB',           # Azul acento
                'success': '#2ECC71',          # Verde éxito
                'warning': '#F1C40F',          # Amarillo advertencia
                'error': '#E74C3C',            # Rojo error
                'info': '#1ABC9C',             # Turquesa información
                
                # Colores de interfaz
                'divider': '#ECF0F1',          # Divisor (gris muy claro)
                'hover': '#F5F7F8',            # Hover (gris muy claro)
                'selected': '#E1E8ED',         # Seleccionado (gris claro)
                'disabled': '#D6DBDF',         # Deshabilitado (gris)
                'input': '#FFFFFF',            # Fondo de entrada (blanco)
                'input_border': '#BDC3C7',     # Borde de entrada (gris claro)
                'toolbar': '#F9F9F9',          # Barra de herramientas (gris muy claro)
                'status_bar': '#F9F9F9',       # Barra de estado (gris muy claro)
            }
        
        # Configurar fuentes
        self.setup_fonts()
        
        # Aplicar estilos
        self.apply_styles()
    
    def setup_fonts(self):
        """Configura las fuentes según el sistema operativo."""
        if self.system == 'Windows':
            self.fonts = {
                'heading1': ('Segoe UI', 18, 'bold'),
                'heading2': ('Segoe UI', 16, 'bold'),
                'heading3': ('Segoe UI', 14, 'bold'),
                'subtitle': ('Segoe UI', 12, 'italic'),
                'body': ('Segoe UI', 10),
                'body_bold': ('Segoe UI', 10, 'bold'),
                'body_italic': ('Segoe UI', 10, 'italic'),
                'small': ('Segoe UI', 9),
                'tiny': ('Segoe UI', 8),
                'monospace': ('Consolas', 9)
            }
        elif self.system == 'Darwin':  # macOS
            self.fonts = {
                'heading1': ('SF Pro Display', 18, 'bold'),
                'heading2': ('SF Pro Display', 16, 'bold'),
                'heading3': ('SF Pro Display', 14, 'bold'),
                'subtitle': ('SF Pro Text', 12, 'italic'),
                'body': ('SF Pro Text', 10),
                'body_bold': ('SF Pro Text', 10, 'bold'),
                'body_italic': ('SF Pro Text', 10, 'italic'),
                'small': ('SF Pro Text', 9),
                'tiny': ('SF Pro Text', 8),
                'monospace': ('SF Mono', 9)
            }
        else:  # Linux y otros
            self.fonts = {
                'heading1': ('Ubuntu', 18, 'bold'),
                'heading2': ('Ubuntu', 16, 'bold'),
                'heading3': ('Ubuntu', 14, 'bold'),
                'subtitle': ('Ubuntu', 12, 'italic'),
                'body': ('Ubuntu', 10),
                'body_bold': ('Ubuntu', 10, 'bold'),
                'body_italic': ('Ubuntu', 10, 'italic'),
                'small': ('Ubuntu', 9),
                'tiny': ('Ubuntu', 8),
                'monospace': ('Ubuntu Mono', 9)
            }
    
    def apply_styles(self):
        """Aplica los estilos a los widgets."""
        # Usar el tema 'clam' como base
        self.style.theme_use('clam')
        
        # Estilos generales
        self.style.configure('.',
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=self.fonts['body'])
        
        # Frame
        self.style.configure('TFrame',
                           background=self.colors['surface'])
        
        # Label
        self.style.configure('TLabel',
                           background=self.colors['surface'],
                           foreground=self.colors['text'],
                           font=self.fonts['body'])
        
        # Button
        self.style.configure('TButton',
                           background=self.colors['primary'],
                           foreground=self.colors['text_on_primary'],
                           font=self.fonts['body_bold'],
                           padding=(10, 5),
                           relief='flat')
        
        self.style.map('TButton',
                     background=[('active', self.colors['primary_dark']),
                                ('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Entry
        self.style.configure('TEntry',
                           background=self.colors['input'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['input'],
                           font=self.fonts['body'],
                           padding=(5, 2),
                           relief='flat',
                           borderwidth=1)
        
        self.style.map('TEntry',
                     fieldbackground=[('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Combobox
        self.style.configure('TCombobox',
                           background=self.colors['input'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['input'],
                           font=self.fonts['body'],
                           padding=(5, 2),
                           relief='flat',
                           arrowsize=15)
        
        self.style.map('TCombobox',
                     fieldbackground=[('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Notebook (pestañas)
        self.style.configure('TNotebook',
                           background=self.colors['background'],
                           tabmargins=(2, 5, 2, 0))
        
        self.style.configure('TNotebook.Tab',
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=self.fonts['body_bold'],
                           padding=(15, 5),
                           borderwidth=0)
        
        self.style.map('TNotebook.Tab',
                     background=[('selected', self.colors['primary']),
                                ('active', self.colors['primary_light'])],
                     foreground=[('selected', self.colors['text_on_primary']),
                                ('active', self.colors['text'])])
        
        # Scrollbar
        self.style.configure('TScrollbar',
                           background=self.colors['background'],
                           troughcolor=self.colors['background'],
                           borderwidth=0,
                           arrowsize=13)
        
        # Progressbar
        self.style.configure('TProgressbar',
                           background=self.colors['primary'],
                           troughcolor=self.colors['background'],
                           borderwidth=0)
        
        # Separator
        self.style.configure('TSeparator',
                           background=self.colors['divider'])
        
        # Treeview (tabla)
        self.style.configure('Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['surface'],
                           font=self.fonts['body'],
                           borderwidth=0,
                           rowheight=25)
        
        self.style.configure('Treeview.Heading',
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=self.fonts['body_bold'],
                           relief='flat',
                           padding=(5, 5))
        
        self.style.map('Treeview',
                     background=[('selected', self.colors['primary_light'])],
                     foreground=[('selected', self.colors['text'])])
        
        # Estilos personalizados
        
        # Botón primario
        self.style.configure('Primary.TButton',
                           background=self.colors['primary'],
                           foreground=self.colors['text_on_primary'],
                           font=self.fonts['body_bold'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Primary.TButton',
                     background=[('active', self.colors['primary_dark']),
                                ('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Botón secundario
        self.style.configure('Secondary.TButton',
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=self.fonts['body_bold'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Secondary.TButton',
                     background=[('active', self.colors['selected']),
                                ('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Botón de acción
        self.style.configure('Action.TButton',
                           background=self.colors['accent'],
                           foreground=self.colors['text_on_primary'],
                           font=self.fonts['body_bold'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Action.TButton',
                     background=[('active', self.colors['accent']),
                                ('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Botón de éxito
        self.style.configure('Success.TButton',
                           background=self.colors['success'],
                           foreground=self.colors['text_on_primary'],
                           font=self.fonts['body_bold'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Success.TButton',
                     background=[('active', self.colors['success']),
                                ('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Botón de advertencia
        self.style.configure('Warning.TButton',
                           background=self.colors['warning'],
                           foreground=self.colors['text'],
                           font=self.fonts['body_bold'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Warning.TButton',
                     background=[('active', self.colors['warning']),
                                ('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Botón de error
        self.style.configure('Error.TButton',
                           background=self.colors['error'],
                           foreground=self.colors['text_on_primary'],
                           font=self.fonts['body_bold'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Error.TButton',
                     background=[('active', self.colors['error']),
                                ('disabled', self.colors['disabled'])],
                     foreground=[('disabled', self.colors['text_tertiary'])])
        
        # Etiqueta de título
        self.style.configure('Title.TLabel',
                           background=self.colors['surface'],
                           foreground=self.colors['text'],
                           font=self.fonts['heading1'])
        
        # Etiqueta de subtítulo
        self.style.configure('Subtitle.TLabel',
                           background=self.colors['surface'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['subtitle'])
        
        # Etiqueta pequeña
        self.style.configure('Small.TLabel',
                           background=self.colors['surface'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['small'])
        
        # Frame de tarjeta
        self.style.configure('Card.TFrame',
                           background=self.colors['card'],
                           relief='flat',
                           borderwidth=0)
        
        # Frame de barra de herramientas
        self.style.configure('Toolbar.TFrame',
                           background=self.colors['toolbar'],
                           relief='flat')
        
        # Frame de barra de estado
        self.style.configure('StatusBar.TFrame',
                           background=self.colors['status_bar'],
                           relief='flat')
        
        # Etiqueta de barra de estado
        self.style.configure('StatusBar.TLabel',
                           background=self.colors['status_bar'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['small'])
    
    def update_colors(self, colors):
        """
        Actualiza los colores y vuelve a aplicar los estilos.
        
        Args:
            colors: Diccionario con los nuevos colores
        """
        self.colors.update(colors)
        self.apply_styles()
    
    def create_tooltip(self, widget, text):
        """
        Crea un tooltip para un widget.
        
        Args:
            widget: Widget al que se le añadirá el tooltip
            text: Texto del tooltip
        """
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Crear ventana de tooltip
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            frame = tk.Frame(tooltip, background=self.colors['background'],
                           borderwidth=1, relief="solid")
            frame.pack(ipadx=5, ipady=5)
            
            label = tk.Label(frame, text=text, justify="left",
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=self.fonts['small'],
                           wraplength=250)
            label.pack()
            
            self.tooltip = tooltip
        
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                del self.tooltip
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def create_round_button(self, parent, text="", command=None, radius=20, **kwargs):
        """
        Crea un botón redondo.
        
        Args:
            parent: Widget padre
            text: Texto del botón
            command: Función a ejecutar al hacer clic
            radius: Radio del botón
            **kwargs: Argumentos adicionales para el botón
            
        Returns:
            El botón creado
        """
        # Valores predeterminados
        bg_color = kwargs.get('background', self.colors['primary'])
        fg_color = kwargs.get('foreground', self.colors['text_on_primary'])
        font = kwargs.get('font', self.fonts['body_bold'])
        
        # Crear frame contenedor
        frame = tk.Frame(parent, bg=parent['background'])
        
        # Crear canvas para dibujar el círculo
        canvas = tk.Canvas(frame, width=radius*2, height=radius*2,
                         bg=parent['background'], highlightthickness=0)
        canvas.pack()
        
        # Dibujar círculo
        canvas.create_oval(2, 2, radius*2-2, radius*2-2, fill=bg_color, outline="")
        
        # Añadir texto
        canvas.create_text(radius, radius, text=text, fill=fg_color, font=font)
        
        # Configurar eventos
        def on_click(event):
            if command:
                command()
        
        def on_enter(event):
            canvas.itemconfig(1, fill=self.colors['primary_dark'])
        
        def on_leave(event):
            canvas.itemconfig(1, fill=bg_color)
        
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        
        return frame
    
    def create_card(self, parent, title=None, **kwargs):
        """
        Crea una tarjeta con título y contenido.
        
        Args:
            parent: Widget padre
            title: Título de la tarjeta (opcional)
            **kwargs: Argumentos adicionales para el frame
            
        Returns:
            Tupla con el frame de la tarjeta y el frame de contenido
        """
        # Valores predeterminados
        padding = kwargs.get('padding', 10)
        
        # Crear frame principal
        card = ttk.Frame(parent, style='Card.TFrame')
        
        # Añadir título si se proporciona
        if title:
            title_frame = ttk.Frame(card, style='Card.TFrame')
            title_frame.pack(fill=tk.X, padx=padding, pady=(padding, 0))
            
            title_label = ttk.Label(title_frame, text=title, style='Title.TLabel')
            title_label.pack(anchor=tk.W)
            
            # Separador
            separator = ttk.Separator(card, orient='horizontal')
            separator.pack(fill=tk.X, padx=padding, pady=(5, 0))
        
        # Frame de contenido
        content_frame = ttk.Frame(card, style='Card.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        
        return card, content_frame

# Función para obtener una instancia de ElegantStyles
def get_elegant_styles(root, theme_manager=None):
    """
    Obtiene una instancia de ElegantStyles.
    
    Args:
        root: La ventana raíz de Tkinter
        theme_manager: Gestor de temas opcional
        
    Returns:
        Una instancia de ElegantStyles
    """
    return ElegantStyles(root, theme_manager) 