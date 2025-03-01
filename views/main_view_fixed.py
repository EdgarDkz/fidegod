import tkinter as tk
from tkinter import ttk, messagebox
from views.personas_view import PersonasView
from views.inventario_view import InventarioView
from views.transacciones_view import TransaccionesView
from views.splash_screen import SplashScreen
from controllers.inventario_controller import InventarioController
import webbrowser
from datetime import datetime
import os
from PIL import Image, ImageTk

class MainView:
    """
    Clase principal que define la vista principal de la aplicación FIDEGOD.
    Gestiona la interfaz de usuario, la navegación entre módulos, temas, notificaciones,
    y la interacción del usuario.
    """
    def __init__(self, parent, theme_manager=None):
        """
        Inicializa la vista principal.

        Args:
            parent: El widget padre (normalmente la ventana principal Tk).
            theme_manager: Gestor de temas para la aplicación.
        """
        self.parent = parent
        self.theme_manager = theme_manager

        # Inicializar componentes y estilos
        self.style = ttk.Style()
        self.controller = InventarioController()
        self.notifications = []  # Lista para almacenar notificaciones

        # Usar colores del theme_manager si está disponible
        if theme_manager:
            self.colors = theme_manager.get_color_palette()
        else:
            # Paleta de colores base - Tema Pastel Suave (Naranja)
            self.colors = {
                'primary': '#f5a05f',           # Naranja pastel principal
                'primary_light': '#ffbe8b',     # Naranja pastel claro
                'primary_dark': '#e58a42',      # Naranja pastel oscuro
                'secondary': '#ffd4b8',         # Melocotón claro
                'background': '#fff5ed',        # Crema muy claro
                'surface': '#ffffff',           # Blanco puro
                'text': '#5d534c',              # Marrón grisáceo oscuro
                'text_secondary': '#8b8178',    # Marrón grisáceo medio
                'divider': '#f0e5de',           # Beige clarito
                'toolbar': '#fff9f4',           # Crema clarito
                'status_bar': '#fff9f4',        # Crema clarito
                'card': '#ffffff',              # Blanco
                'hover': '#ffe8d3',             # Melocotón muy claro
                'selected': '#ffd7b5',          # Melocotón claro seleccionado
                'disabled': '#e6e6e6',          # Gris claro
                'input': '#ffffff',             # Blanco
            }

        # Configurar la interfaz de usuario
        self._setup_ui()
        
        # Configurar eventos
        self._setup_events()
        
        # Inicializar módulos
        self._initialize_modules()
        
        # Mostrar el módulo inicial (Personas)
        self.show_module('personas')
        
        # Verificar actualizaciones de inventario
        self.check_inventory_updates()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario principal."""
        # Configurar el estilo visual
        self._setup_styles()
        
        # Frame principal que contiene toda la interfaz
        self.main_frame = ttk.Frame(self.parent, style='App.TFrame')
        self.main_frame.pack(fill='both', expand=True)
        
        # Configurar la barra superior (toolbar)
        self._setup_toolbar()
        
        # Configurar el panel de navegación lateral
        self._setup_sidebar()
        
        # Configurar el contenedor principal para los módulos
        self.content_frame = ttk.Frame(self.main_frame, style='Content.TFrame')
        self.content_frame.pack(side='left', fill='both', expand=True)
        
        # Configurar la barra de estado
        self._setup_statusbar()
    
    def _setup_styles(self):
        """Configura los estilos visuales para la aplicación."""
        # Usar los estilos del theme_manager si está disponible
        if hasattr(self, 'theme_manager') and self.theme_manager:
            # Los estilos ya están configurados por el theme_manager
            return
            
        # Configuración manual de estilos si no hay theme_manager
        style = self.style
        colors = self.colors
        
        # Estilos para frames
        style.configure('App.TFrame', background=colors['background'])
        style.configure('Toolbar.TFrame', background=colors['toolbar'])
        style.configure('Sidebar.TFrame', background=colors['surface'])
        style.configure('Content.TFrame', background=colors['background'])
        style.configure('Statusbar.TFrame', background=colors['status_bar'])
        
        # Estilos para etiquetas
        style.configure('Title.TLabel', 
                      font=('Segoe UI', 16, 'bold'),
                      background=colors['toolbar'],
                      foreground=colors['primary'])
        
        style.configure('Subtitle.TLabel', 
                      font=('Segoe UI', 12),
                      background=colors['toolbar'],
                      foreground=colors['text_secondary'])
        
        # Estilos para botones de navegación
        style.configure('Nav.TButton', 
                      font=('Segoe UI', 12),
                      background=colors['surface'],
                      foreground=colors['text'],
                      borderwidth=0,
                      focuscolor=colors['primary'],
                      padding=10)
        
        style.map('Nav.TButton',
                background=[('active', colors['hover']),
                           ('selected', colors['selected'])],
                foreground=[('selected', colors['primary'])])
        
        # Estilos para la barra de estado
        style.configure('Status.TLabel',
                      font=('Segoe UI', 10),
                      background=colors['status_bar'],
                      foreground=colors['text_secondary'])
    
    def _setup_toolbar(self):
        """Configura la barra de herramientas superior."""
        # Frame para la barra de herramientas
        toolbar = ttk.Frame(self.main_frame, style='Toolbar.TFrame')
        toolbar.pack(side='top', fill='x', padx=0, pady=0)
        
        # Logo y título de la aplicación
        logo_frame = ttk.Frame(toolbar, style='Toolbar.TFrame')
        logo_frame.pack(side='left', padx=20, pady=10)
        
        # Cargar el logo si existe
        try:
            logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((40, 40), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(logo_frame, image=logo_photo, style='Toolbar.TLabel')
                logo_label.image = logo_photo  # Mantener referencia
                logo_label.pack(side='left', padx=(0, 10))
        except Exception as e:
            print(f"Error al cargar el logo: {e}")
        
        # Título y subtítulo
        title_frame = ttk.Frame(logo_frame, style='Toolbar.TFrame')
        title_frame.pack(side='left')
        
        ttk.Label(title_frame, text="FIDEGOD", style='Title.TLabel').pack(anchor='w')
        ttk.Label(title_frame, text="Sistema de Gestión", style='Subtitle.TLabel').pack(anchor='w')
        
        # Botones de la barra de herramientas (derecha)
        tools_frame = ttk.Frame(toolbar, style='Toolbar.TFrame')
        tools_frame.pack(side='right', padx=20, pady=10)
        
        # Botón de notificaciones
        self.notification_button = ttk.Button(
            tools_frame,
            text="🔔",
            style='Toolbar.TButton',
            command=self.show_notifications
        )
        self.notification_button.pack(side='left', padx=5)
        
        # Botón de ayuda
        help_button = ttk.Button(
            tools_frame,
            text="❓",
            style='Toolbar.TButton',
            command=self.show_help
        )
        help_button.pack(side='left', padx=5)
        
        # Botón de configuración
        settings_button = ttk.Button(
            tools_frame,
            text="⚙️",
            style='Toolbar.TButton',
            command=self.show_settings
        )
        settings_button.pack(side='left', padx=5)
    
    def _setup_sidebar(self):
        """Configura el panel de navegación lateral."""
        # Frame para la barra lateral
        sidebar = ttk.Frame(self.main_frame, style='Sidebar.TFrame', width=200)
        sidebar.pack(side='left', fill='y', padx=0, pady=0)
        sidebar.pack_propagate(False)  # Mantener ancho fijo
        
        # Título del menú
        ttk.Label(
            sidebar,
            text="Menú Principal",
            style='SidebarTitle.TLabel',
            padding=(20, 20, 20, 10)
        ).pack(fill='x')
        
        # Separador
        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', padx=20)
        
        # Botones de navegación
        nav_buttons = [
            ("👥 Personas", lambda: self.show_module('personas')),
            ("📦 Inventario", lambda: self.show_module('inventario')),
            ("💰 Transacciones", lambda: self.show_module('transacciones')),
            ("📊 Reportes", lambda: self.show_module('reportes')),
            ("⚙️ Configuración", self.show_settings)
        ]
        
        # Crear los botones de navegación
        self.nav_buttons = {}
        for i, (text, command) in enumerate(nav_buttons):
            btn = ttk.Button(
                sidebar,
                text=text,
                style='Nav.TButton',
                command=command
            )
            btn.pack(fill='x', padx=10, pady=2)
            
            # Guardar referencia al botón
            module_name = text.split(' ')[1].lower()
            self.nav_buttons[module_name] = btn
    
    def _setup_statusbar(self):
        """Configura la barra de estado inferior."""
        # Frame para la barra de estado
        statusbar = ttk.Frame(self.main_frame, style='Statusbar.TFrame')
        statusbar.pack(side='bottom', fill='x', padx=0, pady=0)
        
        # Información de la versión
        version_label = ttk.Label(
            statusbar,
            text="Versión 1.0.0",
            style='Status.TLabel'
        )
        version_label.pack(side='left', padx=20, pady=5)
        
        # Fecha y hora actual
        self.datetime_label = ttk.Label(
            statusbar,
            text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            style='Status.TLabel'
        )
        self.datetime_label.pack(side='right', padx=20, pady=5)
        
        # Actualizar la hora cada segundo
        self._update_datetime()
    
    def _update_datetime(self):
        """Actualiza la fecha y hora en la barra de estado."""
        self.datetime_label.config(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.parent.after(1000, self._update_datetime)
    
    def _setup_events(self):
        """Configura los eventos de la aplicación."""
        # Vincular evento de cierre de la ventana
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Vincular teclas de método abreviado
        self.parent.bind('<Control-1>', lambda e: self.show_module('personas'))
        self.parent.bind('<Control-2>', lambda e: self.show_module('inventario'))
        self.parent.bind('<Control-3>', lambda e: self.show_module('transacciones'))
        self.parent.bind('<Control-4>', lambda e: self.show_module('reportes'))
        self.parent.bind('<F1>', lambda e: self.show_help())
    
    def _initialize_modules(self):
        """Inicializa los módulos de la aplicación."""
        # Diccionario para almacenar las instancias de los módulos
        self.modules = {}
        
        # Inicializar el módulo de Personas
        self.modules['personas'] = PersonasView(self.content_frame)
        
        # Inicializar el módulo de Inventario
        self.modules['inventario'] = InventarioView(self.content_frame)
        
        # Inicializar el módulo de Transacciones
        self.modules['transacciones'] = TransaccionesView(self.content_frame)
        
        # Ocultar todos los módulos inicialmente
        for module in self.modules.values():
            module.pack_forget()
    
    def show_module(self, module_name):
        """
        Muestra el módulo especificado y oculta los demás.
        
        Args:
            module_name: Nombre del módulo a mostrar ('personas', 'inventario', 'transacciones').
        """
        # Verificar si el módulo existe
        if module_name not in self.modules:
            messagebox.showerror("Error", f"El módulo '{module_name}' no está disponible.")
            return
        
        # Ocultar todos los módulos
        for name, module in self.modules.items():
            module.pack_forget()
            
            # Desactivar el botón de navegación correspondiente
            if name in self.nav_buttons:
                self.nav_buttons[name].state(['!selected'])
        
        # Mostrar el módulo seleccionado
        self.modules[module_name].pack(fill='both', expand=True)
        
        # Activar el botón de navegación correspondiente
        if module_name in self.nav_buttons:
            self.nav_buttons[module_name].state(['selected'])
    
    def show_notifications(self):
        """Muestra el panel de notificaciones."""
        # Si no hay notificaciones, mostrar mensaje
        if not self.notifications:
            messagebox.showinfo("Notificaciones", "No hay notificaciones pendientes.")
            return
        
        # Crear ventana de notificaciones
        notification_window = tk.Toplevel(self.parent)
        notification_window.title("Notificaciones")
        notification_window.geometry("400x300")
        notification_window.transient(self.parent)
        notification_window.grab_set()
        
        # Configurar estilos
        notification_window.configure(bg=self.colors['surface'])
        
        # Título
        ttk.Label(
            notification_window,
            text="Notificaciones",
            font=('Segoe UI', 14, 'bold'),
            background=self.colors['surface'],
            foreground=self.colors['primary']
        ).pack(pady=10)
        
        # Lista de notificaciones
        notification_frame = ttk.Frame(notification_window, style='Card.TFrame')
        notification_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Mostrar cada notificación
        for i, notification in enumerate(self.notifications):
            notification_item = ttk.Frame(notification_frame, style='Card.TFrame')
            notification_item.pack(fill='x', padx=5, pady=5)
            
            ttk.Label(
                notification_item,
                text=notification['title'],
                font=('Segoe UI', 12, 'bold'),
                background=self.colors['surface'],
                foreground=self.colors['text']
            ).pack(anchor='w', padx=10, pady=(10, 5))
            
            ttk.Label(
                notification_item,
                text=notification['message'],
                background=self.colors['surface'],
                foreground=self.colors['text_secondary'],
                wraplength=350
            ).pack(anchor='w', padx=10, pady=(0, 10))
            
            # Separador entre notificaciones
            if i < len(self.notifications) - 1:
                ttk.Separator(notification_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # Botón para cerrar
        ttk.Button(
            notification_window,
            text="Cerrar",
            command=notification_window.destroy
        ).pack(pady=10)
    
    def show_help(self):
        """Muestra la ayuda de la aplicación."""
        # URL de la documentación o ayuda
        help_url = "https://github.com/tu-usuario/fidegod/wiki"
        
        # Intentar abrir el navegador
        try:
            webbrowser.open(help_url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ayuda: {str(e)}")
    
    def show_settings(self):
        """Muestra la configuración de la aplicación."""
        # Crear ventana de configuración
        settings_window = tk.Toplevel(self.parent)
        settings_window.title("Configuración")
        settings_window.geometry("500x400")
        settings_window.transient(self.parent)
        settings_window.grab_set()
        
        # Configurar estilos
        settings_window.configure(bg=self.colors['surface'])
        
        # Título
        ttk.Label(
            settings_window,
            text="Configuración",
            font=('Segoe UI', 16, 'bold'),
            background=self.colors['surface'],
            foreground=self.colors['primary']
        ).pack(pady=10)
        
        # Notebook para las pestañas de configuración
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña de configuración general
        general_tab = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(general_tab, text="General")
        
        # Pestaña de configuración de apariencia
        appearance_tab = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(appearance_tab, text="Apariencia")
        
        # Pestaña de configuración de base de datos
        database_tab = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(database_tab, text="Base de Datos")
        
        # Configuración general
        ttk.Label(
            general_tab,
            text="Configuración General",
            font=('Segoe UI', 14, 'bold'),
            background=self.colors['surface'],
            foreground=self.colors['text']
        ).pack(anchor='w', padx=10, pady=10)
        
        # Opciones de configuración general
        options_frame = ttk.Frame(general_tab, style='Card.TFrame')
        options_frame.pack(fill='x', padx=10, pady=5)
        
        # Opción: Iniciar automáticamente
        autostart_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Iniciar automáticamente con Windows",
            variable=autostart_var,
            style='TCheckbutton'
        ).pack(anchor='w', padx=10, pady=5)
        
        # Opción: Mostrar notificaciones
        notifications_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Mostrar notificaciones",
            variable=notifications_var,
            style='TCheckbutton'
        ).pack(anchor='w', padx=10, pady=5)
        
        # Opción: Comprobar actualizaciones
        updates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Comprobar actualizaciones automáticamente",
            variable=updates_var,
            style='TCheckbutton'
        ).pack(anchor='w', padx=10, pady=5)
        
        # Configuración de apariencia
        ttk.Label(
            appearance_tab,
            text="Configuración de Apariencia",
            font=('Segoe UI', 14, 'bold'),
            background=self.colors['surface'],
            foreground=self.colors['text']
        ).pack(anchor='w', padx=10, pady=10)
        
        # Opciones de configuración de apariencia
        appearance_frame = ttk.Frame(appearance_tab, style='Card.TFrame')
        appearance_frame.pack(fill='x', padx=10, pady=5)
        
        # Opción: Tema
        ttk.Label(
            appearance_frame,
            text="Tema:",
            background=self.colors['surface'],
            foreground=self.colors['text']
        ).pack(anchor='w', padx=10, pady=5)
        
        theme_var = tk.StringVar(value="Claro")
        themes = ["Claro", "Oscuro", "Sistema"]
        theme_combo = ttk.Combobox(
            appearance_frame,
            textvariable=theme_var,
            values=themes,
            state='readonly'
        )
        theme_combo.pack(anchor='w', padx=10, pady=5)
        
        # Opción: Tamaño de fuente
        ttk.Label(
            appearance_frame,
            text="Tamaño de fuente:",
            background=self.colors['surface'],
            foreground=self.colors['text']
        ).pack(anchor='w', padx=10, pady=5)
        
        font_size_var = tk.StringVar(value="Normal")
        font_sizes = ["Pequeño", "Normal", "Grande", "Muy grande"]
        font_size_combo = ttk.Combobox(
            appearance_frame,
            textvariable=font_size_var,
            values=font_sizes,
            state='readonly'
        )
        font_size_combo.pack(anchor='w', padx=10, pady=5)
        
        # Configuración de base de datos
        ttk.Label(
            database_tab,
            text="Configuración de Base de Datos",
            font=('Segoe UI', 14, 'bold'),
            background=self.colors['surface'],
            foreground=self.colors['text']
        ).pack(anchor='w', padx=10, pady=10)
        
        # Opciones de configuración de base de datos
        database_frame = ttk.Frame(database_tab, style='Card.TFrame')
        database_frame.pack(fill='x', padx=10, pady=5)
        
        # Opción: Tipo de base de datos
        ttk.Label(
            database_frame,
            text="Tipo de base de datos:",
            background=self.colors['surface'],
            foreground=self.colors['text']
        ).pack(anchor='w', padx=10, pady=5)
        
        db_type_var = tk.StringVar(value="SQLite")
        db_types = ["SQLite", "MySQL", "PostgreSQL"]
        db_type_combo = ttk.Combobox(
            database_frame,
            textvariable=db_type_var,
            values=db_types,
            state='readonly'
        )
        db_type_combo.pack(anchor='w', padx=10, pady=5)
        
        # Opción: Ruta de la base de datos
        ttk.Label(
            database_frame,
            text="Ruta de la base de datos:",
            background=self.colors['surface'],
            foreground=self.colors['text']
        ).pack(anchor='w', padx=10, pady=5)
        
        db_path_frame = ttk.Frame(database_frame, style='Card.TFrame')
        db_path_frame.pack(fill='x', padx=10, pady=5)
        
        db_path_var = tk.StringVar(value="database.db")
        db_path_entry = ttk.Entry(
            db_path_frame,
            textvariable=db_path_var,
            width=30
        )
        db_path_entry.pack(side='left', fill='x', expand=True)
        
        db_path_button = ttk.Button(
            db_path_frame,
            text="Examinar...",
            command=lambda: self._browse_db_path(db_path_var)
        )
        db_path_button.pack(side='left', padx=5)
        
        # Botones de acción
        button_frame = ttk.Frame(settings_window, style='Card.TFrame')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=settings_window.destroy
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="Guardar",
            command=lambda: self._save_settings(
                autostart_var.get(),
                notifications_var.get(),
                updates_var.get(),
                theme_var.get(),
                font_size_var.get(),
                db_type_var.get(),
                db_path_var.get(),
                settings_window
            )
        ).pack(side='right', padx=5)
    
    def _browse_db_path(self, path_var):
        """
        Abre un diálogo para seleccionar la ruta de la base de datos.
        
        Args:
            path_var: Variable StringVar para almacenar la ruta seleccionada.
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            path_var.set(file_path)
    
    def _save_settings(self, autostart, notifications, updates, theme, font_size, db_type, db_path, window):
        """
        Guarda la configuración de la aplicación.
        
        Args:
            autostart: Booleano para iniciar automáticamente con Windows.
            notifications: Booleano para mostrar notificaciones.
            updates: Booleano para comprobar actualizaciones automáticamente.
            theme: Tema seleccionado.
            font_size: Tamaño de fuente seleccionado.
            db_type: Tipo de base de datos seleccionado.
            db_path: Ruta de la base de datos.
            window: Ventana de configuración a cerrar.
        """
        # Aquí se implementaría la lógica para guardar la configuración
        # Por ahora, solo mostramos un mensaje
        messagebox.showinfo("Configuración", "Configuración guardada correctamente.")
        window.destroy()
    
    def check_inventory_updates(self):
        """Comprueba si hay actualizaciones en el inventario."""
        # Obtener productos con stock bajo
        low_stock_products = self.controller.get_low_stock_products()
        
        # Si hay productos con stock bajo, añadir notificación
        if low_stock_products:
            product_names = ", ".join([p[1] for p in low_stock_products[:3]])
            if len(low_stock_products) > 3:
                product_names += f" y {len(low_stock_products) - 3} más"
            
            self.add_notification(
                "Stock Bajo",
                f"Los siguientes productos tienen stock bajo: {product_names}."
            )
    
    def add_notification(self, title, message):
        """
        Añade una notificación a la lista de notificaciones.
        
        Args:
            title: Título de la notificación.
            message: Mensaje de la notificación.
        """
        self.notifications.append({
            'title': title,
            'message': message,
            'timestamp': datetime.now()
        })
        
        # Actualizar el botón de notificaciones
        if self.notifications:
            self.notification_button.configure(text=f"🔔 ({len(self.notifications)})")
    
    def on_close(self):
        """Maneja el evento de cierre de la aplicación."""
        # Preguntar si se desea cerrar la aplicación
        if messagebox.askyesno("Cerrar", "¿Está seguro de que desea cerrar la aplicación?"):
            # Cerrar la aplicación
            self.parent.destroy() 