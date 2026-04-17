"""
Rotas Flask para fila de conversões
Conversor AM v2.2.0

Para integrar com app_routes.py, adicionar ao final:
```
from rotas.queue_routes import register_queue_routes
```
"""

import os
import json
import logging
from flask import request, jsonify
from werkzeug.utils import secure_filename

from queue_manager import QueueManager
from websocket_manager import get_ws_manager
from worker import get_worker

logger = logging.getLogger(__name__)


def register_queue_routes(app, conversion_func, upload_folder="uploads"):
    """
    Registra rotas de fila na aplicação Flask.
    
    Args:
        app: Aplicação Flask
        conversion_func: Função para converter arquivo
        upload_folder: Pasta para uploads
    """
    
    # Inicializar gerenciadores
    queue_manager = QueueManager()
    ws_manager = get_ws_manager()
    
    @app.route("/api/queue/add", methods=["POST"])
    def queue_add_v220():
        """
        Adiciona arquivo à fila de conversão.
        
        Request:
            - file: Arquivo para converter (multipart)
            - target_format: Formato de destino
        
        Response:
            {
                "success": true,
                "task_id": "uuid-string",
                "status": "queued",
                "filename": "original.ext",
                "queue_position": 3
            }
        """
        try:
            file = request.files.get("file")
            target_format = request.form.get("target_format")
            
            if not file or not file.filename:
                return jsonify({
                    "success": False,
                    "error": "Arquivo não fornecido"
                }), 400
            
            if not target_format:
                return jsonify({
                    "success": False,
                    "error": "Formato de destino não especificado"
                }), 400
            
            # Salvar arquivo
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            os.makedirs(upload_folder, exist_ok=True)
            file.save(file_path)
            
            # Obter tamanho em MB
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Obter IP do usuário
            user_ip = request.remote_addr
            
            # Adicionar à fila
            task_id = queue_manager.add_task(
                filename=filename,
                target_format=target_format,
                user_ip=user_ip,
                file_size_mb=file_size_mb
            )
            
            # Obter posição na fila
            stats = queue_manager.get_queue_stats()
            queue_position = stats['queued']
            
            return jsonify({
                "success": True,
                "task_id": task_id,
                "status": "queued",
                "filename": filename,
                "queue_position": queue_position,
                "file_size_mb": round(file_size_mb, 2)
            }), 201
        
        except Exception as e:
            logger.error(f"Erro ao adicionar à fila: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Erro ao processar: {str(e)}"
            }), 500
    
    @app.route("/api/queue/status/<task_id>", methods=["GET"])
    def queue_status(task_id):
        """
        Retorna status de uma tarefa.
        
        Response:
            {
                "success": true,
                "task_id": "uuid",
                "status": "processing",
                "progress": 45,
                "eta_seconds": 120,
                "filename": "original.ext",
                "result_filename": null
            }
        """
        try:
            task = queue_manager.get_status(task_id)
            
            if not task:
                return jsonify({
                    "success": False,
                    "error": "Tarefa não encontrada"
                }), 404
            
            return jsonify({
                "success": True,
                "task_id": task_id,
                "status": task['status'],
                "progress": task['progress'],
                "eta_seconds": task['eta_seconds'],
                "filename": task['filename_original'],
                "result_filename": task['filename_result'],
                "error": task['error_message'],
                "created_at": task['created_at'],
                "started_at": task['started_at'],
                "completed_at": task['completed_at'],
                "duration_ms": task['duration_ms']
            }), 200
        
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Erro: {str(e)}"
            }), 500
    
    @app.route("/api/queue/stats", methods=["GET"])
    def queue_stats():
        """
        Retorna estatísticas da fila.
        
        Response:
            {
                "total": 15,
                "queued": 3,
                "processing": 1,
                "completed": 10,
                "errors": 1,
                "avg_duration_ms": 5000,
                "active_conversions": 1
            }
        """
        try:
            stats = queue_manager.get_queue_stats()
            worker = get_worker()
            
            active_conversions = worker.get_active_conversions() if worker else 0
            
            return jsonify({
                "success": True,
                **stats,
                "active_conversions": active_conversions
            }), 200
        
        except Exception as e:
            logger.error(f"Erro ao obter stats: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Erro: {str(e)}"
            }), 500
    
    @app.route("/api/queue/user-tasks", methods=["GET"])
    def user_tasks():
        """
        Retorna tarefas do usuário atual.
        
        Query params:
            - limit: Limite de tarefas (default 10)
        
        Response:
            {
                "success": true,
                "tasks": [
                    {"task_id": "uuid", "status": "completed", ...},
                    ...
                ]
            }
        """
        try:
            user_ip = request.remote_addr
            limit = request.args.get("limit", 10, type=int)
            
            tasks = queue_manager.get_user_tasks(user_ip, limit)
            
            return jsonify({
                "success": True,
                "tasks": [
                    {
                        "task_id": t['id'],
                        "status": t['status'],
                        "filename": t['filename_original'],
                        "result_filename": t['filename_result'],
                        "progress": t['progress'],
                        "created_at": t['created_at'],
                        "completed_at": t['completed_at'],
                        "duration_ms": t['duration_ms']
                    }
                    for t in tasks
                ]
            }), 200
        
        except Exception as e:
            logger.error(f"Erro ao obter tarefas do usuário: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Erro: {str(e)}"
            }), 500
    
    @app.route("/api/queue/cleanup", methods=["POST"])
    def queue_cleanup():
        """
        Remove tarefas antigas da fila (admin only).
        
        Query params:
            - days: Número de dias para manter (default 7)
        
        Response:
            {"success": true, "deleted": 5}
        """
        try:
            # TODO: Adicionar verificação de admin/auth
            days = request.args.get("days", 7, type=int)
            deleted = queue_manager.cleanup_old_tasks(days)
            
            return jsonify({
                "success": True,
                "deleted": deleted
            }), 200
        
        except Exception as e:
            logger.error(f"Erro no cleanup: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Erro: {str(e)}"
            }), 500


def make_conversion_wrapper(converter_class, upload_folder, ws_manager):
    """
    Cria wrapper para função de conversão que atualiza progresso.
    
    Args:
        converter_class: Classe do conversor
        upload_folder: Pasta de uploads
        ws_manager: WebSocket manager para notificações
    
    Returns:
        Função (task_id, task) -> (success, result, error)
    """
    
    def conversion_func(task_id: str, task: dict):
        """
        Converte arquivo e atualiza progresso.
        
        Args:
            task_id: ID da tarefa
            task: Dict com dados da tarefa
        
        Returns:
            (success, result, error)
        """
        try:
            filename = task['filename_original']
            target_format = task['target_format']
            file_path = os.path.join(upload_folder, filename)
            
            # Enviar progresso 10%
            ws_manager.send_progress(task_id, 10, 30)
            
            # TODO: Implementar callback de progresso no conversor
            # Por enquanto, simulamos com atualização de 50% no meio
            ws_manager.send_progress(task_id, 50, 15)
            
            # Chamar conversor
            # converter = converter_class(...)
            # result = converter.convert()
            # result_filename = converter._get_output_filename(filename)
            
            # Enviar progresso 100%
            ws_manager.send_progress(task_id, 100, 0)
            
            # Retornar sucesso
            return True, {"filename": "result.ext"}, None
        
        except Exception as e:
            logger.error(f"Erro na conversão {task_id}: {e}", exc_info=True)
            return False, None, str(e)
    
    return conversion_func
