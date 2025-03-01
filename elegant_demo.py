import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw

class ElegantWidgets:
    """
    Clase que proporciona widgets elegantes y personalizados para la aplicación.
    """
    
    def __init__(self, root):
        """
        Inicializa la clase de widgets elegantes.
        
        Args:
            root: Ventana raíz de la aplicación.
        """
        self.root = root
        
        # Configurar paleta de colores
        self.colors = {
            'primary': '#E67E22',          # Naranja cálido
            'primary_light': '#F39C12',    # Naranja ámbar
            'primary_dark': '#D35400',     # Naranja oscuro
            'background': '#F9F9F9',       # Fondo claro
            'surface': '#FFFFFF',          # Superficie blanca
            'text': '#2C3E50',             # Texto principal (azul oscuro)
            'text_secondary': '#7F8C8D',   # Texto secundario (gris)
            'text_tertiary': '#BDC3C7',    # Texto terciario (gris claro)
            'text_on_primary': '#FFFFFF',  # Texto sobre color primario
            'accent': '#3498DB',           # Azul acento
            'success': '#2ECC71',          # Verde éxito
            'warning': '#F1C40F',          # Amarillo advertencia
            'error': '#E74C3C',            # Rojo error
            'info': '#1ABC9C',             # Turquesa información
            'hover': '#ECF0F1',            # Estado hover
            'selected': '#E0F7FA',         # Estado seleccionado
            'disabled': '#ECEFF1',         # Estado deshabilitado
            'divider': '#EAECEE',          # Divisores
            'border': '#E0E0E0',           # Bordes
        }
        
        # Configurar fuentes
        self.fonts = {
            'display': ('Segoe UI', 36, 'bold'),
            'h1': ('Segoe UI', 28, 'bold'),
            'h2': ('Segoe UI', 24, 'bold'),
            'h3': ('Segoe UI', 20, 'bold'),
            'h4': ('Segoe UI', 18, 'bold'),
            'h5': ('Segoe UI', 16, 'bold'),
            'h6': ('Segoe UI', 14, 'bold'),
            'subtitle1': ('Segoe UI', 16, 'normal'),
            'subtitle2': ('Segoe UI', 14, 'normal'),
            'body1': ('Segoe UI', 14, 'normal'),
            'body2': ('Segoe UI', 12, 'normal'),
            'button': ('Segoe UI', 14, 'bold'),
            'caption': ('Segoe UI', 12, 'normal'),
            'overline': ('Segoe UI', 10, 'normal'),
        }
        
        # Configurar estilos
        self.setup_styles()
    
    def setup_styles(self):
        """Configura los estilos para los widgets."""
        style = ttk.Style()
        
        # Configuración general
        style.configure('TFrame', background=self.colors['background'])
        style.configure('TLabel', background=self.colors['background'], foreground=self.colors['text'])
        
        # Estilos para encabezados
        for level in range(1, 7):
            font_key = f'h{level}'
            style.configure(f'Heading{level}.TLabel', 
                          font=self.fonts[font_key],
                          foreground=self.colors['text'],
                          background=self.colors['background'])
        
        # Estilos para botones
        style.configure('TButton', 
                      font=self.fonts['button'],
                      background=self.colors['primary'],
                      foreground=self.colors['text_on_primary'])
        
        # Estilos para tarjetas
        style.configure('Card.TFrame',
                      background=self.colors['surface'],
                      relief='solid',
                      borderwidth=1,
                      bordercolor=self.colors['border'])
    
    def create_elegant_button(self, parent, text, command=None, icon=None, width=None, 
                             height=None, style_type='primary', corner_radius=10, 
                             hover_effect=True, **kwargs):
        """
        Crea un botón elegante con esquinas redondeadas y efectos visuales.
        
        Args:
            parent: Widget padre
            text: Texto del botón
            command: Función a ejecutar al hacer clic
            icon: Ruta al icono (opcional)
            width: Ancho del botón (opcional)
            height: Alto del botón (opcional)
            style_type: Tipo de estilo ('primary', 'secondary', 'outline', etc.)
            corner_radius: Radio de las esquinas redondeadas
            hover_effect: Si se debe aplicar efecto hover
            **kwargs: Argumentos adicionales
            
        Returns:
            El botón creado
        """
        # Determinar colores según el tipo de estilo
        if style_type == 'primary':
            bg_color = self.colors['primary']
            fg_color = self.colors['text_on_primary']
            hover_bg = self.colors['primary_dark']
        elif style_type == 'secondary':
            bg_color = self.colors['background']
            fg_color = self.colors['text']
            hover_bg = self.colors['hover']
        elif style_type == 'outline':
            bg_color = self.colors['background']
            fg_color = self.colors['primary']
            hover_bg = self.colors['hover']
        elif style_type == 'success':
            bg_color = self.colors['success']
            fg_color = self.colors['text_on_primary']
            hover_bg = '#27AE60'  # Verde oscuro
        elif style_type == 'warning':
            bg_color = self.colors['warning']
            fg_color = self.colors['text']
            hover_bg = '#F39C12'  # Amarillo oscuro
        elif style_type == 'error':
            bg_color = self.colors['error']
            fg_color = self.colors['text_on_primary']
            hover_bg = '#C0392B'  # Rojo oscuro
        elif style_type == 'info':
            bg_color = self.colors['info']
            fg_color = self.colors['text_on_primary']
            hover_bg = '#16A085'  # Turquesa oscuro
        else:
            bg_color = self.colors['background']
            fg_color = self.colors['text']
            hover_bg = self.colors['hover']
        
        # Crear frame contenedor para el botón
        button_frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Crear canvas para dibujar el fondo redondeado
        canvas = tk.Canvas(
            button_frame,
            bg=self.colors['background'],
            highlightthickness=0,
            **kwargs
        )
        canvas.pack(fill='both', expand=True)
        
        # Determinar dimensiones
        if width and height:
            canvas.configure(width=width, height=height)
        else:
            # Dimensiones predeterminadas
            canvas.configure(width=150, height=40)
        
        # Crear el botón con esquinas redondeadas
        def draw_rounded_button(color):
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # Crear imagen con esquinas redondeadas
            image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Dibujar rectángulo redondeado
            draw.rounded_rectangle(
                [(0, 0), (width, height)],
                radius=corner_radius,
                fill=color
            )
            
            # Si es un botón outline, dibujar borde
            if style_type == 'outline':
                draw.rounded_rectangle(
                    [(1, 1), (width-1, height-1)],
                    radius=corner_radius-1,
                    outline=self.colors['primary'],
                    width=2
                )
            
            return ImageTk.PhotoImage(image)
        
        # Función para actualizar el botón cuando cambia de tamaño
        def update_button(event=None):
            nonlocal button_image, hover_image
            button_image = draw_rounded_button(bg_color)
            hover_image = draw_rounded_button(hover_bg)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor='nw', image=button_image, tags="background")
            
            # Centrar el texto y el icono
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # Si hay icono, ajustar posición
            if icon:
                try:
                    icon_img = Image.open(icon)
                    icon_img = icon_img.resize((20, 20), Image.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_img)
                    canvas.icon_image = icon_photo  # Mantener referencia
                    
                    # Calcular posiciones
                    if text:
                        # Icono + texto
                        icon_x = width // 2 - 15 - len(text) * 3
                        text_x = width // 2 + 10
                        canvas.create_image(icon_x, height // 2, image=icon_photo, tags="icon")
                        canvas.create_text(text_x, height // 2, text=text, fill=fg_color, 
                                          font=self.fonts['button'], tags="text", anchor='w')
                    else:
                        # Solo icono
                        canvas.create_image(width // 2, height // 2, image=icon_photo, tags="icon")
                except Exception as e:
                    # Si hay error con el icono, mostrar solo texto
                    canvas.create_text(width // 2, height // 2, text=text, fill=fg_color, 
                                      font=self.fonts['button'], tags="text")
            else:
                # Solo texto
                canvas.create_text(width // 2, height // 2, text=text, fill=fg_color, 
                                  font=self.fonts['button'], tags="text")
        
        # Imágenes para estados normal y hover
        button_image = None
        hover_image = None
        
        # Vincular eventos
        canvas.bind("<Configure>", update_button)
        
        if hover_effect:
            def on_enter(event):
                canvas.delete("background")
                canvas.create_image(0, 0, anchor='nw', image=hover_image, tags="background")
                canvas.lift("icon")
                canvas.lift("text")
            
            def on_leave(event):
                canvas.delete("background")
                canvas.create_image(0, 0, anchor='nw', image=button_image, tags="background")
                canvas.lift("icon")
                canvas.lift("text")
            
            canvas.bind("<Enter>", on_enter)
            canvas.bind("<Leave>", on_leave)
        
        # Vincular clic
        if command:
            canvas.bind("<Button-1>", lambda event: command())
            canvas.bind("<ButtonRelease-1>", lambda event: on_leave(event))
        
        # Configurar cursor
        canvas.configure(cursor="hand2")
        
        return button_frame
    
    def create_elegant_label(self, parent, text, font_style='body1', color=None, 
                            padding=(0, 0), height=30, **kwargs):
        """
        Crea una etiqueta elegante con opciones de estilo avanzadas.
        
        Args:
            parent: Widget padre
            text: Texto de la etiqueta
            font_style: Estilo de fuente ('h1', 'body1', etc.)
            color: Color del texto (opcional)
            padding: Padding (x, y)
            height: Altura de la etiqueta
            **kwargs: Argumentos adicionales
            
        Returns:
            La etiqueta creada
        """
        # Crear frame contenedor
        label_frame = ttk.Frame(parent, style='TFrame')
        
        # Determinar color del texto
        if not color:
            color = self.colors['text']
        
        # Crear canvas para dibujar
        canvas = tk.Canvas(
            label_frame,
            bg=self.colors['background'],
            highlightthickness=0,
            height=height,
            **kwargs
        )
        canvas.pack(fill='both', expand=True)
        
        # Función para actualizar la etiqueta
        def update_label(event=None):
            canvas.delete("all")
            
            # Obtener dimensiones
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # Aplicar padding
            pad_x, pad_y = padding
            
            # Crear texto con tipografía elegante
            canvas.create_text(
                pad_x, height // 2,
                text=text,
                fill=color,
                font=self.fonts[font_style],
                anchor='w'
            )
        
        # Vincular eventos
        canvas.bind("<Configure>", update_label)
        
        return label_frame
    
    def create_status_indicator(self, parent, status, size=15, with_text=True, **kwargs):
        """
        Crea un indicador de estado elegante.
        
        Args:
            parent: Widget padre
            status: Estado ('pending', 'success', 'error', 'info')
            size: Tamaño del indicador
            with_text: Si se debe mostrar texto
            **kwargs: Argumentos adicionales
            
        Returns:
            El frame con el indicador
        """
        # Crear frame contenedor
        indicator_frame = ttk.Frame(parent, style='TFrame')
        
        # Determinar colores según el estado
        if status.lower() == 'pending' or status.lower() == 'pendiente':
            color = self.colors['warning']
            text = "Pendiente"
        elif status.lower() == 'success' or status.lower() == 'entregado':
            color = self.colors['success']
            text = "Completado"
        elif status.lower() == 'error' or status.lower() == 'cancelado':
            color = self.colors['error']
            text = "Cancelado"
        else:
            color = self.colors['info']
            text = status.capitalize()
        
        # Crear canvas para dibujar
        canvas = tk.Canvas(
            indicator_frame,
            bg=self.colors['background'],
            highlightthickness=0,
            height=size + 10,
            **kwargs
        )
        canvas.pack(fill='both', expand=True)
        
        # Función para dibujar el indicador
        def draw_indicator():
            canvas.delete("all")
            
            # Dibujar círculo
            canvas.create_oval(
                5, 5, 5 + size, 5 + size,
                fill=color, outline="",
                tags="indicator"
            )
            
            # Si se debe mostrar texto
            if with_text:
                canvas.create_text(
                    5 + size + 10, 5 + size // 2,
                    text=text,
                    fill=self.colors['text'],
                    font=self.fonts['caption'],
                    anchor='w',
                    tags="text"
                )
        
        # Dibujar inicialmente
        draw_indicator()
        
        return indicator_frame


class DemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Demostración de Widgets Elegantes")
        
        # Inicializar widgets elegantes
        self.elegant_widgets = ElegantWidgets(root)
        
        # Configurar la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        # Configurar el fondo de la ventana
        self.root.configure(bg=self.elegant_widgets.colors['background'])
        
        # Frame principal
        main_frame = ttk.Frame(self.root, style='TFrame', padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Demostración de Widgets Elegantes",
            font=self.elegant_widgets.fonts['h1'],
            foreground=self.elegant_widgets.colors['primary'],
            background=self.elegant_widgets.colors['background']
        )
        title_label.pack(pady=(0, 20))
        
        # Contenedor para los componentes
        components_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=20)
        components_frame.pack(fill='both', expand=True)
        
        # Sección de etiquetas elegantes
        self.create_labels_section(components_frame)
        
        # Separador
        ttk.Separator(components_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Sección de botones elegantes
        self.create_buttons_section(components_frame)
        
        # Separador
        ttk.Separator(components_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Sección de indicadores de estado
        self.create_status_indicators_section(components_frame)
    
    def create_labels_section(self, parent):
        # Título de sección
        ttk.Label(
            parent,
            text="Etiquetas Elegantes",
            font=self.elegant_widgets.fonts['h3'],
            foreground=self.elegant_widgets.colors['primary'],
            background=self.elegant_widgets.colors['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        # Contenedor para etiquetas
        labels_frame = ttk.Frame(parent, style='TFrame')
        labels_frame.pack(fill='x', pady=10)
        
        # Etiqueta con tipografía grande
        h1_label = self.elegant_widgets.create_elegant_label(
            labels_frame,
            text="Etiqueta con tipografía grande (h1)",
            font_style='h1',
            color=self.elegant_widgets.colors['text'],
            padding=(10, 5),
            height=50
        )
        h1_label.pack(fill='x', pady=5)
        
        # Etiqueta con tipografía mediana
        h3_label = self.elegant_widgets.create_elegant_label(
            labels_frame,
            text="Etiqueta con tipografía mediana (h3)",
            font_style='h3',
            color=self.elegant_widgets.colors['primary'],
            padding=(10, 5),
            height=40
        )
        h3_label.pack(fill='x', pady=5)
        
        # Etiqueta con tipografía pequeña
        body_label = self.elegant_widgets.create_elegant_label(
            labels_frame,
            text="Etiqueta con tipografía pequeña (body1)",
            font_style='body1',
            color=self.elegant_widgets.colors['text_secondary'],
            padding=(10, 5),
            height=30
        )
        body_label.pack(fill='x', pady=5)
    
    def create_buttons_section(self, parent):
        # Título de sección
        ttk.Label(
            parent,
            text="Botones Elegantes",
            font=self.elegant_widgets.fonts['h3'],
            foreground=self.elegant_widgets.colors['primary'],
            background=self.elegant_widgets.colors['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        # Contenedor para botones
        buttons_frame = ttk.Frame(parent, style='TFrame')
        buttons_frame.pack(fill='x', pady=10)
        
        # Fila 1 de botones
        row1 = ttk.Frame(buttons_frame, style='TFrame')
        row1.pack(fill='x', pady=5)
        
        # Botón primario
        primary_btn = self.elegant_widgets.create_elegant_button(
            row1,
            text="Botón Primario",
            command=lambda: self.show_message("Botón Primario"),
            style_type='primary',
            width=180,
            height=40
        )
        primary_btn.pack(side='left', padx=5)
        
        # Botón secundario
        secondary_btn = self.elegant_widgets.create_elegant_button(
            row1,
            text="Botón Secundario",
            command=lambda: self.show_message("Botón Secundario"),
            style_type='secondary',
            width=180,
            height=40
        )
        secondary_btn.pack(side='left', padx=5)
        
        # Botón outline
        outline_btn = self.elegant_widgets.create_elegant_button(
            row1,
            text="Botón Outline",
            command=lambda: self.show_message("Botón Outline"),
            style_type='outline',
            width=180,
            height=40
        )
        outline_btn.pack(side='left', padx=5)
        
        # Fila 2 de botones
        row2 = ttk.Frame(buttons_frame, style='TFrame')
        row2.pack(fill='x', pady=10)
        
        # Botón de éxito
        success_btn = self.elegant_widgets.create_elegant_button(
            row2,
            text="Botón Éxito",
            command=lambda: self.show_message("Botón Éxito"),
            style_type='success',
            width=180,
            height=40
        )
        success_btn.pack(side='left', padx=5)
        
        # Botón de advertencia
        warning_btn = self.elegant_widgets.create_elegant_button(
            row2,
            text="Botón Advertencia",
            command=lambda: self.show_message("Botón Advertencia"),
            style_type='warning',
            width=180,
            height=40
        )
        warning_btn.pack(side='left', padx=5)
        
        # Botón de error
        error_btn = self.elegant_widgets.create_elegant_button(
            row2,
            text="Botón Error",
            command=lambda: self.show_message("Botón Error"),
            style_type='error',
            width=180,
            height=40
        )
        error_btn.pack(side='left', padx=5)
    
    def create_status_indicators_section(self, parent):
        # Título de sección
        ttk.Label(
            parent,
            text="Indicadores de Estado",
            font=self.elegant_widgets.fonts['h3'],
            foreground=self.elegant_widgets.colors['primary'],
            background=self.elegant_widgets.colors['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        # Contenedor para indicadores
        indicators_frame = ttk.Frame(parent, style='TFrame')
        indicators_frame.pack(fill='x', pady=10)
        
        # Indicador pendiente
        pending_indicator = self.elegant_widgets.create_status_indicator(
            indicators_frame,
            status="pendiente",
            size=20,
            with_text=True,
            width=200
        )
        pending_indicator.pack(fill='x', pady=5)
        
        # Indicador completado
        success_indicator = self.elegant_widgets.create_status_indicator(
            indicators_frame,
            status="entregado",
            size=20,
            with_text=True,
            width=200
        )
        success_indicator.pack(fill='x', pady=5)
        
        # Indicador cancelado
        error_indicator = self.elegant_widgets.create_status_indicator(
            indicators_frame,
            status="cancelado",
            size=20,
            with_text=True,
            width=200
        )
        error_indicator.pack(fill='x', pady=5)
    
    def show_message(self, message):
        """Muestra un mensaje cuando se hace clic en un botón."""
        messagebox.showinfo("Clic en botón", f"Has hecho clic en: {message}")


def main():
    root = tk.Tk()
    root.geometry("800x700")
    app = DemoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 