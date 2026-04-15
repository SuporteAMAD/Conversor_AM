# Deploy Local - Conversor de Arquivos AM v2.0.0

## 🔍 Primer: Identificar o Servidor Existente

O servidor local do I'AM.pdf está rodando onde?

### Opção A: Windows (mesmo PC)
```
C:\Programas\conversor-pdf-local\
├── venv/
├── main.py
└── ...
```

### Opção B: Máquina Linux Local (mesma rede)
```
/opt/conversor-pdf-local/
├── venv/
├── main.py
└── ...
```

## 📦 Estrutura Recomendada no Servidor Local

```
C:\Apps\Conversor-AM\  (Windows) ou /apps/conversor-am/ (Linux)
├── venv/                      # Virtual environment
├── main.py                    # Aplicação Flask
├── requirements.txt           # Dependências
├── config.py                  # Configurações
├── rotas/
│   └── app_routes.py
├── uploads/                   # Arquivos enviados
├── exports/                   # Arquivos convertidos
├── logs/                      # Logs da aplicação
├── README.md
└── .env                       # Variáveis de ambiente (NÃO commitar)
```

## ⚡ Setup Rápido (Windows Local)

### 1. Criar pasta da aplicação
```powershell
# Na sua máquina local (pode ser C:\ ou D:\)
New-Item -ItemType Directory -Path "C:\Apps\Conversor-AM"
cd C:\Apps\Conversor-AM
```

### 2. Copiar arquivos do projeto
```powershell
# Copiar TODOS os arquivos do projeto
Copy-Item -Path "C:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM\*" -Destination "C:\Apps\Conversor-AM" -Recurse
```

### 3. Instalar FFmpeg (CRÍTICO!)
```powershell
# Opção A: Usando Chocolatey (mais fácil)
choco install ffmpeg

# Opção B: Download manual
# 1. Ir para https://ffmpeg.org/download.html
# 2. Download Windows build
# 3. Extrair e adicionar ao PATH

# Verificar se funcionou
ffmpeg -version
```

### 4. Criar e ativar virtual environment
```powershell
cd C:\Apps\Conversor-AM
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 5. Instalar dependências
```powershell
pip install -r requirements.txt

# Verificar instalação
pip list | findstr ffmpeg
```

### 6. Testar aplicação
```powershell
python main.py

# Deve aparecer:
# * Running on http://127.0.0.1:5000
```

### 7. Testar conversão
```powershell
# Em outro terminal PowerShell:
python test_app.py
```

## 🔗 Rodar como Serviço Windows Automático

### Opção A: NSSM (Non-Sucking Service Manager) - Recomendado
```powershell
# Baixar NSSM
# https://nssm.cc/download

# Instalar serviço
nssm install ConversorAM "C:\Apps\Conversor-AM\venv\Scripts\python.exe" "C:\Apps\Conversor-AM\main.py"
nssm set ConversorAM AppDirectory "C:\Apps\Conversor-AM"
nssm set ConversorAM AppStdout "C:\Apps\Conversor-AM\logs\output.log"
nssm set ConversorAM AppStderr "C:\Apps\Conversor-AM\logs\error.log"

# Iniciar
nssm start ConversorAM

# Ver status
nssm status ConversorAM

# Parar
nssm stop ConversorAM
```

### Opção B: Task Scheduler (Agendador de Tarefas Windows)
```powershell
# Criar script batch: C:\Apps\Conversor-AM\start.bat

@echo off
cd C:\Apps\Conversor-AM
.\venv\Scripts\python.exe main.py
pause
```

Depois abrir Task Scheduler:
- Criar tarefa
- Trigger: "Ao iniciar o computador"
- Action: `C:\Apps\Conversor-AM\start.bat`
- Ativar: "Executar se o usuário estiver ou não logado"

## ✅ Validar Funcionamento

### 1. Verificar se está rodando
```powershell
# Testar porta
Test-NetConnection -ComputerName localhost -Port 5000

# Ou abrir no navegador
# http://localhost:5000
```

### 2. Testar conversão de texto
```powershell
# Copiar arquivo de teste
Copy-Item "C:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM\teste_utf8.txt" "C:\Apps\Conversor-AM\"

# Executar teste
python -c "
from main import get_converter, validate_file_type
from werkzeug.datastructures import FileStorage
import io, os

file_storage = FileStorage(
    stream=io.BytesIO(open('teste_utf8.txt', 'rb').read()),
    filename='teste_utf8.txt',
    content_type='text/plain'
)

from main import save_upload_to_temp
input_path = save_upload_to_temp(file_storage, per_file_limit_bytes=50*1024*1024)
converter = get_converter('text', 'pdf', input_path)

with converter:
    data = converter.convert()
    print(f'✅ Conversão OK: {len(data)} bytes')
    
os.remove(input_path)
"
```

### 3. Testar MP3 (se tiver arquivo de teste)
```powershell
# Criar teste com ffmpeg (se disponível)
ffmpeg -f lavfi -i sine=f=440:d=3 -q:a 9 -acodec libmp3lame -ac 2 -b:a 192k teste_audio.mp3

# Tentar conversão
python -c "
from main import get_converter
from werkzeug.datastructures import FileStorage
import io

if os.path.exists('teste_audio.mp3'):
    converter = get_converter('audio', 'wav', 'teste_audio.mp3')
    print(f'✅ Conversor encontrado: {type(converter).__name__}')
"
```

## 🌐 Acessar de Outra Máquina da Rede

### No arquivo de config
Editar `config.py`:
```python
class DevelopmentConfig(Config):
    HOST = "0.0.0.0"  # Permite acesso de qualquer máquina
    PORT = 5000
```

### URL para acessar
```
http://seu-ip-local:5000
# ou
http://seu-hostname:5000

# Descobrir seu IP
ipconfig
```

## 📝 Arquivo .env (Criar em C:\Apps\Conversor-AM\.env)
```
FLASK_ENV=development
FLASK_SECRET=sua-chave-secreta-local
FLASK_DEBUG=0
```

## 🐛 Solução de Problemas

### Erro: "FFmpeg not found"
```powershell
# Verificar PATH
$env:PATH

# Adicionar FFmpeg ao PATH (se necessário)
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\path\to\ffmpeg\bin", "Machine")

# Reiniciar PowerShell e testar
ffmpeg -version
```

### Erro: "Port 5000 already in use"
```powershell
# Encontrar processo na porta
Get-NetTCPConnection -LocalPort 5000

# Matar processo
Stop-Process -Id <PID> -Force

# Ou mudar porta em config.py
PORT = 5001
```

### Erro: "Permission denied" em uploads/exports
```powershell
# Dar permissão de escrita
icacls "C:\Apps\Conversor-AM\uploads" /grant:r "%USERNAME%:F"
icacls "C:\Apps\Conversor-AM\exports" /grant:r "%USERNAME%:F"
```

## 🔍 Monitorar Logs

### Ver erros em tempo real (se rodando em PowerShell)
```
Logs aparecem diretamente no terminal
```

### Se rodar como serviço
```powershell
# NSSM
nssm start ConversorAM
nssm stop ConversorAM

# Verificar log
Get-Content "C:\Apps\Conversor-AM\logs\error.log" -Tail 20
```

## ✅ Checklist Final

- [ ] Pasta `C:\Apps\Conversor-AM` criada e arquivos copiados
- [ ] FFmpeg instalado (`ffmpeg -version` funciona)
- [ ] Virtual environment criado e ativado
- [ ] `pip install -r requirements.txt` executado com sucesso
- [ ] Teste local funciona (`python test_app.py`)
- [ ] Conversão de texto funciona (TXT → PDF)
- [ ] Conversão de áudio funciona (MP3 → WAV)
- [ ] Web interface acessível em `http://localhost:5000`
- [ ] (Opcional) Serviço Windows configurado
- [ ] Acessível de outras máquinas da rede (se necessário)

## 📞 Próximos Passos

Depois de confirmado funcionando:
1. Integrar com I'AM.pdf (mesma máquina)
2. Configurar shared folders se necessário
3. Backup automático de uploads/exports
4. Monitoramento de performance
