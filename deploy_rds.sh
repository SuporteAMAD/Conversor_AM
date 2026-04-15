#!/bin/bash
# Script de deploy para ambiente RDS - Conversor de Arquivos AM
# Executar como root ou com sudo

echo "=== Deploy Conversor de Arquivos AM - Ambiente RDS ==="

# Variáveis
APP_DIR="/opt/conversor-am"
USER="conversor"
SERVICE_NAME="conversor-am"

# Criar usuário se não existir
if ! id "$USER" &>/dev/null; then
    useradd -r -s /bin/false $USER
    echo "Usuário $USER criado"
fi

# Criar diretórios
mkdir -p /rds/shared/uploads
mkdir -p /rds/shared/exports
mkdir -p /rds/shared/logs
mkdir -p $APP_DIR

# Permissões
chown -R $USER:$USER /rds/shared/
chown -R $USER:$USER $APP_DIR

# Copiar arquivos da aplicação
# (Assumindo que os arquivos estão em /tmp/conversor-am)
cp -r /tmp/conversor-am/* $APP_DIR/
chown -R $USER:$USER $APP_DIR

# Instalar dependências
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "ERRO: FFmpeg não encontrado. Instalar: apt install ffmpeg"
    exit 1
fi

# Criar arquivo de serviço systemd
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Conversor de Arquivos AM
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=FLASK_ENV=rds
Environment=FLASK_SECRET=your-secret-key-here
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd e iniciar serviço
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Verificar status
systemctl status $SERVICE_NAME

echo "=== Deploy concluído ==="
echo "Aplicação rodando em: http://localhost:8000"
echo "Logs: journalctl -u $SERVICE_NAME -f"