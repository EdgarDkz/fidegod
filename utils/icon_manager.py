import os
import tkinter as tk
from PIL import Image, ImageTk
import logging

class IconManager:
    """
    Gestor de iconos para la aplicación FIDEGOD.
    Proporciona una forma centralizada de cargar y acceder a los iconos.
    """
    
    def __init__(self):
        """Inicializa el gestor de iconos."""
        self.icons = {}
        self.icon_paths = []
        
        # Configurar rutas de búsqueda de iconos
        self._setup_icon_paths()
    
    def _setup_icon_paths(self):
        """Configura las rutas donde se buscarán los iconos."""
        # Obtener la ruta base del proyecto
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Añadir rutas de búsqueda en orden de prioridad
        self.icon_paths = [
            os.path.join(base_dir, 'assets', 'icons'),
            os.path.join(base_dir, 'views', 'icons'),
            os.path.join(base_dir, 'icons')
        ]
        
        # Crear directorios si no existen
        for path in self.icon_paths:
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                    logging.info(f"Directorio de iconos creado: {path}")
                except Exception as e:
                    logging.warning(f"No se pudo crear el directorio de iconos {path}: {e}")
    
    def load_icon(self, icon_name, size=(24, 24)):
        """
        Carga un icono desde el sistema de archivos.
        
        Args:
            icon_name: Nombre del archivo de icono (con o sin extensión)
            size: Tamaño deseado del icono como tupla (ancho, alto)
            
        Returns:
            Un objeto ImageTk.PhotoImage o None si no se encuentra el icono
        """
        # Si ya está cargado con el mismo tamaño, devolverlo
        icon_key = f"{icon_name}_{size[0]}x{size[1]}"
        if icon_key in self.icons:
            return self.icons[icon_key]
        
        # Extensiones de archivo a buscar
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.PNG']
        
        # Si el nombre ya tiene extensión, buscar solo ese archivo
        if any(icon_name.lower().endswith(ext.lower()) for ext in extensions):
            file_names = [icon_name]
            extensions = ['']  # No añadir extensión
        else:
            # Generar todas las posibles combinaciones de nombre y extensión
            file_names = [f"{icon_name}{ext}" for ext in extensions]
        
        # Buscar el icono en todas las rutas configuradas
        for path in self.icon_paths:
            for file_name in file_names:
                icon_path = os.path.join(path, file_name)
                if os.path.exists(icon_path):
                    try:
                        # Cargar y redimensionar la imagen
                        img = Image.open(icon_path)
                        img = img.resize(size, Image.LANCZOS)
                        photo_img = ImageTk.PhotoImage(img)
                        
                        # Almacenar en caché
                        self.icons[icon_key] = photo_img
                        
                        return photo_img
                    except Exception as e:
                        logging.warning(f"Error al cargar icono {icon_path}: {e}")
        
        # Si no se encuentra, crear un icono placeholder
        return self.create_placeholder_icon(size)
    
    def create_placeholder_icon(self, size=(24, 24)):
        """
        Crea un icono placeholder cuando no se puede cargar el original.
        
        Args:
            size: Tamaño del icono como tupla (ancho, alto)
            
        Returns:
            Un objeto ImageTk.PhotoImage con un icono placeholder
        """
        icon_key = f"placeholder_{size[0]}x{size[1]}"
        
        # Si ya existe un placeholder de este tamaño, devolverlo
        if icon_key in self.icons:
            return self.icons[icon_key]
        
        # Crear una imagen transparente como placeholder
        img = Image.new('RGBA', size, color=(240, 240, 240, 0))
        photo_img = ImageTk.PhotoImage(img)
        
        # Almacenar en caché
        self.icons[icon_key] = photo_img
        
        return photo_img
    
    def get_icon(self, icon_name, size=(24, 24)):
        """
        Obtiene un icono, cargándolo si es necesario.
        
        Args:
            icon_name: Nombre del archivo de icono
            size: Tamaño deseado del icono como tupla (ancho, alto)
            
        Returns:
            Un objeto ImageTk.PhotoImage
        """
        return self.load_icon(icon_name, size)
    
    def preload_icons(self, icon_names, size=(24, 24)):
        """
        Precarga un conjunto de iconos para uso posterior.
        
        Args:
            icon_names: Lista de nombres de iconos a precargar
            size: Tamaño deseado de los iconos
        """
        for icon_name in icon_names:
            self.load_icon(icon_name, size)
    
    def clear_cache(self):
        """Limpia la caché de iconos para liberar memoria."""
        self.icons.clear()

# Instancia global para uso en toda la aplicación
icon_manager = IconManager() 