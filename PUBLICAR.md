# 📦 GUIA DE PUBLICAÇÃO - Conversor de Arquivos AM v2.0.0

**Versão:** 2.0.0  
**Data:** 15 de Abril de 2026  
**Status:** Pronto para Produção ✅

---

## 🚀 Opções de Publicação

Escolha a opção que melhor se adapta ao seu caso:

### 1️⃣ **Deploy Local/Rede Interna** ⭐ (Mais Rápido)
- ✅ Ideal para: Equipe interna, testes, desenvolvimento
- ⏱️ Tempo: ~5 minutos
- 💻 Requisitos: Python 3.10+, FFmpeg
- 📍 Acesso: Apenas na rede local

### 2️⃣ **Deploy em Servidor Linux/RDS** (Mais Robusto)
- ✅ Ideal para: Produção, múltiplos usuários
- ⏱️ Tempo: ~20 minutos
- 💻 Requisitos: Linux/Ubuntu, sudo, domínio (opcional)
- 📍 Acesso: Via IP ou domínio público

### 3️⃣ **Deploy com Docker** (Mais Portável)
- ✅ Ideal para: Consistência entre ambientes
- ⏱️ Tempo: ~10 minutos
- 💻 Requisitos: Docker, Docker Compose
- 📍 Acesso: Qualquer servidor com Docker

### 4️⃣ **Deploy em Plataformas Cloud** (Mais Fácil)
- ✅ Ideal para: Sem gerenciar servidor
- ⏱️ Tempo: ~15 minutos
- 💻 Requisitos: Conta na plataforma
- 📍 Acesso: URL automática

### 5️⃣ **Deploy em Windows Server** (Compatível)
- ✅ Ideal para: Infraestrutura Windows existente
- ⏱️ Tempo: ~15 minutos
- 💻 Requisitos: Windows Server 2019+
- 📍 Acesso: Intranet ou internet

---

## 1️⃣ DEPLOY LOCAL / REDE INTERNA

### ⚡ Rápido (3-5 minutos)

```bash
# 1. Entrar no diretório
cd "c:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM"

# 2. Iniciar o servidor
python main.py

# 3. Acessar
http://localhost:5000
http://192.168.1.100:5000  # De outro PC na rede
```

### ✨ Com Gunicorn (Mais Robusto)

```bash
# 1. Instalar Gunicorn
pip install gunicorn

# 2. Executar
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# 3. Acessar
http://localhost:5000
```

### 📋 Checklist Local
- [ ] Python 3.10+ instalado
- [ ] FFmpeg funcionando (`ffmpeg -version`)
- [ ] `pip install -r requirements.txt` executado
- [ ] Pastas `uploads`, `exports`, `logs` existem
- [ ] Servidor rodando sem erros

---

## 2️⃣ DEPLOY EM SERVIDOR LINUX/RDS

### 📋 Pré-requisitos

```bash
# No seu servidor Linux/Ubuntu
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.10 python3-pip python3-venv ffmpeg nginx
```

### 🔧 Passo a Passo

#### Passo 1: Clonar/Copiar Aplicação

```bash
# Opção A: Via Git
mkdir -p /opt && cd /opt
sudo git clone https://seu-repo-git.com/conversor-am.git
cd conversor-am

# Opção B: Via SCP (do seu PC para o servidor)
scp -r "C:\Caminho\Local\Conversor de Arquivos AM\*" usuario@seu-servidor:/tmp/
ssh usuario@seu-servidor
sudo mv /tmp/Conversor* /opt/conversor-am
cd /opt/conversor-am
```

#### Passo 2: Criar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Passo 3: Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cat > .env << EOF
FLASK_ENV=production
FLASK_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
SERVER_ID=prod-01
PORT=8000
EOF

# Criar diretórios de dados
mkdir -p /rds/shared/{uploads,exports,logs}
chmod 755 /rds/shared/{uploads,exports,logs}
```

#### Passo 4: Teste Local

```bash
# Ativar ambiente
source venv/bin/activate

# Testar
python main.py
# Deve aparecer: Running on http://0.0.0.0:8000

# Parar com Ctrl+C
```

#### Passo 5: Configurar como Serviço Systemd

```bash
# Criar arquivo de serviço
sudo tee /etc/systemd/system/conversor-am.service > /dev/null << EOF
[Unit]
Description=Conversor de Arquivos AM v2.0.0
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/opt/conversor-am
Environment="PATH=/opt/conversor-am/venv/bin"
Environment="FLASK_ENV=production"
Environment="FLASK_SECRET=$(cat .env | grep FLASK_SECRET | cut -d= -f2)"
ExecStart=/opt/conversor-am/venv/bin/python main.py
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Ativar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable conversor-am
sudo systemctl start conversor-am
sudo systemctl status conversor-am
```

#### Passo 6: Configurar Nginx (Proxy Reverso)

```bash
# Criar arquivo de config
sudo tee /etc/nginx/sites-available/conversor-am > /dev/null << EOF
upstream conversor_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name seu-dominio.com;
    
    client_max_body_size 500M;

    location / {
        proxy_pass http://conversor_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
    }
}
EOF

# Ativar site
sudo ln -s /etc/nginx/sites-available/conversor-am /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar config
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx
```

#### Passo 7: Configurar HTTPS (SSL)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Gerar certificado Let's Encrypt
sudo certbot --nginx -d seu-dominio.com

# Auto-renovação (já configurada)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### Passo 8: Monitorar Logs

```bash
# Logs do serviço
sudo journalctl -u conversor-am -f

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 📋 Checklist Linux
- [ ] Python 3.10+ instalado
- [ ] FFmpeg funcionado: `ffmpeg -version`
- [ ] Requirements instalados: `pip install -r requirements.txt`
- [ ] `.env` criado com `FLASK_SECRET`
- [ ] Diretórios `/rds/shared/*` criados
- [ ] Serviço systemd ativo: `systemctl status conversor-am`
- [ ] Nginx configurado e testado: `nginx -t`
- [ ] HTTPS funcionando (opcional)
- [ ] Acesso via `http://seu-dominio.com`

---

## 3️⃣ DEPLOY COM DOCKER 🐳

### 🔧 Criar Dockerfile

Crie arquivo `Dockerfile` na raiz do projeto:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar FFmpeg e dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretórios
RUN mkdir -p /app/uploads /app/exports /app/logs

# Expor porta
EXPOSE 5000

# Variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Executar
CMD ["python", "main.py"]
```

### 🔧 Criar docker-compose.yml

```yaml
version: '3.8'

services:
  conversor-am:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_SECRET=${FLASK_SECRET:-dev-secret-change-in-production}
    volumes:
      - ./uploads:/app/uploads
      - ./exports:/app/exports
      - ./logs:/app/logs
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 🚀 Executar com Docker

```bash
# 1. Build
docker build -t conversor-am:latest .

# 2. Executar
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/exports:/app/exports \
  conversor-am:latest

# 3. Ou com Docker Compose
docker-compose up -d

# 4. Acessar
http://localhost:5000
```

### 📋 Checklist Docker
- [ ] Docker instalado: `docker --version`
- [ ] Dockerfile criado
- [ ] docker-compose.yml criado (opcional)
- [ ] Build bem-sucedido: `docker build -t conversor-am .`
- [ ] Container rodando: `docker ps`
- [ ] Acesso em `http://localhost:5000`

---

## 4️⃣ DEPLOY EM PLATAFORMAS CLOUD

### 🟦 Heroku

```bash
# 1. Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Criar app
heroku create seu-app-name

# 4. Criar Procfile
echo "web: gunicorn main:app" > Procfile
echo "release: python setup_local.py" >> Procfile

# 5. Adicionar buildpack
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku-community/apt-buildpack

# 6. Criar Aptfile
echo "ffmpeg" > Aptfile

# 7. Deploy
git add .
git commit -m "Deploy para Heroku"
git push heroku main

# 8. Acessar
heroku open
```

### 🟦 Railway.app

```bash
# 1. Conectar seu Git (GitHub)
# https://railway.app/project/create

# 2. Selecionar "Deploy from GitHub"
# 3. Selecionar este repositório
# 4. Railway deploy automaticamente

# Ou com CLI:
npm i -g @railway/cli
railway init
railway up
```

### 🟦 PythonAnywhere

```
1. Criar conta em https://www.pythonanywhere.com
2. Upload dos arquivos via Web interface
3. Criar novo Web App (Flask)
4. Configurar WSGI file
5. Ativar
```

### 🟦 Render.com

```bash
# 1. Criar novo Web Service em https://render.com
# 2. Conectar repositório GitHub
# 3. Configurações:
#    - Build: pip install -r requirements.txt
#    - Start: gunicorn main:app
# 4. Deploy automático em cada push
```

---

## 5️⃣ DEPLOY EM WINDOWS SERVER

### 🔧 Instalação

```powershell
# 1. Instalar Python 3.10+
# Download: https://www.python.org/downloads/

# 2. Instalar FFmpeg
# Opção A: Via Chocolatey
choco install ffmpeg

# Opção B: Via nosso script
python install_ffmpeg.py

# 3. Clonar/Copiar projeto
mkdir C:\Apps\Conversor-AM
cd C:\Apps\Conversor-AM
# Copiar arquivos...

# 4. Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 5. Instalar dependências
pip install -r requirements.txt
```

### 🔧 Configurar como Serviço Windows (NSSM)

```powershell
# 1. Baixar NSSM
# https://nssm.cc/download

# 2. Adicionar ao PATH ou usar caminho completo

# 3. Instalar serviço
nssm install ConversorAM "C:\Apps\Conversor-AM\venv\Scripts\python.exe" "C:\Apps\Conversor-AM\main.py"

# 4. Iniciar
nssm start ConversorAM

# 5. Verificar
nssm status ConversorAM
```

### 🔧 Configurar IIS (Opcional)

```powershell
# Usar FastCGI via IIS para mais robustez
# Requer: python-wfastcgi

pip install wfastcgi
wfastcgi-enable

# Configurar site IIS apontando para main.py
```

---

## ✅ Checklist de Publicação Geral

### Antes de Publicar
- [ ] Todos os testes passam: `python test_app.py`
- [ ] Sem erros de sintaxe: `python -m py_compile main.py`
- [ ] FFmpeg funciona: `ffmpeg -version`
- [ ] Arquivo `.env` criado (se não local)
- [ ] `SECRET_KEY` configurada
- [ ] Diretórios de upload/export criados
- [ ] Documentação de deploy revisada

### Publicação
- [ ] Escolher plataforma apropriada
- [ ] Seguir guia de deploy escolhido
- [ ] Testar em staging primeiro
- [ ] Verificar logs e monitoramento
- [ ] Testar conversões em produção

### Pós-Publicação
- [ ] Monitorar logs
- [ ] Testar uploads grandes
- [ ] Verificar performance
- [ ] Configurar backups
- [ ] Configurar alertas
- [ ] Documentar processo

---

## 🔗 Links Úteis

- **Documentação Flask:** https://flask.palletsprojects.com/
- **Gunicorn:** https://gunicorn.org/
- **Nginx:** https://nginx.org/
- **Let's Encrypt:** https://letsencrypt.org/
- **Docker:** https://docker.com/
- **Heroku:** https://heroku.com/
- **Railway:** https://railway.app/
- **Render:** https://render.com/

---

## 🆘 Troubleshooting

### Problema: "FFmpeg not found"
```bash
# Solução 1: Instalar FFmpeg
apt install ffmpeg  # Linux
choco install ffmpeg  # Windows
brew install ffmpeg  # Mac

# Solução 2: Configurar PATH
export PATH="/path/to/ffmpeg/bin:$PATH"
```

### Problema: Porta 5000 em uso
```bash
# Linux: Encontrar processo
sudo lsof -i :5000

# Mudar porta em main.py ou via config
python main.py --port 8000
```

### Problema: Permissão negada nos uploads
```bash
# Linux: Dar permissões
sudo chown -R seu-usuario:seu-usuario uploads/ exports/ logs/
chmod 755 uploads/ exports/ logs/
```

### Problema: FFmpeg-python não encontra FFmpeg
```bash
# Adicionar ao código (já feito em setup_ffmpeg_path)
import os
os.environ['PATH'] = '/path/to/ffmpeg/bin:' + os.environ['PATH']
```

---

**Última Atualização:** 15 de Abril de 2026  
**Status:** Pronto para Produção ✅
