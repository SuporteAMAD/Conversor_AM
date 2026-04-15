FROM python:3.10-slim

WORKDIR /app

# Instalar FFmpeg e dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpoppler-cpp-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretórios de dados
RUN mkdir -p /app/uploads /app/exports /app/logs

# Expor porta
EXPOSE 5000

# Variáveis de ambiente
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV FLASK_SECRET=docker-secret-change-in-production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Executar aplicação com Gunicorn para produção
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
