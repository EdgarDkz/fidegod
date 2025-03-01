import tkinter as tk
from tkinter import ttk
from styles.theme_manager import ThemeManager
from styles.elegant_widgets import ElegantWidgets

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FIDEGOD - Prueba de Componentes Elegantes")
        
        # Inicializar el gestor de temas
        self.theme_manager = ThemeManager(root)
        
        # Inicializar widgets elegantes
        self.elegant_widgets = ElegantWidgets(self.theme_manager)
        
        # Configurar la interfaz
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, style='TFrame', padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Prueba de Componentes Elegantes",
            style='Heading1.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Contenedor para los componentes
        components_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=20)
        components_frame.pack(fill='both', expand=True)
        
        # Etiqueta elegante
        label_frame = ttk.Frame(components_frame, style='TFrame', padding=10)
        label_frame.pack(fill='x', pady=10)
        
        ttk.Label(label_frame, text="Etiqueta Elegante:", style='TLabel').pack(anchor='w')
        
        elegant_label = self.elegant_widgets.create_elegant_label(
            label_frame,
            text="Esta es una etiqueta elegante con tipografía mejorada",
            font_style='h5',
            color=self.theme_manager.get_color_palette()['primary'],
            padding=(10, 5),
            height=40
        )
        elegant_label.pack(fill='x', pady=5)
        
        # Botón elegante
        button_frame = ttk.Frame(components_frame, style='TFrame', padding=10)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Label(button_frame, text="Botones Elegantes:", style='TLabel').pack(anchor='w')
        
        buttons_container = ttk.Frame(button_frame, style='TFrame')
        buttons_container.pack(fill='x', pady=5)
        
        # Botón primario
        primary_btn = self.elegant_widgets.create_elegant_button(
            buttons_container,
            text="Botón Primario",
            command=lambda: self.show_message("Botón Primario"),
            style_type='primary',
            width=150,
            height=40
        )
        primary_btn.pack(side='left', padx=5)
        
        # Botón secundario
        secondary_btn = self.elegant_widgets.create_elegant_button(
            buttons_container,
            text="Botón Secundario",
            command=lambda: self.show_message("Botón Secundario"),
            style_type='secondary',
            width=150,
            height=40
        )
        secondary_btn.pack(side='left', padx=5)
        
        # Botón outline
        outline_btn = self.elegant_widgets.create_elegant_button(
            buttons_container,
            text="Botón Outline",
            command=lambda: self.show_message("Botón Outline"),
            style_type='outline',
            width=150,
            height=40
        )
        outline_btn.pack(side='left', padx=5)
        
        # Indicadores de estado
        status_frame = ttk.Frame(components_frame, style='TFrame', padding=10)
        status_frame.pack(fill='x', pady=10)
        
        ttk.Label(status_frame, text="Indicadores de Estado:", style='TLabel').pack(anchor='w')
        
        statuses = ['pendiente', 'entregado', 'cancelado']
        
        for status in statuses:
            from views.elegant_status_indicator import ElegantStatusIndicator
            
            indicator = ElegantStatusIndicator(
                status_frame,
                self.theme_manager,
                status=status,
                size=24,
                with_text=True,
                with_icon=True,
                with_animation=status == 'pendiente'
            )
            indicator.pack(fill='x', pady=5)
    
    def show_message(self, message):
        """Muestra un mensaje cuando se hace clic en un botón."""
        print(f"Clic en: {message}")

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = TestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 