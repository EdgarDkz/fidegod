import sqlite3
import csv
from datetime import datetime
import os
from tkinter import messagebox
import pandas as pd

class GestionDB:
    def __init__(self):
        self.db_name = 'gestion_inventario.db'

    # Funciones para gestión de personas
    def agregar_persona(self, nombre, telefono, direccion, municipio, fecha_peticion, fecha_entrega):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
            INSERT INTO personas (nombre, telefono, direccion, municipio, fecha_peticion, fecha_entrega)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, telefono, direccion, municipio, fecha_peticion, fecha_entrega))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al agregar persona: {e}")
            return False
        finally:
            conexion.close()

    def obtener_personas(self, filtro=None):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            if filtro:
                cursor.execute('''
                SELECT * FROM personas 
                WHERE nombre LIKE ? OR telefono LIKE ? OR municipio LIKE ?
                ''', (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
            else:
                cursor.execute('SELECT * FROM personas')
            return cursor.fetchall()
        finally:
            conexion.close()

    def actualizar_persona(self, id, nombre, telefono, direccion, municipio, fecha_peticion, fecha_entrega):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
            UPDATE personas 
            SET nombre=?, telefono=?, direccion=?, municipio=?, fecha_peticion=?, fecha_entrega=?
            WHERE id=?
            ''', (nombre, telefono, direccion, municipio, fecha_peticion, fecha_entrega, id))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar persona: {e}")
            return False
        finally:
            conexion.close()

    def eliminar_persona(self, id):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            
            # Primero eliminamos la persona seleccionada
            cursor.execute('DELETE FROM personas WHERE id=?', (id,))
            
            # Actualizamos los IDs de los registros posteriores
            cursor.execute('''
                UPDATE personas 
                SET id = id - 1 
                WHERE id > ?
            ''', (id,))
            
            # Reiniciamos la secuencia del autoincremento
            cursor.execute('''
                UPDATE sqlite_sequence 
                SET seq = (SELECT MAX(id) FROM personas) 
                WHERE name = 'personas'
            ''')
            
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar persona: {e}")
            return False
        finally:
            conexion.close()

    # Funciones para gestión de inventario
    def agregar_articulo(self, nombre_articulo, descripcion, cantidad_disponible, imagen, fecha_ingreso):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO inventario (nombre_articulo, descripcion, cantidad_disponible, imagen, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre_articulo, descripcion, cantidad_disponible, imagen, fecha_ingreso))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al agregar artículo: {e}")
            return False
        finally:
            conexion.close()

    def obtener_inventario(self, filtro=None):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            if filtro:
                cursor.execute('''
                SELECT * FROM inventario 
                WHERE nombre_articulo LIKE ? OR descripcion LIKE ?
                ''', (f'%{filtro}%', f'%{filtro}%'))
            else:
                cursor.execute('SELECT * FROM inventario')
            return cursor.fetchall()
        finally:
            conexion.close()

    def registrar_transaccion(self, id_articulo, tipo, cantidad):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()

            # Obtener la cantidad actual del artículo
            cursor.execute('SELECT cantidad_disponible FROM inventario WHERE id=?', (id_articulo,))
            cantidad_actual = cursor.fetchone()[0]

            # Actualizar la cantidad según el tipo de transacción
            if tipo == 'entrada':
                nueva_cantidad = cantidad_actual + cantidad
            elif tipo == 'salida':
                nueva_cantidad = cantidad_actual - cantidad
                if nueva_cantidad < 0:
                    return False  # No se puede tener cantidad negativa

            # Actualizar el inventario
            cursor.execute('UPDATE inventario SET cantidad_disponible=? WHERE id=?', (nueva_cantidad, id_articulo))
            conexion.commit()

            # Registrar la transacción
            cursor.execute('INSERT INTO transacciones (id_articulo, tipo, cantidad, fecha) VALUES (?, ?, ?, ?)',
                           (id_articulo, tipo, cantidad, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conexion.commit()

            return True
        except Exception as e:
            print(f"Error al registrar transacción: {e}")
            return False
        finally:
            conexion.close()

    def exportar_a_csv(self, tipo):
        try:
            conexion = sqlite3.connect(self.db_name)
            
            if tipo == 'personas':
                df = pd.read_sql_query('''
                    SELECT 
                        nombre as "Nombre",
                        telefono as "Teléfono",
                        direccion as "Dirección",
                        municipio as "Municipio",
                        fecha_peticion as "Fecha Petición",
                        fecha_entrega as "Fecha Entrega"
                    FROM personas
                    ORDER BY nombre
                ''', conexion)
                filename = 'Reporte_Personas.xlsx'
            else:
                df = pd.read_sql_query('''
                    SELECT 
                        nombre_articulo as "Nombre Artículo",
                        descripcion as "Descripción",
                        cantidad_disponible as "Cantidad"
                    FROM inventario
                    ORDER BY nombre_articulo
                ''', conexion)
                filename = 'Reporte_Inventario.xlsx'

            # Crear un writer de Excel
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            workbook = writer.book
            worksheet = workbook.add_worksheet('Reporte')
            
            # Escribir los encabezados
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value)
                
            # Escribir los datos
            for row_num, row in enumerate(df.values):
                for col_num, value in enumerate(row):
                    worksheet.write(row_num + 1, col_num, value)

            # Obtener el rango de la tabla
            end_row = len(df.index)
            end_col = len(df.columns) - 1
            table_range = f'A1:{chr(65 + end_col)}{end_row + 1}'

            # Agregar la tabla con formato
            worksheet.add_table(table_range, {
                'columns': [{'header': col} for col in df.columns],
                'style': 'Table Style Medium 2',
                'autofilter': True
            })

            # Ajustar el ancho de las columnas
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.set_column(i, i, max_length)

            writer.close()
            
            return True, f"Datos exportados a {filename}"
        except Exception as e:
            return False, f"Error al exportar: {e}"
        finally:
            conexion.close()

    def obtener_articulo(self, id):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM inventario WHERE id=?', (id,))
            return cursor.fetchone()
        finally:
            conexion.close()

    def actualizar_articulo(self, id, nombre_articulo, descripcion, cantidad_disponible, imagen, fecha_ingreso):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            
            # Actualizar el artículo, incluyendo la fecha de ingreso
            cursor.execute(''' 
            UPDATE inventario 
            SET nombre_articulo=?, descripcion=?, cantidad_disponible=?, imagen=?, fecha_ingreso=?
            WHERE id=? 
            ''', (nombre_articulo, descripcion, cantidad_disponible, imagen, fecha_ingreso, id))
            
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar artículo: {e}")
            return False
        finally:
            conexion.close()

    def eliminar_articulo(self, id):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            
            # Primero eliminamos el artículo seleccionado
            cursor.execute('DELETE FROM inventario WHERE id=?', (id,))
            
            # Actualizamos los IDs de los registros posteriores
            cursor.execute('''
                UPDATE inventario 
                SET id = id - 1 
                WHERE id > ?
            ''', (id,))
            
            # Reiniciamos la secuencia del autoincremento
            cursor.execute('''
                UPDATE sqlite_sequence 
                SET seq = (SELECT MAX(id) FROM inventario) 
                WHERE name = 'inventario'
            ''')
            
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar artículo: {e}")
            return False
        finally:
            conexion.close()

    def buscar_articulos(self, filtro):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT * FROM inventario 
                WHERE nombre_articulo LIKE ? OR descripcion LIKE ?
            ''', (f'%{filtro}%', f'%{filtro}%'))
            return cursor.fetchall()
        finally:
            conexion.close()

    def eliminar_columna_stock_minimo(self):
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        
        # Crear una nueva tabla sin la columna stock_minimo
        cursor.execute('''
        CREATE TABLE inventario_nueva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_articulo TEXT NOT NULL,
            descripcion TEXT,
            cantidad_disponible INTEGER DEFAULT 0,
            imagen TEXT,
            fecha_ingreso DATE
        )
        ''')
        
        # Copiar los datos de la tabla antigua a la nueva
        cursor.execute('''
        INSERT INTO inventario_nueva (id, nombre_articulo, descripcion, cantidad_disponible, imagen, fecha_ingreso)
        SELECT id, nombre_articulo, descripcion, cantidad_disponible, imagen, fecha_ingreso FROM inventario
        ''')
        
        # Eliminar la tabla antigua
        cursor.execute('DROP TABLE inventario')
        
        # Renombrar la nueva tabla
        cursor.execute('ALTER TABLE inventario_nueva RENAME TO inventario')
        
        conexion.commit()
        conexion.close()

    def obtener_transacciones(self):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT t.id, i.nombre_articulo, t.tipo, t.cantidad, t.fecha, i.cantidad_disponible 
                FROM transacciones t 
                JOIN inventario i ON t.id_articulo = i.id
            ''')
            return cursor.fetchall()
        finally:
            conexion.close()

    def obtener_cantidad_articulo(self, id_articulo):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('SELECT cantidad_disponible FROM inventario WHERE id=?', (id_articulo,))
            return cursor.fetchone()[0]
        finally:
            conexion.close()
