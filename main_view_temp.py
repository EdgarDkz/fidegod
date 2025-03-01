import tkinter as tk
from tkinter import ttk, messagebox
from views.personas_view import PersonasView
from views.inventario_view import InventarioView
from views.transacciones_view import TransaccionesView
from views.splash_screen import SplashScreen
from controllers.inventario_controller import InventarioController
import webbrowser
from datetime import datetime
import os
from PIL import Image, ImageTk

class MainView:
    """
    Clase principal que define la vista principal de la aplicación FIDEGOD.
    Gestiona la interfaz de usuario, la navegación entre módulos, temas, notificaciones,
    y la interacción del usuario.
    """
    def __init__(self, parent, theme_manager=None):
        """
        Inicializa la vista principal.

        Args:
            parent: El widget padre (normalmente la ventana principal Tk).
            theme_manager: Gestor de temas para la aplicación.
        """
        self.parent = parent
        self.theme_manager = theme_manager

        # Inicializar componentes y estilos
        self.style = ttk.Style()
        self.controller = InventarioController()
        self.notifications = []  # Lista para almacenar notificaciones

        # Usar colores del theme_manager si está disponible
        if theme_manager:
            self.colors = theme_manager.get_color_palette()
        else:
            # Paleta de colores base - Tema Pastel Suave (Naranja)
            self.colors = {
                'primary': '#f5a05f',           # Naranja pastel principal
                'primary_light': '#ffbe8b',     # Naranja pastel claro
                'primary_dark': '#e58a42',      # Naranja pastel oscuro
                'secondary': '#ffd4b8',         # Melocotón claro
                'background': '#fff5ed',        # Crema muy claro
                'surface': '#ffffff',           # Blanco puro
                'text': '#5d534c',              # Marrón grisáceo oscuro
                'text_secondary': '#8b8178',    # Marrón grisáceo medio
                'divider': '#f0e5de',           # Beige clarito
                'toolbar': '#fff9f4',           # Crema clarito
                'status_bar': '#fff9f4',        # Crema clarito
                'card': '#ffffff',              # Blanco
                'hover': '#ffe8d3',             # Melocotón muy claro
                'selected': '#ffd7b5',          # Melocotón claro seleccionado
                'disabled': '#e6e6e6',          # Gris claro
                'input': '#ffffff',             # Blanco
            } 