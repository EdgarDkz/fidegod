import sqlite3
from datetime import datetime
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os

class InventarioController:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        self.current_image = None
        self.setup_database()  # Initialize database on creation

    def execute_query(self, query, params=(), fetch=False):
        """Ejecuta una consulta SQL en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
        conn.commit()
        conn.close()
        return result

    def setup_database(self):
        """Crear la tabla de inventario si no existe"""
        query = '''
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL,
                fecha_ingreso DATE NOT NULL,
                imagen_path TEXT,
                categoria TEXT,
                ubicacion TEXT,
                stock_minimo INTEGER
            )
        '''
        self.execute_query(query)

    def get_articulos(self, filtros=None):
        """Obtener todos los artículos del inventario, con opción de filtros avanzados y ordenados por ID descendente."""
        try:
            # Intentar reordenar los IDs, pero no interrumpir si falla
            self.reorder_inventario_ids()
            
            query = '''
                SELECT id, nombre, descripcion, cantidad, fecha_ingreso, categoria, ubicacion, stock_minimo
                FROM inventario
            '''
            where_clauses = []
            params = []
            
            if filtros:
                if 'nombre' in filtros and filtros['nombre']:
                    where_clauses.append("nombre LIKE ?")
                    params.append(f"%{filtros['nombre']}%")
                
                if 'categoria' in filtros and filtros['categoria']:
                    where_clauses.append("categoria = ?")
                    params.append(filtros['categoria'])
                
                if 'ubicacion' in filtros and filtros['ubicacion']:
                    where_clauses.append("ubicacion = ?")
                    params.append(filtros['ubicacion'])
                
                if 'stock_minimo' in filtros and filtros['stock_minimo']:
                    where_clauses.append("cantidad <= stock_minimo")
                
                if 'fecha_desde' in filtros and filtros['fecha_desde']:
                    where_clauses.append("fecha_ingreso >= ?")
                    params.append(filtros['fecha_desde'])
                
                if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
                    where_clauses.append("fecha_ingreso <= ?")
                    params.append(filtros['fecha_hasta'])
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " ORDER BY id DESC"
            
            return self.execute_query(query, params, fetch=True)
        except Exception as e:
            print(f"Error al obtener artículos: {e}")
            return []  # Devolver lista vacía en caso de error

    def agregar_articulo(self, nombre, descripcion, cantidad, imagen_path, fecha_ingreso, categoria, ubicacion, stock_minimo):
        """Agrega un nuevo artículo al inventario, incluyendo categoría, ubicación y stock mínimo."""
        query = '''
            INSERT INTO inventario (nombre, descripcion, cantidad, imagen_path, fecha_ingreso, categoria, ubicacion, stock_minimo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (nombre, descripcion, cantidad, imagen_path, fecha_ingreso, categoria, ubicacion, stock_minimo)
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al agregar artículo: {e}")
            return False

    def actualizar_articulo(self, articulo_id, nombre, descripcion, cantidad, categoria=None, ubicacion=None, stock_minimo=None):
        """Actualiza un artículo existente, incluyendo categoría, ubicación y stock mínimo."""
        query = """
            UPDATE inventario
            SET nombre=?, descripcion=?, cantidad=?, categoria=?, ubicacion=?, stock_minimo=?
            WHERE id=?
        """
        params = (nombre, descripcion, cantidad, categoria, ubicacion, stock_minimo, articulo_id)
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al actualizar el artículo: {e}")
            return False


    def eliminar_articulo(self, id):
        """Eliminar un artículo del inventario y reorganizar IDs"""
        query = 'DELETE FROM inventario WHERE id = ?'
        try:
            self.execute_query(query, (id,))
            self.reorder_inventario_ids()
            return True
        except Exception as e:
            print(f"Error al eliminar artículo: {e}")
            return False

    def buscar_articulos(self, termino):
        """Buscar artículos por nombre o descripción"""
        query = '''
            SELECT id, nombre, descripcion, cantidad, fecha_ingreso, categoria, ubicacion, stock_minimo
            FROM inventario
            WHERE nombre LIKE ? OR descripcion LIKE ?
            ORDER BY id DESC
        '''
        return self.execute_query(query, (f'%{termino}%', f'%{termino}%'), fetch=True)

    def get_imagen_articulo(self, id):
        """Obtener la ruta de la imagen de un artículo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT imagen_path FROM inventario WHERE id = ?', (id,))
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else None

    def eliminar_imagen(self, articulo_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = """UPDATE inventario SET imagen_path=NULL WHERE id=?"""
            cursor.execute(query, (articulo_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al eliminar la imagen: {e}")
            return False

    def guardar_imagen(self, articulo_id, imagen_path):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = """UPDATE inventario SET imagen_path=? WHERE id=?"""
            cursor.execute(query, (imagen_path, articulo_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al guardar la imagen: {e}")
            return False

    def abrir_dialogo_articulo(self, dialog_class, parent, callback=None, mode='add', articulo=None): # Añadido mode y articulo
        """Abre el diálogo para agregar o editar un artículo."""
        if mode == 'add':
            dialog = dialog_class(parent, self, on_save=callback, mode='add') # Pasa mode='add'
        elif mode == 'edit':
            dialog = dialog_class(parent, self, on_save=callback, mode='edit', articulo=articulo) # Pasa mode='edit' y articulo


    def seleccionar_imagen(self, image_label):
        """Maneja la selección de una imagen para un artículo"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            try:
                # Abrir y redimensionar imagen
                image = Image.open(file_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                # Mostrar imagen
                image_label.configure(image=photo, text="")
                image_label.image = photo
                self.current_image = file_path

                return True, file_path
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
                return False, None
        return False, None

    def cargar_imagen_articulo(self, articulo_id, image_label):
        """Carga y muestra la imagen del artículo"""
        imagen_path = self.get_imagen_articulo(articulo_id)
        if imagen_path and os.path.exists(imagen_path):
            try:
                # Abrir y redimensionar imagen
                image = Image.open(imagen_path)
                # Calcular el tamaño para ajustar al frame manteniendo la proporción
                frame_width = image_label.winfo_width()
                frame_height = image_label.winfo_height()
                image.thumbnail((frame_width, frame_height))
                photo = ImageTk.PhotoImage(image)

                # Mostrar imagen
                image_label.configure(image=photo, text="")
                image_label.image = photo  # Mantener referencia
                self.current_image = imagen_path
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
                image_label.configure(image="", text="Error al cargar la imagen")
                return False
        else:
            image_label.configure(image="", text="No tiene imagen")
            self.current_image = None
            return False

    def confirmar_eliminar_articulo(self, articulo_id):
        """Confirma y elimina un artículo"""
        if messagebox.askyesno("Confirmar eliminación",
                             "¿Está seguro de que desea eliminar este artículo?"):
            if self.eliminar_articulo(articulo_id):
                messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                return True
        return False

    def confirmar_eliminar_imagen(self, articulo_id, image_label):
        """Confirma y elimina la imagen de un artículo"""
        if messagebox.askyesno("Confirmar eliminación",
                             "¿Está seguro de que desea eliminar la imagen?"):
            image_label.configure(image='', text="No tiene imagen")
            self.current_image = None

            if self.eliminar_imagen(articulo_id):
                return True
        return False

    def validar_y_actualizar_articulo(self, articulo_id, nombre, descripcion, cantidad, categoria, ubicacion, stock_minimo): # Añadidos nuevos campos
        """Valida y actualiza los datos de un artículo, incluyendo categoría, ubicación y stock mínimo."""
        if not nombre.strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False

        try:
            cantidad_num = int(cantidad)
            if cantidad_num < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero positivo")
            return False

        if self.actualizar_articulo(articulo_id, nombre, descripcion, cantidad, categoria, ubicacion, stock_minimo): # Pasa nuevos campos a actualizar_articulo
            messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
            return True
        else:
            messagebox.showerror("Error", "No se pudo actualizar el artículo. Verifique los datos.")
            return False


    def reorder_inventario_ids(self):
        """Reordena los IDs del inventario para asegurar que sean consecutivos."""
        try:
            # Obtener todos los artículos ordenados por ID
            query = "SELECT id FROM inventario ORDER BY id"
            articulos = self.execute_query(query, fetch=True)
            
            # Si no hay artículos, no hay nada que reordenar
            if not articulos:
                return
            
            # Verificar si los IDs son consecutivos
            ids_consecutivos = True
            for i, articulo in enumerate(articulos, start=1):
                if articulo[0] != i:
                    ids_consecutivos = False
                    break
            
            # Si los IDs ya son consecutivos, no hay nada que hacer
            if ids_consecutivos:
                return
            
            # Crear una tabla temporal
            self.execute_query("CREATE TEMPORARY TABLE temp_inventario AS SELECT * FROM inventario ORDER BY id")
            
            # Vaciar la tabla original
            self.execute_query("DELETE FROM inventario")
            
            # Insertar los datos de nuevo con IDs consecutivos
            self.execute_query("""
                INSERT INTO inventario (nombre, descripcion, cantidad, fecha_ingreso, imagen_path, categoria, ubicacion, stock_minimo)
                SELECT nombre, descripcion, cantidad, fecha_ingreso, imagen_path, categoria, ubicacion, stock_minimo
                FROM temp_inventario
                ORDER BY id
            """)
            
            # Eliminar la tabla temporal
            self.execute_query("DROP TABLE temp_inventario")
        except sqlite3.OperationalError as e:
            # Si la base de datos está bloqueada, mostrar un mensaje pero no interrumpir
            print(f"Error al reordenar IDs: {e}")
        except Exception as e:
            # Para otros errores, registrar pero no interrumpir
            print(f"Error al reordenar IDs: {e}")

    def get_inventario_for_export(self):
        """Obtiene los datos del inventario en formato adecuado para exportación"""
        query = '''
            SELECT id, nombre, descripcion, cantidad, stock_minimo, ubicacion, fecha_ingreso, categoria
            FROM inventario
            ORDER BY id
        '''
        try:
            return self.execute_query(query, fetch=True)
        except Exception as e:
            print(f"Error al obtener datos para exportación: {e}")
            return []

    def get_categorias(self):
        """Obtiene todas las categorías únicas disponibles en la base de datos"""
        query = '''
            SELECT DISTINCT categoria
            FROM inventario
            WHERE categoria IS NOT NULL AND categoria != ''
            ORDER BY categoria
        '''
        try:
            result = self.execute_query(query, fetch=True)
            # Convertir la lista de tuplas en una lista simple
            return [categoria[0] for categoria in result]
        except Exception as e:
            print(f"Error al obtener categorías: {e}")
            return ["Herramientas", "Electrónicos", "Muebles", "Oficina", "Otros"]

    def validar_stock(self, articulo_id):
        """Valida si el stock de un artículo está por debajo del mínimo."""
        query = '''
            SELECT cantidad, stock_minimo
            FROM inventario
            WHERE id = ?
        '''
        result = self.execute_query(query, (articulo_id,), fetch=True)
        if result:
            cantidad, stock_minimo = result[0]
            if stock_minimo is not None:
                if cantidad <= 0:
                    return "Crítico"
                elif cantidad <= stock_minimo:
                    return "Bajo"
            return "OK"
        return None # Artículo no encontrado

    def get_articulo_by_id(self, articulo_id):
        """Obtiene un artículo por su ID"""
        query = '''
            SELECT 
                id,
                nombre,
                descripcion,
                cantidad,
                imagen_path,
                categoria,
                ubicacion,
                stock_minimo,
                fecha_ingreso
            FROM inventario
            WHERE id = ?
        '''
        result = self.execute_query(query, (articulo_id,), fetch=True)
        return result[0] if result else None
    
    