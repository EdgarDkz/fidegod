import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from tkcalendar import DateEntry
from datetime import datetime

class EditProductoDialog(tk.Toplevel):
    def __init__(self, parent, title, producto):
        super().__init__(parent)
        self.title(title)
        self.producto = producto
        self.result = None
        
        # Configuración de la ventana
        self.geometry('600x800')
        self.resizable(False, False)
        self.grab_set()
        
        # Variables - Corregido el orden de los índices
        self.nombre_var = tk.StringVar(value=producto[1])  # nombre
        self.descripcion_var = tk.StringVar(value=producto[2])  # descripcion
        self.cantidad_var = tk.StringVar(value=str(producto[3]))  # cantidad
        self.categoria_var = tk.StringVar(value=producto[5] if producto[5] else '')  # categoria
        self.ubicacion_var = tk.StringVar(value=producto[6] if producto[6] else '')  # ubicacion
        self.stock_minimo_var = tk.StringVar(value=str(producto[7]) if producto[7] else '')  # stock_minimo
        
        self.setup_styles()
        self.create_widgets()
        self.center_window()

    def setup_styles(self):
        style = ttk.Style(self)
        
        # Colores
        colors = {
            'primary': '#007bff',
            'success': '#28a745',
            'danger': '#dc3545',
            'surface': '#ffffff',
            'background': '#f8f9fa',
            'text': '#212529'
        }
        
        # Fuentes
        fonts = {
            'header': ('Segoe UI', 16, 'bold'),
            'subheader': ('Segoe UI', 14, 'bold'),
            'normal': ('Segoe UI', 10),
            'small': ('Segoe UI', 9)
        }
        
        # Configurar estilos
        style.configure('Dialog.TFrame',
                       background=colors['surface'])
        
        style.configure('Header.TLabel',
                       font=fonts['header'],
                       foreground=colors['text'],
                       background=colors['surface'])
        
        style.configure('Field.TLabel',
                       font=fonts['normal'],
                       foreground=colors['text'],
                       background=colors['surface'])
        
        style.configure('Success.TButton',
                       font=fonts['normal'],
                       background=colors['success'])
        
        style.configure('Danger.TButton',
                       font=fonts['normal'],
                       background=colors['danger'])

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self, style='Dialog.TFrame', padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Dialog.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="✏️ Editar Producto",
            style='Header.TLabel'
        ).pack(side='left')
        
        # Form container
        form_frame = ttk.Frame(main_frame, style='Dialog.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        # Fields
        fields = [
            ('Nombre del Producto', self.nombre_var, 'entry'),
            ('Descripción', self.descripcion_var, 'text'),
            ('Cantidad', self.cantidad_var, 'spinbox'),
            ('Stock Mínimo', self.stock_minimo_var, 'spinbox'),
            ('Ubicación', self.ubicacion_var, 'entry'),
            ('Categoría', self.categoria_var, 'combobox', ["Herramientas", "Electrónicos", "Muebles", "Otros"])
        ]
        
        self.widgets = {}
        for i, (label, var, widget_type, *args) in enumerate(fields):
            field_frame = ttk.Frame(form_frame, style='Dialog.TFrame')
            field_frame.pack(fill='x', pady=5)
            
            ttk.Label(
                field_frame,
                text=f"{label}:",
                style='Field.TLabel'
            ).pack(anchor='w')
            
            if widget_type == 'entry':
                widget = ttk.Entry(
                    field_frame,
                    textvariable=var,
                    width=50
                )
            elif widget_type == 'text':
                widget = tk.Text(
                    field_frame,
                    height=4,
                    width=48
                )
                widget.insert('1.0', var.get())
            elif widget_type == 'spinbox':
                widget = ttk.Spinbox(
                    field_frame,
                    from_=0,
                    to=9999,
                    textvariable=var,
                    width=10
                )
            elif widget_type == 'combobox':
                widget = ttk.Combobox(
                    field_frame,
                    textvariable=var,
                    values=args[0],
                    state='readonly',
                    width=47
                )
            
            widget.pack(anchor='w', pady=2)
            self.widgets[label] = widget
        
        # Botones de acción
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=20, pady=15)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        tk.Button(
            button_frame,
            text="Guardar",
            command=self.save_changes,
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
            command=self.destroy,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        ).grid(row=0, column=1, padx=5, sticky='ew')

    def save_changes(self):
        # Validar campos
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre del producto es obligatorio")
            return
        
        try:
            cantidad = int(self.cantidad_var.get())
            if cantidad < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero positivo")
            return
        
        try:
            stock_minimo = int(self.stock_minimo_var.get()) if self.stock_minimo_var.get() else None
            if stock_minimo is not None and stock_minimo < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El stock mínimo debe ser un número válido no negativo")
            return
        
        # Preparar datos
        self.result = {
            'id': self.producto[0],
            'nombre': self.nombre_var.get().strip(),
            'descripcion': self.widgets['Descripción'].get('1.0', 'end-1c').strip(),
            'cantidad': cantidad,
            'categoria': self.categoria_var.get(),
            'ubicacion': self.ubicacion_var.get(),
            'stock_minimo': stock_minimo
        }
        
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}') 