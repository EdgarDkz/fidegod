import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gestion import GestionDB
from datetime import datetime
import os
from PIL import Image, ImageTk

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión")
        self.root.geometry("1200x700")
        
        self.db = GestionDB()
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Crear pestañas
        self.tab_personas = ttk.Frame(self.notebook)
        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_transacciones = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_personas, text='Gestión de Personas')
        self.notebook.add(self.tab_inventario, text='Gestión de Inventario')
        self.notebook.add(self.tab_transacciones, text='Transacciones')
        
        # Inicializar componentes
        self.setup_personas_tab()
        self.setup_inventario_tab()
        self.setup_transacciones_tab()
        
        # Verificar stock mínimo al inicio
        self.verificar_stock_minimo()

    def setup_personas_tab(self):
        # Frame para búsqueda
        frame_busqueda = ttk.LabelFrame(self.tab_personas, text="Búsqueda")
        frame_busqueda.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(frame_busqueda, text="Buscar:").pack(side='left', padx=5)
        self.entry_busqueda_personas = ttk.Entry(frame_busqueda)
        self.entry_busqueda_personas.pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text="Buscar", 
                command=self.buscar_personas).pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text="Exportar a CSV", 
                command=lambda: self.db.exportar_a_csv('personas')).pack(side='right', padx=5)
        # Frame para el TreeView
        frame_tree = ttk.Frame(self.tab_personas)
        frame_tree.pack(fill='both', expand=True, padx=5, pady=5)

        # Crear Treeview
        self.tree_personas = ttk.Treeview(frame_tree, columns=('ID', 'Nombre', 'Teléfono', 'Dirección', 
        'Municipio', 'Fecha Petición', 'Fecha Entrega'),
                                        show='headings')

        # Configurar columnas
        for col in self.tree_personas['columns']:
            self.tree_personas.heading(col, text=col)
            self.tree_personas.column(col, width=100)

        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(frame_tree, orient='vertical', command=self.tree_personas.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_personas.configure(yscrollcommand=scrollbar.set)
        self.tree_personas.pack(fill='both', expand=True)

        # Frame para formulario
        self.frame_formulario = ttk.LabelFrame(self.tab_personas, text="Detalles de Persona")
        self.frame_formulario.pack(fill='x', padx=5, pady=5)

        # Campos del formulario
        self.campos_persona = {}
        campos = [('Nombre:', 'nombre'), ('Teléfono:', 'telefono'), 
                ('Dirección:', 'direccion'), ('Municipio:', 'municipio'),
                ('Fecha Petición:', 'fecha_peticion'), ('Fecha Entrega:', 'fecha_entrega')]

        for i, (label, campo) in enumerate(campos):
            ttk.Label(self.frame_formulario, text=label).grid(row=i, column=0, padx=5, pady=2)
            entry = ttk.Entry(self.frame_formulario)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.campos_persona[campo] = entry

        # Botones
        frame_botones = ttk.Frame(self.frame_formulario)
        frame_botones.grid(row=len(campos), column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Agregar", 
                command=self.agregar_persona).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar", 
                command=self.actualizar_persona).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar", 
                command=self.eliminar_persona).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar", 
                command=self.limpiar_campos_persona).pack(side='left', padx=5)

        # Bind para selección en el TreeView
        self.tree_personas.bind('<<TreeviewSelect>>', self.seleccionar_persona)
        
        # Cargar datos iniciales
        self.actualizar_lista_personas()

    def setup_inventario_tab(self):
        # Similar al setup_personas_tab pero para inventario
        pass

    def setup_transacciones_tab(self):
        # Implementar vista de transacciones
        pass

    # Métodos para gestión de personas
    def actualizar_lista_personas(self):
        for item in self.tree_personas.get_children():
            self.tree_personas.delete(item)
        personas = self.db.obtener_personas()
        for persona in personas:
            self.tree_personas.insert('', 'end', values=persona)

    def buscar_personas(self):
        filtro = self.entry_busqueda_personas.get()
        for item in self.tree_personas.get_children():
            self.tree_personas.delete(item)
        personas = self.db.obtener_personas(filtro)
        for persona in personas:
            self.tree_personas.insert('', 'end', values=persona)

    def agregar_persona(self):
        valores = {campo: entry.get() for campo, entry in self.campos_persona.items()}
        if not valores['nombre']:
            messagebox.showwarning("Error", "El nombre es obligatorio")
            return
        if self.db.agregar_persona(**valores):
            messagebox.showinfo("Éxito", "Persona agregada correctamente")
            self.limpiar_campos_persona()
            self.actualizar_lista_personas()
        else:
            messagebox.showerror("Error", "No se pudo agregar la persona")

    def actualizar_persona(self):
        seleccion = self.tree_personas.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una persona para actualizar")
            return
        
        item = self.tree_personas.item(seleccion[0])
        id_persona = item['values'][0]
        valores = {campo: entry.get() for campo, entry in self.campos_persona.items()}
        
        if self.db.actualizar_persona(id_persona, **valores):
            messagebox.showinfo("Éxito", "Persona actualizada correctamente")
            self.limpiar_campos_persona()
            self.actualizar_lista_personas()
        else:
            messagebox.showerror("Error", "No se pudo actualizar la persona")

    def eliminar_persona(self):
        seleccion = self.tree_personas.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione una persona para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta persona?"):
            item = self.tree_personas.item(seleccion[0])
            id_persona = item['values'][0]
            
            if self.db.eliminar_persona(id_persona):
                messagebox.showinfo("Éxito", "Persona eliminada correctamente")
                self.limpiar_campos_persona()
                self.actualizar_lista_personas()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la persona")

    def seleccionar_persona(self, event):
        seleccion = self.tree_personas.selection()
        if seleccion:
            item = self.tree_personas.item(seleccion[0])
            valores = item['values']
            for i, (campo, entry) in enumerate(self.campos_persona.items()):
                entry.delete(0, tk.END)
                entry.insert(0, valores[i + 1])

    def limpiar_campos_persona(self):
        for entry in self.campos_persona.values():
            entry.delete(0, tk.END)
        if self.tree_personas.selection():
            self.tree_personas.selection_remove(self.tree_personas.selection())

    def verificar_stock_minimo(self):
        items_bajo_stock = self.db.verificar_stock_minimo()
        if items_bajo_stock:
            mensaje = "Los siguientes artículos están bajo el stock mínimo:\n\n"
            for item in items_bajo_stock:
                mensaje += f"- {item[0]}: {item[1]} unidades (mínimo: {item[2]})\n"
            messagebox.showwarning("Alerta de Stock", mensaje)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
