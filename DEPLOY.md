# Guia de Deploy - Conversor de Arquivos AM v2.0.0

## Pré-requisitos do Servidor

### Sistema Operacional
- **Linux/Ubuntu 20.04+** (recomendado)
- Ou Windows Server 2019+ (com WSL2)

### Pacotes do Sistema
```bash
# Atualizar
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install -y python3.10 python3-pip python3-venv
sudo apt install -y ffmpeg  # ESSENCIAL para audio/video

# Instalar outras dependências necessárias
sudo apt install -y libpoppler-cpp-dev  # Para PDF (pdf2docx)
```

## 📋 Opção 1: Deploy Automático (RDS/Linux)

### Passo 1: Preparar os arquivos
```bash
# Na sua máquina local
cd "c:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM"

# Compactar a aplicação
# (usar WinRAR, 7-Zip ou PowerShell)
```

### Passo 2: Copiar para o servidor
```bash
# Do seu PC (PowerShell no Windows)
$serverIp = "seu-ip-servidor"
$destPath = "/tmp/conversor-am"

# Transferir via SCP ou SFTP
# Ou: zip tudo e upload pelo navegador/painel
```

### Passo 3: Executar script de deploy
```bash
# SSH no servidor
ssh usuario@seu-ip-servidor

# Executar o script de deploy
sudo bash /tmp/conversor-am/deploy_rds.sh
```

## 📋 Opção 2: Deploy Manual (Qualquer Servidor)

### Passo 1: Criar diretório da aplicação
```bash
sudo mkdir -p /opt/conversor-am
sudo chown $USER:$USER /opt/conversor-am
cd /opt/conversor-am
```

### Passo 2: Copiar arquivos
```bash
# Opção A: Via SCP/SFTP
scp -r C:\Caminho\Local\conversor-am\* usuario@servidor:/opt/conversor-am/

# Opção B: Via Git (se tiver repo)
git clone <seu-repo> .
```

### Passo 3: Criar e ativar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### Passo 4: Instalar dependências
```bash
pip install -r requirements.txt

# Verificar FFmpeg
ffmpeg -version
```

### Passo 5: Configurar variáveis de ambiente
```bash
# Criar arquivo .env
echo "FLASK_ENV=rds" > .env
echo "FLASK_SECRET=sua-chave-secreta-aqui" >> .env

# Criar diretórios necessários
mkdir -p /rds/shared/{uploads,exports,logs}
chmod 755 /rds/shared/{uploads,exports,logs}
```

### Passo 6: Testar aplicação
```bash
# Teste local
python main.py

# Deve aparecer:
# * Running on http://0.0.0.0:8000
```

### Passo 7: Configurar como serviço (systemd)
```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/conversor-am.service
```

Colar:
```ini
[Unit]
Description=Conversor de Arquivos AM
After=network.target

[Service]
User=seu-usuario
WorkingDirectory=/opt/conversor-am
Environment=FLASK_ENV=rds
Environment=FLASK_SECRET=sua-chave-secreta
ExecStart=/opt/conversor-am/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable conversor-am
sudo systemctl start conversor-am
sudo systemctl status conversor-am
```

## 🌐 Configurar Proxy Reverso (Nginx)

### Instalar Nginx
```bash
sudo apt install -y nginx
```

### Configurar
```bash
sudo nano /etc/nginx/sites-available/conversor-am
```

Colar:
```nginx
upstream conversor_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name seu-dominio.com;

    client_max_body_size 500M;

    location / {
        proxy_pass http://conversor_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/conversor-am /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Configurar SSL/HTTPS (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## ✅ Checklist de Deploy

- [ ] FFmpeg instalado no servidor (`ffmpeg -version`)
- [ ] Python 3.10+ instalado
- [ ] Diretórios `/rds/shared/{uploads,exports,logs}` criados
- [ ] `requirements.txt` instalado via pip
- [ ] Arquivo `.env` com variáveis corretas
- [ ] Aplicação testada localmente (`python main.py`)
- [ ] Serviço systemd configurado e iniciado
- [ ] Nginx/proxy reverso funcionando
- [ ] SSL/HTTPS configurado
- [ ] Logs monitorados (`journalctl -u conversor-am -f`)

## 📊 Monitoramento e Logs

```bash
# Ver status do serviço
sudo systemctl status conversor-am

# Ver últimos 50 logs
journalctl -u conversor-am -n 50

# Seguir logs em tempo real
journalctl -u conversor-am -f

# Ver erros
journalctl -u conversor-am --priority=err
```

## 🚨 Solução de Problemas

### Erro: "FFmpeg not found"
```bash
sudo apt install ffmpeg
ffmpeg -version
```

### Erro: "Permission denied"
```bash
sudo chown -R seu-usuario:seu-usuario /opt/conversor-am
sudo chmod -R 755 /opt/conversor-am
```

### Erro: "Port 8000 already in use"
```bash
# Matar processo na porta 8000
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Conversão falhando
```bash
# Verificar logs
journalctl -u conversor-am -f

# Testar conversor localmente
python test_app.py
```

## 📈 Escalabilidade

Para múltiplos servidores/workers:

```bash
# Instalar Gunicorn
pip install gunicorn

# Rodas com múltiplos workers
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

Ou usar no `systemd`:
```ini
ExecStart=/opt/conversor-am/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## 🎯 Próximos Passos

1. Escolher servidor (Cloud, dedicado, VPS)
2. Instalar pré-requisitos
3. Seguir um dos dois métodos acima
4. Testar em staging antes de produção
5. Configurar backups dos uploads/exports
