# 📋 Dinâmica de Armazenamento e Fila de Conversões

## 🔍 Dinâmica Atual (v2.1.0)

### 📂 Estrutura de Diretórios

```
Conversor de Arquivos AM/
├── uploads/              # Arquivos enviados pelo usuário (temporário)
├── exports/              # Arquivos convertidos (auditoria + download)
├── logs/                 # Logs de execução
├── temp/                 # Arquivos temporários do SO (auto-limpeza)
├── main.py              # Core com conversores
├── config.py            # Configurações por ambiente
└── rotas/
    └── app_routes.py    # Rotas Flask
```

### 🔄 Fluxo Atual (Síncrono)

```
┌─────────────────────────────────────────────────────────────┐
│ USUÁRIO ENVIA ARQUIVO                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ /convert (POST)                                             │
│ 1. Validar arquivo                                          │
│ 2. Salvar em uploads/                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ GET CONVERTER                                               │
│ 1. BaseConverter → GenericAudioConverter, etc.              │
│ 2. Mapear codecs FFmpeg/Pillow                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ CONVERT (SÍNCRONO - BLOQUEIA!)                              │
│ ⏳ USUÁRIO AGUARDA AQUI                                     │
│ 1. Executar FFmpeg/Pillow                                   │
│ 2. Processar em tempfile.mkstemp()                          │
│ 3. Arquivo temporário no SO (/tmp ou AppData)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ SALVAR RESULTADO                                            │
│ 1. save_converted_copy() → exports/                         │
│ 2. Auditar conversão em logs/                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ RETORNAR PARA DOWNLOAD                                      │
│ 1. Converter bytes → HEX (para transmissão)                 │
│ 2. JavaScript cria Blob e faz download                      │
└─────────────────────────────────────────────────────────────┘
```

### ⚠️ Problemas Atuais

1. **Síncro = Bloqueante:**
   - Se conversão leva 2 min, usuário espera 2 min inteiros
   - Timeout em conversões longas (vídeos grandes)
   - Interface fica congelada

2. **Sem Fila:**
   - Múltiplos usuários enviam 3 arquivos cada = caos
   - Sem priorização
   - Sem controle de CPU/RAM

3. **Armazenamento Precário:**
   - `tempfile.mkstemp()` em diretório temporário do SO
   - Sem limpeza automática de arquivos antigos
   - Sem rastreamento de consumo de disco

4. **Sem Monitoramento:**
   - Progresso é simulado em JS (fake!)
   - Usuário não sabe realmente quanto tempo falta
   - Sem logs de performance

---

## 💡 Solução Proposta: Fila de Conversões com WebSocket

### 📊 Arquitetura Nova

```
┌──────────────────────────────────────────────────────────────┐
│                    USUÁRIO 1, 2, 3, 4...                     │
└──┬──────────────────────────────────────────────────┬────────┘
   │                                                  │
   ▼                                                  ▼
┌─────────────────────┐                    ┌─────────────────────┐
│   POST /convert     │                    │  GET /queue-status  │
│   (Upload File)     │                    │  (WebSocket)        │
└────────┬────────────┘                    └─────────┬───────────┘
         │                                           │
         ▼                                           │
┌──────────────────────────────────────────┐        │
│   VALIDAR & SALVAR EM uploads/           │        │
│   (Rápido - 1-2 segundos)                │        │
│                                          │        │
│   Arquivo: uploads/UUID_original.ext     │        │
└────────┬─────────────────────────────────┘        │
         │                                           │
         ▼                                           │
┌──────────────────────────────────────────┐        │
│  ADD TO QUEUE (Redis ou SQLite)          │        │
│  {                                       │        │
│    id: UUID,                            │        │
│    file: "UUID_original.ext",           │        │
│    status: "queued",                    │        │
│    progress: 0%,                        │        │
│    eta: null                            │        │
│  }                                       │        │
│                                          │        │
│  Retornar: {queue_id: UUID}             │        │
└────────┬─────────────────────────────────┘        │
         │                                           │
         ▼                                           │
    ┌────────────────────────────────────────────┐  │
    │  QUEUE WORKER (Thread/Process Pool)        │  │
    │  ┌──────────────────────────────────────┐  │  │
    │  │ Worker 1: MAX 1 conversão por vez   │  │  │
    │  │ 1. Pop próxima tarefa                │  │  │
    │  │ 2. Status = "processing"             │  │  │
    │  │ 3. CONVERTER (FFmpeg/Pillow)         │  │  │
    │  │ 4. Atualizar progress em tempo real  │  │  │
    │  │ 5. Status = "completed"              │  │  │
    │  │ 6. Salvar em exports/UUID_result.ext │  │  │
    │  └──────────────────────────────────────┘  │  │
    │  ┌──────────────────────────────────────┐  │  │
    │  │ Worker 2: Paralelo                   │  │  │
    │  │ (Opcional para CPU multi-core)       │  │  │
    │  └──────────────────────────────────────┘  │  │
    └────────────────┬─────────────────────────────┘  │
                     │                                │
                     ▼                                │
         ┌──────────────────────────┐               │
         │  UPDATE QUEUE STATUS     │               │
         │  {                       │               │
         │    status: "processing"  │               │
         │    progress: 45%         │◄──────────────┘
         │    eta: "2m 30s"         │
         │  }                       │
         └──────────────────────────┘
```

### 🗂️ Novo Schema de Armazenamento

```python
# Queue Item (Redis ou SQLite)
{
    "id": "a1b2c3d4-e5f6-4f8c-9a0b-1c2d3e4f5a6b",
    "filename_original": "meu_video.mp4",
    "filename_result": "meu_video_convertido.mkv",
    "status": "queued|processing|completed|error",
    "progress": 0,  # 0-100%
    "eta_seconds": 120,
    "created_at": "2026-04-16T13:00:00Z",
    "started_at": "2026-04-16T13:01:30Z",
    "completed_at": "2026-04-16T13:03:45Z",
    "duration_ms": 135000,
    "file_size_mb": 50.5,
    "error_message": null,
    "user_ip": "192.168.1.100"
}
```

### 📂 Diretórios Remodelados

```
Conversor de Arquivos AM/
├── uploads/
│   ├── a1b2c3d4_original.mp4
│   ├── e5f6g7h8_original.docx
│   └── ...
│
├── processing/           # ← NOVO
│   ├── a1b2c3d4_temp.mkv
│   └── ...
│
├── exports/
│   ├── a1b2c3d4_converted.mkv
│   ├── e5f6g7h8_converted.pdf
│   └── ...
│
├── queue/                # ← NOVO (SQLite database)
│   └── queue.db
│
└── logs/
    ├── conversor_am.log
    ├── conversions_audit.log  # ← NOVO
    └── worker.log            # ← NOVO
```

---

## 🛠️ Implementação em 3 Fases

### ✅ Fase 1: Queue Backend (Redis ou SQLite)

```python
# queue_manager.py - NOVO

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class ConversionStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class QueueManager:
    """Gerencia fila de conversões com SQLite (mais simples que Redis)."""
    
    def __init__(self, db_path: str = "queue/queue.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Criar tabela se não existir."""
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
    
    def add_task(self, filename: str, target_format: str, user_ip: str) -> str:
        """Adiciona tarefa à fila."""
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversions 
                (id, filename_original, status, created_at, user_ip, target_format)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (task_id, filename, ConversionStatus.QUEUED.value, now, user_ip, target_format))
            conn.commit()
        
        return task_id
    
    def get_task(self) -> Optional[Dict]:
        """Pega próxima tarefa da fila."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversions 
                WHERE status = 'queued'
                ORDER BY created_at ASC
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_progress(self, task_id: str, progress: int, eta_seconds: int = None):
        """Atualiza progresso da tarefa."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversions 
                SET progress = ?, status = ?, eta_seconds = ?
                WHERE id = ?
            """, (progress, ConversionStatus.PROCESSING.value, eta_seconds, task_id))
            conn.commit()
    
    def mark_completed(self, task_id: str, filename_result: str, duration_ms: int):
        """Marca tarefa como concluída."""
        now = datetime.utcnow().isoformat() + "Z"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversions 
                SET status = ?, completed_at = ?, duration_ms = ?, 
                    filename_result = ?, progress = 100
                WHERE id = ?
            """, (ConversionStatus.COMPLETED.value, now, duration_ms, filename_result, task_id))
            conn.commit()
    
    def mark_error(self, task_id: str, error_msg: str):
        """Marca tarefa com erro."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversions 
                SET status = ?, error_message = ?
                WHERE id = ?
            """, (ConversionStatus.ERROR.value, error_msg, task_id))
            conn.commit()
    
    def get_status(self, task_id: str) -> Optional[Dict]:
        """Retorna status da tarefa."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM conversions WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_queue_stats(self) -> Dict:
        """Retorna estatísticas da fila."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued,
                    SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
                    AVG(duration_ms) as avg_duration_ms
                FROM conversions
            """)
            row = cursor.fetchone()
            return {
                "total": row[0] or 0,
                "queued": row[1] or 0,
                "processing": row[2] or 0,
                "completed": row[3] or 0,
                "errors": row[4] or 0,
                "avg_duration_ms": int(row[5]) if row[5] else 0
            }
```

### ✅ Fase 2: Worker Thread

```python
# worker.py - NOVO

import threading
import time
import logging
from queue_manager import QueueManager
from main import get_converter

logger = logging.getLogger(__name__)

class ConversionWorker:
    """Worker que processa conversões da fila."""
    
    def __init__(self, queue_manager: QueueManager):
        self.queue = queue_manager
        self.running = False
        self.thread = None
    
    def start(self):
        """Inicia worker em thread separada."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.thread.start()
            logger.info("Worker iniciado")
    
    def stop(self):
        """Para o worker."""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Worker parado")
    
    def _worker_loop(self):
        """Loop principal do worker."""
        while self.running:
            try:
                # Pega próxima tarefa
                task = self.queue.get_task()
                if not task:
                    # Nada na fila, espera 1 segundo
                    time.sleep(1)
                    continue
                
                task_id = task['id']
                logger.info(f"Processando tarefa {task_id}")
                
                # Marcar como processando
                self.queue.update_progress(task_id, 0)
                
                # Fazer conversão
                try:
                    start_time = time.time()
                    
                    # AQUI: Chamar converter com callback de progresso
                    converter = get_converter(
                        file_type=self._detect_type(task['filename_original']),
                        target_format=task['target_format'],
                        input_path=f"uploads/{task['filename_original']}"
                    )
                    
                    # Converter (implementar callback de progresso)
                    result_data = converter.convert()
                    
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    # Salvar resultado
                    result_filename = f"{task_id}_result.{task['target_format']}"
                    with open(f"exports/{result_filename}", "wb") as f:
                        f.write(result_data)
                    
                    # Marcar como concluído
                    self.queue.mark_completed(task_id, result_filename, duration_ms)
                    logger.info(f"Tarefa {task_id} concluída em {duration_ms}ms")
                
                except Exception as e:
                    error_msg = str(e)
                    self.queue.mark_error(task_id, error_msg)
                    logger.error(f"Erro na tarefa {task_id}: {error_msg}")
            
            except Exception as e:
                logger.error(f"Erro no worker: {e}")
                time.sleep(5)
    
    def _detect_type(self, filename: str) -> str:
        """Detecta tipo de arquivo pela extensão."""
        ext = filename.split('.')[-1].lower()
        if ext in ['mp3', 'wav', 'flac', 'aac']:
            return 'audio'
        elif ext in ['mp4', 'avi', 'mkv', 'mov']:
            return 'video'
        elif ext in ['png', 'jpg', 'bmp', 'gif']:
            return 'image'
        return 'unknown'
```

### ✅ Fase 3: API & WebSocket

```python
# rotas/app_routes.py - MODIFICADO

from flask import Flask, request, jsonify
from flask_sock import Sock  # Para WebSocket
from queue_manager import QueueManager
from worker import ConversionWorker

app = Flask(__name__)
sock = Sock(app)

queue_manager = QueueManager()
worker = ConversionWorker(queue_manager)
worker.start()

@app.route("/convert", methods=["POST"])
def convert():
    """Upload e adiciona à fila (não mais síncrono!)."""
    file = request.files.get("file")
    target_format = request.form.get("target_format")
    
    if not file:
        return {"success": False, "error": "Arquivo não fornecido"}, 400
    
    # Salvar arquivo
    filename = file.filename
    file.save(f"uploads/{filename}")
    
    # Adicionar à fila
    user_ip = request.remote_addr
    task_id = queue_manager.add_task(filename, target_format, user_ip)
    
    # Retornar ID para monitoramento
    return {
        "success": True,
        "queue_id": task_id,
        "message": "Arquivo adicionado à fila"
    }

@sock.route('/queue-status/<task_id>')
def queue_status(ws, task_id):
    """WebSocket para monitorar progresso em tempo real."""
    try:
        while True:
            status = queue_manager.get_status(task_id)
            
            if not status:
                ws.send(json.dumps({
                    "error": "Tarefa não encontrada"
                }))
                break
            
            # Enviar status atualizado
            ws.send(json.dumps({
                "id": status['id'],
                "status": status['status'],
                "progress": status['progress'],
                "eta_seconds": status['eta_seconds'],
                "filename_result": status['filename_result'],
                "error": status['error_message']
            }))
            
            # Se concluído ou erro, encerrar
            if status['status'] in ['completed', 'error']:
                break
            
            # Atualizar a cada 500ms
            time.sleep(0.5)
    
    except Exception as e:
        logger.error(f"Erro em WebSocket: {e}")
    
    finally:
        ws.close()

@app.route("/queue-stats", methods=["GET"])
def get_stats():
    """Retorna estatísticas da fila."""
    stats = queue_manager.get_queue_stats()
    return stats
```

---

## 📊 Benefícios da Fila

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Múltiplos uploads** | ❌ Falha/Timeout | ✅ Fila ordenada |
| **Resposta ao usuário** | ⏳ 2min bloqueia | ✅ Instantânea |
| **Progresso real** | 📊 Fake em JS | ✅ Tempo real via WebSocket |
| **CPU/RAM** | 📈 Picos altos | ✅ Controlado |
| **Rastreamento** | ❌ Nenhum | ✅ Auditoria completa |
| **Retentativa** | ❌ Falha = reenviar | ✅ Retry automático |
| **Escalabilidade** | 1 servidor = limite | ✅ Múltiplos workers |

---

## 🚀 Próximos Passos

### Curto Prazo (v2.2.0)
- [ ] Implementar QueueManager com SQLite
- [ ] Criar ConversionWorker com thread
- [ ] Adicionar endpoints `/convert` (AJAX) e `/queue-status` (WebSocket)
- [ ] Testar com múltiplos arquivos

### Médio Prazo (v2.3.0)
- [ ] Suportar múltiplos workers (thread pool)
- [ ] Dashboard de fila em tempo real
- [ ] Retry automático em caso de erro
- [ ] Limpeza automática de arquivos antigos

### Longo Prazo (v2.4.0+)
- [ ] Redis para alta performance
- [ ] Celery para distribuição em rede
- [ ] Banco de dados para auditoria
- [ ] Métricas e alertas (Prometheus)

---

## 📈 Armazenamento: Estratégia de Limpeza

```python
# cleanup.py - NOVO

import os
import time
from datetime import datetime, timedelta

class StorageManager:
    """Gerencia limpeza e espaço em disco."""
    
    def cleanup_old_files(self, days: int = 7):
        """Remove arquivos com mais de N dias."""
        cutoff = time.time() - (days * 86400)
        
        for directory in ['uploads', 'exports', 'processing']:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    logger.info(f"Removido: {filepath}")
    
    def get_disk_usage(self) -> Dict:
        """Retorna uso de disco por diretório."""
        usage = {}
        for directory in ['uploads', 'exports', 'processing']:
            total_size = sum(
                os.path.getsize(os.path.join(directory, f))
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            )
            usage[directory] = total_size / (1024 * 1024)  # MB
        return usage
```

---

## 🎯 Resumo

**Dinâmica Atual:**
- ✅ Simples, funciona para 1 usuário
- ❌ Bloqueia em conversões longas
- ❌ Sem fila ou priorização

**Solução Proposta:**
- ✅ Fila assíncrona com SQLite
- ✅ Worker thread
- ✅ Progresso em tempo real (WebSocket)
- ✅ Escalável para múltiplos usuários
- ✅ Auditoria e rastreamento

**Esforço Estimado:**
- Fase 1 (Queue): 2-3h
- Fase 2 (Worker): 2-3h
- Fase 3 (API): 2-3h
- Testes: 2-3h
- **Total: ~10h de desenvolvimento**

Quer que eu implemente isso? 🚀
