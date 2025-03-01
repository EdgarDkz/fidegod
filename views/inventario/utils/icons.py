"""
Utilidades para el manejo de íconos en la aplicación.
"""

import os
from PIL import Image, ImageTk

class IconManager:
    """
    Clase para gestionar la carga y el manejo de íconos en la aplicación.
    """
    def __init__(self, icon_size=(20, 20)):
        """
        Inicializa el gestor de íconos.

        Args:
            icon_size: Tupla con el tamaño por defecto de los íconos (ancho, alto)
        """
        self.icon_size = icon_size
        self.icons = {}
        self.icon_paths = self._get_icon_paths()

    def _get_icon_paths(self):
        """
        Obtiene las rutas posibles donde pueden estar los íconos.

        Returns:
            Lista de rutas posibles para los íconos
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        
        return [
            os.path.join(current_dir, '..', 'icons'),  # views/inventario/icons
            os.path.join(base_dir, 'icons'),          # views/icons
            os.path.join(base_dir, '..', 'icons'),    # /icons
        ]

    def load_icon(self, filename, size=None):
        """
        Carga un ícono desde el sistema de archivos.

        Args:
            filename: Nombre del archivo del ícono
            size: Tupla opcional con el tamaño deseado del ícono (ancho, alto)

        Returns:
            ImageTk.PhotoImage con el ícono cargado o None si no se pudo cargar
        """
        if not size:
            size = self.icon_size

        # Si el ícono ya está cargado con el mismo tamaño, retornarlo
        icon_key = f"{filename}_{size[0]}x{size[1]}"
        if icon_key in self.icons:
            return self.icons[icon_key]

        # Buscar el ícono en las rutas posibles
        for icon_path in self.icon_paths:
            full_path = os.path.join(icon_path, filename)
            if os.path.exists(full_path):
                try:
                    image = Image.open(full_path)
                    image = image.resize(size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.icons[icon_key] = photo
                    return photo
                except Exception as e:
                    print(f"Error loading icon {filename}: {e}")
                    return None

        print(f"Warning: Icon {filename} not found in any of the search paths")
        return None

    def get_icon(self, name, size=None):
        """
        Obtiene un ícono por su nombre.

        Args:
            name: Nombre del ícono (sin extensión)
            size: Tupla opcional con el tamaño deseado del ícono (ancho, alto)

        Returns:
            ImageTk.PhotoImage con el ícono cargado o None si no se pudo cargar
        """
        # Mapeo de nombres de íconos a archivos
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

        if name in icon_files:
            return self.load_icon(icon_files[name], size)
        else:
            print(f"Warning: No icon mapping found for {name}")
            return None 