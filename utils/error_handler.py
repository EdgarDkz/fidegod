"""
Módulo para el manejo de errores en la aplicación FIDEGOD.
Proporciona funciones para capturar, registrar y mostrar errores de manera elegante.
"""

import sys
import traceback
import logging
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class ErrorHandler:
    """
    Clase para manejar errores en la aplicación.
    Proporciona métodos para capturar, registrar y mostrar errores.
    """
    
    def __init__(self):
        """Inicializa el manejador de errores."""
        self.last_error = None
        self.error_count = 0
        
        # Configurar el manejador de excepciones no capturadas
        sys.excepthook = self.handle_uncaught_exception
    
    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """
        Maneja excepciones no capturadas.
        
        Args:
            exc_type: Tipo de excepción
            exc_value: Valor de la excepción
            exc_traceback: Traceback de la excepción
        """
        # Evitar que se muestre el traceback en la consola
        if issubclass(exc_type, KeyboardInterrupt):
            # Permitir que Ctrl+C funcione normalmente
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Registrar el error
        self.log_error(exc_value, exc_traceback)
        
        # Mostrar mensaje de error
        self.show_error_dialog("Error no capturado", str(exc_value))
    
    def log_error(self, error, tb=None):
        """
        Registra un error en el log.
        
        Args:
            error: Excepción o mensaje de error
            tb: Traceback (opcional)
        """
        self.last_error = error
        self.error_count += 1
        
        # Obtener el traceback si no se proporciona
        if tb is None:
            tb = traceback.format_exc()
        
        # Registrar el error
        logging.error(f"Error: {error}")
        logging.error(f"Traceback: {tb}")
    
    def show_error_dialog(self, title, message, details=None):
        """
        Muestra un diálogo de error.
        
        Args:
            title: Título del diálogo
            message: Mensaje de error
            details: Detalles adicionales (opcional)
        """
        try:
            # Intentar mostrar un diálogo de error personalizado
            self._show_custom_error_dialog(title, message, details)
        except Exception:
            # Si falla, usar messagebox estándar
            messagebox.showerror(title, message)
    
    def _show_custom_error_dialog(self, title, message, details=None):
        """
        Muestra un diálogo de error personalizado.
        
        Args:
            title: Título del diálogo
            message: Mensaje de error
            details: Detalles adicionales (opcional)
        """
        # Crear una nueva ventana para el error
        try:
            # Intentar obtener la ventana principal
            for widget in tk._default_root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    parent = widget
                    break
            else:
                parent = tk._default_root
        except Exception:
            # Si no hay ventana principal, crear una nueva
            parent = tk.Tk()
            parent.withdraw()
        
        # Crear diálogo
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Configurar estilo
        bg_color = "#f8f9fa"
        text_color = "#343a40"
        error_color = "#dc3545"
        button_bg = "#e9ecef"
        button_fg = "#343a40"
        
        dialog.configure(bg=bg_color)
        
        # Icono de error
        error_frame = tk.Frame(dialog, bg=bg_color)
        error_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Crear un canvas para el icono de error
        icon_size = 48
        icon_canvas = tk.Canvas(error_frame, width=icon_size, height=icon_size, 
                              bg=bg_color, highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 15))
        
        # Dibujar un círculo rojo con una X
        icon_canvas.create_oval(2, 2, icon_size-2, icon_size-2, 
                              fill=error_color, outline=error_color)
        icon_canvas.create_line(15, 15, icon_size-15, icon_size-15, 
                              fill="white", width=3)
        icon_canvas.create_line(icon_size-15, 15, 15, icon_size-15, 
                              fill="white", width=3)
        
        # Mensaje de error
        message_frame = tk.Frame(error_frame, bg=bg_color)
        message_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        error_title = tk.Label(message_frame, text="Se ha producido un error", 
                             font=("Segoe UI", 12, "bold"), bg=bg_color, fg=error_color)
        error_title.pack(anchor=tk.W)
        
        error_message = tk.Label(message_frame, text=message, 
                               font=("Segoe UI", 10), bg=bg_color, fg=text_color,
                               wraplength=400, justify=tk.LEFT)
        error_message.pack(anchor=tk.W, pady=(5, 0))
        
        # Detalles (opcional)
        if details:
            details_frame = tk.Frame(dialog, bg=bg_color)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
            
            details_label = tk.Label(details_frame, text="Detalles:", 
                                   font=("Segoe UI", 10, "bold"), bg=bg_color, fg=text_color)
            details_label.pack(anchor=tk.W)
            
            # Crear un widget de texto con scroll
            details_text = tk.Text(details_frame, height=8, width=50, 
                                 font=("Consolas", 9), bg="white", fg=text_color)
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(details_frame, command=details_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            details_text.config(yscrollcommand=scrollbar.set)
            
            details_text.insert(tk.END, details)
            details_text.config(state=tk.DISABLED)
        
        # Botones
        button_frame = tk.Frame(dialog, bg=bg_color)
        button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Botón para copiar el error
        def copy_error():
            dialog.clipboard_clear()
            copy_text = f"{message}\n\n{details if details else ''}"
            dialog.clipboard_append(copy_text)
            dialog.update()
        
        copy_button = tk.Button(button_frame, text="Copiar", command=copy_error,
                              bg=button_bg, fg=button_fg, relief=tk.FLAT,
                              padx=10, font=("Segoe UI", 9))
        copy_button.pack(side=tk.LEFT)
        
        # Botón para cerrar
        close_button = tk.Button(button_frame, text="Cerrar", command=dialog.destroy,
                               bg=button_bg, fg=button_fg, relief=tk.FLAT,
                               padx=10, font=("Segoe UI", 9))
        close_button.pack(side=tk.RIGHT)
        
        # Centrar en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Manejar el cierre con la X
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        
        # Esperar a que se cierre el diálogo
        dialog.wait_window()
    
    def handle_exception(self, func):
        """
        Decorador para manejar excepciones en funciones.
        
        Args:
            func: Función a decorar
            
        Returns:
            Función decorada
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.log_error(e)
                self.show_error_dialog("Error", str(e), traceback.format_exc())
                return None
        return wrapper

# Instancia global para uso en toda la aplicación
error_handler = ErrorHandler() 