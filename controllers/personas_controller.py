from models.db import Database
from models.history_manager import HistoryManager, AddPersonaCommand, EditPersonaCommand, DeletePersonaCommand

class PersonasController:
    def __init__(self):
        self.db = Database()
        self.history_manager = HistoryManager()

    def add_persona(self, **kwargs):
        """Agrega una nueva persona usando el sistema de historial"""
        # Si no se proporciona ID, obtener el siguiente ID disponible
        if 'id' not in kwargs:
            current_personas = self.get_personas()
            next_id = max([p[0] for p in current_personas], default=0) + 1
            kwargs['id'] = next_id

        # Crear y ejecutar el comando
        command = AddPersonaCommand(self.db, kwargs)
        self.history_manager.execute_command(command)

    def update_persona(self, id, **kwargs):
        """Actualiza una persona usando el sistema de historial"""
        try:
            # Obtener datos antiguos antes de la actualización
            old_data = next((p for p in self.get_personas() if p[0] == id), None)
            if old_data:
                old_data_dict = {
                    'id': old_data[0],
                    'nombre': old_data[1],
                    'articulo': old_data[2],
                    'telefono': old_data[3],
                    'direccion': old_data[4],
                    'municipio': old_data[5],
                    'fecha_pedido': old_data[6],
                    'fecha_entrega': old_data[7],
                    'estado': old_data[8]
                }

                # Preparar nuevos datos
                new_data = old_data_dict.copy()
                new_data.update(kwargs)

                # Crear y ejecutar el comando
                command = EditPersonaCommand(self.db, old_data_dict, new_data)
                self.history_manager.execute_command(command)
            else:
                raise ValueError(f"Persona con ID {id} no encontrada para actualizar.")
        except Exception as e:
            print(f"Error al actualizar persona: {e}")
            raise # Re-raise the exception to be handled by the caller if needed

    def reorder_ids(self):
        """Reordena los IDs de todas las personas para mantener una secuencia continua"""
        personas = self.get_personas()
        # Ordenar por ID actual para mantener el orden relativo
        personas.sort(key=lambda x: x[0])

        # Crear un mapeo de ID viejo a nuevo
        id_mapping = {old_id: new_id + 1 for new_id, (old_id, *_) in enumerate(personas)}

        # Actualizar cada registro con su nuevo ID
        for old_id, nombre, articulo, telefono, direccion, municipio, fecha_pedido, fecha_entrega, estado in personas:
            new_id = id_mapping[old_id]
            if new_id != old_id:  # Solo actualizar si el ID ha cambiado
                self.db.update_persona_id(old_id, new_id)

    def delete_persona(self, id):
        """Elimina una persona usando el sistema de historial y reordena los IDs"""
        # Obtener datos de la persona antes de eliminar
        persona_data = next((p for p in self.get_personas() if p[0] == id), None)
        if persona_data:
            persona_dict = {
                'id': persona_data[0],
                'nombre': persona_data[1],
                'articulo': persona_data[2],
                'telefono': persona_data[3],
                'direccion': persona_data[4],
                'municipio': persona_data[5],
                'fecha_pedido': persona_data[6],
                'fecha_entrega': persona_data[7],
                'estado': persona_data[8]
            }

            # Crear y ejecutar el comando
            command = DeletePersonaCommand(self.db, persona_dict)
            self.history_manager.execute_command(command)

            # Reordenar IDs después de la eliminación
            self.reorder_ids()

    def get_personas(self):
        """Obtiene todas las personas de la base de datos"""
        return self.db.get_personas()

    def undo_last_change(self) -> bool:
        """Deshace el último cambio"""
        return self.history_manager.undo()

    def redo_last_change(self) -> bool:
        """Rehace el último cambio deshecho"""
        return self.history_manager.redo()

    def can_undo(self) -> bool:
        """Verifica si es posible deshacer"""
        return self.history_manager.can_undo()

    def can_redo(self) -> bool:
        """Verifica si es posible rehacer"""
        return self.history_manager.can_redo()

    def get_undo_description(self) -> str:
        """Obtiene la descripción del comando que se puede deshacer"""
        return self.history_manager.get_undo_description()

    def get_redo_description(self) -> str:
        """Obtiene la descripción del comando que se puede rehacer"""
        return self.history_manager.get_redo_description()

    def update_table(self):
        """Actualiza y devuelve todas las personas de la base de datos."""
        return self.get_personas()  # Devolver los datos para que la vista los use