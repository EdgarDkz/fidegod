import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter

class ElegantTable(ttk.Frame):
    """
    Tabla de datos elegante que utiliza tipografía y efectos visuales
    en lugar de fondos de color para resaltar elementos.
    """
    
    def __init__(self, parent, theme_manager, columns, data=None, height=400, 
                 with_search=True, with_pagination=True, with_sorting=True, 
                 with_selection=True, with_context_menu=True, *args, **kwargs):
        """
        Inicializa la tabla elegante.
        
        Args:
            parent: Widget padre
            theme_manager: Gestor de temas
            columns: Lista de configuraciones de columnas [(id, name, width)]
            data: Datos iniciales para la tabla
            height: Altura de la tabla
            with_search: Si se debe incluir búsqueda
            with_pagination: Si se debe incluir paginación
            with_sorting: Si se debe permitir ordenar
            with_selection: Si se debe permitir selección
            with_context_menu: Si se debe incluir menú contextual
            *args, **kwargs: Argumentos adicionales para el Frame
        """
        super().__init__(parent, *args, **kwargs)
        
        self.theme_manager = theme_manager
        self.colors = theme_manager.get_color_palette()
        self.fonts = theme_manager.get_fonts()
        
        self.columns = columns
        self.data = data or []
        self.filtered_data = self.data.copy()
        self.current_page = 1
        self.items_per_page = 10
        self.sort_column = None
        self.sort_ascending = True
        
        # Opciones
        self.with_search = with_search
        self.with_pagination = with_pagination
        self.with_sorting = with_sorting
        self.with_selection = with_selection
        self.with_context_menu = with_context_menu
        
        # Configurar estilos
        self.setup_styles()
        
        # Configurar la interfaz
        self.setup_ui(height)
        
        # Cargar datos iniciales
        self.load_data(self.data)
    
    def setup_styles(self):
        """Configura los estilos personalizados para la tabla."""
        style = ttk.Style()
        
        # Estilo para el Treeview (tabla)
        style.configure(
            'Elegant.Treeview',
            background=self.colors['surface'],
            fieldbackground=self.colors['surface'],
            foreground=self.colors['text'],
            rowheight=40,
            borderwidth=0,
            font=self.fonts['body1']
        )
        
        # Estilo para los encabezados
        style.configure(
            'Elegant.Treeview.Heading',
            background=self.colors['background'],
            foreground=self.colors['primary'],
            relief='flat',
            borderwidth=0,
            font=self.fonts['h6']
        )
        
        # Configurar selección
        style.map(
            'Elegant.Treeview',
            background=[('selected', self.colors['selected'])],
            foreground=[('selected', self.colors['text'])]
        )
    
    def setup_ui(self, height):
        """Configura la interfaz de usuario de la tabla."""
        # Frame principal
        main_frame = ttk.Frame(self, style='Card.TFrame')
        main_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Barra de búsqueda
        if self.with_search:
            self.setup_search_bar(main_frame)
        
        # Contenedor de la tabla
        table_container = ttk.Frame(main_frame, style='TFrame')
        table_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(table_container, orient='vertical')
        y_scroll.pack(side='right', fill='y')
        
        x_scroll = ttk.Scrollbar(table_container, orient='horizontal')
        x_scroll.pack(side='bottom', fill='x')
        
        # Crear Treeview (tabla)
        self.tree = ttk.Treeview(
            table_container,
            columns=[col[0] for col in self.columns],
            show='headings',
            style='Elegant.Treeview',
            height=height // 40,  # Aproximadamente la altura en filas
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        self.tree.pack(fill='both', expand=True)
        
        # Configurar scrollbars
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        # Configurar columnas
        for col_id, col_name, col_width in self.columns:
            self.tree.heading(col_id, text=col_name, anchor='w')
            self.tree.column(col_id, width=col_width, anchor='w')
        
        # Configurar eventos
        if self.with_sorting:
            for col_id, _, _ in self.columns:
                self.tree.heading(col_id, command=lambda c=col_id: self.sort_by_column(c))
        
        if self.with_selection:
            self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        if self.with_context_menu:
            self.setup_context_menu()
        
        # Configurar efectos visuales
        self.tree.tag_configure('even_row', background=self.colors['background'])
        self.tree.tag_configure('odd_row', background=self.colors['surface'])
        
        # Configurar estados
        self.tree.tag_configure('pending', foreground=self.colors['warning'])
        self.tree.tag_configure('completed', foreground=self.colors['success'])
        self.tree.tag_configure('canceled', foreground=self.colors['error'])
        
        # Barra de paginación
        if self.with_pagination:
            self.setup_pagination(main_frame)
    
    def setup_search_bar(self, parent):
        """Configura la barra de búsqueda."""
        search_frame = ttk.Frame(parent, style='TFrame')
        search_frame.pack(fill='x', padx=10, pady=10)
        
        # Etiqueta
        search_label = ttk.Label(
            search_frame,
            text="🔍 Buscar:",
            style='TLabel',
            font=self.fonts['subtitle2']
        )
        search_label.pack(side='left', padx=(0, 10))
        
        # Campo de búsqueda
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            style='TEntry',
            width=30
        )
        search_entry.pack(side='left', fill='x', expand=True)
        
        # Botón de búsqueda
        search_button = ttk.Button(
            search_frame,
            text="Buscar",
            style='Primary.TButton',
            command=self.search_data
        )
        search_button.pack(side='left', padx=10)
        
        # Botón para limpiar búsqueda
        clear_button = ttk.Button(
            search_frame,
            text="Limpiar",
            style='Secondary.TButton',
            command=self.clear_search
        )
        clear_button.pack(side='left')
        
        # Vincular evento Enter
        search_entry.bind('<Return>', lambda e: self.search_data())
    
    def setup_pagination(self, parent):
        """Configura la barra de paginación."""
        pagination_frame = ttk.Frame(parent, style='TFrame')
        pagination_frame.pack(fill='x', padx=10, pady=10)
        
        # Información de página
        self.page_info_var = tk.StringVar(value="Página 1 de 1")
        page_info = ttk.Label(
            pagination_frame,
            textvariable=self.page_info_var,
            style='TLabel',
            font=self.fonts['caption']
        )
        page_info.pack(side='left')
        
        # Botones de navegación
        buttons_frame = ttk.Frame(pagination_frame, style='TFrame')
        buttons_frame.pack(side='right')
        
        # Botón primera página
        first_button = ttk.Button(
            buttons_frame,
            text="⏮",
            style='Secondary.TButton',
            command=self.go_to_first_page,
            width=3
        )
        first_button.pack(side='left', padx=2)
        
        # Botón página anterior
        prev_button = ttk.Button(
            buttons_frame,
            text="◀",
            style='Secondary.TButton',
            command=self.go_to_prev_page,
            width=3
        )
        prev_button.pack(side='left', padx=2)
        
        # Selector de página
        self.page_var = tk.StringVar(value="1")
        page_entry = ttk.Entry(
            buttons_frame,
            textvariable=self.page_var,
            style='TEntry',
            width=5
        )
        page_entry.pack(side='left', padx=2)
        page_entry.bind('<Return>', lambda e: self.go_to_page(int(self.page_var.get())))
        
        # Botón página siguiente
        next_button = ttk.Button(
            buttons_frame,
            text="▶",
            style='Secondary.TButton',
            command=self.go_to_next_page,
            width=3
        )
        next_button.pack(side='left', padx=2)
        
        # Botón última página
        last_button = ttk.Button(
            buttons_frame,
            text="⏭",
            style='Secondary.TButton',
            command=self.go_to_last_page,
            width=3
        )
        last_button.pack(side='left', padx=2)
        
        # Selector de elementos por página
        items_frame = ttk.Frame(pagination_frame, style='TFrame')
        items_frame.pack(side='right', padx=(0, 20))
        
        items_label = ttk.Label(
            items_frame,
            text="Elementos por página:",
            style='TLabel',
            font=self.fonts['caption']
        )
        items_label.pack(side='left', padx=(0, 5))
        
        self.items_var = tk.StringVar(value=str(self.items_per_page))
        items_combo = ttk.Combobox(
            items_frame,
            textvariable=self.items_var,
            values=["5", "10", "20", "50", "100"],
            state='readonly',
            style='TCombobox',
            width=5
        )
        items_combo.pack(side='left')
        items_combo.bind('<<ComboboxSelected>>', self.change_items_per_page)
    
    def setup_context_menu(self):
        """Configura el menú contextual."""
        self.context_menu = tk.Menu(self, tearoff=0, bg=self.colors['surface'], fg=self.colors['text'])
        self.context_menu.add_command(label="Ver detalles", command=self.view_details)
        self.context_menu.add_command(label="Editar", command=self.edit_item)
        self.context_menu.add_command(label="Eliminar", command=self.delete_item)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exportar selección", command=self.export_selection)
        
        # Vincular evento de clic derecho
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Muestra el menú contextual."""
        # Seleccionar el ítem bajo el cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def load_data(self, data):
        """
        Carga datos en la tabla.
        
        Args:
            data: Lista de datos para cargar
        """
        # Guardar datos
        self.data = data
        self.filtered_data = data.copy()
        
        # Actualizar tabla
        self.update_table()
    
    def update_table(self):
        """Actualiza la visualización de la tabla con los datos filtrados y paginados."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calcular paginación
        total_pages = max(1, (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page)
        self.current_page = min(self.current_page, total_pages)
        
        # Actualizar información de página
        self.page_info_var.set(f"Página {self.current_page} de {total_pages}")
        self.page_var.set(str(self.current_page))
        
        # Obtener datos de la página actual
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = self.filtered_data[start_idx:end_idx]
        
        # Insertar datos en la tabla
        for i, row in enumerate(page_data):
            # Determinar etiquetas para la fila
            tags = ('even_row',) if i % 2 == 0 else ('odd_row',)
            
            # Añadir etiqueta de estado si existe
            if 'estado' in row and isinstance(row, dict):
                estado = row['estado'].lower()
                if estado in ['pendiente', 'entregado', 'cancelado']:
                    tags = tags + (estado,)
            
            # Insertar fila
            if isinstance(row, dict):
                values = [row.get(col[0], "") for col in self.columns]
            else:
                values = row
            
            self.tree.insert('', 'end', values=values, tags=tags)
    
    def search_data(self):
        """Filtra los datos según el texto de búsqueda."""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            self.filtered_data = self.data.copy()
        else:
            # Filtrar datos
            self.filtered_data = []
            for row in self.data:
                # Convertir a string para búsqueda
                if isinstance(row, dict):
                    row_text = ' '.join(str(v).lower() for v in row.values())
                else:
                    row_text = ' '.join(str(v).lower() for v in row)
                
                # Añadir si coincide
                if search_text in row_text:
                    self.filtered_data.append(row)
        
        # Resetear a primera página y actualizar
        self.current_page = 1
        self.update_table()
    
    def clear_search(self):
        """Limpia el filtro de búsqueda."""
        self.search_var.set('')
        self.filtered_data = self.data.copy()
        self.current_page = 1
        self.update_table()
    
    def sort_by_column(self, column):
        """
        Ordena los datos por columna.
        
        Args:
            column: ID de la columna para ordenar
        """
        # Cambiar dirección si es la misma columna
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True
        
        # Obtener índice de la columna
        col_idx = next((i for i, col in enumerate(self.columns) if col[0] == column), 0)
        
        # Ordenar datos
        self.filtered_data.sort(
            key=lambda x: x[column] if isinstance(x, dict) else x[col_idx],
            reverse=not self.sort_ascending
        )
        
        # Actualizar tabla
        self.update_table()
        
        # Actualizar visual de encabezado
        for col in [c[0] for c in self.columns]:
            if col == column:
                direction = "▲" if self.sort_ascending else "▼"
                self.tree.heading(col, text=f"{next((c[1] for c in self.columns if c[0] == col), col)} {direction}")
            else:
                self.tree.heading(col, text=next((c[1] for c in self.columns if c[0] == col), col))
    
    def on_select(self, event):
        """Maneja el evento de selección de fila."""
        selected = self.tree.selection()
        if selected:
            # Obtener datos de la fila seleccionada
            item = selected[0]
            values = self.tree.item(item, 'values')
            
            # Aquí se puede implementar lógica adicional
            print(f"Seleccionado: {values}")
    
    def go_to_page(self, page):
        """
        Va a una página específica.
        
        Args:
            page: Número de página
        """
        total_pages = max(1, (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page)
        page = max(1, min(page, total_pages))
        
        self.current_page = page
        self.update_table()
    
    def go_to_first_page(self):
        """Va a la primera página."""
        self.go_to_page(1)
    
    def go_to_prev_page(self):
        """Va a la página anterior."""
        self.go_to_page(self.current_page - 1)
    
    def go_to_next_page(self):
        """Va a la página siguiente."""
        self.go_to_page(self.current_page + 1)
    
    def go_to_last_page(self):
        """Va a la última página."""
        total_pages = max(1, (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page)
        self.go_to_page(total_pages)
    
    def change_items_per_page(self, event=None):
        """Cambia el número de elementos por página."""
        try:
            self.items_per_page = int(self.items_var.get())
            self.current_page = 1
            self.update_table()
        except ValueError:
            pass
    
    def view_details(self):
        """Ver detalles del elemento seleccionado."""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Implementar lógica para ver detalles
        print("Ver detalles")
    
    def edit_item(self):
        """Editar el elemento seleccionado."""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Implementar lógica para editar
        print("Editar elemento")
    
    def delete_item(self):
        """Eliminar el elemento seleccionado."""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Implementar lógica para eliminar
        print("Eliminar elemento")
    
    def export_selection(self):
        """Exportar los elementos seleccionados."""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Implementar lógica para exportar
        print("Exportar selección")
    
    def get_selected_data(self):
        """
        Obtiene los datos de los elementos seleccionados.
        
        Returns:
            Lista de datos seleccionados
        """
        selected = self.tree.selection()
        selected_data = []
        
        for item in selected:
            values = self.tree.item(item, 'values')
            selected_data.append(values)
        
        return selected_data
    
    def get_all_data(self):
        """
        Obtiene todos los datos de la tabla.
        
        Returns:
            Lista de todos los datos
        """
        return self.data
    
    def get_filtered_data(self):
        """
        Obtiene los datos filtrados.
        
        Returns:
            Lista de datos filtrados
        """
        return self.filtered_data


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ejemplo de Tabla Elegante")
    
    # Datos de ejemplo
    columns = [
        ('id', 'ID', 50),
        ('nombre', 'Nombre', 150),
        ('articulo', 'Artículo', 200),
        ('direccion', 'Dirección', 250),
        ('municipio', 'Municipio', 120),
        ('estado', 'Estado', 100)
    ]
    
    data = [
        {'id': 1, 'nombre': 'Juan Pérez', 'articulo': 'Laptop HP', 'direccion': 'Calle 123', 'municipio': 'Linares', 'estado': 'Pendiente'},
        {'id': 2, 'nombre': 'María López', 'articulo': 'Monitor Dell', 'direccion': 'Av. Principal', 'municipio': 'Allende', 'estado': 'Entregado'},
        {'id': 3, 'nombre': 'Carlos Ruiz', 'articulo': 'Teclado Logitech', 'direccion': 'Plaza Central', 'municipio': 'Montemorelos', 'estado': 'Cancelado'},
        # Añadir más datos...
    ]
    
    # Crear tabla
    table = ElegantTable(
        root,
        None,  # Aquí iría el theme_manager
        columns,
        data,
        height=400
    )
    table.pack(fill='both', expand=True, padx=20, pady=20)
    
    root.mainloop() 