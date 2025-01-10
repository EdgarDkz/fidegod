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
    def agregar_articulo(self, nombre_articulo, descripcion, cantidad_disponible, imagen):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
            INSERT INTO inventario (nombre_articulo, descripcion, cantidad_disponible, imagen)
            VALUES (?, ?, ?, ?)
            ''', (nombre_articulo, descripcion, cantidad_disponible, imagen))
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
            
            # Verificar stock actual
            cursor.execute('SELECT cantidad_disponible FROM inventario WHERE id=?', (id_articulo,))
            stock_actual = cursor.fetchone()[0]
            
            if tipo == 'salida' and stock_actual < cantidad:
                return False, "Stock insuficiente"

            # Actualizar inventario
            nueva_cantidad = stock_actual + cantidad if tipo == 'entrada' else stock_actual - cantidad
            cursor.execute('''
            UPDATE inventario SET cantidad_disponible=? WHERE id=?
            ''', (nueva_cantidad, id_articulo))

            # Registrar transacción
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT INTO transacciones (id_articulo, tipo, cantidad, fecha)
            VALUES (?, ?, ?, ?)
            ''', (id_articulo, tipo, cantidad, fecha_actual))

            conexion.commit()
            return True, "Transacción exitosa"
        except Exception as e:
            print(f"Error en transacción: {e}")
            return False, str(e)
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

    def verificar_stock_minimo(self):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
            SELECT nombre_articulo, cantidad_disponible, stock_minimo 
            FROM inventario 
            WHERE cantidad_disponible <= stock_minimo
            ''')
            return cursor.fetchall()
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

    def actualizar_articulo(self, id, nombre_articulo, descripcion, cantidad_disponible, imagen):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute('''
            UPDATE inventario 
            SET nombre_articulo=?, descripcion=?, cantidad_disponible=?, imagen=?
            WHERE id=?
            ''', (nombre_articulo, descripcion, cantidad_disponible, imagen, id))
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
