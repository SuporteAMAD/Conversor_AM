# 🚀 GUIA DE PUBLICAÇÃO - Conversor de Arquivos AM v2.0.1

**Status:** ✅ Publicada com Docker
**Data:** 15 de Abril de 2026
**Imagem:** gabrielwaschburger/conversor-am:v2.0.1

---

## 🎯 IMAGEM DOCKER PUBLICADA

A aplicação está disponível como imagem Docker no Docker Hub:

```bash
# Imagem oficial
gabrielwaschburger/conversor-am:v2.0.1

# Arquivo local (backup)
conversor-am-v2.0.1.tar
```

---

## 🌐 OPÇÕES DE DEPLOY

### 1️⃣ Deploy Simples (Qualquer Servidor)

```bash
# Em qualquer servidor com Docker:

# Opção A: Pull do Docker Hub
docker run -d \
  --name conversor-am \
  -p 80:5000 \
  -v /opt/uploads:/app/uploads \
  -v /opt/exports:/app/exports \
  -e FLASK_SECRET="$(openssl rand -hex 32)" \
  gabrielwaschburger/conversor-am:v2.0.1

# Opção B: Load do arquivo local
docker load < conversor-am-v2.0.1.tar
docker run -d --name conversor-am -p 80:5000 gabrielwaschburger/conversor-am:v2.0.1

# Acessar: http://seu-servidor.com
```

### 2️⃣ Deploy com Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  conversor-am:
    image: gabrielwaschburger/conversor-am:v2.0.1
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_SECRET=your-secret-here
    volumes:
      - ./uploads:/app/uploads
      - ./exports:/app/exports
      - ./logs:/app/logs
    restart: unless-stopped
```

### 3️⃣ Deploy em Nuvem

#### Railway.app (Recomendado)
```bash
# 1. Criar projeto no Railway
# 2. Conectar GitHub ou usar Docker
# 3. Configurar:
#    - Image: gabrielwaschburger/conversor-am:v2.0.1
#    - Port: 5000
# URL automática gerada
```

#### Render.com
```bash
# 1. Novo Web Service
# 2. Docker Image: gabrielwaschburger/conversor-am:v2.0.1
# 3. Port: 5000
# URL automática gerada
```

#### VPS/Droplet
```bash
# Ubuntu/Debian VPS
sudo apt update && sudo apt install -y docker.io
sudo systemctl start docker

# Executar container
sudo docker run -d \
  --name conversor-am \
  --restart unless-stopped \
  -p 80:5000 \
  gabrielwaschburger/conversor-am:v2.0.1
```

---

## 🔧 CONFIGURAÇÕES AVANÇADAS

### Volumes Persistentes
```bash
docker run -d \
  --name conversor-am \
  -p 80:5000 \
  -v /dados/uploads:/app/uploads \
  -v /dados/exports:/app/exports \
  -v /dados/logs:/app/logs \
  gabrielwaschburger/conversor-am:v2.0.1
```

### Variáveis de Ambiente
```bash
docker run -d \
  --name conversor-am \
  -p 80:5000 \
  -e FLASK_ENV=production \
  -e FLASK_SECRET=your-super-secret-key \
  -e SERVER_ID=prod-server-01 \
  gabrielwaschburger/conversor-am:v2.0.1
```

### HTTPS com Nginx Proxy
```bash
# Instalar Nginx
sudo apt install nginx

# Criar config
sudo tee /etc/nginx/sites-available/conversor-am << EOF
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Ativar
sudo ln -s /etc/nginx/sites-available/conversor-am /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 📊 MONITORAMENTO

### Logs
```bash
# Ver logs do container
docker logs conversor-am

# Seguir logs em tempo real
docker logs -f conversor-am
```

### Status
```bash
# Verificar se está rodando
docker ps | grep conversor-am

# Health check
curl -f http://localhost:5000/
```

### Recursos
```bash
# Uso de CPU/Memória
docker stats conversor-am
```

---

## 🔄 ATUALIZAÇÃO

```bash
# Parar container atual
docker stop conversor-am

# Remover container antigo
docker rm conversor-am

# Pull nova versão (quando disponível)
docker pull gabrielwaschburger/conversor-am:latest

# Executar nova versão
docker run -d --name conversor-am -p 80:5000 gabrielwaschburger/conversor-am:latest
```

---

## 🆘 TROUBLESHOOTING

### Container não inicia
```bash
# Ver logs detalhados
docker logs conversor-am

# Verificar portas em uso
sudo netstat -tlnp | grep :80
```

### Erro de permissão
```bash
# Criar diretórios com permissões
sudo mkdir -p /opt/conversor-data/{uploads,exports,logs}
sudo chmod 755 /opt/conversor-data/*
```

### Memória insuficiente
```bash
# Limitar uso de memória
docker run -d \
  --name conversor-am \
  --memory=1g \
  --memory-swap=2g \
  -p 80:5000 \
  gabrielwaschburger/conversor-am:v2.0.1
```

---

## 📋 CHECKLIST DE DEPLOY

- [x] Imagem Docker criada e testada
- [x] Push para Docker Hub realizado
- [x] Arquivo .tar de backup criado
- [x] Documentação de deploy atualizada
- [ ] Servidor de produção configurado
- [ ] Domínio/URL configurado
- [ ] HTTPS/SSL configurado
- [ ] Backup automático configurado
- [ ] Monitoramento implementado

---

**🎉 APLICATIVO PRONTO PARA PRODUÇÃO!**

Acesse: https://hub.docker.com/r/gabrielwaschburger/conversor-am</content>
<parameter name="filePath">c:\Users\gabriel.waschburger\Documents\Conversor de Arquivos AM\DEPLOY_PUBLICADO.md