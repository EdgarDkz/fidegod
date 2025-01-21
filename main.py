import sqlite3
import tkinter as tk
from interfaz import Aplicacion
from gestion import crear_base_datos

def crear_base_datos():
    conexion = sqlite3.connect('gestion_inventario.db')
    cursor = conexion.cursor()

    # Crear tabla inventario si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_articulo TEXT NOT NULL,
        descripcion TEXT,
        cantidad_disponible INTEGER DEFAULT 0,
        imagen TEXT,
        fecha_ingreso DATE
    )
    ''')

    # Crear tabla transacciones si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_articulo INTEGER,
        tipo TEXT CHECK(tipo IN ('entrada', 'salida')),
        cantidad INTEGER,
        fecha TEXT,
        stock_actual INTEGER,
        FOREIGN KEY (id_articulo) REFERENCES inventario(id)
    )
    ''')

    # Crear tabla personas si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        articulo TEXT,
        telefono TEXT,
        direccion TEXT,
        municipio TEXT,
        fecha_peticion TEXT,
        fecha_entrega TEXT
    )
    ''')

    conexion.commit()
    conexion.close()

def main():
    # Crear la base de datos si no existe
    crear_base_datos()
    
    # Iniciar la aplicación
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()

if __name__ == "__main__":
    main()
