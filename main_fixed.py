import tkinter as tk
from tkinter import ttk, messagebox
from controllers.inventario_controller import InventarioController
from controllers.personas_controller import PersonasController
from controllers.transacciones_controller import TransaccionesController
from views.personas_view import PersonasView
from views.inventario_view import InventarioView
from views.transacciones_view import TransaccionesView

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FIDEGOD - Sistema de Gestión")
        self.root.state('zoomed')  # Maximizar la ventana
        
        # Configurar el estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar colores
        self.colors = {
            'primary': '#fb8404',           # Naranja principal
            'primary_light': '#fcad58',     # Naranja más claro
            'primary_dark': '#cb6304',      # Naranja oscuro
            'secondary': '#76849a',         # Gris medio
            'background': '#f4efdf',        # Beige claro
            'surface': '#FFFFFF',           # Blanco
            'text': '#181d22',              # Gris oscuro/negro
            'text_secondary': '#76849a',    # Gris medio
        }
        
        # Configurar estilos
        self.setup_styles()
        
        # Crear el notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Inicializar controladores
        self.inventario_controller = InventarioController()
        self.personas_controller = PersonasController()
        self.transacciones_controller = TransaccionesController()
        
        # Crear frames para cada pestaña
        self.personas_frame = ttk.Frame(self.notebook)
        self.inventario_frame = ttk.Frame(self.notebook)
        self.transacciones_frame = ttk.Frame(self.notebook)
        
        # Añadir pestañas al notebook
        self.notebook.add(self.personas_frame, text="Clientes y Pedidos")
        self.notebook.add(self.inventario_frame, text="Inventario")
        self.notebook.add(self.transacciones_frame, text="Transacciones")
        
        # Inicializar vistas
        self.personas_view = PersonasView(self.personas_frame, self.style)
        self.inventario_view = InventarioView(self.inventario_frame, self.inventario_controller)
        self.transacciones_view = TransaccionesView(self.transacciones_frame, self.style)
        
        # Configurar barra de estado
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(10, 5))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Sistema listo")
        self.status_label.pack(side=tk.LEFT)
        
        self.date_label = ttk.Label(self.status_bar, text=self.get_current_date())
        self.date_label.pack(side=tk.RIGHT)
    
    def setup_styles(self):
        """Configura los estilos para la aplicación."""
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
    
    def get_current_date(self):
        """Retorna la fecha actual formateada."""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M")

def main():
    try:
        root = tk.Tk()
        app = MainApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar la aplicación: {str(e)}")
        print(f"Error detallado: {e}")

if __name__ == "__main__":
    main() 