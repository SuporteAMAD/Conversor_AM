"""
WebSocket para progresso de conversão em tempo real
Conversor AM v2.2.0
"""

import json
import logging
from typing import Dict, Set
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Gerencia conexões WebSocket para atualização de progresso.
    Usa Queue para comunicação thread-safe.
    """
    
    def __init__(self):
        """Inicializa WebSocket manager."""
        # Mapear task_id -> List[conexões] (usando list em vez de set para flexibilidade)
        self.connections: Dict[str, list] = {}
        # Queue para mensagens broadcast
        self.message_queue = Queue()
    
    def register_connection(self, task_id: str, connection):
        """
        Registra conexão WebSocket para uma tarefa.
        
        Args:
            task_id: ID da tarefa
            connection: Objeto de conexão WebSocket
        """
        if task_id not in self.connections:
            self.connections[task_id] = []
        self.connections[task_id].append(connection)
        logger.info(f"Conexão WebSocket registrada: {task_id} ({len(self.connections[task_id])} total)")
    
    def unregister_connection(self, task_id: str, connection):
        """
        Remove conexão WebSocket.
        
        Args:
            task_id: ID da tarefa
            connection: Objeto de conexão WebSocket
        """
        if task_id in self.connections:
            try:
                self.connections[task_id].remove(connection)
            except ValueError:
                pass
            if not self.connections[task_id]:
                del self.connections[task_id]
            logger.info(f"Conexão WebSocket removida: {task_id}")
    
    def send_progress(self, task_id: str, progress: int, eta_seconds: int = None):
        """
        Envia atualização de progresso para todas as conexões da tarefa.
        
        Args:
            task_id: ID da tarefa
            progress: Percentual (0-100)
            eta_seconds: ETA em segundos
        """
        message = {
            "type": "progress",
            "task_id": task_id,
            "progress": progress,
            "eta_seconds": eta_seconds
        }
        
        if task_id in self.connections:
            for conn in list(self.connections[task_id]):
                try:
                    conn.send(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Erro ao enviar progresso: {e}")
                    self.unregister_connection(task_id, conn)
    
    def send_completion(self, task_id: str, success: bool, result: Dict = None, error: str = None):
        """
        Envia notificação de conclusão.
        
        Args:
            task_id: ID da tarefa
            success: True se sucesso
            result: Dict com dados de resultado
            error: Mensagem de erro se falhou
        """
        message = {
            "type": "completion",
            "task_id": task_id,
            "success": success,
            "result": result or {},
            "error": error
        }
        
        if task_id in self.connections:
            for conn in list(self.connections[task_id]):
                try:
                    conn.send(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Erro ao enviar conclusão: {e}")
                    self.unregister_connection(task_id, conn)
    
    def get_connected_count(self, task_id: str) -> int:
        """Retorna número de conexões ativas para uma tarefa."""
        return len(self.connections.get(task_id, set()))


# Instância global
_ws_manager = WebSocketManager()


def get_ws_manager() -> WebSocketManager:
    """Retorna instância global do WebSocket manager."""
    return _ws_manager
