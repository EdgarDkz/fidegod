import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry
from datetime import datetime
from controllers.personas_controller import PersonasController
import os
from PIL import Image, ImageTk

class EditPersonaDialog(tk.Toplevel):
    def __init__(self, parent, title, persona, on_close_callback=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.geometry('600x780')
        self.configure(bg='#fff5ed')  # Color de fondo base

        # Paleta de colores
        self.color_palette = {
            'primary': '#fb8404',           # Naranja principal
            'primary_light': '#fcad58',     # Naranja más claro
            'primary_dark': '#cb6304',      # Naranja oscuro
            'secondary': '#76849a',         # Gris medio
            'background': '#fff5ed',        # Crema muy claro
            'surface': '#FFFFFF',           # Blanco
            'error': '#dc3545',            # Rojo error
            'success': '#28a745',          # Verde éxito
            'warning': '#fbb333',          # Naranja claro
            'info': '#17a2b8',            # Azul información
            'text': '#181d22',            # Gris oscuro/negro
            'text_secondary': '#76849a',   # Gris medio
            'divider': '#fcc56e',         # Naranja muy claro
            'toolbar': '#f4efdf',         # Beige claro
            'status_bar': '#f4efdf',      # Beige claro
            'card': '#FFFFFF',            # Blanco
            'hover': '#fcad58',           # Naranja más claro
            'selected': '#fcc56e',        # Naranja muy claro
            'disabled': '#e0e0e0',        # Gris claro
            'input': '#FFFFFF',           # Blanco
            'border': '#fbb333',          # Naranja claro
            'text_header': '#fb8404'      # Naranja para encabezados
        }

        # IDs y valores originales
        self.persona = persona
        self.persona_id = persona[0]  # Asegurar que tenemos el ID
        
        # Controlador
        self.controller = PersonasController()
        
        # Variables para almacenar datos
        self.vars = {
            'nombre': tk.StringVar(value=persona[1] if persona[1] else ""),
            'articulo': tk.StringVar(value=persona[2] if persona[2] else ""),
            'telefono': tk.StringVar(value=persona[3] if persona[3] else ""),
            'direccion': tk.StringVar(value=persona[4] if persona[4] else ""),
            'municipio': tk.StringVar(value=persona[5] if persona[5] else ""),
        }
        
        # Variables para fechas
        self.fecha_pedido_value = persona[6] if persona[6] else datetime.now().strftime('%Y-%m-%d')
        self.fecha_entrega_value = persona[7] if persona[7] else None
        
        # Estado y pendiente
        self.estado_original = persona[8] if persona[8] else "Pendiente"
        self.entrega_pendiente = tk.BooleanVar(value=(self.estado_original == 'Pendiente'))
        
        # Callback para actualizar vista padre
        self.on_close_callback = on_close_callback
        self.result = None
        
        # Cargar recursos
        self.load_icons()
        self.setup_validation()
        self.setup_styles()
        
        # Frame principal con scroll
        self.setup_main_layout()
        
        # Crear widgets
        self.create_widgets()
        self.create_buttons()
        self.center_window()

    def load_icons(self):
        """Cargar iconos para la interfaz"""
        self.icons = {}
        icon_path = os.path.join('views', 'icons')
        icon_files = {
            'user': 'user.png',
            'phone': 'telefono.png',
            'location': 'localizacion.png',
            'calendar': 'calendar.png',
            'save': 'articulo.png',
            'cancel': 'cancelar.png'
        }

        for icon_name, file_name in icon_files.items():
            try:
                path = os.path.join(icon_path, file_name)
                if os.path.exists(path):
                    img = Image.open(path)
                    img = img.resize((20, 20), Image.Resampling.LANCZOS)
                    self.icons[icon_name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"No se pudo cargar el icono {icon_name}: {e}")

    def setup_styles(self):
        """Configura los estilos personalizados para los widgets"""
        self.style = ttk.Style()
        
        # Configuración base
        self.style.configure('TFrame', background=self.color_palette['surface'])
        self.style.configure('App.TFrame', background=self.color_palette['surface'])
        
        # Configurar estilos para etiquetas
        self.style.configure('DialogHeader.TLabel', 
                             font=('Segoe UI', 16, 'bold'), 
                             foreground=self.color_palette['primary'],
                             background=self.color_palette['surface'])
        
        self.style.configure('DialogSection.TLabel', 
                             font=('Segoe UI', 12, 'bold'), 
                             foreground=self.color_palette['primary_dark'],
                             background=self.color_palette['surface'])
        
        self.style.configure('DialogField.TLabel', 
                             font=('Segoe UI', 10), 
                             foreground=self.color_palette['text'],
                             background=self.color_palette['surface'])
        
        # Configurar estilos para entradas
        self.style.configure('TEntry', 
                             font=('Segoe UI', 10),
                             fieldbackground=self.color_palette['input'])
        
        self.style.map('TEntry',
                      bordercolor=[('focus', self.color_palette['primary'])])
        
        # Configurar estilos para combos
        self.style.configure('TCombobox', 
                             font=('Segoe UI', 10),
                             fieldbackground=self.color_palette['input'])
        
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', self.color_palette['input'])],
                      selectbackground=[('readonly', self.color_palette['primary_light'])])
        
        # Configurar estilos para frames
        self.style.configure('Card.TFrame', 
                            background=self.color_palette['surface'],
                            relief='ridge',
                            borderwidth=1)
        
        # Configurar LabelFrame
        self.style.configure('TLabelframe', 
                            background=self.color_palette['surface'],
                            bordercolor=self.color_palette['primary_light'])
        
        self.style.configure('TLabelframe.Label', 
                            font=('Segoe UI', 11, 'bold'),
                            foreground=self.color_palette['primary'],
                            background=self.color_palette['surface'])
        
        # Configurar Checkbutton
        self.style.configure('TCheckbutton',
                           background=self.color_palette['surface'],
                           foreground=self.color_palette['text'])
        
        # Configurar Separator
        self.style.configure('TSeparator',
                           background=self.color_palette['divider'])

    def setup_main_layout(self):
        """Configura el layout principal con scroll"""
        # Contenedor principal
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Canvas y Scrollbar
        self.canvas = tk.Canvas(
            self.container,
            bg=self.color_palette['background'],
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
            width=600  # Ancho fijo para el contenido
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

    def create_widgets(self):
        """Crear y organizar widgets"""
        # Asegúrate de que este método se esté llamando
        print("Creando widgets...")
        # Aquí va el código para crear los widgets

    def create_entry_field(self, parent, label_text, variable, row):
        """Crea un campo de entrada con etiqueta e icono opcional"""
        label = ttk.Label(
            parent, 
            text=label_text, 
            style='DialogField.TLabel'
        )
        label.grid(row=row, column=0, sticky='w', pady=10, padx=5)
        
        entry = ttk.Entry(
            parent,
            textvariable=variable,
            font=('Segoe UI', 10)
        )
        entry.grid(row=row, column=1, sticky='ew', pady=10, padx=5)
        
        # Agregar el icono si está disponible
        if variable == self.vars['telefono']:
            entry.config(validate='key', validatecommand=(self.validate_command, '%S'))
        
        if variable in self.icons:
            label.config(image=self.icons[variable], compound='left', padding=(0, 0, 5, 0))

    def create_buttons(self):
        """Crea los botones de acción"""
        # Sección de botones de acción
        buttons_frame = ttk.Frame(self.main_frame, style='App.TFrame')
        buttons_frame.pack(pady=(10, 20), padx=15, fill='x')
        
        # Separador decorativo
        separator = ttk.Separator(buttons_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        # Contenedor para los botones
        action_buttons = ttk.Frame(buttons_frame, style='App.TFrame')
        action_buttons.pack(anchor='center')
        
        # Botones de acción
        guardar_button = tk.Button(
            action_buttons,
            text="✓ Guardar Cambios",
            command=self.save,
            bg=self.color_palette['success'],
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            font=('Segoe UI', 11, 'bold'),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        guardar_button.pack(side='left', padx=10)
        
        cancelar_button = tk.Button(
            action_buttons,
            text="✕ Cancelar",
            command=self.destroy,
            bg=self.color_palette['error'],
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            font=('Segoe UI', 11, 'bold'),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancelar_button.pack(side='left', padx=10)
        
        # Agregar tooltips
        self.create_tooltip(guardar_button, "Guardar los cambios y actualizar en la base de datos")
        self.create_tooltip(cancelar_button, "Cerrar sin guardar cambios")

    def create_tooltip(self, widget, text):
        """Crear tooltip para los widgets"""
        def show_tooltip(event):
            tooltip = tk.Toplevel(self)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip, 
                text=text, 
                justify='left',
                background="#ffffe0", 
                relief='solid', 
                borderwidth=1,
                font=("Segoe UI", 9)
            )
            label.pack(padx=3, pady=3)
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)

    def setup_validation(self):
        """Configura la validación para el campo de teléfono"""
        self.validate_command = self.register(self.validate_phone)
    
    def validate_phone(self, char):
        """Validar que solo se ingresen números en el campo de teléfono"""
        return char.isdigit()

    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def validate(self):
        """Validar campos requeridos"""
        # Validar nombre
        if not self.vars['nombre'].get().strip():
            messagebox.showerror('Error', 'El nombre del cliente es obligatorio.')
            return False
            
        # Validar artículo
        articulo_text = self.articulo_text.get('1.0', 'end-1c').strip()
        if not articulo_text:
            messagebox.showerror('Error', 'La descripción del artículo es obligatoria.')
            return False
            
        # Validar teléfono
        telefono = self.vars['telefono'].get().strip()
        if not telefono or not telefono.isdigit():
            messagebox.showerror('Error', 'El teléfono debe contener solo dígitos.')
            return False
            
        # Validar dirección
        if not self.vars['direccion'].get().strip():
            messagebox.showerror('Error', 'La dirección es obligatoria.')
            return False
            
        # Validar municipio
        if not self.vars['municipio'].get():
            messagebox.showerror('Error', 'Debe seleccionar un municipio.')
            return False
            
        return True

    def get_data(self):
        """Obtener los datos del formulario"""
        if not self.validate():
            return None
        
        # Determinar estado y fecha de entrega según checkbox
        estado = 'Pendiente' if self.entrega_pendiente.get() else 'Entregado'
        fecha_entrega = None if self.entrega_pendiente.get() else self.persona[7]
        
        # Si ya estaba entregado y se mantiene como entregado, conservar la fecha
        if not self.entrega_pendiente.get() and self.estado_original == 'Entregado':
            fecha_entrega = self.persona[7]
        # Si cambia de pendiente a entregado, poner fecha actual
        elif not self.entrega_pendiente.get() and self.estado_original == 'Pendiente':
            fecha_entrega = datetime.now().strftime('%Y-%m-%d')
            
        return {
            'id': self.persona_id,  # Aseguramos pasar el ID
            'nombre': self.vars['nombre'].get().strip(),
            'articulo': self.articulo_text.get('1.0', 'end-1c').strip(),
            'telefono': self.vars['telefono'].get().strip(),
            'direccion': self.vars['direccion'].get().strip(),
            'municipio': self.vars['municipio'].get(),
            'fecha_pedido': self.fecha_pedido.get_date().strftime('%Y-%m-%d'),
            'fecha_entrega': fecha_entrega,
            'estado': estado
        }

    def save(self):
        """Guardar los cambios y actualizar en la base de datos"""
        # Obtener datos validados
        data = self.get_data()
        if not data:
            return
        
        try:
            # Debug para verificar los datos
            print("Datos a actualizar:", data)
            
            # Actualizar en la base de datos - Pasamos el ID y los demás datos como kwargs
            persona_id = data.pop('id')  # Extraer el ID
            self.controller.update_persona(persona_id, **data)
            
            # Mensaje de éxito
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            
            # Guardar resultado para quien llamó el diálogo
            self.result = True
            
            # Llamar al callback si existe
            if self.on_close_callback:
                self.on_close_callback()
                
            # Cerrar el diálogo
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
            print(f"Error detallado: {str(e)}")

if __name__ == '__main__':
    # Ejemplo de uso para probar el diálogo
    root = tk.Tk()
    root.withdraw() # Oculta la ventana principal

    # Persona de ejemplo (simulando datos de la base de datos)
    persona_ejemplo = (1, "Nombre Ejemplo", "Artículo Ejemplo", "1234567890", "Dirección Ejemplo", "Montemorelos", "2023-01-15", "2023-01-20", "Entregado")

    dialog = EditPersonaDialog(root, "Editar Persona", persona_ejemplo)
    dialog.wait_window(dialog) # Espera a que se cierre el diálogo

    if dialog.result:
        print("Dialogo cerrado con Aceptar")
    else:
        print("Dialogo cerrado con Cancelar o cerrado sin acción.")

    root.mainloop()