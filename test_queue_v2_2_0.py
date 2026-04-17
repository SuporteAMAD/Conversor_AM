"""
Testes para fila v2.2.0
Testes simples para validar funcionalidade básica
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

from queue_manager import QueueManager, ConversionStatus
from worker import ConversionWorker
from websocket_manager import get_ws_manager


def test_queue_manager():
    """Testa funcionalidade básica do QueueManager."""
    print("\n=== Testando QueueManager ===")
    
    # Usar arquivo temporário para teste
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        qm = QueueManager(db_path)
        
        # Test 1: Adicionar tarefas
        print("Test 1: Adicionar tarefas...")
        task1 = qm.add_task("video.avi", "mp4", "192.168.1.1", 150.5)
        task2 = qm.add_task("audio.wav", "mp3", "192.168.1.1", 50.0)
        task3 = qm.add_task("image.jpg", "png", "192.168.1.2", 5.0)
        
        assert task1 and task2 and task3, "Falha ao adicionar tarefas"
        print(f"✓ 3 tarefas adicionadas: {task1}, {task2}, {task3}")
        
        # Test 2: Obter próxima tarefa
        print("\nTest 2: Obter próxima tarefa...")
        next_task = qm.get_next_task()
        assert next_task['id'] == task1, "Tarefa incorreta retornada"
        assert next_task['status'] == ConversionStatus.QUEUED.value, "Status incorreto"
        print(f"✓ Próxima tarefa: {next_task['id']} ({next_task['filename_original']})")
        
        # Test 3: Atualizar progresso
        print("\nTest 3: Atualizar progresso...")
        qm.update_progress(task1, 50, 60)
        status = qm.get_status(task1)
        assert status['progress'] == 50, "Progresso não atualizado"
        assert status['status'] == ConversionStatus.PROCESSING.value, "Status não processando"
        print(f"✓ Progresso atualizado: {status['progress']}%")
        
        # Test 4: Marcar como completo
        print("\nTest 4: Marcar como completo...")
        qm.mark_completed(task1, "video.mp4", 300000)
        status = qm.get_status(task1)
        assert status['status'] == ConversionStatus.COMPLETED.value, "Status não completed"
        assert status['filename_result'] == "video.mp4", "Filename resultado incorreto"
        print(f"✓ Tarefa marcada como completa: {status['duration_ms']}ms")
        
        # Test 5: Marcar com erro
        print("\nTest 5: Marcar com erro...")
        qm.mark_error(task3, "Formato não suportado")
        status = qm.get_status(task3)
        assert status['status'] == ConversionStatus.ERROR.value, "Status não error"
        assert "Formato" in status['error_message'], "Erro não registrado"
        print(f"✓ Erro registrado: {status['error_message']}")
        
        # Test 6: Obter estatísticas
        print("\nTest 6: Obter estatísticas...")
        stats = qm.get_queue_stats()
        print(f"✓ Stats:")
        print(f"  - Total: {stats['total']}")
        print(f"  - Queued: {stats['queued']}")
        print(f"  - Processing: {stats['processing']}")
        print(f"  - Completed: {stats['completed']}")
        print(f"  - Errors: {stats['errors']}")
        print(f"  - Avg duration: {stats['avg_duration_ms']}ms")
        
        # Test 7: Tarefas do usuário
        print("\nTest 7: Tarefas do usuário...")
        user_tasks = qm.get_user_tasks("192.168.1.1", limit=5)
        assert len(user_tasks) >= 2, "Tarefas do usuário não encontradas"
        print(f"✓ Usuário tem {len(user_tasks)} tarefas")
        
        # Test 8: Cleanup
        print("\nTest 8: Cleanup de tarefas antigas...")
        deleted = qm.cleanup_old_tasks(days=0)  # Deletar tudo com 0 dias
        print(f"✓ {deleted} tarefas antigas removidas")
        
        print("\n✓ Todos os testes do QueueManager passaram!")
        
        # Fechar e aguardar
        qm.close()
        time.sleep(0.5)
        return True
    
    finally:
        # Cleanup
        time.sleep(0.5)
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except:
                pass


def test_worker():
    """Testa funcionalidade básica do Worker."""
    print("\n=== Testando ConversionWorker ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        qm = QueueManager(db_path)
        
        # Criar função de conversão mock
        def mock_convert(task_id, task):
            """Mock de conversão que simula sucesso."""
            time.sleep(0.5)  # Simular processamento
            return True, {"filename": "result.mp4"}, None
        
        # Test 1: Criar worker
        print("Test 1: Criar worker...")
        worker = ConversionWorker(
            conversion_func=mock_convert,
            queue_manager=qm,
            max_concurrent=2,
            check_interval=0.5
        )
        print(f"✓ Worker criado")
        
        # Test 2: Adicionar tarefas
        print("\nTest 2: Adicionar tarefas...")
        task1 = qm.add_task("video1.avi", "mp4", "192.168.1.1", 100)
        task2 = qm.add_task("video2.avi", "mp4", "192.168.1.1", 100)
        print(f"✓ 2 tarefas adicionadas")
        
        # Test 3: Iniciar worker
        print("\nTest 3: Iniciar worker...")
        worker.start()
        time.sleep(1)  # Deixar processar
        print(f"✓ Worker iniciado")
        
        # Test 4: Verificar processamento
        print("\nTest 4: Verificar processamento...")
        active = worker.get_active_conversions()
        print(f"✓ Conversões ativas: {active}")
        
        # Test 5: Aguardar conclusão
        print("\nTest 5: Aguardar conclusão...")
        time.sleep(3)
        worker.stop()
        
        # Verificar tarefas completadas
        status1 = qm.get_status(task1)
        status2 = qm.get_status(task2)
        assert status1['status'] == ConversionStatus.COMPLETED.value, "Task1 não completa"
        assert status2['status'] == ConversionStatus.COMPLETED.value, "Task2 não completa"
        print(f"✓ Ambas as tarefas completadas")
        
        print("\n✓ Todos os testes do Worker passaram!")
        
        qm.close()
        time.sleep(0.5)
        return True
    
    finally:
        time.sleep(0.5)
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except:
                pass


def test_websocket_manager():
    """Testa WebSocket manager."""
    print("\n=== Testando WebSocketManager ===")
    
    ws_manager = get_ws_manager()
    
    # Test 1: Registrar conexão (mock)
    print("Test 1: Registrar conexão...")
    mock_conn = {"id": "conn1"}
    task_id = "task123"
    ws_manager.register_connection(task_id, mock_conn)
    assert ws_manager.get_connected_count(task_id) == 1, "Conexão não registrada"
    print(f"✓ Conexão registrada")
    
    # Test 2: Enviar progresso
    print("\nTest 2: Enviar progresso...")
    ws_manager.send_progress(task_id, 50, 60)
    print(f"✓ Progresso enviado")
    
    # Test 3: Enviar conclusão
    print("\nTest 3: Enviar conclusão...")
    ws_manager.send_completion(task_id, True, {"filename": "result.mp4"})
    print(f"✓ Conclusão enviada")
    
    # Test 4: Unregister conexão
    print("\nTest 4: Remover conexão...")
    ws_manager.unregister_connection(task_id, mock_conn)
    assert ws_manager.get_connected_count(task_id) == 0, "Conexão não removida"
    print(f"✓ Conexão removida")
    
    print("\n✓ Todos os testes do WebSocketManager passaram!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("TESTES DA FILA v2.2.0")
    print("=" * 60)
    
    try:
        all_passed = True
        
        all_passed &= test_queue_manager()
        all_passed &= test_worker()
        all_passed &= test_websocket_manager()
        
        if all_passed:
            print("\n" + "=" * 60)
            print("✓ TODOS OS TESTES PASSARAM!")
            print("=" * 60)
        else:
            print("\n✗ Alguns testes falharam")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
