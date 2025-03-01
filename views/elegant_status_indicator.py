import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont
import os

class ElegantStatusIndicator(ttk.Frame):
    """
    Indicador de estado elegante que utiliza tipografía y efectos visuales
    en lugar de fondos de color para resaltar el texto.
    """
    
    def __init__(self, parent, theme_manager, status="pendiente", size=20, with_text=True, 
                with_icon=True, with_animation=False, *args, **kwargs):
        """
        Inicializa el indicador de estado elegante.
        
        Args:
            parent: Widget padre
            theme_manager: Gestor de temas
            status: Estado ('pendiente', 'entregado', 'cancelado', etc.)
            size: Tamaño del indicador
            with_text: Si se debe mostrar texto
            with_icon: Si se debe mostrar icono
            with_animation: Si se debe animar el indicador
            *args, **kwargs: Argumentos adicionales para el Frame
        """
        super().__init__(parent, *args, **kwargs)
        
        self.theme_manager = theme_manager
        self.colors = theme_manager.get_color_palette()
        self.fonts = theme_manager.get_fonts()
        
        self.status = status.lower()
        self.size = size
        self.with_text = with_text
        self.with_icon = with_icon
        self.with_animation = with_animation
        
        # Configurar estilos
        self.configure(style='TFrame')
        
        # Crear canvas para dibujar
        self.canvas = tk.Canvas(
            self,
            bg=self.colors['background'],
            highlightthickness=0,
            height=self.size + 20 if with_text else self.size,
            **kwargs
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Inicializar
        self.setup_status_properties()
        self.draw_indicator()
        
        # Configurar animación si está habilitada
        if self.with_animation and self.status == 'pendiente':
            self.animate()
    
    def setup_status_properties(self):
        """Configura las propiedades según el estado."""
        # Configuración por estado
        status_config = {
            'pendiente': {
                'color': self.colors['warning'],
                'text': 'Pendiente',
                'icon': '⏳',
                'font_style': 'button'
            },
            'entregado': {
                'color': self.colors['success'],
                'text': 'Entregado',
                'icon': '✅',
                'font_style': 'button'
            },
            'cancelado': {
                'color': self.colors['error'],
                'text': 'Cancelado',
                'icon': '❌',
                'font_style': 'button'
            },
            'en proceso': {
                'color': self.colors['info'],
                'text': 'En Proceso',
                'icon': '🔄',
                'font_style': 'button'
            },
            'completado': {
                'color': self.colors['success'],
                'text': 'Completado',
                'icon': '✅',
                'font_style': 'button'
            },
            'error': {
                'color': self.colors['error'],
                'text': 'Error',
                'icon': '⚠️',
                'font_style': 'button'
            }
        }
        
        # Usar configuración predeterminada si el estado no está definido
        if self.status not in status_config:
            self.status_color = self.colors['info']
            self.status_text = self.status.capitalize()
            self.status_icon = '📌'
            self.font_style = 'button'
        else:
            config = status_config[self.status]
            self.status_color = config['color']
            self.status_text = config['text']
            self.status_icon = config['icon']
            self.font_style = config['font_style']
    
    def draw_indicator(self):
        """Dibuja el indicador de estado."""
        self.canvas.delete("all")
        
        # Calcular dimensiones
        width = self.canvas.winfo_width() or 200
        height = self.canvas.winfo_height() or self.size + 20
        
        # Dibujar indicador circular
        if self.with_icon:
            # Dibujar círculo con icono
            circle_x = 10 + self.size // 2
            circle_y = height // 2
            
            # Círculo de fondo
            self.canvas.create_oval(
                10, circle_y - self.size // 2,
                10 + self.size, circle_y + self.size // 2,
                fill=self.status_color,
                outline="",
                tags="indicator"
            )
            
            # Icono
            self.canvas.create_text(
                circle_x, circle_y,
                text=self.status_icon,
                fill=self.colors['text_on_primary'],
                font=('Segoe UI Emoji', self.size // 2),
                tags="icon"
            )
            
            # Texto
            if self.with_text:
                # Crear texto con tipografía elegante
                text_x = 20 + self.size
                
                # Sombra sutil para dar profundidad
                self.canvas.create_text(
                    text_x + 1, circle_y + 1,
                    text=self.status_text,
                    fill=self.colors['text_tertiary'],
                    font=self.fonts[self.font_style],
                    anchor='w',
                    tags="text_shadow"
                )
                
                # Texto principal
                self.canvas.create_text(
                    text_x, circle_y,
                    text=self.status_text,
                    fill=self.status_color,
                    font=self.fonts[self.font_style],
                    anchor='w',
                    tags="text"
                )
        else:
            # Solo texto con estilo
            if self.with_text:
                text_x = 10
                text_y = height // 2
                
                # Sombra sutil
                self.canvas.create_text(
                    text_x + 1, text_y + 1,
                    text=self.status_text,
                    fill=self.colors['text_tertiary'],
                    font=self.fonts[self.font_style],
                    anchor='w',
                    tags="text_shadow"
                )
                
                # Texto principal
                self.canvas.create_text(
                    text_x, text_y,
                    text=self.status_text,
                    fill=self.status_color,
                    font=self.fonts[self.font_style],
                    anchor='w',
                    tags="text"
                )
    
    def animate(self):
        """Anima el indicador de estado."""
        if not self.with_animation or self.status != 'pendiente':
            return
        
        # Obtener ángulo actual
        angle = getattr(self, 'animation_angle', 0)
        angle = (angle + 5) % 360
        self.animation_angle = angle
        
        # Actualizar rotación del icono
        if hasattr(self, 'icon_image'):
            # Si hay una imagen, rotarla
            rotated_image = self.original_icon_image.rotate(angle)
            self.icon_image = ImageTk.PhotoImage(rotated_image)
            self.canvas.itemconfig("icon_image", image=self.icon_image)
        else:
            # Si es un emoji, cambiar entre varios
            icons = ['⏳', '⌛']
            self.canvas.itemconfig("icon", text=icons[angle // 180])
        
        # Programar siguiente frame
        self.after(100, self.animate)
    
    def update_status(self, new_status):
        """
        Actualiza el estado del indicador.
        
        Args:
            new_status: Nuevo estado
        """
        self.status = new_status.lower()
        self.setup_status_properties()
        self.draw_indicator()
        
        # Iniciar o detener animación según corresponda
        if self.with_animation:
            if self.status == 'pendiente':
                self.animate()
            else:
                self.with_animation = False
    
    def set_size(self, new_size):
        """
        Actualiza el tamaño del indicador.
        
        Args:
            new_size: Nuevo tamaño
        """
        self.size = new_size
        self.canvas.configure(height=self.size + 20 if self.with_text else self.size)
        self.draw_indicator()
    
    def toggle_text(self):
        """Alterna la visibilidad del texto."""
        self.with_text = not self.with_text
        self.canvas.configure(height=self.size + 20 if self.with_text else self.size)
        self.draw_indicator()
    
    def toggle_icon(self):
        """Alterna la visibilidad del icono."""
        self.with_icon = not self.with_icon
        self.draw_indicator()
    
    def toggle_animation(self):
        """Alterna la animación."""
        self.with_animation = not self.with_animation
        if self.with_animation and self.status == 'pendiente':
            self.animate()


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ejemplo de Indicador de Estado Elegante")
    
    # Crear frame contenedor
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill='both', expand=True)
    
    # Crear indicadores de estado
    statuses = ['pendiente', 'entregado', 'cancelado', 'en proceso', 'error']
    
    for status in statuses:
        indicator = ElegantStatusIndicator(
            frame,
            None,  # Aquí iría el theme_manager
            status=status,
            size=24,
            with_text=True,
            with_icon=True,
            with_animation=status == 'pendiente'
        )
        indicator.pack(fill='x', pady=10)
    
    root.mainloop() 