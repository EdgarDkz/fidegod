import tkinter as tk
from tkinter import ttk, font
import platform

class ThemeManager:
    """
    Gestor de temas para la aplicación FIDEGOD.
    Proporciona estilos elegantes y modernos con tipografía mejorada.
    """
    
    def __init__(self, root):
        """
        Inicializa el gestor de temas.
        
        Args:
            root: La ventana raíz de la aplicación.
        """
        self.root = root
        self.style = ttk.Style()
        
        # Detectar sistema operativo para seleccionar fuentes adecuadas
        self.system = platform.system()
        
        # Configurar fuentes base según el sistema operativo
        self.setup_fonts()
        
        # Paleta de colores elegante
        self.color_palette = {
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
            
            # Colores de estado
            'hover': '#ECF0F1',            # Estado hover
            'selected': '#E0F7FA',         # Estado seleccionado
            'disabled': '#ECEFF1',         # Estado deshabilitado
            'divider': '#EAECEE',          # Divisores
            
            # Colores de interfaz
            'toolbar': '#FFFFFF',          # Barra de herramientas
            'status_bar': '#FAFAFA',       # Barra de estado
            'input': '#FFFFFF',            # Campos de entrada
            'border': '#E0E0E0',           # Bordes
        }
        
        # Aplicar estilos
        self.apply_theme()
    
    def setup_fonts(self):
        """Configura las fuentes según el sistema operativo."""
        if self.system == 'Windows':
            base_font = 'Segoe UI'
            monospace_font = 'Consolas'
        elif self.system == 'Darwin':  # macOS
            base_font = 'SF Pro'
            monospace_font = 'SF Mono'
        else:  # Linux y otros
            base_font = 'Noto Sans'
            monospace_font = 'Noto Mono'
        
        # Definir jerarquía de fuentes
        self.fonts = {
            'display': (base_font, 36, 'bold'),
            'h1': (base_font, 28, 'bold'),
            'h2': (base_font, 24, 'bold'),
            'h3': (base_font, 20, 'bold'),
            'h4': (base_font, 18, 'bold'),
            'h5': (base_font, 16, 'bold'),
            'h6': (base_font, 14, 'bold'),
            'subtitle1': (base_font, 16, 'normal'),
            'subtitle2': (base_font, 14, 'normal'),
            'body1': (base_font, 14, 'normal'),
            'body2': (base_font, 12, 'normal'),
            'button': (base_font, 14, 'bold'),
            'caption': (base_font, 12, 'normal'),
            'overline': (base_font, 10, 'normal'),
            'monospace': (monospace_font, 12, 'normal'),
        }
        
        # Registrar fuentes personalizadas
        self.register_fonts()
    
    def register_fonts(self):
        """Registra las fuentes personalizadas para su uso en la aplicación."""
        for name, (family, size, weight) in self.fonts.items():
            font_obj = font.Font(family=family, size=size, weight=weight)
            self.root.option_add(f"*{name}Font", font_obj)
    
    def apply_theme(self):
        """Aplica el tema elegante a toda la aplicación."""
        colors = self.color_palette
        
        # Configuración general
        self.root.configure(background=colors['background'])
        self.style.configure('TFrame', background=colors['background'])
        self.style.configure('TLabel', background=colors['background'], foreground=colors['text'])
        
        # Estilos para encabezados y títulos
        for level in range(1, 7):
            font_key = f'h{level}'
            self.style.configure(f'Heading{level}.TLabel', 
                                font=self.fonts[font_key],
                                foreground=colors['text'],
                                background=colors['background'],
                                padding=(0, 10, 0, 10))
        
        # Estilos para botones
        self.style.configure('TButton', 
                            font=self.fonts['button'],
                            background=colors['primary'],
                            foreground=colors['text_on_primary'],
                            borderwidth=0,
                            focuscolor=colors['primary_dark'],
                            padding=(20, 10))
        
        self.style.map('TButton',
                      background=[('active', colors['primary_dark']),
                                 ('disabled', colors['disabled'])],
                      foreground=[('disabled', colors['text_tertiary'])])
        
        # Botones de acción específicos
        button_styles = {
            'Primary.TButton': (colors['primary'], colors['primary_dark'], colors['text_on_primary']),
            'Success.TButton': (colors['success'], '#27AE60', colors['text_on_primary']),
            'Warning.TButton': (colors['warning'], '#F39C12', colors['text']),
            'Error.TButton': (colors['error'], '#C0392B', colors['text_on_primary']),
            'Info.TButton': (colors['info'], '#16A085', colors['text_on_primary']),
            'Secondary.TButton': (colors['background'], colors['hover'], colors['text']),
            'Outline.TButton': (colors['background'], colors['hover'], colors['primary'])
        }
        
        for style_name, (bg, active_bg, fg) in button_styles.items():
            self.style.configure(style_name,
                              font=self.fonts['button'],
                              background=bg,
                              foreground=fg,
                              borderwidth=1,
                              relief='solid',
                              bordercolor=colors['border'] if 'Outline' in style_name else bg,
                              focuscolor=active_bg,
                              padding=(20, 10))
            
            self.style.map(style_name,
                         background=[('active', active_bg),
                                    ('disabled', colors['disabled'])],
                         foreground=[('disabled', colors['text_tertiary'])])
        
        # Estilos para entradas de texto
        self.style.configure('TEntry',
                            font=self.fonts['body1'],
                            fieldbackground=colors['input'],
                            foreground=colors['text'],
                            bordercolor=colors['border'],
                            borderwidth=1,
                            padding=8)
        
        self.style.map('TEntry',
                      fieldbackground=[('disabled', colors['disabled'])],
                      foreground=[('disabled', colors['text_tertiary'])])
        
        # Estilos para combobox
        self.style.configure('TCombobox',
                            font=self.fonts['body1'],
                            fieldbackground=colors['input'],
                            foreground=colors['text'],
                            bordercolor=colors['border'],
                            arrowcolor=colors['primary'],
                            padding=8)
        
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', colors['input']),
                                      ('disabled', colors['disabled'])],
                      foreground=[('disabled', colors['text_tertiary'])])
        
        # Estilos para Treeview (tablas)
        self.style.configure('Treeview',
                            font=self.fonts['body2'],
                            background=colors['surface'],
                            fieldbackground=colors['surface'],
                            foreground=colors['text'],
                            bordercolor=colors['border'],
                            rowheight=40)
        
        self.style.configure('Treeview.Heading',
                            font=self.fonts['h6'],
                            background=colors['primary'],
                            foreground=colors['text_on_primary'],
                            relief='flat',
                            borderwidth=0,
                            padding=10)
        
        self.style.map('Treeview',
                      background=[('selected', colors['selected'])],
                      foreground=[('selected', colors['text'])])
        
        # Estilos para paneles y tarjetas
        self.style.configure('Card.TFrame',
                            background=colors['card'],
                            relief='solid',
                            borderwidth=1,
                            bordercolor=colors['border'])
        
        # Estilos para pestañas
        self.style.configure('TNotebook',
                            background=colors['background'],
                            borderwidth=0)
        
        self.style.configure('TNotebook.Tab',
                            font=self.fonts['button'],
                            background=colors['background'],
                            foreground=colors['text_secondary'],
                            borderwidth=0,
                            padding=(20, 10))
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', colors['primary']),
                                 ('active', colors['hover'])],
                      foreground=[('selected', colors['text_on_primary']),
                                 ('active', colors['text'])])
        
        # Estilos para barras de desplazamiento
        self.style.configure('Vertical.TScrollbar',
                            background=colors['background'],
                            troughcolor=colors['background'],
                            bordercolor=colors['border'],
                            arrowcolor=colors['primary'],
                            relief='flat',
                            borderwidth=0)
        
        self.style.configure('Horizontal.TScrollbar',
                            background=colors['background'],
                            troughcolor=colors['background'],
                            bordercolor=colors['border'],
                            arrowcolor=colors['primary'],
                            relief='flat',
                            borderwidth=0)
        
        # Estilos para separadores
        self.style.configure('TSeparator',
                            background=colors['divider'])
        
        # Estilos para etiquetas de estado
        self.style.configure('Status.TLabel',
                            font=self.fonts['caption'],
                            background=colors['status_bar'],
                            foreground=colors['text_secondary'],
                            padding=(10, 5))
        
        # Estilos para paneles de filtro
        self.style.configure('Filter.TFrame',
                            background=colors['surface'],
                            relief='solid',
                            borderwidth=1,
                            bordercolor=colors['border'],
                            padding=15)
        
        self.style.configure('FilterTitle.TLabel',
                            font=self.fonts['h5'],
                            foreground=colors['primary'],
                            background=colors['surface'],
                            padding=(0, 5, 0, 15))
        
        self.style.configure('FilterLabel.TLabel',
                            font=self.fonts['button'],
                            foreground=colors['text'],
                            background=colors['surface'],
                            padding=(0, 5))
        
        # Estilos para indicadores de estado
        status_styles = {
            'Pending.TLabel': (colors['warning'], colors['text']),
            'Success.TLabel': (colors['success'], colors['text_on_primary']),
            'Error.TLabel': (colors['error'], colors['text_on_primary']),
            'Info.TLabel': (colors['info'], colors['text_on_primary'])
        }
        
        for style_name, (bg, fg) in status_styles.items():
            self.style.configure(style_name,
                              font=self.fonts['caption'],
                              background=bg,
                              foreground=fg,
                              relief='solid',
                              borderwidth=0,
                              padding=(10, 5))
    
    def get_color_palette(self):
        """Retorna la paleta de colores actual."""
        return self.color_palette
    
    def get_fonts(self):
        """Retorna las fuentes configuradas."""
        return self.fonts
    
    def create_custom_widget(self, parent, widget_type, style=None, **kwargs):
        """
        Crea un widget personalizado con estilos aplicados.
        
        Args:
            parent: Widget padre
            widget_type: Tipo de widget a crear ('TLabel', 'TButton', etc.)
            style: Estilo específico a aplicar
            **kwargs: Argumentos adicionales para el widget
            
        Returns:
            El widget creado
        """
        if style:
            return widget_type(parent, style=style, **kwargs)
        return widget_type(parent, **kwargs) 