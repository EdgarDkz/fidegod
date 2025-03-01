import sqlite3

class Database:
    def __init__(self, db_name="database.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.migrate_database() # Llamar a la función de migración al inicializar la base de datos

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            articulo TEXT,
            telefono TEXT,
            direccion TEXT,
            municipio TEXT,
            fecha_pedido TEXT,
            fecha_entrega TEXT,
            estado TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            imagen_path TEXT,
            fecha_ingreso TEXT,
            categoria TEXT,         -- Nueva columna Categoría
            ubicacion TEXT,         -- Nueva columna Ubicación
            stock_minimo INTEGER    -- Nueva columna Stock Mínimo
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY,
            articulo TEXT,
            tipo TEXT,
            cantidad INTEGER,
            stock_anterior INTEGER,
            stock_actual INTEGER,
            fecha TEXT
        )''')
        self.connection.commit()

    def migrate_database(self):
        """Migra la base de datos añadiendo las nuevas columnas a la tabla inventario si no existen."""
        try:
            self.cursor.execute("SELECT categoria FROM inventario LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE inventario ADD COLUMN categoria TEXT")
            self.connection.commit()
            print("Columna 'categoria' añadida a la tabla inventario.")

        try:
            self.cursor.execute("SELECT ubicacion FROM inventario LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE inventario ADD COLUMN ubicacion TEXT")
            self.connection.commit()
            print("Columna 'ubicacion' añadida a la tabla inventario.")

        try:
            self.cursor.execute("SELECT stock_minimo FROM inventario LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE inventario ADD COLUMN stock_minimo INTEGER")
            self.connection.commit()
            print("Columna 'stock_minimo' añadida a la tabla inventario.")


    def add_persona(self, nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado, id=None):
        if id is not None:
            # Si se proporciona un ID, intentar insertar con ese ID específico
            self.cursor.execute('''INSERT INTO personas (id, nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (id, nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado))
        else:
            # Si no se proporciona ID, dejar que SQLite asigne uno automáticamente
            self.cursor.execute('''INSERT INTO personas (nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                (nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado))
        self.connection.commit()

    def get_personas(self):
        self.cursor.execute('SELECT * FROM personas')
        return self.cursor.fetchall()

    def update_persona(self, persona_id, **kwargs):
        """Actualiza los datos de una persona en la base de datos.

        Args:
            persona_id: ID de la persona a actualizar
            **kwargs: Pares clave-valor de los campos a actualizar
        """
        try:
            # Construir la consulta SQL dinámicamente
            columns = ', '.join(f"{k} = ?" for k in kwargs.keys())
            values = list(kwargs.values()) + [persona_id]

            # Ejecutar la consulta
            self.cursor.execute(f'UPDATE personas SET {columns} WHERE id = ?', values)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar persona en la base de datos: {str(e)}")
            self.connection.rollback()
            return False

    def delete_persona(self, persona_id):
        self.cursor.execute('DELETE FROM personas WHERE id = ?', (persona_id,))
        self.connection.commit()

    def add_producto(self, nombre, descripcion, cantidad, imagen, fecha_ingreso, categoria=None, ubicacion=None, stock_minimo=None): # Añadidos nuevos campos como argumentos opcionales
        self.cursor.execute('''INSERT INTO inventario (nombre, descripcion, cantidad, imagen_path, fecha_ingreso, categoria, ubicacion, stock_minimo)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (nombre, descripcion, cantidad, imagen, fecha_ingreso, categoria, ubicacion, stock_minimo))
        self.connection.commit()

    def get_inventario(self):
        self.cursor.execute('SELECT * FROM inventario')
        return self.cursor.fetchall()

    def get_inventario_for_export(self):
        """Obtiene todos los datos del inventario para exportar, incluyendo las nuevas columnas."""
        self.cursor.execute('SELECT id, nombre, descripcion, cantidad, stock_minimo, ubicacion, fecha_ingreso, categoria FROM inventario ORDER BY id DESC')
        return self.cursor.fetchall()

    def update_producto(self, producto_id, **kwargs):
        columns = ', '.join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [producto_id]
        self.cursor.execute(f'UPDATE inventario SET {columns} WHERE id = ?', values)
        self.connection.commit()

    def delete_producto(self, producto_id):
        try:
            self.cursor.execute('DELETE FROM inventario WHERE id = ?', (producto_id,))
            self.connection.commit()
            self.reorder_inventario_ids()  # Llama a la función para reordenar los IDs después de la eliminación
        except Exception as e:
            self.connection.rollback()  # Revierte la transacción en caso de error
            print(f"Error al eliminar el producto: {e}")

    def add_transaccion(self, articulo, tipo, cantidad, stock_anterior, stock_actual, fecha):
        self.cursor.execute('''INSERT INTO transacciones (articulo, tipo, cantidad, stock_anterior, stock_actual, fecha)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (articulo, tipo, cantidad, stock_anterior, stock_actual, fecha))
        self.connection.commit()

    def get_transacciones(self):
        self.cursor.execute('SELECT * FROM transacciones')
        return self.cursor.fetchall()

    def update_transaccion(self, transaccion_id, **kwargs):
        columns = ', '.join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [transaccion_id]
        self.cursor.execute(f'UPDATE transacciones SET {columns} WHERE id = ?', values)
        self.connection.commit()

    def delete_transaccion(self, transaccion_id):
        self.cursor.execute('DELETE FROM transacciones WHERE id = ?', (transaccion_id,))
        self.connection.commit()

    def reorder_personas_ids(self):
        """Reorganiza los IDs en la tabla personas para que sean continuos."""
        # Crear una tabla temporal con la estructura correcta
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS personas_temp (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            articulo TEXT,
            telefono TEXT,
            direccion TEXT,
            municipio TEXT,
            fecha_pedido TEXT,
            fecha_entrega TEXT,
            estado TEXT
        )''')

        # Copiar los datos a la tabla temporal, excluyendo el ID
        self.cursor.execute('''INSERT INTO personas_temp (id, nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado)
                              SELECT ROW_NUMBER() OVER (ORDER BY id) AS new_id, nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado
                              FROM personas
                              ORDER BY id''')

        # Eliminar la tabla original
        self.cursor.execute('DROP TABLE personas')

        # Renombrar la tabla temporal a la original
        self.cursor.execute('ALTER TABLE personas_temp RENAME TO personas')

        self.connection.commit()

    def reorder_inventario_ids(self):
        try:
            # Crear una tabla temporal con la estructura correcta para inventario
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS inventario_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL,
                imagen_path TEXT,
                fecha_ingreso TEXT,
                categoria TEXT,
                ubicacion TEXT,
                stock_minimo INTEGER
            )''')

            # Copiar los datos a la tabla temporal, excluyendo el ID
            self.cursor.execute('''INSERT INTO inventario_temp (nombre, descripcion, cantidad, imagen_path, fecha_ingreso, categoria, ubicacion, stock_minimo)
                                  SELECT nombre, descripcion, cantidad, imagen_path, fecha_ingreso, categoria, ubicacion, stock_minimo
                                  FROM inventario
                                  ORDER BY id''')

            # Eliminar la tabla original
            self.cursor.execute('DROP TABLE inventario')

            # Renombrar la tabla temporal a la original
            self.cursor.execute('ALTER TABLE inventario_temp RENAME TO inventario')

            self.connection.commit()
        except Exception as e:
            self.connection.rollback()  # Revierte la transacción en caso de error
            print(f"Error al reordenar los IDs del inventario: {e}")

    def update_persona_id(self, old_id: int, new_id: int) -> None:
        """Actualiza el ID de una persona en la base de datos"""
        try:
            # Primero verificar si el nuevo ID ya existe
            self.cursor.execute("SELECT id FROM personas WHERE id = ?", (new_id,))
            exists = self.cursor.fetchone()

            if exists:
                # Si existe, usar un ID temporal (negativo) primero
                temp_id = -new_id
                self.cursor.execute("""
                    UPDATE personas
                    SET id = ?
                    WHERE id = ?
                """, (temp_id, old_id))

                # Luego actualizar al ID final
                self.cursor.execute("""
                    UPDATE personas
                    SET id = ?
                    WHERE id = ?
                """, (new_id, temp_id))
            else:
                # Si no existe, actualizar directamente
                self.cursor.execute("""
                    UPDATE personas
                    SET id = ?
                    WHERE id = ?
                """, (new_id, old_id))

            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Error al actualizar ID: {str(e)}")