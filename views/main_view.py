import tkinter as tk
from tkinter import ttk, messagebox, font
from views.personas_view import PersonasView
from views.inventario_view import InventarioView
from views.transacciones_view import TransaccionesView
from controllers.inventario_controller import InventarioController
from controllers.personas_controller import PersonasController
from controllers.transacciones_controller import TransaccionesController
import webbrowser
from datetime import datetime
import os
from PIL import Image, ImageTk
from utils.icon_manager import icon_manager

class MainView:
    """
    Clase principal que define la vista principal de la aplicación FIDEGOD.
    Gestiona la interfaz de usuario, la navegación entre módulos, temas, notificaciones,
    y la interacción del usuario.
    """
    def __init__(self, parent, theme_manager=None, elegant_styles=None):
        """
        Inicializa la vista principal.

        Args:
            parent: El widget padre (normalmente la ventana principal Tk).
            theme_manager: Gestor de temas para la aplicación.
            elegant_styles: Estilos elegantes para la aplicación.
        """
        self.parent = parent
        self.theme_manager = theme_manager
        self.elegant_styles = elegant_styles
        self.parent.title("FIDEGOD - Sistema de Gestión")
        self.parent.state('zoomed')  # Maximizar la ventana

        # Inicializar componentes y estilos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Inicializar controladores
        self.inventario_controller = InventarioController()
        self.personas_controller = PersonasController()
        self.transacciones_controller = TransaccionesController()
        
        # Usar colores del theme_manager si está disponible
        if theme_manager:
            self.colors = theme_manager.get_color_palette()
        else:
            # Paleta de colores base - Tema Profesional (Naranja)
            self.colors = {
                'primary': '#f5a05f',           # Naranja principal
                'primary_light': '#ffbe8b',     # Naranja claro
                'primary_dark': '#e58a42',      # Naranja oscuro
                'secondary': '#76849a',         # Gris medio
                'background': '#f8f9fa',        # Gris muy claro
                'surface': '#ffffff',           # Blanco
                'text': '#343a40',              # Gris oscuro
                'text_secondary': '#6c757d',    # Gris medio
                'divider': '#dee2e6',           # Gris claro
                'toolbar': '#f8f9fa',           # Gris muy claro
                'status_bar': '#f8f9fa',        # Gris muy claro
                'card': '#ffffff',              # Blanco
                'hover': '#f1f3f5',             # Gris claro hover
                'selected': '#e9ecef',          # Gris claro seleccionado
                'disabled': '#e9ecef',          # Gris claro
                'input': '#ffffff',             # Blanco
                'accent': '#20c997',            # Verde azulado
                'warning': '#ffc107',           # Amarillo
                'error': '#dc3545',             # Rojo
                'success': '#28a745',           # Verde
                'info': '#17a2b8',              # Azul claro
            }
        
        # Configurar estilos
        self.setup_styles()
        
        # Cargar iconos
        self.load_icons()
        
        # Configurar la interfaz de usuario
        self.setup_ui()
        
        # Inicializar notificaciones
        self.notifications = []
        
        # Actualizar la barra de estado con la fecha actual
        self.update_status_bar()

    def setup_styles(self):
        """Configura los estilos para la aplicación."""
        # Si hay estilos elegantes disponibles, usarlos
        if self.elegant_styles:
            # Los estilos ya están configurados en elegant_styles
            return
        
        # Configuración manual de estilos si no hay estilos elegantes
        self.style.configure('TFrame', background=self.colors['surface'])
        self.style.configure('TNotebook', background=self.colors['background'])
        self.style.configure('TNotebook.Tab', 
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           padding=[10, 5],
                           font=('Segoe UI', 10))
        
        self.style.map('TNotebook.Tab',
                     background=[('selected', self.colors['primary'])],
                     foreground=[('selected', self.colors['surface'])])
        
        self.style.configure('TLabel', 
                           background=self.colors['surface'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
                           
        self.style.configure('Toolbar.TFrame', 
                           background=self.colors['toolbar'],
                           relief='flat')
                           
        self.style.configure('StatusBar.TFrame', 
                           background=self.colors['status_bar'],
                           relief='sunken')
                           
        self.style.configure('StatusBar.TLabel', 
                           background=self.colors['status_bar'],
                           foreground=self.colors['text_secondary'],
                           font=('Segoe UI', 9))
                           
        self.style.configure('QuickAccess.TFrame', 
                           background=self.colors['primary_light'],
                           relief='flat')
                           
        self.style.configure('QuickAccess.TButton', 
                           background=self.colors['primary_light'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
                           
        self.style.map('QuickAccess.TButton',
                     background=[('active', self.colors['primary'])],
                     foreground=[('active', self.colors['surface'])])

    def load_icons(self):
        """Carga los iconos para la interfaz de usuario."""
        self.icons = {}
        icon_files = {
            'new': 'nuevo',
            'open': 'abrir',
            'save': 'guardar',
            'print': 'imprimir',
            'settings': 'configuracion',
            'help': 'ayuda',
            'exit': 'salir',
            'user': 'user',
            'inventory': 'inventario',
            'transaction': 'transaccion',
            'report': 'reporte',
            'search': 'buscar',
            'notification': 'notificacion',
            'home': 'home',
            'refresh': 'refresh',
            'export': 'exportar',
            'import': 'importar',
            'filter': 'filtro',
            'calendar': 'calendar',
            'chart': 'grafico',
            'logo': 'logo'
        }
        
        # Cargar iconos usando el gestor de iconos
        for key, icon_name in icon_files.items():
            self.icons[key] = icon_manager.get_icon(icon_name, size=(24, 24))

    def setup_ui(self):
        """Configura la interfaz de usuario principal."""
        # Crear el contenedor principal
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configurar la barra de menú
        self.setup_menu()
        
        # Configurar la barra de herramientas
        self.setup_toolbar()
        
        # Configurar la barra de accesos rápidos
        self.setup_quick_access()
        
        # Crear el notebook (pestañas)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear frames para cada pestaña
        self.personas_frame = ttk.Frame(self.notebook)
        self.inventario_frame = ttk.Frame(self.notebook)
        self.transacciones_frame = ttk.Frame(self.notebook)
        
        # Añadir pestañas al notebook
        self.notebook.add(self.personas_frame, text="Clientes y Pedidos")
        self.notebook.add(self.inventario_frame, text="Inventario")
        self.notebook.add(self.transacciones_frame, text="Transacciones")
        
        # Inicializar vistas de forma perezosa (lazy loading)
        # Solo se crearán cuando se seleccione la pestaña correspondiente
        self.personas_view = None
        self.inventario_view = None
        self.transacciones_view = None
        
        # Configurar barra de estado
        self.setup_status_bar()
        
        # Vincular eventos
        self.bind_events()
        
        # Vincular evento de cambio de pestaña para cargar las vistas cuando sea necesario
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Inicializar la primera pestaña (Personas)
        self.load_tab_content(0)

    def setup_menu(self):
        """Configura la barra de menú principal."""
        self.menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=self.menu_bar)
        
        # Menú Archivo
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self.on_new, accelerator="Ctrl+N", image=self.icons.get('new'), compound=tk.LEFT)
        file_menu.add_command(label="Abrir", command=self.on_open, accelerator="Ctrl+O", image=self.icons.get('open'), compound=tk.LEFT)
        file_menu.add_separator()
        file_menu.add_command(label="Guardar", command=self.on_save, accelerator="Ctrl+S", image=self.icons.get('save'), compound=tk.LEFT)
        file_menu.add_command(label="Guardar como...", command=self.on_save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Imprimir", command=self.on_print, accelerator="Ctrl+P", image=self.icons.get('print'), compound=tk.LEFT)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_exit, accelerator="Alt+F4", image=self.icons.get('exit'), compound=tk.LEFT)
        self.menu_bar.add_cascade(label="Archivo", menu=file_menu)
        
        # Menú Editar
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Deshacer", command=self.on_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rehacer", command=self.on_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cortar", command=self.on_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copiar", command=self.on_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Pegar", command=self.on_paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Buscar", command=self.on_search, accelerator="Ctrl+F", image=self.icons.get('search'), compound=tk.LEFT)
        self.menu_bar.add_cascade(label="Editar", menu=edit_menu)
        
        # Menú Ver
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Actualizar", command=self.on_refresh, accelerator="F5", image=self.icons.get('refresh'), compound=tk.LEFT)
        view_menu.add_separator()
        
        # Submenu de temas
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_menu.add_command(label="Claro", command=lambda: self.on_change_theme("light"))
        theme_menu.add_command(label="Oscuro", command=lambda: self.on_change_theme("dark"))
        theme_menu.add_command(label="Naranja", command=lambda: self.on_change_theme("orange"))
        theme_menu.add_command(label="Azul", command=lambda: self.on_change_theme("blue"))
        view_menu.add_cascade(label="Tema", menu=theme_menu)
        
        view_menu.add_separator()
        self.show_toolbar_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Mostrar barra de herramientas", variable=self.show_toolbar_var, command=self.toggle_toolbar)
        
        self.show_quick_access_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Mostrar accesos rápidos", variable=self.show_quick_access_var, command=self.toggle_quick_access)
        
        self.show_status_bar_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Mostrar barra de estado", variable=self.show_status_bar_var, command=self.toggle_status_bar)
        
        self.menu_bar.add_cascade(label="Ver", menu=view_menu)
        
        # Menú Herramientas
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="Configuración", command=self.on_settings, image=self.icons.get('settings'), compound=tk.LEFT)
        tools_menu.add_separator()
        tools_menu.add_command(label="Exportar datos", command=self.on_export, image=self.icons.get('export'), compound=tk.LEFT)
        tools_menu.add_command(label="Importar datos", command=self.on_import, image=self.icons.get('import'), compound=tk.LEFT)
        tools_menu.add_separator()
        tools_menu.add_command(label="Generar reportes", command=self.on_reports, image=self.icons.get('report'), compound=tk.LEFT)
        self.menu_bar.add_cascade(label="Herramientas", menu=tools_menu)
        
        # Menú Ayuda
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Manual de usuario", command=self.on_user_manual, image=self.icons.get('help'), compound=tk.LEFT)
        help_menu.add_command(label="Soporte técnico", command=self.on_support)
        help_menu.add_separator()
        help_menu.add_command(label="Acerca de", command=self.on_about)
        self.menu_bar.add_cascade(label="Ayuda", menu=help_menu)

    def setup_toolbar(self):
        """Configura la barra de herramientas."""
        self.toolbar = ttk.Frame(self.main_container, style='Toolbar.TFrame')
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Botones de la barra de herramientas
        toolbar_buttons = [
            ("Nuevo", self.on_new, 'new'),
            ("Abrir", self.on_open, 'open'),
            ("Guardar", self.on_save, 'save'),
            (None, None, None),  # Separador
            ("Imprimir", self.on_print, 'print'),
            (None, None, None),  # Separador
            ("Buscar", self.on_search, 'search'),
            ("Actualizar", self.on_refresh, 'refresh'),
            (None, None, None),  # Separador
            ("Exportar", self.on_export, 'export'),
            ("Reportes", self.on_reports, 'report'),
            (None, None, None),  # Separador
            ("Configuración", self.on_settings, 'settings'),
            ("Ayuda", self.on_user_manual, 'help')
        ]
        
        for i, (text, command, icon_key) in enumerate(toolbar_buttons):
            if text is None:  # Separador
                separator = ttk.Separator(self.toolbar, orient='vertical')
                separator.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.Y)
            else:
                btn = ttk.Button(
                    self.toolbar,
                    text="",
                    image=self.icons.get(icon_key),
                    command=command,
                    style='Toolbar.TButton',
                    width=3
                )
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                
                # Crear tooltip
                self.create_tooltip(btn, text)
        
        # Espacio flexible
        spacer = ttk.Frame(self.toolbar, style='Toolbar.TFrame')
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botón de notificaciones en el lado derecho
        self.notification_btn = ttk.Button(
            self.toolbar,
            text="",
            image=self.icons.get('notification'),
            command=self.show_notifications,
            style='Toolbar.TButton',
            width=3
        )
        self.notification_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        self.create_tooltip(self.notification_btn, "Notificaciones")
        
        # Indicador de notificaciones
        self.notification_indicator = tk.Canvas(
            self.toolbar,
            width=16,
            height=16,
            bg=self.colors['toolbar'],
            highlightthickness=0
        )
        self.notification_indicator.place(in_=self.notification_btn, x=28, y=2)
        self.update_notification_indicator(0)  # Inicialmente sin notificaciones

    def setup_quick_access(self):
        """Configura la barra de accesos rápidos."""
        self.quick_access = ttk.Frame(self.main_container, style='QuickAccess.TFrame')
        self.quick_access.pack(fill=tk.X, padx=0, pady=0)
        
        # Botones de acceso rápido
        quick_buttons = [
            ("Inicio", self.on_home, 'home'),
            ("Clientes", self.on_goto_personas, 'user'),
            ("Inventario", self.on_goto_inventario, 'inventory'),
            ("Transacciones", self.on_goto_transacciones, 'transaction'),
            ("Reportes", self.on_reports, 'report'),
            ("Calendario", self.on_calendar, 'calendar'),
            ("Gráficos", self.on_charts, 'chart')
        ]
        
        for text, command, icon_key in quick_buttons:
            btn_frame = ttk.Frame(self.quick_access, style='QuickAccess.TFrame')
            btn_frame.pack(side=tk.LEFT, padx=1, pady=1)
            
            btn = ttk.Button(
                btn_frame,
                text=text,
                image=self.icons.get(icon_key),
                compound=tk.TOP,
                command=command,
                style='QuickAccess.TButton',
                width=12
            )
            btn.pack(padx=5, pady=5)

    def setup_status_bar(self):
        """Configura la barra de estado."""
        self.status_bar = ttk.Frame(self.parent, style='StatusBar.TFrame')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(
            self.status_bar,
            text="Sistema listo",
            style='StatusBar.TLabel'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Separador
        ttk.Separator(self.status_bar, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y, pady=2)
        
        # Contador de elementos
        self.items_count_label = ttk.Label(
            self.status_bar,
            text="Elementos: 0",
            style='StatusBar.TLabel'
        )
        self.items_count_label.pack(side=tk.LEFT, padx=10)
        
        # Separador
        ttk.Separator(self.status_bar, orient='vertical').pack(side=tk.LEFT, padx=5, fill=tk.Y, pady=2)
        
        # Usuario actual
        self.user_label = ttk.Label(
            self.status_bar,
            text="Usuario: Admin",
            style='StatusBar.TLabel'
        )
        self.user_label.pack(side=tk.LEFT, padx=10)
        
        # Fecha y hora (lado derecho)
        self.date_label = ttk.Label(
            self.status_bar,
            text=self.get_current_date(),
            style='StatusBar.TLabel'
        )
        self.date_label.pack(side=tk.RIGHT, padx=10)

    def bind_events(self):
        """Vincula eventos a la interfaz."""
        # Vincular eventos de teclado
        self.parent.bind("<Control-n>", lambda e: self.on_new())
        self.parent.bind("<Control-o>", lambda e: self.on_open())
        self.parent.bind("<Control-s>", lambda e: self.on_save())
        self.parent.bind("<Control-p>", lambda e: self.on_print())
        self.parent.bind("<Control-f>", lambda e: self.on_search())
        self.parent.bind("<F5>", lambda e: self.on_refresh())
        
        # Actualizar fecha cada minuto
        self.parent.after(60000, self.update_date)

    def create_tooltip(self, widget, text):
        """Crea un tooltip para un widget."""
        # Si hay estilos elegantes disponibles, usarlos
        if self.elegant_styles:
            self.elegant_styles.create_tooltip(widget, text)
            return
        
        # Implementación manual si no hay estilos elegantes
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Crear ventana de tooltip
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(
                self.tooltip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", "8")
            )
            label.pack(ipadx=2, ipady=2)
        
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                del self.tooltip
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def update_status_bar(self):
        """Actualiza la información en la barra de estado."""
        # Actualizar contador de elementos según la pestaña activa
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:  # Personas
            if self.personas_view and hasattr(self, 'personas_controller'):
                count = len(self.personas_controller.get_personas())
                self.items_count_label.config(text=f"Clientes: {count}")
        elif current_tab == 1:  # Inventario
            if self.inventario_view and hasattr(self, 'inventario_controller'):
                count = len(self.inventario_controller.get_articulos())
                self.items_count_label.config(text=f"Artículos: {count}")
        elif current_tab == 2:  # Transacciones
            if self.transacciones_view and hasattr(self, 'transacciones_controller'):
                count = len(self.transacciones_controller.get_transacciones())
                self.items_count_label.config(text=f"Transacciones: {count}")

    def update_date(self):
        """Actualiza la fecha y hora en la barra de estado."""
        self.date_label.config(text=self.get_current_date())
        # Programar la próxima actualización
        self.parent.after(60000, self.update_date)

    def get_current_date(self):
        """Retorna la fecha y hora actual formateada."""
        return datetime.now().strftime("%d/%m/%Y %H:%M")

    def update_notification_indicator(self, count):
        """Actualiza el indicador de notificaciones."""
        self.notification_indicator.delete("all")
        if count > 0:
            # Dibujar círculo rojo con el número de notificaciones
            self.notification_indicator.create_oval(0, 0, 16, 16, fill="#dc3545", outline="")
            self.notification_indicator.create_text(8, 8, text=str(count), fill="white", font=("Segoe UI", "7", "bold"))
        else:
            # Sin notificaciones, no mostrar nada
            pass

    def toggle_toolbar(self):
        """Muestra u oculta la barra de herramientas."""
        if self.show_toolbar_var.get():
            self.toolbar.pack(fill=tk.X, padx=5, pady=2, after=self.menu_bar)
        else:
            self.toolbar.pack_forget()

    def toggle_quick_access(self):
        """Muestra u oculta la barra de accesos rápidos."""
        if self.show_quick_access_var.get():
            self.quick_access.pack(fill=tk.X, padx=0, pady=0, after=self.toolbar)
        else:
            self.quick_access.pack_forget()

    def toggle_status_bar(self):
        """Muestra u oculta la barra de estado."""
        if self.show_status_bar_var.get():
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.status_bar.pack_forget()

    # Métodos para manejar eventos de menú y barra de herramientas
    def on_new(self):
        """Maneja el evento de Nuevo."""
        messagebox.showinfo("Nuevo", "Función Nuevo no implementada")

    def on_open(self):
        """Maneja el evento de Abrir."""
        messagebox.showinfo("Abrir", "Función Abrir no implementada")

    def on_save(self):
        """Maneja el evento de Guardar."""
        messagebox.showinfo("Guardar", "Función Guardar no implementada")

    def on_save_as(self):
        """Maneja el evento de Guardar como."""
        messagebox.showinfo("Guardar como", "Función Guardar como no implementada")

    def on_print(self):
        """Maneja el evento de Imprimir."""
        messagebox.showinfo("Imprimir", "Función Imprimir no implementada")

    def on_exit(self):
        """Maneja el evento de Salir."""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir de la aplicación?"):
            self.parent.destroy()

    def on_undo(self):
        """Maneja el evento de Deshacer."""
        messagebox.showinfo("Deshacer", "Función Deshacer no implementada")

    def on_redo(self):
        """Maneja el evento de Rehacer."""
        messagebox.showinfo("Rehacer", "Función Rehacer no implementada")

    def on_cut(self):
        """Maneja el evento de Cortar."""
        messagebox.showinfo("Cortar", "Función Cortar no implementada")

    def on_copy(self):
        """Maneja el evento de Copiar."""
        messagebox.showinfo("Copiar", "Función Copiar no implementada")

    def on_paste(self):
        """Maneja el evento de Pegar."""
        messagebox.showinfo("Pegar", "Función Pegar no implementada")

    def on_search(self):
        """Maneja el evento de Buscar."""
        messagebox.showinfo("Buscar", "Función Buscar no implementada")

    def on_refresh(self):
        """Maneja el evento de Actualizar."""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:  # Personas
            if self.personas_view and hasattr(self.personas_view, 'load_data'):
                self.personas_view.load_data()
        elif current_tab == 1:  # Inventario
            if self.inventario_view and hasattr(self.inventario_view, 'cargar_datos'):
                self.inventario_view.cargar_datos()
        elif current_tab == 2:  # Transacciones
            if self.transacciones_view and hasattr(self.transacciones_view, 'load_data'):
                self.transacciones_view.load_data()
        
        self.update_status_bar()
        self.status_label.config(text="Datos actualizados")

    def on_change_theme(self, theme_name):
        """Cambia el tema de la aplicación."""
        if self.theme_manager:
            self.theme_manager.set_theme(theme_name)
            self.colors = self.theme_manager.get_color_palette()
            self.setup_styles()
            self.update_ui_colors()
        else:
            messagebox.showinfo("Cambiar tema", f"Cambio de tema a {theme_name} no implementado")

    def update_ui_colors(self):
        """Actualiza los colores de la interfaz después de cambiar el tema."""
        # Actualizar colores de widgets principales
        self.toolbar.configure(style='Toolbar.TFrame')
        self.quick_access.configure(style='QuickAccess.TFrame')
        self.status_bar.configure(style='StatusBar.TFrame')
        
        # Actualizar colores en las vistas
        if self.personas_view and hasattr(self.personas_view, 'update_theme'):
            self.personas_view.update_theme(self.colors)
        if self.inventario_view and hasattr(self.inventario_view, 'update_theme'):
            self.inventario_view.update_theme(self.colors)
        if self.transacciones_view and hasattr(self.transacciones_view, 'update_theme'):
            self.transacciones_view.update_theme(self.colors)

    def on_settings(self):
        """Abre la ventana de configuración."""
        messagebox.showinfo("Configuración", "Ventana de configuración no implementada")

    def on_export(self):
        """Exporta datos según la pestaña activa."""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:  # Personas
            if self.personas_view and hasattr(self.personas_view, 'export_to_excel'):
                self.personas_view.export_to_excel()
        elif current_tab == 1:  # Inventario
            if self.inventario_view and hasattr(self.inventario_view, 'exportar_a_excel'):
                self.inventario_view.exportar_a_excel()
        elif current_tab == 2:  # Transacciones
            if self.transacciones_view and hasattr(self.transacciones_view, 'export_to_excel'):
                self.transacciones_view.export_to_excel()

    def on_import(self):
        """Importa datos según la pestaña activa."""
        messagebox.showinfo("Importar", "Función de importación no implementada")

    def on_reports(self):
        """Genera reportes según la pestaña activa."""
        messagebox.showinfo("Reportes", "Generación de reportes no implementada")

    def on_user_manual(self):
        """Abre el manual de usuario."""
        try:
            # Intentar abrir el manual de usuario (PDF o URL)
            manual_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'manual.pdf')
            if os.path.exists(manual_path):
                webbrowser.open(manual_path)
            else:
                # Si no existe localmente, abrir URL
                webbrowser.open("https://ejemplo.com/manual")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el manual: {str(e)}")

    def on_support(self):
        """Abre la página de soporte técnico."""
        try:
            webbrowser.open("https://ejemplo.com/soporte")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la página de soporte: {str(e)}")

    def on_about(self):
        """Muestra información sobre la aplicación."""
        about_window = tk.Toplevel(self.parent)
        about_window.title("Acerca de FIDEGOD")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.transient(self.parent)
        about_window.grab_set()
        
        # Centrar en la pantalla
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Contenido
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo
        if 'logo' in self.icons:
            logo_label = ttk.Label(frame, image=self.icons['logo'])
            logo_label.pack(pady=10)
        
        # Título
        title_label = ttk.Label(
            frame,
            text="FIDEGOD",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=5)
        
        # Versión
        version_label = ttk.Label(
            frame,
            text="Versión 1.0.0",
            font=("Segoe UI", 10)
        )
        version_label.pack()
        
        # Descripción
        description_label = ttk.Label(
            frame,
            text="Sistema de Gestión para Inventario y Pedidos",
            font=("Segoe UI", 10),
            wraplength=350,
            justify="center"
        )
        description_label.pack(pady=10)
        
        # Copyright
        copyright_label = ttk.Label(
            frame,
            text="© 2023 FIDEGOD. Todos los derechos reservados.",
            font=("Segoe UI", 8)
        )
        copyright_label.pack(pady=5)
        
        # Botón cerrar
        close_button = ttk.Button(
            frame,
            text="Cerrar",
            command=about_window.destroy
        )
        close_button.pack(pady=10)

    def on_home(self):
        """Navega a la página de inicio."""
        # Por defecto, ir a la primera pestaña
        self.notebook.select(0)

    def on_goto_personas(self):
        """Navega a la pestaña de Personas."""
        self.notebook.select(0)

    def on_goto_inventario(self):
        """Navega a la pestaña de Inventario."""
        self.notebook.select(1)

    def on_goto_transacciones(self):
        """Navega a la pestaña de Transacciones."""
        self.notebook.select(2)

    def on_calendar(self):
        """Abre el calendario."""
        messagebox.showinfo("Calendario", "Función de calendario no implementada")

    def on_charts(self):
        """Muestra gráficos estadísticos."""
        messagebox.showinfo("Gráficos", "Función de gráficos no implementada")

    def on_tab_changed(self, event):
        """Maneja el evento de cambio de pestaña."""
        current_tab = self.notebook.index(self.notebook.select())
        tab_names = ["Clientes y Pedidos", "Inventario", "Transacciones"]
        self.status_label.config(text=f"Módulo: {tab_names[current_tab]}")
        
        # Cargar el contenido de la pestaña si aún no está cargado
        self.load_tab_content(current_tab)

    def load_tab_content(self, tab_index):
        """Carga el contenido de la pestaña seleccionada si aún no está cargado."""
        if tab_index == 0 and self.personas_view is None:  # Personas
            self.personas_view = PersonasView(self.personas_frame, self.style)
        elif tab_index == 1 and self.inventario_view is None:  # Inventario
            self.inventario_view = InventarioView(self.inventario_frame, self.inventario_controller)
        elif tab_index == 2 and self.transacciones_view is None:  # Transacciones
            self.transacciones_view = TransaccionesView(self.transacciones_frame, self.style)
        
        # Actualizar la barra de estado
        self.update_status_bar()

    def show_notifications(self):
        """Muestra las notificaciones pendientes."""
        if not self.notifications:
            messagebox.showinfo("Notificaciones", "No hay notificaciones pendientes")
            return
        
        # Crear ventana de notificaciones
        notif_window = tk.Toplevel(self.parent)
        notif_window.title("Notificaciones")
        notif_window.geometry("400x300")
        notif_window.transient(self.parent)
        notif_window.grab_set()
        
        # Centrar en la pantalla
        notif_window.update_idletasks()
        width = notif_window.winfo_width()
        height = notif_window.winfo_height()
        x = (notif_window.winfo_screenwidth() // 2) - (width // 2)
        y = (notif_window.winfo_screenheight() // 2) - (height // 2)
        notif_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Contenido
        frame = ttk.Frame(notif_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            frame,
            text="Notificaciones",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(pady=(0, 10), anchor="w")
        
        # Lista de notificaciones
        notif_frame = ttk.Frame(frame)
        notif_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(notif_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas para scrolling
        canvas = tk.Canvas(notif_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Frame dentro del canvas
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Añadir notificaciones
        for i, notif in enumerate(self.notifications):
            notif_item = ttk.Frame(inner_frame, padding=5)
            notif_item.pack(fill=tk.X, pady=2)
            
            # Título de la notificación
            ttk.Label(
                notif_item,
                text=notif.get('title', 'Notificación'),
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w")
            
            # Mensaje
            ttk.Label(
                notif_item,
                text=notif.get('message', ''),
                wraplength=350
            ).pack(anchor="w", pady=(2, 0))
            
            # Fecha
            ttk.Label(
                notif_item,
                text=notif.get('date', ''),
                font=("Segoe UI", 8),
                foreground=self.colors['text_secondary']
            ).pack(anchor="e")
            
            # Separador
            if i < len(self.notifications) - 1:
                ttk.Separator(inner_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Actualizar scrollregion
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Marcar todas como leídas",
            command=lambda: self.mark_all_read(notif_window)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cerrar",
            command=notif_window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def mark_all_read(self, window):
        """Marca todas las notificaciones como leídas."""
        self.notifications = []
        self.update_notification_indicator(0)
        window.destroy()
        messagebox.showinfo("Notificaciones", "Todas las notificaciones han sido marcadas como leídas")

    def add_notification(self, title, message):
        """Añade una nueva notificación."""
        self.notifications.append({
            'title': title,
            'message': message,
            'date': datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        self.update_notification_indicator(len(self.notifications))