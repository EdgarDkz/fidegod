import tkinter as tk
from tkinter import ttk

class AppStyles:
    """Clase para manejar estilos compartidos en toda la aplicación"""
    
    def __init__(self):
        # Paleta de colores predefinida - puedes personalizarla según necesites
        self.color_palette = {
            'primary': '#f2a900',  # Naranja Principal
            'primary_light': '#ffcc66',  # Naranja Secundario Claro
            'primary_dark': '#d89f00',  # Naranja Secundario Oscuro
            'secondary': '#f2b600',  # Naranja Secundario
            'background': '#FFF8F0',  # Fondo blanco
            'surface': '#ffdb99',  # Superficie
            'error': '#f2a3a3',  # Color de error
            'success': '#a3d6a3',  # Color de éxito
            'warning': '#f2d66e',  # Color de advertencia
            'info': '#f2c58a',  # Color de información
            'text': '#424242',  # Gris Cálido / Neutro para Texto
            'text_secondary': '#76849a',  # Texto secundario
            'text_header': '#f2a900',  # Para encabezados
            'divider': '#d9d9d9',  # Gris claro para divisores
            'border': '#d9b300',  # Color de borde
        }
        
        # Aplicar los estilos al inicializar
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos compartidos para toda la aplicación"""
        style = ttk.Style()
        colors = self.color_palette
        
        # Estilos para títulos de paneles con marcos distintivos
        
        # Título del panel de filtros
        style.configure('CustomFilterTitle.TLabel',
                        background=colors['surface'],
                        foreground=colors['primary'],
                        font=('Segoe UI', 18, 'bold'),
                        padding=10,
                        borderwidth=2,
                        relief="groove")
        
        # Título del panel principal
        style.configure('MainPanelTitle.TLabel',
                        background=colors['surface'],
                        foreground=colors['primary'],
                        font=('Segoe UI', 20, 'bold'),
                        padding=10,
                        borderwidth=2,
                        relief="ridge")
        
        # Título del panel de detalles
        style.configure('DetailPanelTitle.TLabel',
                        background=colors['background'],
                        foreground=colors['primary'],
                        font=('Segoe UI', 16, 'bold'),
                        padding=10,
                        borderwidth=2,
                        relief="groove")
        
        # Estilos para el panel de filtros
        style.configure('Filter.TFrame', 
                      background=colors['background'],
                      relief='flat')
        
        # Estilos para la tabla
        style.configure('Custom.Treeview',
                    background=colors['surface'],
                    fieldbackground=colors['surface'],
                    foreground=colors['text'],
                    rowheight=40,
                    font=('Segoe UI', 12))

        style.configure('Custom.Treeview.Heading',
                    background=colors['primary'],
                    foreground='white',
                    font=('Segoe UI', 12, 'bold'),
                    relief='flat',
                    borderwidth=0,
                    padding=10)
        
        # Puedes añadir más estilos compartidos aquí según necesites

# Instancia global de estilos para usarse en toda la aplicación
app_styles = AppStyles() 