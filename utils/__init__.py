"""
Paquete de utilidades para la aplicación FIDEGOD.
Contiene herramientas y funciones auxiliares utilizadas en toda la aplicación.
"""

# Configuración de logging
import logging
import os
import sys
from datetime import datetime

# Configurar el sistema de logging
def setup_logging():
    """Configura el sistema de logging para la aplicación."""
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Nombre del archivo de log con fecha
    log_file = os.path.join(log_dir, f'fidegod_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Configurar el logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Mensaje inicial
    logging.info("Sistema de logging inicializado")

# Inicializar logging
setup_logging()

# Importar componentes principales para facilitar su uso
from utils.icon_manager import icon_manager
from utils.config import config
from utils.error_handler import error_handler 