import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter

class ElegantWidgets:
    """
    Clase que proporciona widgets elegantes y personalizados para la aplicación.
    """
    
    def __init__(self, theme_manager):
        """
        Inicializa la clase de widgets elegantes.
        
        Args:
            theme_manager: Instancia del gestor de temas.
        """
        self.theme_manager = theme_manager
        self.colors = theme_manager.get_color_palette()
        self.fonts = theme_manager.get_fonts()
        
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
                            icon=None, underline=False, padding=(0, 0), **kwargs):
        """
        Crea una etiqueta elegante con opciones de estilo avanzadas.
        
        Args:
            parent: Widget padre
            text: Texto de la etiqueta
            font_style: Estilo de fuente ('h1', 'body1', etc.)
            color: Color del texto (opcional)
            icon: Ruta al icono (opcional)
            underline: Si se debe subrayar el texto
            padding: Padding (x, y)
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
            
            # Si hay icono, ajustar posición
            if icon:
                try:
                    icon_img = Image.open(icon)
                    icon_img = icon_img.resize((20, 20), Image.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_img)
                    canvas.icon_image = icon_photo  # Mantener referencia
                    
                    # Calcular posiciones
                    icon_x = pad_x
                    text_x = icon_x + 25
                    
                    canvas.create_image(icon_x, height // 2, image=icon_photo, anchor='w')
                    canvas.create_text(text_x, height // 2, text=text, fill=color, 
                                      font=self.fonts[font_style], anchor='w')
                except Exception as e:
                    # Si hay error con el icono, mostrar solo texto
                    canvas.create_text(pad_x, height // 2, text=text, fill=color, 
                                      font=self.fonts[font_style], anchor='w')
            else:
                # Solo texto
                canvas.create_text(pad_x, height // 2, text=text, fill=color, 
                                  font=self.fonts[font_style], anchor='w')
            
            # Si se debe subrayar, dibujar línea
            if underline:
                text_width = len(text) * (self.fonts[font_style][1] * 0.6)  # Estimación del ancho
                y_pos = height // 2 + self.fonts[font_style][1] // 2 + 2
                
                if icon:
                    x_start = text_x
                else:
                    x_start = pad_x
                
                canvas.create_line(
                    x_start, y_pos, 
                    x_start + text_width, y_pos,
                    fill=color, width=1
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
        if status.lower() == 'pending':
            color = self.colors['warning']
            text = "Pendiente"
        elif status.lower() == 'success':
            color = self.colors['success']
            text = "Completado"
        elif status.lower() == 'error':
            color = self.colors['error']
            text = "Error"
        elif status.lower() == 'canceled':
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
    
    def create_search_entry(self, parent, placeholder="Buscar...", command=None, **kwargs):
        """
        Crea un campo de búsqueda elegante.
        
        Args:
            parent: Widget padre
            placeholder: Texto de placeholder
            command: Función a ejecutar al buscar
            **kwargs: Argumentos adicionales
            
        Returns:
            El frame con el campo de búsqueda
        """
        # Crear frame contenedor
        search_frame = ttk.Frame(parent, style='Card.TFrame')
        search_frame.pack_propagate(False)
        
        # Configurar altura mínima
        if 'height' not in kwargs:
            kwargs['height'] = 40
        
        # Crear variable para el texto
        search_var = tk.StringVar()
        
        # Crear entry
        entry = ttk.Entry(
            search_frame,
            textvariable=search_var,
            style='TEntry',
            **kwargs
        )
        entry.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=5)
        
        # Mostrar placeholder
        entry.insert(0, placeholder)
        entry.config(foreground=self.colors['text_tertiary'])
        
        # Crear botón de búsqueda
        search_button = ttk.Button(
            search_frame,
            text="🔍",
            style='Secondary.TButton',
            command=lambda: command(search_var.get()) if command else None
        )
        search_button.pack(side='right', padx=5, pady=5)
        
        # Funciones para manejar el placeholder
        def on_entry_focus_in(event):
            if search_var.get() == placeholder:
                entry.delete(0, 'end')
                entry.config(foreground=self.colors['text'])
        
        def on_entry_focus_out(event):
            if not search_var.get():
                entry.insert(0, placeholder)
                entry.config(foreground=self.colors['text_tertiary'])
        
        # Vincular eventos
        entry.bind("<FocusIn>", on_entry_focus_in)
        entry.bind("<FocusOut>", on_entry_focus_out)
        entry.bind("<Return>", lambda event: command(search_var.get()) if command else None)
        
        return search_frame
    
    def create_filter_panel(self, parent, filters, apply_command=None, clear_command=None):
        """
        Crea un panel de filtros elegante.
        
        Args:
            parent: Widget padre
            filters: Lista de configuraciones de filtros [(label, var, type, values)]
            apply_command: Función para aplicar filtros
            clear_command: Función para limpiar filtros
            
        Returns:
            El panel de filtros
        """
        # Crear frame contenedor
        filter_frame = ttk.Frame(parent, style='Filter.TFrame')
        
        # Título del panel
        title_label = ttk.Label(
            filter_frame,
            text="🔍 Filtros de Búsqueda",
            style='FilterTitle.TLabel'
        )
        title_label.pack(anchor='w', pady=(0, 15))
        
        # Crear widgets para cada filtro
        for label, var, filter_type, values in filters:
            # Frame para el filtro
            row_frame = ttk.Frame(filter_frame, style='TFrame')
            row_frame.pack(fill='x', pady=(0, 10))
            
            # Etiqueta
            filter_label = ttk.Label(
                row_frame,
                text=label,
                style='FilterLabel.TLabel'
            )
            filter_label.pack(side='top', anchor='w', pady=(0, 5))
            
            # Widget según el tipo
            if filter_type == 'entry':
                widget = ttk.Entry(
                    row_frame,
                    textvariable=var,
                    style='TEntry'
                )
                widget.pack(fill='x')
            elif filter_type == 'combobox':
                widget = ttk.Combobox(
                    row_frame,
                    textvariable=var,
                    values=values,
                    state='readonly',
                    style='TCombobox'
                )
                widget.pack(fill='x')
            
            # Separador
            ttk.Separator(filter_frame, orient='horizontal').pack(fill='x', pady=(0, 10))
        
        # Panel de botones
        button_panel = ttk.Frame(filter_frame, style='TFrame')
        button_panel.pack(fill='x', pady=(10, 0))
        
        # Botón limpiar
        clear_btn = self.create_elegant_button(
            button_panel,
            text="Limpiar Filtros",
            command=clear_command,
            style_type='secondary',
            width=120,
            height=35
        )
        clear_btn.pack(side='left', padx=(0, 5))
        
        # Botón aplicar
        apply_btn = self.create_elegant_button(
            button_panel,
            text="Aplicar Filtros",
            command=apply_command,
            style_type='primary',
            width=120,
            height=35
        )
        apply_btn.pack(side='left')
        
        return filter_frame 