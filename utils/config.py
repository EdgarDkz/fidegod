"""
Módulo de configuración para la aplicación FIDEGOD.
Gestiona la configuración global y las preferencias del usuario.
"""

import os
import json
import logging
from pathlib import Path

class Config:
    """
    Clase para gestionar la configuración de la aplicación.
    Permite cargar, guardar y acceder a la configuración desde cualquier parte de la aplicación.
    """
    
    # Valores predeterminados
    DEFAULT_CONFIG = {
        "app": {
            "name": "FIDEGOD",
            "version": "1.0.0",
            "company": "FIDEGOD",
            "description": "Sistema de Gestión para Inventario y Pedidos"
        },
        "ui": {
            "theme": "orange",  # Tema predeterminado
            "font_size": "medium",  # Tamaño de fuente
            "show_toolbar": True,
            "show_statusbar": True,
            "show_quick_access": True,
            "window_size": {
                "width": 1280,
                "height": 720
            },
            "maximized": True
        },
        "database": {
            "type": "sqlite",  # sqlite o mysql
            "path": "database.db",  # Para SQLite
            "host": "localhost",  # Para MySQL
            "port": 3306,  # Para MySQL
            "name": "fidegod",  # Para MySQL
            "user": "",  # Para MySQL
            "password": ""  # Para MySQL
        },
        "paths": {
            "logs": "logs",
            "exports": "exports",
            "reports": "reports",
            "backups": "backups"
        },
        "features": {
            "auto_backup": True,
            "backup_interval_days": 7,
            "check_updates": True,
            "auto_save": True,
            "save_interval_minutes": 5
        }
    }
    
    def __init__(self):
        """Inicializa la configuración."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = self._get_config_path()
        self.load()
    
    def _get_config_path(self):
        """Obtiene la ruta del archivo de configuración."""
        # Directorio base de la aplicación
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Directorio de configuración
        config_dir = os.path.join(base_dir, 'config')
        
        # Crear directorio si no existe
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except Exception as e:
                logging.error(f"No se pudo crear el directorio de configuración: {e}")
                # Usar directorio actual como fallback
                config_dir = base_dir
        
        # Ruta completa del archivo
        return os.path.join(config_dir, 'config.json')
    
    def load(self):
        """Carga la configuración desde el archivo."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                    # Actualizar la configuración manteniendo los valores predeterminados
                    # para claves que no estén en el archivo
                    self._update_dict_recursive(self.config, loaded_config)
                    
                logging.info(f"Configuración cargada desde {self.config_file}")
            else:
                # Si no existe, guardar la configuración predeterminada
                self.save()
                logging.info("Archivo de configuración no encontrado, se ha creado uno nuevo")
        except Exception as e:
            logging.error(f"Error al cargar la configuración: {e}")
    
    def save(self):
        """Guarda la configuración en el archivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info(f"Configuración guardada en {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"Error al guardar la configuración: {e}")
            return False
    
    def _update_dict_recursive(self, target_dict, source_dict):
        """
        Actualiza un diccionario de forma recursiva.
        
        Args:
            target_dict: Diccionario a actualizar
            source_dict: Diccionario con los nuevos valores
        """
        for key, value in source_dict.items():
            if key in target_dict:
                if isinstance(value, dict) and isinstance(target_dict[key], dict):
                    # Si ambos son diccionarios, actualizar recursivamente
                    self._update_dict_recursive(target_dict[key], value)
                else:
                    # Si no son diccionarios, simplemente actualizar el valor
                    target_dict[key] = value
            else:
                # Si la clave no existe en el diccionario destino, añadirla
                target_dict[key] = value
    
    def get(self, section, key=None, default=None):
        """
        Obtiene un valor de configuración.
        
        Args:
            section: Sección de la configuración (app, ui, database, etc.)
            key: Clave específica dentro de la sección (opcional)
            default: Valor predeterminado si no se encuentra (opcional)
            
        Returns:
            El valor de configuración o el valor predeterminado
        """
        try:
            if section in self.config:
                if key is not None:
                    return self.config[section].get(key, default)
                return self.config[section]
            return default
        except Exception as e:
            logging.error(f"Error al obtener configuración {section}.{key}: {e}")
            return default
    
    def set(self, section, key, value):
        """
        Establece un valor de configuración.
        
        Args:
            section: Sección de la configuración
            key: Clave dentro de la sección
            value: Valor a establecer
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            return True
        except Exception as e:
            logging.error(f"Error al establecer configuración {section}.{key}: {e}")
            return False
    
    def get_all(self):
        """
        Obtiene toda la configuración.
        
        Returns:
            Diccionario con toda la configuración
        """
        return self.config.copy()

# Instancia global para uso en toda la aplicación
config = Config() 