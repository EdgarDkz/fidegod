import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from PIL import Image, ImageTk
import os
from tkcalendar import DateEntry

class AddProductoDialog(tk.Toplevel):
    def __init__(self, parent, controller, mode='add', articulo=None, on_save=None):
        super().__init__(parent)
        self.title("Agregar Nuevo Artículo" if mode == 'add' else "Editar Artículo")
        self.controller = controller
        self.mode = mode
        self.articulo = articulo
        self.on_save = on_save  # Guardar el callback

        # Configuración de la ventana
        self.resizable(False, False)
        self.grab_set()
        self.geometry('500x950') # Increased height

        # Variables
        self.vars = {
            'nombre': tk.StringVar(),
            'descripcion': tk.StringVar(),
            'cantidad': tk.StringVar(),
            'categoria': tk.StringVar(),
            'ubicacion': tk.StringVar(),
            'stock_minimo': tk.StringVar(),
        }
        self.current_image = None
        self.image_path_var = tk.StringVar()
        self.result = None

        # Estilos
        self.setup_styles()

        # Si estamos editando, cargar datos
        if articulo and mode == 'edit':
            self.cargar_datos_articulo()

        # Crear la interfaz
        self.create_widgets()
        self.center_window()

    def setup_styles(self):
        """Configura los estilos personalizados para los widgets"""
        self.style = ttk.Style()

        self.style.configure('DialogHeader.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#333')
        self.style.configure('DialogSection.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#007bff')
        self.style.configure('DialogField.TLabel', font=('Segoe UI', 10), foreground='#555')
        self.style.configure('DialogEntry.TEntry', font=('Segoe UI', 10))
        self.style.configure('DialogButton.TButton',  padding=8)
        self.style.configure('AccentDialogButton.TButton',  padding=8, background='#28a745', foreground='white')
        self.style.map('AccentDialogButton.TButton', background=[('active', '#218838')])


    def create_widgets(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill='both')

        # Título del diálogo
        title_label = ttk.Label(
            main_frame,
            text="Información del Artículo",
            style='DialogHeader.TLabel'
        )
        title_label.pack(pady=(0, 20))

        # Frame para los campos
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill='x', pady=5)
        fields_frame.columnconfigure(1, weight=1) # Make column 1 expandable

        # Nombre del Artículo
        ttk.Label(fields_frame, text="Nombre del Artículo:", style='DialogField.TLabel').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        ttk.Entry(fields_frame, textvariable=self.vars['nombre'], style='DialogEntry.TEntry').grid(row=0, column=1, sticky='ew', pady=5, padx=5)

        # Descripción
        ttk.Label(fields_frame, text="Descripción:", style='DialogField.TLabel').grid(row=1, column=0, sticky='nw', pady=(10,0), padx=5) # sticky='nw' for top-left align
        self.descripcion_text = tk.Text(fields_frame, height=3, width=40, font=('Segoe UI', 10), wrap='word') # wrap='word' for line wrapping
        self.descripcion_text.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(5,10), padx=5)
        if self.mode == 'edit' and self.articulo:
            self.descripcion_text.insert('1.0', self.articulo[2])

        # Cantidad
        ttk.Label(fields_frame, text="Cantidad:", style='DialogField.TLabel').grid(row=3, column=0, sticky='w', pady=5, padx=5)
        ttk.Spinbox(fields_frame, from_=0, to=9999, textvariable=self.vars['cantidad'], width=10, style='DialogEntry.TEntry').grid(row=3, column=1, sticky='w', pady=5, padx=5)

        # Categoría
        ttk.Label(fields_frame, text="Categoría:", style='DialogField.TLabel').grid(row=4, column=0, sticky='w', pady=5, padx=5)
        self.categoria_combo = ttk.Combobox(fields_frame, textvariable=self.vars['categoria'], values=["Herramientas", "Electrónicos", "Muebles", "Otros"], state='readonly', style='DialogEntry.TEntry')
        self.categoria_combo.grid(row=4, column=1, sticky='ew', pady=5, padx=5)

        # Ubicación
        ttk.Label(fields_frame, text="Ubicación:", style='DialogField.TLabel').grid(row=5, column=0, sticky='w', pady=5, padx=5)
        ttk.Entry(fields_frame, textvariable=self.vars['ubicacion'], style='DialogEntry.TEntry').grid(row=5, column=1, sticky='ew', pady=5, padx=5)

        # Stock Mínimo
        ttk.Label(fields_frame, text="Stock Mínimo:", style='DialogField.TLabel').grid(row=6, column=0, sticky='w', pady=5, padx=5)
        ttk.Spinbox(fields_frame, from_=0, to=9999, textvariable=self.vars['stock_minimo'], width=10, style='DialogEntry.TEntry').grid(row=6, column=1, sticky='w', pady=5, padx=5)

        # Fecha de Ingreso
        ttk.Label(fields_frame, text="Fecha de Ingreso:", style='DialogField.TLabel').grid(row=7, column=0, sticky='w', pady=(10,0), padx=5)
        self.fecha_ingreso = DateEntry(fields_frame, width=20, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd') # ASSIGNED to self.fecha_ingreso
        self.fecha_ingreso.grid(row=7, column=1, sticky='w', pady=(10,0), padx=5)


        # Frame para la imagen
        image_frame = ttk.LabelFrame(main_frame, text="Imagen del Artículo", padding=10)
        image_frame.pack(fill='x', pady=20, padx=10)
        image_frame.columnconfigure(0, weight=1)

        # Label to display image path
        self.image_path_label = ttk.Label(image_frame, textvariable=self.image_path_var, style='DialogField.TLabel', wraplength=350) # wraplength for long paths
        self.image_path_label.grid(row=0, column=0, sticky='ew', pady=(0, 5), padx=5)
        self.image_path_var.set("No se ha seleccionado imagen")

        # Label para mostrar la imagen (preview) - centered
        self.image_label = ttk.Label(image_frame)
        self.image_label.grid(row=1, column=0, sticky='nsew', pady=10, padx=5) # sticky='nsew' to center in frame

        # Frame para botones de imagen
        image_buttons_frame = ttk.Frame(image_frame)
        image_buttons_frame.grid(row=2, column=0, pady=10)

        tk.Button(
            image_buttons_frame,
            text="Seleccionar Imagen",
            command=self.select_image,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=10,
            pady=5
        ).pack(side='left', padx=5)

        tk.Button(
            image_buttons_frame,
            text="Eliminar Imagen",
            command=self.remove_image,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=10,
            pady=5
        ).pack(side='left', padx=5)

        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10, padx=10)

        # Frame para botones de acción
        buttons_frame = ttk.Frame(self)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=15)

        tk.Button(
            buttons_frame,
            text="Guardar",
            command=self.save_producto,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        ).grid(row=0, column=0, sticky='ew', padx=5)

        tk.Button(
            buttons_frame,
            text="Cancelar",
            command=self.destroy,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        ).grid(row=0, column=1, sticky='ew', padx=5)


    def create_form_field(self, parent, label, var_name, row): # No longer used, kept for reference if needed
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.vars[var_name], width=40).grid(row=row, column=1, sticky='w', pady=5)


    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                image.thumbnail((200, 200), Image.Resampling.LANCZOS) # Thumbnail for preview
                photo = ImageTk.PhotoImage(image)

                self.image_label.configure(image=photo)
                self.image_label.image = photo
                self.current_image = file_path
                self.image_path_var.set(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")

    def remove_image(self):
        self.image_label.configure(image="")
        self.image_label.image = None
        self.current_image = None
        self.image_path_var.set("No se ha seleccionado imagen")

    def save_producto(self):
        # Validar campos obligatorios
        if not self.vars['nombre'].get().strip():
            messagebox.showerror("Error", "El nombre del artículo es obligatorio")
            return

        try:
            cantidad = int(self.vars['cantidad'].get())
            if cantidad < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")
            return

        try:
            stock_minimo = int(self.vars['stock_minimo'].get()) if self.vars['stock_minimo'].get() else None
            if stock_minimo is not None and stock_minimo < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El stock mínimo debe ser un número válido no negativo.")
            return


        # Preparar datos
        data = {
            'nombre': self.vars['nombre'].get().strip(),
            'descripcion': self.descripcion_text.get('1.0', 'end-1c'),
            'cantidad': cantidad,
            'imagen_path': self.current_image,
            'fecha_ingreso': self.fecha_ingreso.get_date().strftime('%Y-%m-%d'), # Get date from self.fecha_ingreso
            'categoria': self.vars['categoria'].get(),
            'ubicacion': self.vars['ubicacion'].get(),
            'stock_minimo': stock_minimo,
        }

        try:
            if self.mode == 'add':
                self.controller.agregar_articulo(**data)
                mensaje = "Artículo agregado correctamente"
                if self.on_save:
                    self.on_save()
            elif self.mode == 'edit':
                data['id'] = self.articulo[0]
                self.controller.actualizar_articulo(**data)
                mensaje = "Artículo actualizado correctamente"

            self.result = data
            messagebox.showinfo("Éxito", mensaje)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def cargar_datos_articulo(self):
        """Carga los datos del artículo para edición"""
        self.vars['nombre'].set(self.articulo[1])
        self.vars['descripcion'].set(self.articulo[2])
        self.vars['cantidad'].set(str(self.articulo[3]))
        self.vars['categoria'].set(self.articulo[7] or '')
        self.vars['ubicacion'].set(self.articulo[6] or '')
        self.vars['stock_minimo'].set(str(self.articulo[5]) if self.articulo[5] is not None else '')

        if self.articulo[4]:
            self.current_image = self.articulo[4]
            self.image_path_var.set(self.current_image)
            try:
                image = Image.open(self.current_image)
                image.thumbnail((200, 200), Image.Resampling.LANCZOS) # Thumbnail for preview
                photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=photo)
                self.image_label.image = photo
            except Exception as e:
                messagebox.showerror("Error al cargar imagen", str(e))


    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
