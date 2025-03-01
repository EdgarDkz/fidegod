import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from controllers.personas_controller import PersonasController
from tkcalendar import DateEntry  # Asegúrate de importar DateEntry

class ConfirmarEntregaDialog(tk.Toplevel):
    def __init__(self, parent, title, persona):
        super().__init__(parent)
        self.title(title)
        self.persona = persona
        self.result = None
        self.controller = PersonasController()

        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()

        # Centrar la ventana
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                 parent.winfo_rooty() + 50))

        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Información del pedido
        ttk.Label(main_frame, text="Confirmar Entrega de Pedido", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Detalles del pedido
        details = [
            ("Cliente:", self.persona[1]),
            ("Artículo:", self.persona[2]),
            ("Dirección:", self.persona[4]),
            ("Municipio:", self.persona[5])
        ]

        for i, (label, value) in enumerate(details, start=1):
            ttk.Label(main_frame, text=label, font=('Segoe UI', 10, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(main_frame, text=value).grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        # Fecha de entrega
        ttk.Label(main_frame, text="Fecha de Entrega:", font=('Segoe UI', 10, 'bold')).grid(row=len(details)+1, column=0, sticky=tk.W, pady=(10, 2))
        
        # Selector de fecha
        self.fecha_entrega_entry = DateEntry(main_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_entrega_entry.grid(row=len(details)+1, column=1, sticky=tk.W, pady=(10, 2), padx=(10, 0))

        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(details)+2, column=0, columnspan=2, pady=(20, 0))

        # Botones
        confirm_button = tk.Button(
            button_frame,
            text="Confirmar",
            command=self.confirmar_entrega,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        )
        confirm_button.pack(side='left', padx=5)

        cancel_button = tk.Button(
            button_frame,
            text="Cancelar",
            command=self.on_cancel,
            bg="SystemButtonFace",
            relief=tk.RAISED,
            borderwidth=2,
            font=('Segoe UI', 10),
            padx=20,
            pady=5
        )
        cancel_button.pack(side='right', padx=5)

    def confirmar_entrega(self):
        try:
            # Obtener la fecha de entrega seleccionada
            fecha_entrega = self.fecha_entrega_entry.get()
            # Actualizar el estado a "Entregado" y la fecha de entrega
            self.controller.update_persona(self.persona[0], estado="Entregado", fecha_entrega=fecha_entrega)  # Use update_persona
            messagebox.showinfo("Éxito", "Entrega confirmada correctamente para el " + fecha_entrega)
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al confirmar la entrega: {str(e)}")
            self.result = False

    def on_cancel(self):
        self.result = False
        self.destroy()