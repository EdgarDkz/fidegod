import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
from gestion import GestionDB
from tkcalendar import DateEntry

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
        campos_normales = [
            ('Nombre:', 'nombre'), 
            ('Teléfono:', 'telefono'), 
            ('Dirección:', 'direccion'), 
            ('Municipio:', 'municipio')
        ]
        campos_fecha = [
            ('Fecha Petición:', 'fecha_peticion'),
            ('Fecha Entrega:', 'fecha_entrega')
        ]

        # Crear campos normales (Entry)
        for i, (label, campo) in enumerate(campos_normales):
            ttk.Label(self.frame_formulario, text=label).grid(row=i, column=0, padx=5, pady=2)
            entry = ttk.Entry(self.frame_formulario)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.campos_persona[campo] = entry

        # Crear campos de fecha (DateEntry)
        for i, (label, campo) in enumerate(campos_fecha, start=len(campos_normales)):
            ttk.Label(self.frame_formulario, text=label).grid(row=i, column=0, padx=5, pady=2)
            date_entry = DateEntry(self.frame_formulario, 
                                 width=20,
                                 background='darkblue',
                                 foreground='white',
                                 borderwidth=2,
                                 date_pattern='yyyy-mm-dd')
            date_entry.grid(row=i, column=1, padx=5, pady=2)
            self.campos_persona[campo] = date_entry

        # Botones
        frame_botones = ttk.Frame(self.frame_formulario)
        frame_botones.grid(row=len(campos_normales) + len(campos_fecha), column=0, columnspan=2, pady=10)

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
        # Frame para búsqueda
        frame_busqueda = ttk.LabelFrame(self.tab_inventario, text="Búsqueda")
        frame_busqueda.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(frame_busqueda, text="Buscar:").pack(side='left', padx=5)
        self.entry_busqueda_inventario = ttk.Entry(frame_busqueda)
        self.entry_busqueda_inventario.pack(side='left', padx=5)
        ttk.Button(frame_busqueda, text="Buscar", 
                command=self.buscar_articulos).pack(side='left', padx=5)
        
        # Frame principal dividido en dos
        frame_principal = ttk.PanedWindow(self.tab_inventario, orient=tk.HORIZONTAL)
        frame_principal.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame para detalles del artículo
        self.frame_detalles_articulo = ttk.LabelFrame(self.tab_inventario, text="Detalles del Artículo")
        self.frame_detalles_articulo.pack(fill='x', padx=5, pady=5)
        
        # Campos del formulario
        self.campos_inventario = {}
        campos_normales = [
            ('Nombre del Artículo:', 'nombre_articulo'), 
            ('Descripción:', 'descripcion'), 
            ('Cantidad Disponible:', 'cantidad_disponible'),
            ('Fecha de Ingreso:', 'fecha_ingreso')  # Asegúrate de que este campo esté aquí
        ]
        
        # Crear campos normales (Entry y DateEntry)
        for i, (label, campo) in enumerate(campos_normales):
            ttk.Label(self.frame_detalles_articulo, text=label).grid(row=i, column=0, padx=5, pady=2)
            if campo == 'fecha_ingreso':
                date_entry = DateEntry(self.frame_detalles_articulo, 
                                       width=20,
                                       background='darkblue',
                                       foreground='white',
                                       borderwidth=2,
                                       date_pattern='yyyy-mm-dd')
                date_entry.grid(row=i, column=1, padx=5, pady=2)
                self.campos_inventario[campo] = date_entry
            else:
                entry = ttk.Entry(self.frame_detalles_articulo)
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.campos_inventario[campo] = entry
        
        # Frame para la imagen
        frame_imagen = ttk.LabelFrame(self.frame_detalles_articulo, text="Imagen del Artículo")
        frame_imagen.grid(row=len(campos_normales), column=0, columnspan=2, padx=5, pady=5)
        
        # Label para mostrar la imagen
        self.label_imagen = ttk.Label(frame_imagen)
        self.label_imagen.pack(padx=5, pady=5)
        
        # Variable para guardar la ruta de la imagen
        self.ruta_imagen = None
        
        # Botones para la imagen
        ttk.Button(frame_imagen, text="Seleccionar Imagen", 
                command=self.seleccionar_imagen).pack(side='left', padx=5)
        ttk.Button(frame_imagen, text="Eliminar Imagen", 
                command=self.eliminar_imagen).pack(side='left', padx=5)
        
        # Botones de acción
        frame_botones = ttk.Frame(self.frame_detalles_articulo)
        frame_botones.grid(row=len(campos_normales)+1, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botones, text="Agregar", 
                command=self.agregar_articulo).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Actualizar", 
                command=self.actualizar_articulo).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Eliminar", 
                command=self.eliminar_articulo).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Limpiar", 
                command=self.limpiar_campos_inventario).pack(side='left', padx=5)
        
        # Crear Treeview
        self.tree_inventario = ttk.Treeview(frame_principal, columns=('ID', 'Nombre', 'Descripción', 'Cantidad', 'Imagen', 'Fecha de Ingreso'), show='headings')

        # Configurar columnas
        for col in self.tree_inventario['columns']:
            self.tree_inventario.heading(col, text=col)
            self.tree_inventario.column(col, width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(frame_principal, orient='vertical', command=self.tree_inventario.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree_inventario.configure(yscrollcommand=scrollbar.set)
        self.tree_inventario.pack(fill='both', expand=True)
        
        # Bind para selección en el TreeView
        self.tree_inventario.bind('<<TreeviewSelect>>', self.seleccionar_articulo)
        
        # Cargar datos iniciales
        self.actualizar_lista_inventario()

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
                if isinstance(entry, DateEntry):
                    try:
                        entry.set_date(valores[i + 1])
                    except:
                        entry.set_date(None)
                else:
                    entry.delete(0, tk.END)
                    entry.insert(0, valores[i + 1] if valores[i + 1] else '')

    def limpiar_campos_persona(self):
        for campo, entry in self.campos_persona.items():
            if isinstance(entry, DateEntry):
                entry.set_date(None)  # Limpiar campos de fecha
            else:
                entry.delete(0, tk.END)  # Limpiar campos normales
        if self.tree_personas.selection():
            self.tree_personas.selection_remove(self.tree_personas.selection())


    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if ruta:
            self.ruta_imagen = ruta
            # Mostrar la imagen en el label
            imagen = Image.open(ruta)
            imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)  # Redimensionar
            foto = ImageTk.PhotoImage(imagen)
            self.label_imagen.configure(image=foto)
            self.label_imagen.image = foto  # Mantener referencia

    def eliminar_imagen(self):
        try:
            # Verificar si hay un artículo seleccionado
            seleccion = self.tree_inventario.selection()
            if not seleccion:
                messagebox.showwarning("Aviso", "Por favor, seleccione un artículo primero.")
                return
            
            item = seleccion[0]
            item_id = self.tree_inventario.item(item)['values'][0]
            
            # Obtener el artículo actual
            articulo = self.db.obtener_articulo(item_id)
            if not articulo or not articulo[4]:  # Si no hay artículo o no tiene imagen
                messagebox.showinfo("Información", "Este artículo no tiene una imagen para eliminar.")
                return
            
            # Confirmar la eliminación
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la imagen de este artículo?"):
                # Actualizar el artículo manteniendo todos los datos excepto la imagen
                if self.db.actualizar_articulo(
                    id=item_id,
                    nombre_articulo=articulo[1],  # Mantener el nombre del artículo
                    descripcion=articulo[2],        # Mantener la descripción
                    cantidad_disponible=articulo[3],  # Mantener la cantidad
                    imagen=None,  # Eliminar la imagen
                    fecha_ingreso=articulo[5]  # Asegúrate de pasar la fecha de ingreso
                ):
                    # Limpiar la imagen en la interfaz
                    self.label_imagen.configure(image='')
                    self.label_imagen.image = None
                    self.ruta_imagen = None
                    
                    # Actualizar la lista de inventario
                    self.actualizar_lista_inventario()
                    messagebox.showinfo("Éxito", "Imagen eliminada correctamente.")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la imagen.")
                
        except Exception as e:
            print(f"Error al eliminar imagen: {e}")
            messagebox.showerror("Error", "Ocurrió un error al intentar eliminar la imagen.")

    def agregar_articulo(self):
        valores = {campo: entry.get() for campo, entry in self.campos_inventario.items()}
        
        # Validar campos numéricos
        try:
            valores['cantidad_disponible'] = int(valores['cantidad_disponible'])
        except ValueError:
            messagebox.showwarning("Error", "La cantidad debe ser un número")
            return
        
        # Manejar la imagen
        if self.ruta_imagen:
            nombre_archivo = f"imagenes/{os.path.basename(self.ruta_imagen)}"
            os.makedirs("imagenes", exist_ok=True)
            Image.open(self.ruta_imagen).save(nombre_archivo)
            valores['imagen'] = nombre_archivo
        else:
            valores['imagen'] = None
        
        # Asegúrate de incluir la fecha de ingreso
        fecha_ingreso = valores.pop('fecha_ingreso', None)  # Extraer la fecha de ingreso

        if self.db.agregar_articulo(**valores, fecha_ingreso=fecha_ingreso):
            messagebox.showinfo("Éxito", "Artículo agregado correctamente")
            self.limpiar_campos_inventario()
            self.actualizar_lista_inventario()
        else:
            messagebox.showerror("Error", "No se pudo agregar el artículo")

    def actualizar_lista_inventario(self):
        # Limpiar el TreeView
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        
        # Obtener y mostrar los artículos
        articulos = self.db.obtener_inventario()
        for articulo in articulos:
            # Preparar la miniatura de la imagen si existe
            imagen_texto = "🖼️"  # Emoji por defecto para indicar que hay imagen
            if articulo[4]:  # Si existe la imagen
                imagen_texto = "Ver"  # Texto para indicar que hay una imagen
            else:
                imagen_texto = ""  # Texto si no hay imagen

            # Asegúrate de que el índice para la fecha de ingreso sea correcto
            valores = (
                articulo[0],  # ID
                articulo[1],  # Nombre
                articulo[2],  # Descripción
                articulo[3],  # Cantidad
                imagen_texto,  # Texto para la imagen
                articulo[5]    # Fecha de Ingreso (asegúrate de que este índice sea correcto)
            )
            self.tree_inventario.insert('', 'end', values=valores)

    def seleccionar_articulo(self, event):
        seleccion = self.tree_inventario.selection()
        if seleccion:
            item = self.tree_inventario.item(seleccion[0])
            valores = item['values']
            
            # Llenar campos
            for i, (campo, entry) in enumerate(self.campos_inventario.items()):
                entry.delete(0, tk.END)
                entry.insert(0, valores[i + 1])  # Asegúrate de que esto esté correcto
            
            # Cargar imagen si existe
            articulo = self.db.obtener_articulo(valores[0])
            if articulo and articulo[4]:  # Si hay ruta de imagen
                self.ruta_imagen = articulo[4]
                try:
                    imagen = Image.open(self.ruta_imagen)
                    imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(imagen)
                    self.label_imagen.configure(image=foto)
                    self.label_imagen.image = foto
                except Exception as e:
                    print(f"Error al cargar la imagen: {e}")
                    self.ruta_imagen = None
                    self.label_imagen.configure(image='')
            
            # Establecer la fecha de ingreso en el DateEntry
            if articulo and articulo[5]:  # Asegúrate de que este índice sea correcto
                self.campos_inventario['fecha_ingreso'].set_date(articulo[5])  # Establecer la fecha

    def buscar_articulos(self):
        filtro = self.entry_busqueda_inventario.get()
        for item in self.tree_inventario.get_children():
            self.tree_inventario.delete(item)
        articulos = self.db.obtener_inventario(filtro)
        for articulo in articulos:
            self.tree_inventario.insert('', 'end', values=articulo[:-1])  # Excluir la ruta de la imagen

    def limpiar_campos_inventario(self):
        # Limpiar campos de texto
        for entry in self.campos_inventario.values():
            entry.delete(0, tk.END)
        
        # Limpiar imagen
        self.label_imagen.configure(image='')
        self.label_imagen.image = None
        self.ruta_imagen = None  # Importante: resetear la ruta de la imagen
        
        # Deseleccionar item en el TreeView si hay alguno seleccionado
        if self.tree_inventario.selection():
            self.tree_inventario.selection_remove(self.tree_inventario.selection())

    def eliminar_articulo(self):
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un artículo para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este artículo?"):
            item = self.tree_inventario.item(seleccion[0])
            id_articulo = item['values'][0]
            
            # Eliminar la imagen si existe
            articulo = self.db.obtener_articulo(id_articulo)
            if articulo and articulo[4]:  # Si hay imagen
                try:
                    os.remove(articulo[4])
                except:
                    pass
            
            if self.db.eliminar_articulo(id_articulo):
                messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                self.limpiar_campos_inventario()
                self.actualizar_lista_inventario()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el artículo")

    def actualizar_articulo(self):
        seleccion = self.tree_inventario.selection()
        if not seleccion:
            messagebox.showwarning("Error", "Seleccione un artículo para actualizar")
            return
        
        item = self.tree_inventario.item(seleccion[0])
        id_articulo = item['values'][0]
        valores = {campo: entry.get() for campo, entry in self.campos_inventario.items()}
        
        # Validar campos numéricos
        try:
            valores['cantidad_disponible'] = int(valores['cantidad_disponible'])
        except ValueError:
            messagebox.showwarning("Error", "La cantidad debe ser un número")
            return
        
        # Manejar la imagen
        if self.ruta_imagen:
            nombre_archivo = f"imagenes/{os.path.basename(self.ruta_imagen)}"
            os.makedirs("imagenes", exist_ok=True)
            if self.ruta_imagen != nombre_archivo:
                Image.open(self.ruta_imagen).save(nombre_archivo)
            valores['imagen'] = nombre_archivo
        else:
            articulo = self.db.obtener_articulo(id_articulo)
            valores['imagen'] = articulo[4] if articulo else None
        
        # Asegúrate de incluir la fecha de ingreso
        fecha_ingreso = valores.pop('fecha_ingreso', None)  # Extraer la fecha de ingreso

        if self.db.actualizar_articulo(id_articulo, **valores, fecha_ingreso=fecha_ingreso):
            messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
            self.limpiar_campos_inventario()
            self.actualizar_lista_inventario()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el artículo")

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()