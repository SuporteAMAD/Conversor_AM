"""
Queue Manager para Conversor AM v2.2.0
Gerencia fila de conversões com SQLite
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class ConversionStatus(Enum):
    """Estados possíveis de uma conversão."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class QueueManager:
    """
    Gerencia fila de conversões usando SQLite.
    Simples, sem dependências externas, funciona localmente.
    """
    
    def __init__(self, db_path: str = "queue/queue.db"):
        """Inicializa QueueManager e cria banco de dados."""
        self.db_path = db_path
        self._local = None  # Para thread-local storage se necessário
        
        # Criar diretório queue/ se não existir
        Path("queue").mkdir(exist_ok=True)
        
        # Inicializar banco de dados
        self._init_db()
        logger.info(f"QueueManager inicializado com db: {db_path}")
    
    def close(self):
        """Fecha conexões abertas (para cleanup em testes)."""
        import sqlite3
        # Não há conexões globais mantidas, SQLite fecha automaticamente
        pass
    
    def _init_db(self):
        """Cria tabela de conversões se não existir."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversions (
                    id TEXT PRIMARY KEY,
                    filename_original TEXT NOT NULL,
                    filename_result TEXT,
                    status TEXT DEFAULT 'queued',
                    progress INTEGER DEFAULT 0,
                    eta_seconds INTEGER,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    duration_ms INTEGER,
                    file_size_mb REAL,
                    error_message TEXT,
                    user_ip TEXT,
                    target_format TEXT
                )
            """)
            conn.commit()
    
    def add_task(self, filename: str, target_format: str, user_ip: str, file_size_mb: float = 0) -> str:
        """
        Adiciona nova tarefa à fila.
        
        Args:
            filename: Nome do arquivo original
            target_format: Formato de destino (ex: 'mp4', 'mp3')
            user_ip: IP do usuário que fez upload
            file_size_mb: Tamanho do arquivo em MB
        
        Returns:
            ID da tarefa adicionada
        """
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversions 
                (id, filename_original, status, created_at, user_ip, target_format, file_size_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task_id, filename, ConversionStatus.QUEUED.value, now, user_ip, target_format, file_size_mb))
            conn.commit()
        
        logger.info(f"Tarefa adicionada à fila: {task_id}")
        return task_id
    
    def get_next_task(self) -> Optional[Dict]:
        """
        Pega próxima tarefa da fila para processar.
        
        Returns:
            Dict com dados da tarefa ou None se fila vazia
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversions 
                WHERE status = ?
                ORDER BY created_at ASC
                LIMIT 1
            """, (ConversionStatus.QUEUED.value,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_progress(self, task_id: str, progress: int, eta_seconds: Optional[int] = None):
        """
        Atualiza progresso de uma tarefa em processamento.
        
        Args:
            task_id: ID da tarefa
            progress: Percentual de progresso (0-100)
            eta_seconds: Tempo estimado restante em segundos
        """
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.utcnow().isoformat() + "Z"
            conn.execute("""
                UPDATE conversions 
                SET progress = ?, status = ?, eta_seconds = ?, started_at = 
                    COALESCE(started_at, ?)
                WHERE id = ?
            """, (progress, ConversionStatus.PROCESSING.value, eta_seconds, now, task_id))
            conn.commit()
    
    def mark_completed(self, task_id: str, filename_result: str, duration_ms: int):
        """
        Marca tarefa como concluída.
        
        Args:
            task_id: ID da tarefa
            filename_result: Nome do arquivo convertido
            duration_ms: Tempo total de processamento em milissegundos
        """
        now = datetime.utcnow().isoformat() + "Z"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversions 
                SET status = ?, completed_at = ?, duration_ms = ?, 
                    filename_result = ?, progress = 100
                WHERE id = ?
            """, (ConversionStatus.COMPLETED.value, now, duration_ms, filename_result, task_id))
            conn.commit()
        
        logger.info(f"Tarefa concluída: {task_id} ({duration_ms}ms)")
    
    def mark_error(self, task_id: str, error_msg: str):
        """
        Marca tarefa com erro.
        
        Args:
            task_id: ID da tarefa
            error_msg: Mensagem de erro
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversions 
                SET status = ?, error_message = ?
                WHERE id = ?
            """, (ConversionStatus.ERROR.value, error_msg, task_id))
            conn.commit()
        
        logger.error(f"Tarefa com erro: {task_id} - {error_msg}")
    
    def get_status(self, task_id: str) -> Optional[Dict]:
        """
        Retorna status atual de uma tarefa.
        
        Args:
            task_id: ID da tarefa
        
        Returns:
            Dict com dados da tarefa ou None se não encontrada
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversions WHERE id = ?
            """, (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_queue_stats(self) -> Dict:
        """
        Retorna estatísticas da fila.
        
        Returns:
            Dict com total, queued, processing, completed, errors, avg_duration
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as queued,
                    SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as errors,
                    AVG(duration_ms) as avg_duration_ms
                FROM conversions
            """, (
                ConversionStatus.QUEUED.value,
                ConversionStatus.PROCESSING.value,
                ConversionStatus.COMPLETED.value,
                ConversionStatus.ERROR.value
            ))
            row = cursor.fetchone()
            return {
                "total": row[0] or 0,
                "queued": row[1] or 0,
                "processing": row[2] or 0,
                "completed": row[3] or 0,
                "errors": row[4] or 0,
                "avg_duration_ms": int(row[5]) if row[5] else 0
            }
    
    def get_user_tasks(self, user_ip: str, limit: int = 10) -> List[Dict]:
        """
        Retorna tarefas de um usuário.
        
        Args:
            user_ip: IP do usuário
            limit: Limite de tarefas a retornar
        
        Returns:
            Lista de dicts com dados das tarefas
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversions 
                WHERE user_ip = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_ip, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_tasks(self, days: int = 7):
        """
        Remove tarefas completadas com mais de N dias.
        
        Args:
            days: Número de dias para manter histórico
        """
        with sqlite3.connect(self.db_path) as conn:
            # Calcular data limite
            from datetime import timedelta
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
            
            # Deletar tarefas antigas (apenas completed ou error)
            cursor = conn.execute("""
                DELETE FROM conversions
                WHERE status IN (?, ?)
                AND completed_at < ?
            """, (ConversionStatus.COMPLETED.value, ConversionStatus.ERROR.value, cutoff))
            
            deleted = cursor.rowcount
            conn.commit()
            
            logger.info(f"Limpeza: {deleted} tarefas antigas removidas")
            return deleted
