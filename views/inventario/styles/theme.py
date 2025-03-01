"""
Configuración de estilos para el módulo de inventario.
"""

from tkinter import ttk
from .colors import COLOR_PALETTE

def setup_styles(style: ttk.Style):
    """
    Configura los estilos visuales para la aplicación.
    
    Args:
        style: Objeto ttk.Style para configurar los estilos
    """
    # Definición de fuentes con tamaños ajustados
    fonts = {
        'heading': ('Segoe UI', 28, 'bold'),
        'subheading': ('Segoe UI', 18, 'bold'),
        'body': ('Segoe UI', 12),
        'button': ('Segoe UI', 11, 'bold'),
        'caption': ('Segoe UI', 10)
    }

    # Estilos para el Treeview (tabla de datos)
    style.configure('Custom.Treeview',
                   background=COLOR_PALETTE['surface'],
                   fieldbackground=COLOR_PALETTE['surface'],
                   foreground=COLOR_PALETTE['text'],
                   rowheight=40,
                   font=fonts['body'])

    style.configure('Custom.Treeview.Heading',
                   background=COLOR_PALETTE['primary'],
                   foreground='white',
                   font=('Segoe UI', 12, 'bold'),
                   relief='flat',
                   borderwidth=0,
                   padding=10)

    # Estilo para la selección en el Treeview
    style.map('Custom.Treeview',
             background=[('selected', COLOR_PALETTE['selected'])],
             foreground=[('selected', COLOR_PALETTE['text'])])

    # Estilos base para frames
    style.configure('App.TFrame',
                   background=COLOR_PALETTE['background'])

    style.configure('Card.TFrame',
                   background=COLOR_PALETTE['surface'],
                   relief='solid',
                   borderwidth=1)

    # Estilos para etiquetas
    style.configure('Header.TLabel',
                   font=fonts['heading'],
                   background=COLOR_PALETTE['surface'],
                   foreground=COLOR_PALETTE['text_header'])

    style.configure('Subheading.TLabel',
                   font=fonts['subheading'],
                   background=COLOR_PALETTE['surface'],
                   foreground=COLOR_PALETTE['text'])

    # Estilos para botones
    button_styles = {
        'Primary.TButton': (COLOR_PALETTE['primary'], COLOR_PALETTE['primary_dark'], 'white'),
        'Success.TButton': (COLOR_PALETTE['success'], COLOR_PALETTE['primary_dark'], 'white'),
        'Warning.TButton': (COLOR_PALETTE['warning'], COLOR_PALETTE['primary_dark'], COLOR_PALETTE['text']),
        'Error.TButton': (COLOR_PALETTE['error'], COLOR_PALETTE['primary_dark'], 'white'),
        'Info.TButton': (COLOR_PALETTE['info'], COLOR_PALETTE['primary_dark'], COLOR_PALETTE['text']),
        'Secondary.TButton': (COLOR_PALETTE['secondary'], COLOR_PALETTE['primary_dark'], COLOR_PALETTE['text'])
    }

    for style_name, (bg, active_bg, fg) in button_styles.items():
        style.configure(style_name,
                      font=fonts['button'],
                      background=bg,
                      foreground=fg,
                      borderwidth=1,
                      bordercolor=COLOR_PALETTE['border'],
                      relief='solid',
                      focuscolor=active_bg,
                      padding=(20, 10))

        style.map(style_name,
                 background=[('active', active_bg),
                           ('disabled', COLOR_PALETTE['disabled'])],
                 foreground=[('disabled', '#FFFFFF')])

    # Estilo para separadores visuales
    style.configure('TSeparator',
                   background=COLOR_PALETTE['divider'])

    # Estilo para el panel de filtros
    style.configure('Surface.TFrame',
                   background=COLOR_PALETTE['surface'],
                   relief='solid',
                   borderwidth=1)

    # Estilo para etiquetas dentro del panel de filtros
    style.configure('Filter.TLabel',
                   font=fonts['body'],
                   background=COLOR_PALETTE['surface'],
                   foreground=COLOR_PALETTE['text_filter_label'],
                   padding=5)

    # Estilo para campos de entrada y comboboxes
    style.configure('Modern.TEntry',
                   font=fonts['body'],
                   padding=8,
                   relief='solid',
                   borderwidth=1,
                   bordercolor=COLOR_PALETTE['border'])

    style.configure('Modern.TCombobox',
                   font=fonts['body'],
                   padding=8,
                   relief='solid',
                   borderwidth=1,
                   bordercolor=COLOR_PALETTE['border'])

    # Estilos para scrollbars
    style.configure('Vertical.TScrollbar',
                   background=COLOR_PALETTE['primary_light'],
                   troughcolor=COLOR_PALETTE['background'],
                   bordercolor=COLOR_PALETTE['border'],
                   arrowcolor=COLOR_PALETTE['primary'])

    style.configure('Horizontal.TScrollbar',
                   background=COLOR_PALETTE['primary_light'],
                   troughcolor=COLOR_PALETTE['background'],
                   bordercolor=COLOR_PALETTE['border'],
                   arrowcolor=COLOR_PALETTE['primary'])

    # Estilo para la barra de estado
    style.configure('Statusbar.TLabel',
                   font=fonts['caption'],
                   background=COLOR_PALETTE['surface'],
                   foreground=COLOR_PALETTE['text_secondary']) 