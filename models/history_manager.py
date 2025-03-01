from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import datetime

class Command(ABC):
    """Clase base abstracta para comandos"""
    
    @abstractmethod
    def execute(self) -> None:
        """Ejecuta el comando"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Deshace el comando"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Retorna una descripción del comando"""
        pass

class DeletePersonaCommand(Command):
    def __init__(self, controller, persona_data: Dict[str, Any]):
        self.controller = controller
        self.persona_data = persona_data
        self.timestamp = datetime.now()
        self.old_id = persona_data['id']
        # Guardar el estado de los IDs al momento de la eliminación
        self.affected_records = self._get_affected_records()
    
    def _get_affected_records(self) -> List[Dict[str, Any]]:
        """Guarda los registros que serán afectados por el reordenamiento"""
        personas = self.controller.get_personas()
        return [
            {
                'id': p[0],
                'nombre': p[1],
                'articulo': p[2],
                'telefono': p[3],
                'direccion': p[4],
                'municipio': p[5],
                'fecha_pedido': p[6],
                'fecha_entrega': p[7],
                'estado': p[8]
            }
            for p in personas if p[0] > self.old_id
        ]
    
    def execute(self) -> None:
        self.controller.delete_persona(self.persona_data['id'])
    
    def undo(self) -> None:
        """Restaura el registro eliminado a su posición original"""
        current_personas = self.controller.get_personas()
        
        # Primero, mover los registros que estaban después del ID eliminado
        for record in reversed(self.affected_records):
            # Mover cada registro una posición adelante
            self.controller.update_persona_id(record['id'] - 1, record['id'])
        
        # Ahora restaurar el registro eliminado en su posición original
        self.controller.add_persona(
            id=self.old_id,
            nombre=self.persona_data['nombre'],
            articulo=self.persona_data['articulo'],
            telefono=self.persona_data['telefono'],
            direccion=self.persona_data['direccion'],
            municipio=self.persona_data['municipio'],
            fecha_pedido=self.persona_data['fecha_pedido'],
            fecha_entrega=self.persona_data['fecha_entrega'],
            estado=self.persona_data['estado']
        )
    
    def get_description(self) -> str:
        return f"Eliminación de {self.persona_data['nombre']} ({self.timestamp.strftime('%H:%M:%S')})"

class EditPersonaCommand(Command):
    def __init__(self, controller, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        self.controller = controller
        self.old_data = old_data
        self.new_data = new_data
        self.timestamp = datetime.now()
    
    def execute(self) -> None:
        # Extraer el ID y el resto de los datos
        persona_id = self.new_data.pop('id')
        # Llamar a update_persona con el ID como primer argumento
        self.controller.update_persona(persona_id, **self.new_data)
        # Restaurar el ID en new_data para futuras operaciones
        self.new_data['id'] = persona_id
    
    def undo(self) -> None:
        # Extraer el ID y el resto de los datos
        persona_id = self.old_data.pop('id')
        # Llamar a update_persona con el ID como primer argumento
        self.controller.update_persona(persona_id, **self.old_data)
        # Restaurar el ID en old_data para futuras operaciones
        self.old_data['id'] = persona_id
    
    def get_description(self) -> str:
        return f"Edición de {self.new_data['nombre']} ({self.timestamp.strftime('%H:%M:%S')})"

class AddPersonaCommand(Command):
    def __init__(self, controller, persona_data: Dict[str, Any]):
        self.controller = controller
        self.persona_data = persona_data
        self.timestamp = datetime.now()
    
    def execute(self) -> None:
        self.controller.add_persona(**self.persona_data)
    
    def undo(self) -> None:
        self.controller.delete_persona(self.persona_data['id'])
    
    def get_description(self) -> str:
        return f"Adición de {self.persona_data['nombre']} ({self.timestamp.strftime('%H:%M:%S')})"

class HistoryManager:
    def __init__(self, max_history: int = 50):
        self.history: List[Command] = []
        self.current_index: int = -1
        self.max_history = max_history
    
    def execute_command(self, command: Command) -> None:
        """Ejecuta un nuevo comando y lo agrega al historial"""
        # Eliminar cualquier comando futuro si estamos en medio del historial
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Ejecutar el comando
        command.execute()
        
        # Agregar al historial
        self.history.append(command)
        self.current_index += 1
        
        # Mantener el límite de historial
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def undo(self) -> bool:
        """Deshace el último comando. Retorna True si se pudo deshacer."""
        if self.can_undo():
            self.history[self.current_index].undo()
            self.current_index -= 1
            return True
        return False
    
    def redo(self) -> bool:
        """Rehace el último comando deshecho. Retorna True si se pudo rehacer."""
        if self.can_redo():
            self.current_index += 1
            self.history[self.current_index].execute()
            return True
        return False
    
    def can_undo(self) -> bool:
        """Verifica si es posible deshacer"""
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        """Verifica si es posible rehacer"""
        return self.current_index < len(self.history) - 1
    
    def get_undo_description(self) -> str:
        """Obtiene la descripción del comando que se puede deshacer"""
        if self.can_undo():
            return self.history[self.current_index].get_description()
        return ""
    
    def get_redo_description(self) -> str:
        """Obtiene la descripción del comando que se puede rehacer"""
        if self.can_redo():
            return self.history[self.current_index + 1].get_description()
        return ""
    
    def clear(self) -> None:
        """Limpia el historial"""
        self.history.clear()
        self.current_index = -1 