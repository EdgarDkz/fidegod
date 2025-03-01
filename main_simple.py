import tkinter as tk
from tkinter import ttk
from views.main_view import MainView

def main():
    root = tk.Tk()
    
    # Configurar la ventana principal
    root.title("FIDEGOD - Sistema de Gestión")
    
    # Crear la aplicación principal
    app = MainView(root)
    
    # Configurar tamaño y posición de la ventana principal
    root.state('zoomed')  # Maximizar la ventana
    
    # Iniciar el loop principal
    root.mainloop()

if __name__ == "__main__": 
    main() 