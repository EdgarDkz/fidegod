import tkinter as tk
from tkinter import ttk, messagebox
from controllers.transacciones_controller import TransaccionesController
from PIL import Image, ImageTk
import os
import tkinter.font
from tkinter import filedialog
import pandas as pd

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief='solid', borderwidth=1,
                         font=('Arial', '8', 'normal'))
        label.pack(ipadx=1, ipady=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class FilterPanel(ttk.Frame):
    def __init__(self, parent, transacciones_view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transacciones_view = transacciones_view

        # Variables para filtros
        self.articulo_var = tk.StringVar()
        self.tipo_var = tk.StringVar(value='Todos')
        self.fecha_desde_var = tk.StringVar()
        self.fecha_hasta_var = tk.StringVar()

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style(self)
        base_font = ('Segoe UI', 11)

        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#333')
        style.configure('Surface.TFrame', background='#f7f7f7', relief='flat', borderwidth=0)
        style.configure('Filter.TLabel', font=base_font, foreground='#555')
        style.configure('Modern.TEntry', font=base_font, padding=10, borderwidth=1, relief='solid')
        style.configure('Modern.TCombobox', font=base_font, padding=10, borderwidth=1, relief='solid')
        style.configure('Card.TFrame', background='#f0f2f5', relief='flat', borderwidth=0, padding=15)
        style.configure('SectionHeader.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#333', background='#f0f2f5')

    def create_widgets(self):
        filter_container = ttk.Frame(self, style='Card.TFrame', padding=20)
        filter_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        filter_container.columnconfigure(0, weight=1)

        # Header
        header_frame = ttk.Frame(filter_container, style='Surface.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(
            header_frame,
            text="🔍 Filtros de Búsqueda",
            style='Header.TLabel',
            padding=(0, 10, 0, 10)
        ).grid(row=0, column=0, sticky='w')

        ttk.Separator(header_frame, orient='horizontal').grid(row=1, column=0, sticky='ew', pady=(10, 20))

        # Contenedor de filtros
        filters_group = ttk.Frame(filter_container, style='Surface.TFrame', padding=15)
        filters_group.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        filters_group.columnconfigure(0, weight=1)

        # Configurar filtros
        filters_data = [
            ('Artículo:', 'articulo_var', '📦'),
            ('Tipo:', 'tipo_var', '🔄'),
            ('Fecha Desde:', 'fecha_desde_var', '📅'),
            ('Fecha Hasta:', 'fecha_hasta_var', '📅')
        ]

        for i, (label_text, var_name, icon) in enumerate(filters_data):
            filter_frame = ttk.Frame(filters_group, style='Surface.TFrame')
            filter_frame.grid(row=i, column=0, sticky='ew', pady=(10, 10))

            ttk.Label(
                filter_frame,
                text=f"{icon} {label_text}",
                style='Filter.TLabel',
                padding=(5, 5, 5, 5)
            ).grid(row=0, column=0, sticky='nw')

            if var_name == 'tipo_var':
                combo = ttk.Combobox(
                    filter_frame,
                    textvariable=getattr(self, var_name),
                    values=["Todos", "Entrada", "Salida"],
                    state='readonly',
                    style='Modern.TCombobox'
                )
                combo.grid(row=1, column=0, sticky='ew', padx=(0, 10), pady=(5,10))
                combo.bind('<<ComboboxSelected>>', self.update_filters)
            elif 'fecha' in var_name:
                from tkcalendar import DateEntry
                date_entry = DateEntry(
                    filter_frame,
                    width=20,
                    background='darkblue',
                    foreground='white',
                    date_pattern='yyyy-mm-dd',
                    font=('Segoe UI', 11)
                )
                date_entry.grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(5,10))
                date_entry.bind('<<DateEntrySelected>>', self.update_filters)
            else:
                entry = ttk.Entry(
                    filter_frame,
                    textvariable=getattr(self, var_name),
                    style='Modern.TEntry'
                )
                entry.grid(row=1, column=0, sticky='ew', padx=(0, 10), pady=(5,10))
                entry.bind('<KeyRelease>', self.update_filters)

    def update_filters(self, event=None):
        self.transacciones_view.update_filters_from_panel(
            articulo_filter=self.articulo_var.get(),
            tipo_filter=self.tipo_var.get(),
            fecha_desde_filter=self.fecha_desde_var.get(),
            fecha_hasta_filter=self.fecha_hasta_var.get()
        )

class TransaccionesView:
    def __init__(self, parent, style=None):
        self.parent = parent
        self.style = style
        self.controller = TransaccionesController()
        
        # Paleta de colores base
        self.color_palette = {
            'primary': '#fb8404',           # Naranja principal
            'primary_light': '#fcad58',     # Naranja más claro
            'primary_dark': '#cb6304',      # Naranja oscuro
            'secondary': '#76849a',         # Gris medio
            'background': '#f4efdf',        # Beige claro
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
            'text_header': '#181d22'      # Gris oscuro/negro
        }
        
        # Cargar iconos primero
        self.load_icons()
        
        # Configuración inicial
        self.setup_styles()
        self.setup_ui()
        self.load_data()

    def get_theme_colors(self, theme):
        themes = {
            "light": {
                'primary': '#007BFF',
                'surface': '#FFFFFF',
                'background': '#F8F9FA',
                'text_header': '#333333',
                'text_section_header': '#333333',
                'text_filter_label': '#777777',
                'text_value_label': '#333333',
                'button_success': '#28A745',
                'button_primary': '#007BFF',
                'button_danger': '#DC3545',
                'button_warning': '#FFC107',
                'button_info': '#17A2B8',
                'border': '#DEE2E6',
                'hover': '#E9ECEF',
                'treeview_selection_bg': '#E1E1E1',
                'treeview_selection_fg': '#000000'
            },
            "dark": {
                'primary': '#4FC3F7',
                'surface': '#333333',
                'background': '#222222',
                'text_header': '#FFFFFF',
                'text_section_header': '#FFFFFF',
                'text_filter_label': '#CCCCCC',
                'text_value_label': '#FFFFFF',
                'button_success': '#689F38',
                'button_primary': '#0288D1',
                'button_danger': '#E53935',
                'button_warning': '#FFA000',
                'button_info': '#2196F3',
                'border': '#495057',
                'hover': '#495057',
                'treeview_selection_bg': '#2E4053',
                'treeview_selection_fg': '#FFFFFF'
            }
        }
        return themes[theme]

    def load_icons(self):
        """Carga todos los iconos necesarios para la interfaz."""
        icon_files = {
            'edit': 'editar.png',
            'delete': 'eliminar.png',
            'confirm': 'confirmar.png',
            'cancel': 'cancelar.png',
            'pending': 'pendiente.png',
            'out': 'salida.png',
            'in': 'recibe.png',
            'user': 'user.png',
            'article': 'articulo.png',
            'phone': 'telefono.png',
            'location': 'localizacion.png',
            'calendar': 'calendar.png',
            'excel': 'excel.png',
            'clean': 'limpiar.png',
            'apply': 'aplicar.png',
            'delete1': 'eliminar1.png',
            'undo': 'undo.png',
            'redo': 'redo.png',
            'add': 'agregar.png',
            'search': 'buscar.png'
        }

        self.icons = {}
        for key, filename in icon_files.items():
            icon = self.load_and_resize_icon(filename)
            if icon:
                self.icons[key] = icon
            else:
                print(f"Warning: Could not load icon {filename}")

    def setup_styles(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        
        # Configurar estilos base
        style.configure('Surface.TFrame',
                       background=self.color_palette['surface'],
                       relief='flat',
                       borderwidth=0)
                       
        style.configure('Header.TLabel',
                       font=('Segoe UI', 22, 'bold'),
                       background=self.color_palette['surface'],
                       foreground=self.color_palette['text_header'])
                       
        # Estilos para botones
        button_styles = [
            ('Success.TButton', self.color_palette['success']),
            ('Primary.TButton', self.color_palette['primary']),
            ('Danger.TButton', self.color_palette['error']),
            ('Warning.TButton', self.color_palette['warning']),
            ('Info.TButton', self.color_palette['info'])
        ]

        for style_name, color in button_styles:
            style.configure(style_name,
                          font=('Segoe UI', 12, 'bold'),
                          background=color,
                          foreground='white',
                          padding=10)

        # Estilo para el Treeview
        style.configure('Treeview',
                       background=self.color_palette['surface'],
                       fieldbackground=self.color_palette['surface'],
                       font=('Segoe UI', 11),
                       rowheight=35)

        style.configure('Treeview.Heading',
                       font=('Segoe UI', 12, 'bold'),
                       background=self.color_palette['background'],
                       relief='flat',
                       padding=10)

        style.map('Treeview',
                 background=[('selected', self.color_palette['primary_light'])],
                 foreground=[('selected', self.color_palette['primary_dark'])])

        # Estilos para etiquetas de campos
        style.configure('Field.TLabel',
                       font=('Segoe UI', 11),
                       background=self.color_palette['surface'],
                       foreground=self.color_palette['text_secondary'])

        style.configure('Value.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       background=self.color_palette['surface'],
                       foreground=self.color_palette['text'])

        # Estilo para marcos de tarjetas
        style.configure('Card.TFrame',
                       background=self.color_palette['surface'],
                       relief='solid',
                       borderwidth=1)

        style.configure('SectionHeader.TLabel',
                       font=('Segoe UI', 14, 'bold'),
                       background=self.color_palette['surface'],
                       foreground=self.color_palette['text_header'])

    def setup_ui(self):
        # Configurar grid principal
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Frame principal
        self.main_frame = ttk.Frame(self.parent, style='Surface.TFrame')
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=0, pady=5)

        # Configurar columnas del main_frame
        self.main_frame.columnconfigure(0, minsize=280, weight=0)  # Panel izquierdo
        self.main_frame.columnconfigure(1, minsize=650, weight=1)  # Panel central
        self.main_frame.columnconfigure(2, minsize=280, weight=0)  # Panel derecho
        self.main_frame.rowconfigure(0, weight=1)

        # Configurar paneles
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        left_panel = tk.Frame(self.main_frame, bg=self.color_palette['surface'])
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)

        # Usar FilterPanel
        self.filter_panel = FilterPanel(left_panel, self)
        self.filter_panel.grid(row=0, column=0, sticky='nsew')

        # Frame para botones
        button_frame = tk.Frame(left_panel, bg=self.color_palette['surface'])
        button_frame.grid(row=1, column=0, sticky='ew', pady=(15, 0))
        button_frame.columnconfigure((0, 1), weight=1)

        # Botones de filtro
        tk.Button(
            button_frame,
            text="Limpiar",
            image=self.icons['clean'],
            compound='left',
            command=self.clear_filters,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 11),
            padx=15,
            pady=8
        ).grid(row=0, column=0, padx=5, sticky='ew')

        tk.Button(
            button_frame,
            text="Aplicar",
            image=self.icons['apply'],
            compound='left',
            command=self.apply_filters,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 11),
            padx=15,
            pady=8
        ).grid(row=0, column=1, padx=5, sticky='ew')

        # Botón de exportar
        tk.Button(
            left_panel,
            text="Exportar a Excel",
            image=self.icons['excel'],
            compound='left',
            command=self.export_to_excel,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 11),
            padx=15,
            pady=8
        ).grid(row=2, column=0, sticky='ew', pady=(15, 0))

    def setup_center_panel(self):
        center_panel = ttk.Frame(self.main_frame, style='Surface.TFrame')
        center_panel.grid(row=0, column=1, sticky='nsew', padx=10)
        center_panel.columnconfigure(0, weight=1)
        center_panel.rowconfigure(2, weight=1)

        # Header
        header_frame = ttk.Frame(center_panel, style='Surface.TFrame', padding=15)
        header_frame.grid(row=0, column=0, sticky='ew')
        
        ttk.Label(
            header_frame,
            text="Registro de Transacciones",
            style='Header.TLabel'
        ).grid(row=0, column=0, sticky='w')

        # Barra de herramientas
        toolbar_frame = ttk.Frame(center_panel, style='Surface.TFrame', padding=10)
        toolbar_frame.grid(row=1, column=0, sticky='ew')

        # Botones de acción
        buttons = [
            ("Nueva Transacción", self.add_transaccion, 'Success.TButton', self.icons['add']),
            ("Editar", self.edit_transaccion, 'Primary.TButton', self.icons['edit']),
            ("Eliminar", self.delete_transaccion, 'Danger.TButton', self.icons['delete'])
        ]

        for i, (text, command, style, icon) in enumerate(buttons):
            btn = ttk.Button(
                toolbar_frame,
                text=text,
                command=command,
                style=style,
                image=icon,
                compound='left'
            )
            btn.grid(row=0, column=i, padx=8, pady=8)
            Tooltip(btn, f"{text}")

        # Treeview
        tree_frame = ttk.Frame(center_panel, style='Surface.TFrame')
        tree_frame.grid(row=2, column=0, sticky='nsew')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame)
        y_scroll.grid(row=0, column=1, sticky='ns')
        
        x_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        x_scroll.grid(row=1, column=0, sticky='ew')

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Artículo', 'Tipo', 'Cantidad', 'Stock Anterior', 
                    'Stock Actual', 'Fecha', 'Hora', 'Usuario'),
            show='headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Configurar columnas
        column_widths = {
            'ID': 50,
            'Artículo': 200,
            'Tipo': 100,
            'Cantidad': 100,
            'Stock Anterior': 120,
            'Stock Actual': 120,
            'Fecha': 100,
            'Hora': 100,
            'Usuario': 150
        }

        for col in self.tree['columns']:
            self.tree.column(col, width=column_widths.get(col, 100), anchor='w')
            self.tree.heading(col, text=col, anchor='w')

        # Configurar scrollbars
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        # Eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Button-3>', self.show_context_menu)

    def setup_right_panel(self):
        right_panel = ttk.Frame(self.main_frame, style='Detail.TFrame', padding=15)
        right_panel.grid(row=0, column=2, sticky='nsew', padx=(10, 0))
        right_panel.columnconfigure(0, weight=1)

        # Header
        ttk.Label(
            right_panel,
            text="Detalles de la Transacción",
            style='Section.TLabel'
        ).grid(row=0, column=0, sticky='w', pady=(0, 15))

        # Separador después del título
        ttk.Separator(
            right_panel,
            orient='horizontal',
            style='Detail.TSeparator'
        ).grid(row=1, column=0, sticky='ew', pady=(0, 15))

        # Detalles
        details_frame = ttk.LabelFrame(
            right_panel,
            text="Información de la Transacción",
            style='Detail.TLabelframe',
            padding=15
        )
        details_frame.grid(row=2, column=0, sticky='ew')

        # Campos de detalles
        self.detail_labels = {}
        fields = [
            ('ID Transacción', 'id', '🔢'),
            ('Artículo', 'articulo', '📦'),
            ('Tipo', 'tipo', '🔄'),
            ('Cantidad', 'cantidad', '📊'),
            ('Stock Anterior', 'stock_anterior', '📈'),
            ('Stock Actual', 'stock_actual', '📉'),
            ('Fecha', 'fecha', '📅'),
            ('Hora', 'hora', '⏰'),
            ('Usuario', 'usuario', '👤')
        ]

        for i, (label, key, icon) in enumerate(fields):
            field_frame = ttk.Frame(details_frame, style='Detail.TFrame')
            field_frame.grid(row=i, column=0, columnspan=2, sticky='ew', pady=5)

            ttk.Label(
                field_frame,
                text=f"{icon} {label}:",
                style='Field.TLabel'
            ).pack(side='left', padx=(0, 15))

            self.detail_labels[key] = ttk.Label(
                field_frame,
                text="",
                style='Value.TLabel'
            )
            self.detail_labels[key].pack(side='left')

            # Separador entre campos
            if i < len(fields) - 1:  # No añadir separador después del último campo
                ttk.Separator(
                    details_frame,
                    orient='horizontal',
                    style='Detail.TSeparator'
                ).grid(row=i+1, column=0, columnspan=2, sticky='ew', pady=8)

        # Estadísticas
        stats_frame = ttk.LabelFrame(
            right_panel,
            text="Estadísticas",
            style='Detail.TLabelframe',
            padding=15
        )
        stats_frame.grid(row=3, column=0, sticky='ew', pady=(20, 0))

        self.stats_labels = {}
        stats = [
            ('Total Entradas', 'total_entradas', '📥'),
            ('Total Salidas', 'total_salidas', '📤'),
            ('Balance', 'balance', '⚖️')
        ]

        for i, (label, key, icon) in enumerate(stats):
            stat_frame = ttk.Frame(stats_frame, style='Detail.TFrame')
            stat_frame.grid(row=i, column=0, columnspan=2, sticky='ew', pady=5)

            ttk.Label(
                stat_frame,
                text=f"{icon} {label}:",
                style='Field.TLabel'
            ).pack(side='left', padx=(0, 15))

            self.stats_labels[key] = ttk.Label(
                stat_frame,
                text="0",
                style='Value.TLabel'
            )
            self.stats_labels[key].pack(side='left')

            # Separador entre estadísticas
            if i < len(stats) - 1:  # No añadir separador después de la última estadística
                ttk.Separator(
                    stats_frame,
                    orient='horizontal',
                    style='Detail.TSeparator'
                ).grid(row=i+1, column=0, columnspan=2, sticky='ew', pady=8)

    def load_and_resize_icon(self, filename, size=(20, 20)):
        """Carga y redimensiona iconos desde la carpeta de iconos."""
        try:
            # Construir la ruta al archivo de icono
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, 'icons', filename)
            
            if not os.path.exists(icon_path):
                print(f"Warning: Icon {filename} not found at {icon_path}")
                return None

            image = Image.open(icon_path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading icon {filename}: {e}")
            return None

    def update_filters_from_panel(self, articulo_filter, tipo_filter, fecha_desde_filter, fecha_hasta_filter):
        self.articulo_filter = articulo_filter.lower()
        self.tipo_filter = tipo_filter
        self.fecha_desde_filter = fecha_desde_filter
        self.fecha_hasta_filter = fecha_hasta_filter
        self.filter_treeview()

    def clear_filters(self):
        self.filter_panel.articulo_var.set('')
        self.filter_panel.tipo_var.set('Todos')
        self.filter_panel.fecha_desde_var.set('')
        self.filter_panel.fecha_hasta_var.set('')
        self.load_data()

    def apply_filters(self):
        self.filter_treeview()

    def filter_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        transacciones = self.controller.get_transacciones()
        
        for transaccion in transacciones:
            if self.matches_filters(transaccion):
                self.tree.insert('', 'end', values=transaccion)

    def matches_filters(self, transaccion):
        # Implementar lógica de filtrado aquí
        return True  # Por ahora acepta todas las transacciones

    def on_select(self, event):
        if selected := self.tree.selection():
            transaccion = self.tree.item(selected[0])['values']
            self.update_details(transaccion)

    def update_details(self, transaccion):
        # Actualizar labels de detalles
        fields = ['id', 'articulo', 'tipo', 'cantidad', 'stock_anterior',
                 'stock_actual', 'fecha', 'hora', 'usuario']
        
        for i, field in enumerate(fields):
            self.detail_labels[field].config(text=str(transaccion[i]))

    def show_context_menu(self, event):
        # Implementar menú contextual aquí
        pass

    def add_transaccion(self):
        # Implementar agregar transacción
        pass

    def edit_transaccion(self):
        # Implementar editar transacción
        pass

    def delete_transaccion(self):
        # Implementar eliminar transacción
        pass

    def export_to_excel(self):
        try:
            transacciones = self.controller.get_transacciones()
            df = pd.DataFrame(transacciones, columns=self.tree['columns'])
            
            file_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Éxito", "Datos exportados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        transacciones = self.controller.get_transacciones()
        for transaccion in transacciones:
            self.tree.insert('', 'end', values=transaccion)