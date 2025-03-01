from models.db import Database

class TransaccionesController:
    def __init__(self):
        self.db = Database()

    def add_transaccion(self, articulo, tipo, cantidad, stock_anterior, stock_actual, fecha):
        self.db.add_transaccion(articulo, tipo, cantidad, stock_anterior, stock_actual, fecha)

    def get_transacciones(self):
        return self.db.get_transacciones()

    def update_transaccion(self, transaccion_id, **kwargs):
        self.db.update_transaccion(transaccion_id, **kwargs)

    def delete_transaccion(self, transaccion_id):
        self.db.delete_transaccion(transaccion_id) 