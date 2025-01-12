import sqlite3

def crear_base_datos():
    conexion = sqlite3.connect('gestion_inventario.db')
    cursor = conexion.cursor()

    # Crear tabla personas con la nueva columna articulo
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

    # Eliminar la tabla si ya existe
    cursor.execute('DROP TABLE IF EXISTS inventario;')
    cursor.execute('DROP TABLE IF EXISTS transacciones;')

    # Crear tabla inventario
    cursor.execute('''
    CREATE TABLE inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_articulo TEXT NOT NULL,
        descripcion TEXT,
        cantidad_disponible INTEGER DEFAULT 0,
        imagen TEXT,
        fecha_ingreso DATE
    )
    ''')

    # Crear tabla transacciones con la columna stock_actual
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

    conexion.commit()
    conexion.close()

if __name__ == '__main__':
    crear_base_datos()
