import tkinter as tk
import os
import sys
import time
import traceback
import logging
from views.main_view import MainView
from styles.theme_manager import ThemeManager
from styles.elegant_styles import get_elegant_styles
from views.splash_screen import SplashScreen
from utils.config import config
from utils.error_handler import error_handler

def initialize_application(root, splash_screen=None):
    """
    Inicializa la aplicación principal.
    
    Args:
        root: La ventana raíz de Tkinter
        splash_screen: Pantalla de inicio opcional para mostrar progreso
    
    Returns:
        La instancia de MainView creada
    """
    try:
        # Configurar la ventana principal
        app_config = config.get('app')
        root.title(f"{app_config['name']} - {app_config['description']}")
        
        # Configurar el tamaño de la ventana
        ui_config = config.get('ui')
        if ui_config.get('maximized', True):
            root.state('zoomed')  # Maximizar en Windows
        else:
            window_size = ui_config.get('window_size', {'width': 1280, 'height': 720})
            root.geometry(f"{window_size['width']}x{window_size['height']}")
        
        # Configurar el icono de la aplicación
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views', 'icons', 'fide.PNG')
            if os.path.exists(icon_path):
                root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            logging.warning(f"No se pudo cargar el icono de la aplicación: {e}")
        
        # Crear directorios necesarios
        create_required_directories()
        
        # Actualizar la pantalla de inicio si existe
        if splash_screen:
            splash_screen.update_loading(20, "Inicializando tema...")
        
        # Inicializar el gestor de temas
        theme_name = ui_config.get('theme', 'orange')
        theme_manager = ThemeManager(root)
        if hasattr(theme_manager, 'set_theme'):
            theme_manager.set_theme(theme_name)
        
        # Aplicar estilos elegantes
        if splash_screen:
            splash_screen.update_loading(40, "Aplicando estilos...")
        
        elegant_styles = get_elegant_styles(root, theme_manager)
        
        # Actualizar la pantalla de inicio si existe
        if splash_screen:
            splash_screen.update_loading(60, "Cargando interfaz principal...")
        
        # Crear la vista principal
        app = MainView(root, theme_manager, elegant_styles)
        
        # Configurar el cierre de la aplicación
        root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
        
        # Finalizar la carga si hay pantalla de inicio
        if splash_screen:
            splash_screen.update_loading(100, "¡Listo!")
            splash_screen.finish_loading()
        
        # Mostrar la ventana principal
        root.deiconify()
        
        return app
    except Exception as e:
        # Usar el manejador de errores para mostrar y registrar el error
        error_handler.log_error(e)
        error_handler.show_error_dialog(
            "Error de Inicialización", 
            f"No se pudo inicializar la aplicación: {str(e)}",
            traceback.format_exc()
        )
        
        # Cerrar la aplicación de forma segura
        if splash_screen:
            splash_screen.destroy()
        root.destroy()
        sys.exit(1)

def create_required_directories():
    """Crea los directorios necesarios para la aplicación."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Valores predeterminados para las rutas
    default_paths = {
        'logs': 'logs',
        'exports': 'exports',
        'reports': 'reports',
        'backups': 'backups'
    }
    
    # Obtener rutas de la configuración
    paths_config = config.get('paths')
    
    # Si no hay configuración, usar los valores predeterminados
    if paths_config is None:
        paths_config = default_paths
    
    # Crear directorios
    for dir_name, dir_path in paths_config.items():
        full_path = os.path.join(base_dir, dir_path)
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
                logging.info(f"Directorio creado: {full_path}")
            except Exception as e:
                logging.warning(f"No se pudo crear el directorio {full_path}: {e}")

def on_close(root):
    """Maneja el evento de cierre de la aplicación."""
    try:
        # Guardar configuración
        ui_config = config.get('ui')
        
        # Guardar estado de maximizado
        ui_config['maximized'] = root.state() == 'zoomed'
        
        # Si no está maximizado, guardar tamaño
        if not ui_config['maximized']:
            ui_config['window_size'] = {
                'width': root.winfo_width(),
                'height': root.winfo_height()
            }
        
        # Guardar configuración
        config.save()
        
        # Cerrar la aplicación
        root.destroy()
    except Exception as e:
        # Usar el manejador de errores
        error_handler.log_error(e)
        logging.error(f"Error al cerrar la aplicación: {e}")
        root.destroy()

def main():
    """Función principal que inicia la aplicación."""
    try:
        # Crear la ventana principal
        root = tk.Tk()
        
        # Ocultar la ventana principal temporalmente
        root.withdraw()
        
        # Mostrar pantalla de inicio
        splash = SplashScreen(root, lambda: initialize_application(root, splash))
        
        # Iniciar el bucle principal
        root.mainloop()
    except Exception as e:
        # Usar el manejador de errores para mostrar y registrar el error
        error_handler.log_error(e)
        error_handler.show_error_dialog(
            "Error Crítico", 
            f"Se ha producido un error crítico: {str(e)}",
            traceback.format_exc()
        )
        
        # Asegurar que la aplicación se cierre correctamente
        try:
            if 'root' in locals():
                root.destroy()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
