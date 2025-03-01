import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk  # Para manejar iconos
from controllers.personas_controller import PersonasController  # Agregamos esta importación
import os

class AddPersonaDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.setup_validation()  # Llamar a la función de configuración de validación

        # Configuración de la ventana
        window_width = 450
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Colores del tema
        self.colors = {
            'primary': '#1a73e8',  # Azul Google
            'primary_light': '#e8f0fe',
            'secondary': '#5f6368',  # Gris Google
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'error': '#d93025',  # Rojo Google
            'success': '#1e8e3e',  # Verde Google
            'border': '#dadce0'  # Gris claro para bordes
        }

        self.configure(bg=self.colors['background'])
        self.controller = PersonasController()
        self.result = None
        
        # Almacenar referencias a las imágenes
        self.icons = {}

        # Configurar estilo
        self.setup_styles()
        
        # Variables
        self.setup_variables()
        
        # Crear contenedor principal con scroll
        self.create_scrollable_frame()
        
        # Crear la interfaz
        self.create_widgets()
        
        # Bindings
        self.bind('<Return>', lambda e: self.add_persona())
        self.bind('<Escape>', lambda e: self.cancelar())

    def setup_styles(self):
        """Configurar estilos personalizados"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Estilo para frames
        self.style.configure(
            'App.TFrame',
            background=self.colors['background']
        )

        # Estilo para LabelFrames
        self.style.configure(
            'App.TLabelframe',
            background=self.colors['background'],
            bordercolor=self.colors['border']
        )
        self.style.configure(
            'App.TLabelframe.Label',
            background=self.colors['background'],
            foreground=self.colors['primary'],
            font=('Segoe UI', 11, 'bold'),
            padding=(0, 10)
        )

        # Estilo para etiquetas
        self.style.configure(
            'App.TLabel',
            background=self.colors['background'],
            foreground=self.colors['secondary'],
            font=('Segoe UI', 10)
        )

        # Estilo para el título
        self.style.configure(
            'Title.TLabel',
            background=self.colors['background'],
            foreground=self.colors['primary'],
            font=('Segoe UI', 16, 'bold'),
            padding=(0, 10)
        )

        # Estilo para entradas
        self.style.configure(
            'App.TEntry',
            fieldbackground=self.colors['surface'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border'],
            borderwidth=1,
            font=('Segoe UI', 10)
        )

        # Estilo para Combobox
        self.style.configure(
            'App.TCombobox',
            fieldbackground=self.colors['surface'],
            background=self.colors['primary'],
            arrowcolor=self.colors['primary'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border'],
            font=('Segoe UI', 10)
        )

        # Estilo para Checkbutton
        self.style.configure(
            'App.TCheckbutton',
            background=self.colors['background'],
            foreground=self.colors['secondary'],
            font=('Segoe UI', 10)
        )

        # Estilo para botones
        self.style.configure(
            'Primary.TButton',
            background=self.colors['primary'],
            foreground='white',
            bordercolor=self.colors['primary'],
            lightcolor=self.colors['primary'],
            darkcolor=self.colors['primary'],
            font=('Segoe UI', 10, 'bold'),
            padding=(20, 8)
        )
        self.style.map(
            'Primary.TButton',
            background=[('active', self.colors['primary_light'])],
            foreground=[('active', self.colors['primary'])]
        )

        self.style.configure(
            'Secondary.TButton',
            background=self.colors['surface'],
            foreground=self.colors['secondary'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border'],
            font=('Segoe UI', 10),
            padding=(20, 8)
        )
        self.style.map(
            'Secondary.TButton',
            background=[('active', '#e8eaed')],
            foreground=[('active', self.colors['secondary'])]
        )

    def setup_variables(self):
        """Inicializar variables"""
        self.vars = {
            'nombre': tk.StringVar(),
            'articulo': tk.StringVar(),
            'telefono': tk.StringVar(),
            'direccion': tk.StringVar(),
            'municipio': tk.StringVar(),
            'no_contacto': tk.BooleanVar(),
            'explicacion_contacto': tk.StringVar(),
        }
        # Variable para fecha de entrega
        self.fecha_entrega_var = tk.BooleanVar()
        self.fecha_entrega_var.trace('w', self.toggle_fecha_entrega)

    def create_scrollable_frame(self):
        """Crear un frame con scroll"""
        # Contenedor principal
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Canvas y Scrollbar
        self.canvas = tk.Canvas(
            self.container,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.container,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # Frame que contendrá los widgets
        self.scrollable_frame = ttk.Frame(
            self.canvas,
            style='App.TFrame'
        )
        
        # Configurar el scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Crear ventana en el canvas con el frame
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=430  # Ancho fijo para el contenido
        )
        
        # Configurar el canvas para que se expanda
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bindings para el scroll con el mouse
        self.bind_mousewheel()
        
        # Binding para ajustar el ancho del frame cuando se redimensiona el canvas
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Binding para limpiar los eventos cuando se cierre la ventana
        self.bind('<Destroy>', self._on_destroy)

    def bind_mousewheel(self):
        """Vincular el evento de la rueda del mouse"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.mousewheel_bound = True

    def unbind_mousewheel(self):
        """Desvincular el evento de la rueda del mouse"""
        if hasattr(self, 'mousewheel_bound') and self.mousewheel_bound:
            self.canvas.unbind_all("<MouseWheel>")
            self.mousewheel_bound = False

    def _on_destroy(self, event):
        """Manejar el evento de destrucción de la ventana"""
        if event.widget == self:
            self.unbind_mousewheel()

    def _on_mousewheel(self, event):
        """Manejar el scroll con el mouse"""
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_canvas_configure(self, event):
        """Ajustar el ancho del frame cuando se redimensiona el canvas"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def setup_validation(self):
        """Configura la validación para el campo de teléfono"""
        self.validate_command = self.register(self.validate_phone)

    def validate_phone(self, char):
        """Validar que solo se ingresen números en el campo de teléfono"""
        return char.isdigit()  # Permitir solo dígitos

    def create_widgets(self):
        """Crear y organizar widgets"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.scrollable_frame, style='App.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="Registro de Nueva Persona",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))

        # Frame para los campos
        form_frame = ttk.LabelFrame(
            main_frame,
            text="Información Personal",
            style='App.TLabelframe',
            padding=15
        )
        form_frame.pack(fill=tk.X, pady=(0, 15))

        # Campos principales
        self.create_entry_field(form_frame, "Nombre:", 'nombre', 0)
        self.create_entry_field(form_frame, "Artículo:", 'articulo', 1)

        # Frame para información de contacto
        contact_frame = ttk.LabelFrame(
            main_frame,
            text="Información de Contacto",
            style='App.TLabelframe',
            padding=15
        )
        contact_frame.pack(fill=tk.X, pady=(0, 15))

        # Checkbox No Contacto
        no_contacto_frame = ttk.Frame(contact_frame, style='App.TFrame')
        no_contacto_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.no_contacto_check = ttk.Checkbutton(
            no_contacto_frame,
            text="Sin información de contacto",
            variable=self.vars['no_contacto'],
            command=self.toggle_no_contacto,
            style='App.TCheckbutton'
        )
        self.no_contacto_check.pack(side=tk.LEFT)

        # Frame para teléfono y explicación
        self.contact_details_frame = ttk.Frame(contact_frame, style='App.TFrame')
        self.contact_details_frame.pack(fill=tk.X)

        # Campo de teléfono
        self.telefono_frame = ttk.Frame(self.contact_details_frame, style='App.TFrame')
        self.telefono_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            self.telefono_frame,
            text="Teléfono:",
            style='App.TLabel'
        ).pack(side=tk.LEFT)
        
        self.telefono_entry = ttk.Entry(
            self.telefono_frame,
            textvariable=self.vars['telefono'],
            style='App.TEntry',
            validate='key',
            validatecommand=(self.validate_command, '%S')
        )
        self.telefono_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Campo de explicación
        self.explicacion_frame = ttk.Frame(self.contact_details_frame, style='App.TFrame')
        self.explicacion_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            self.explicacion_frame,
            text="Detalles de contacto:",
            style='App.TLabel'
        ).pack(anchor=tk.W)
        
        self.explicacion_text = tk.Text(
            self.explicacion_frame,
            height=3,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            bg=self.colors['surface'],
            relief='flat',
            borderwidth=1
        )
        self.explicacion_text.pack(fill=tk.X, pady=(5, 0))
        self.explicacion_frame.pack_forget()

        # Frame para dirección
        address_frame = ttk.LabelFrame(
            main_frame,
            text="Ubicación",
            style='App.TLabelframe',
            padding=15
        )
        address_frame.pack(fill=tk.X, pady=(0, 15))

        # Campos de dirección
        self.create_entry_field(address_frame, "Dirección:", 'direccion', 0)

        # Municipio (Combobox)
        municipio_frame = ttk.Frame(address_frame, style='App.TFrame')
        municipio_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            municipio_frame,
            text="Municipio:",
            style='App.TLabel'
        ).pack(side=tk.LEFT)
        
        municipios = ["Allende", "Hualahuises", "Linares", "Montemorelos", "Rayones", "Terán"]
        self.municipio_combo = ttk.Combobox(
            municipio_frame,
            textvariable=self.vars['municipio'],
            values=municipios,
            state='readonly',
            style='App.TCombobox'
        )
        self.municipio_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Frame para fechas
        dates_frame = ttk.LabelFrame(
            main_frame,
            text="Fechas",
            style='App.TLabelframe',
            padding=15
        )
        dates_frame.pack(fill=tk.X, pady=(0, 20))

        # Fecha de pedido
        pedido_frame = ttk.Frame(dates_frame, style='App.TFrame')
        pedido_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            pedido_frame,
            text="Fecha Pedido:",
            style='App.TLabel'
        ).pack(side=tk.LEFT)
        
        self.fecha_pedido = DateEntry(
            pedido_frame,
            width=20,
            background=self.colors['primary'],
            foreground='white',
            date_pattern='yyyy-mm-dd',
            borderwidth=0
        )
        self.fecha_pedido.pack(side=tk.LEFT, padx=(10, 0))

        # Fecha de entrega
        entrega_frame = ttk.Frame(dates_frame, style='App.TFrame')
        entrega_frame.pack(fill=tk.X, pady=5)
        ttk.Label(
            entrega_frame,
            text="Fecha Entrega:",
            style='App.TLabel'
        ).pack(side=tk.LEFT)
        
        self.fecha_entrega = DateEntry(
            entrega_frame,
            width=20,
            background=self.colors['primary'],
            foreground='white',
            date_pattern='yyyy-mm-dd',
            borderwidth=0
        )
        self.fecha_entrega.pack(side=tk.LEFT, padx=(10, 0))

        # Checkbox para no seleccionar fecha de entrega
        self.check_fecha_entrega = ttk.Checkbutton(
            dates_frame,
            text="Sin fecha de entrega definida",
            variable=self.fecha_entrega_var,
            style='App.TCheckbutton'
        )
        self.check_fecha_entrega.pack(pady=(5, 0))

        # Botones de acción
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=20, pady=15)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        tk.Button(
            button_frame,
            text="Guardar",
            command=self.add_persona,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        ).grid(row=0, column=0, padx=5, sticky='ew')

        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.cancelar,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        ).grid(row=0, column=1, padx=5, sticky='ew')

    def load_icon(self, filename, size):
        """Cargar y redimensionar un ícono"""
        try:
            # Construir la ruta al directorio de iconos
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icons', filename)
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                image = image.resize(size, Image.Resampling.LANCZOS)  # Usar LANCZOS en lugar de ANTIALIAS
                photo = ImageTk.PhotoImage(image)
                # Guardar referencia
                self.icons[filename] = photo
                return photo
            else:
                print(f"No se encontró el ícono: {filename}")
                return None
        except Exception as e:
            print(f"Error al cargar el ícono {filename}: {str(e)}")
            return None

    def create_entry_field(self, parent, label, var_name, row):
        """Crear un campo de entrada con etiqueta"""
        frame = ttk.Frame(parent, style='App.TFrame')
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text=label, style='App.TLabel').pack(side=tk.LEFT)
        ttk.Entry(
            frame,
            textvariable=self.vars[var_name]
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

    def toggle_no_contacto(self):
        """Manejar el cambio en el checkbox de no contacto"""
        if self.vars['no_contacto'].get():
            self.telefono_frame.pack_forget()
            self.explicacion_frame.pack(fill=tk.X, pady=5)
            self.vars['telefono'].set('no contacto')
        else:
            self.explicacion_frame.pack_forget()
            self.telefono_frame.pack(fill=tk.X, pady=5)
            self.vars['telefono'].set('')
            self.explicacion_text.delete('1.0', tk.END)

    def toggle_fecha_entrega(self, *args):
        """Manejar el cambio en el checkbox de fecha de entrega"""
        if self.fecha_entrega_var.get():
            self.fecha_entrega.pack_forget()
        else:
            self.fecha_entrega.pack(side=tk.LEFT, padx=(10, 0))

    def add_persona(self):
        """Validar y agregar persona"""
        # Validar campos requeridos
        required_fields = {
            'nombre': 'Nombre',
            'articulo': 'Artículo',
            'direccion': 'Dirección',
            'municipio': 'Municipio'
        }
        # Verificar campos requeridos
        for field, label in required_fields.items():
            if not self.vars[field].get().strip():
                messagebox.showerror(
                    "Error",
                    f"El campo {label} es requerido."
                )
                return

        # Validar información de contacto
        if not self.vars['no_contacto'].get():
            if not self.vars['telefono'].get().strip():
                messagebox.showerror(
                    "Error",
                    "Debe ingresar un número de teléfono o marcar 'Sin información de contacto'."
                )
                return
        else:
            if not self.explicacion_text.get('1.0', tk.END).strip():
                messagebox.showerror(
                    "Error",
                    "Debe proporcionar detalles sobre la falta de información de contacto."
                )
                return

        try:
            # Preparar datos
            fecha_entrega = None if self.fecha_entrega_var.get() else self.fecha_entrega.get_date().strftime('%Y-%m-%d')
            estado = 'Pendiente' if self.fecha_entrega_var.get() else 'Entregado'

            # Preparar información de contacto
            telefono = self.vars['telefono'].get()
            if self.vars['no_contacto'].get():
                telefono = f"no contacto: {self.explicacion_text.get('1.0', tk.END).strip()}"

            # Crear diccionario de datos
            data = {
                'nombre': self.vars['nombre'].get().strip(),
                'articulo': self.vars['articulo'].get().strip(),
                'telefono': telefono,
                'direccion': self.vars['direccion'].get().strip(),
                'municipio': self.vars['municipio'].get(),
                'fecha_pedido': self.fecha_pedido.get_date().strftime('%Y-%m-%d'),
                'fecha_entrega': fecha_entrega,
                'estado': estado
            }

            # Guardar datos
            self.controller.add_persona(**data)
            self.result = data
            messagebox.showinfo("Éxito", "Persona agregada correctamente.")
            self.controller.update_table()
            self.unbind_mousewheel()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar los datos: {str(e)}")

    def cancelar(self):
        """Cerrar el diálogo"""
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea cancelar? Los datos no guardados se perderán."):
            self.unbind_mousewheel()
            self.destroy()