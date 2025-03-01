"""
Componente Tooltip para mostrar información emergente al pasar el mouse sobre widgets.
"""

import tkinter as tk

class Tooltip:
    """
    Clase para crear tooltips (textos emergentes) para widgets.

    Muestra un mensaje de texto cuando el cursor del ratón se sitúa sobre el widget
    y lo oculta cuando el cursor se aleja.
    """
    def __init__(self, widget, text, background="#ffffe0", font=('Arial', '8', 'normal')):
        """
        Inicializa el Tooltip.

        Args:
            widget: El widget al que se asociará el tooltip.
            text: El texto que se mostrará en el tooltip.
            background: Color de fondo del tooltip (por defecto: beige claro)
            font: Fuente del texto del tooltip (por defecto: Arial 8)
        """
        self.widget = widget
        self.text = text
        self.background = background
        self.font = font
        self.tooltip_window = None
        
        # Vincular eventos del mouse
        self.widget.bind("<Enter>", self._show_tooltip)
        self.widget.bind("<Leave>", self._hide_tooltip)
        self.widget.bind("<Motion>", self._move_tooltip)

    def _show_tooltip(self, event=None):
        """Muestra el tooltip."""
        # Obtener posición del widget
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # Crear ventana del tooltip
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Eliminar decoración de ventana
        tw.wm_geometry(f"+{x}+{y}")

        # Crear etiqueta con el texto
        label = tk.Label(
            tw,
            text=self.text,
            background=self.background,
            relief='solid',
            borderwidth=1,
            font=self.font
        )
        label.pack(ipadx=1, ipady=1)

    def _hide_tooltip(self, event=None):
        """Oculta el tooltip si está visible."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def _move_tooltip(self, event):
        """Mueve el tooltip con el cursor."""
        if self.tooltip_window:
            x, y = event.x_root + 15, event.y_root + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

    def update_text(self, new_text):
        """
        Actualiza el texto del tooltip.

        Args:
            new_text: Nuevo texto a mostrar en el tooltip
        """
        self.text = new_text 