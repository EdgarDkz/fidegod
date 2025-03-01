import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, initialize_callback, theme_manager=None):
        super().__init__(parent)
        self.parent = parent
        self.initialize_callback = initialize_callback
        self.theme_manager = theme_manager
        
        # Configuración de la ventana
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        
        # Dimensiones ajustadas para layout horizontal
        width = 800
        height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Usar colores del theme_manager si está disponible
        if theme_manager:
            colors = theme_manager.get_color_palette()
            self.colors = {
                'background': colors['background'],
                'orange': colors['primary'],
                'text': colors['text'],
                'progress_bg': colors['divider'],
                'progress_fill': colors['primary_light']
            }
        else:
            # Colores oficiales por defecto
            self.colors = {
                'background': '#FFFFFF',
                'orange': '#FF6B00',
                'text': '#333333',
                'progress_bg': '#E0E0E0',
                'progress_fill': '#FF9D5C'
            }
        
        # Configurar estilos
        self.setup_styles()
        
        # Frame principal
        self.configure(bg=self.colors['background'])
        
        # Crear contenido
        self.create_content()
        
        # Iniciar la aplicación después de mostrar la pantalla de inicio
        self.after(500, self.start_initialization)
    
    def setup_styles(self):
        """Configura los estilos para la pantalla de inicio."""
        style = ttk.Style()
        
        # Estilo para la barra de progreso
        style.configure('Splash.Horizontal.TProgressbar',
                      background=self.colors['progress_fill'],
                      troughcolor=self.colors['progress_bg'],
                      borderwidth=0,
                      thickness=10)
    
    def create_content(self):
        """Crea el contenido de la pantalla de inicio."""
        # Frame principal con padding
        main_frame = tk.Frame(self, bg=self.colors['background'], padx=40, pady=40)
        main_frame.pack(fill='both', expand=True)
        
        # Dividir en dos columnas
        left_frame = tk.Frame(main_frame, bg=self.colors['background'])
        left_frame.pack(side='left', fill='both', expand=True)
        
        right_frame = tk.Frame(main_frame, bg=self.colors['background'])
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Logo en el lado izquierdo
        self.load_logo(left_frame)
        
        # Contenido en el lado derecho
        self.create_right_content(right_frame)
    
    def load_logo(self, parent):
        """Carga y muestra el logo de la aplicación."""
        try:
            # Buscar el logo en varias ubicaciones posibles
            logo_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'views', 'icons', 'fide.PNG'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'logo.png'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'views', 'icons', 'logo.png')
            ]
            
            logo_path = None
            for path in logo_paths:
                if os.path.exists(path):
                    logo_path = path
                    break
            
            if logo_path:
                # Cargar y redimensionar el logo
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((300, 300), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                # Mostrar el logo
                logo_label = tk.Label(parent, image=self.logo_photo, bg=self.colors['background'])
                logo_label.pack(pady=20)
            else:
                # Si no se encuentra el logo, mostrar un texto
                logo_label = tk.Label(parent, text="FIDEGOD", font=('Segoe UI', 48, 'bold'),
                                    fg=self.colors['orange'], bg=self.colors['background'])
                logo_label.pack(pady=20)
        except Exception as e:
            print(f"Error al cargar el logo: {e}")
            # Mostrar un texto en caso de error
            logo_label = tk.Label(parent, text="FIDEGOD", font=('Segoe UI', 48, 'bold'),
                                fg=self.colors['orange'], bg=self.colors['background'])
            logo_label.pack(pady=20)
    
    def create_right_content(self, parent):
        """Crea el contenido del lado derecho de la pantalla de inicio."""
        # Título
        title_label = tk.Label(parent, text="FIDEGOD", font=('Segoe UI', 36, 'bold'),
                             fg=self.colors['orange'], bg=self.colors['background'])
        title_label.pack(pady=(40, 10))
        
        # Subtítulo
        subtitle_label = tk.Label(parent, text="Sistema de Gestión Empresarial",
                                font=('Segoe UI', 16), fg=self.colors['text'],
                                bg=self.colors['background'])
        subtitle_label.pack(pady=(0, 40))
        
        # Mensaje de carga
        self.loading_message = tk.Label(parent, text="Iniciando...",
                                      font=('Segoe UI', 12), fg=self.colors['text'],
                                      bg=self.colors['background'])
        self.loading_message.pack(pady=(20, 10))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(parent, style='Splash.Horizontal.TProgressbar',
                                      length=300, mode='determinate')
        self.progress.pack(pady=10)
        
        # Versión
        version_label = tk.Label(parent, text="Versión 1.0.0",
                               font=('Segoe UI', 10), fg=self.colors['text_secondary'] if 'text_secondary' in self.colors else self.colors['text'],
                               bg=self.colors['background'])
        version_label.pack(pady=(40, 0))
    
    def start_initialization(self):
        """Inicia el proceso de inicialización de la aplicación."""
        # Establecer progreso inicial
        self.update_loading(0, "Iniciando aplicación...")
        
        # Iniciar la aplicación
        self.after(100, self.initialize_callback)
    
    def update_loading(self, progress=None, message=None):
        """
        Actualiza el progreso y el mensaje de carga.
        
        Args:
            progress: Valor del progreso (0-100)
            message: Mensaje a mostrar
        """
        if progress is not None:
            self.progress['value'] = progress
        
        if message is not None:
            self.loading_message.config(text=message)
        
        # Actualizar la interfaz
        self.update_idletasks()
        
        # Pequeña pausa para que se vea la animación
        time.sleep(0.05)
    
    def finish_loading(self):
        """Finaliza la carga y cierra la pantalla de inicio."""
        # Asegurar que la barra de progreso esté completa
        self.update_loading(100, "¡Listo!")
        
        # Pequeña pausa para mostrar el progreso completo
        self.after(500, self.destroy) 