"""
Worker Thread para processar conversões da fila
Conversor AM v2.2.0
"""

import os
import threading
import time
import logging
from typing import Callable, Optional
from datetime import datetime
import traceback

from queue_manager import QueueManager, ConversionStatus

logger = logging.getLogger(__name__)


class ConversionWorker:
    """
    Worker thread que processa conversões da fila.
    Executa conversões sequencialmente usando funções do conversor.
    """
    
    def __init__(self, 
                 conversion_func: Callable,
                 queue_manager: QueueManager,
                 max_concurrent: int = 1,
                 check_interval: float = 2.0):
        """
        Inicializa worker.
        
        Args:
            conversion_func: Função para converter arquivo (task_data -> (success, result, error))
            queue_manager: Instância do QueueManager
            max_concurrent: Número máximo de conversões simultâneas
            check_interval: Intervalo em segundos para verificar fila
        """
        self.conversion_func = conversion_func
        self.queue_manager = queue_manager
        self.max_concurrent = max_concurrent
        self.check_interval = check_interval
        
        self.active_threads = []
        self.is_running = False
        self.worker_thread = None
        
        logger.info(f"ConversionWorker inicializado (max_concurrent={max_concurrent})")
    
    def start(self):
        """Inicia thread do worker."""
        if self.is_running:
            logger.warning("Worker já está rodando")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Worker iniciado")
    
    def stop(self):
        """Para thread do worker."""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=10)
        logger.info("Worker parado")
    
    def _worker_loop(self):
        """Loop principal do worker - verifica fila e processa tarefas."""
        while self.is_running:
            try:
                # Limpar threads completadas
                self.active_threads = [t for t in self.active_threads if t.is_alive()]
                
                # Se temos slots disponíveis e há tarefas na fila
                if len(self.active_threads) < self.max_concurrent:
                    task = self.queue_manager.get_next_task()
                    if task:
                        # Iniciar nova thread para processar tarefa
                        thread = threading.Thread(
                            target=self._process_task,
                            args=(task,),
                            daemon=True
                        )
                        thread.start()
                        self.active_threads.append(thread)
                
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Erro no worker loop: {e}", exc_info=True)
                time.sleep(self.check_interval)
    
    def _process_task(self, task: dict):
        """
        Processa uma tarefa de conversão.
        
        Args:
            task: Dict com dados da tarefa
        """
        task_id = task['id']
        filename_original = task['filename_original']
        start_time = time.time()
        
        logger.info(f"Iniciando conversão: {task_id} ({filename_original})")
        
        try:
            # Atualizar status para PROCESSING
            self.queue_manager.update_progress(task_id, 0, None)
            
            # Chamar função de conversão
            # A função deve aceitar task_id para atualizar progresso
            success, result, error = self.conversion_func(task_id, task)
            
            if success:
                # Marca como concluído
                duration_ms = int((time.time() - start_time) * 1000)
                filename_result = result.get('filename') if isinstance(result, dict) else str(result)
                
                self.queue_manager.mark_completed(task_id, filename_result, duration_ms)
                logger.info(f"Conversão concluída: {task_id} ({duration_ms}ms)")
            else:
                # Erro na conversão
                self.queue_manager.mark_error(task_id, error or "Erro desconhecido")
                logger.error(f"Erro na conversão: {task_id} - {error}")
        
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.queue_manager.mark_error(task_id, error_msg)
            logger.error(f"Exceção na conversão: {task_id} - {error_msg}")
    
    def get_active_conversions(self) -> int:
        """Retorna número de conversões ativas."""
        return len([t for t in self.active_threads if t.is_alive()])


# Instância global (inicializada depois)
_worker = None


def init_worker(conversion_func: Callable, 
                queue_manager: Optional[QueueManager] = None,
                max_concurrent: int = 1) -> ConversionWorker:
    """
    Inicializa worker global.
    
    Args:
        conversion_func: Função para converter
        queue_manager: QueueManager (cria se None)
        max_concurrent: Máximo de conversões simultâneas
    
    Returns:
        Instância do ConversionWorker
    """
    global _worker
    
    if queue_manager is None:
        queue_manager = QueueManager()
    
    _worker = ConversionWorker(
        conversion_func=conversion_func,
        queue_manager=queue_manager,
        max_concurrent=max_concurrent
    )
    return _worker


def get_worker() -> Optional[ConversionWorker]:
    """Retorna instância global do worker."""
    return _worker


def start_worker():
    """Inicia worker global."""
    if _worker:
        _worker.start()


def stop_worker():
    """Para worker global."""
    if _worker:
        _worker.stop()
