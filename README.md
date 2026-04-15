# Conversor de Arquivos AM

[![Build Status](https://github.com/gabrielwaschburger/conversor-am/workflows/%F0%9F%90%B3%20Build%20e%20Push%20Docker/badge.svg)](https://github.com/gabrielwaschburger/conversor-am/actions)
[![Docker Hub](https://img.shields.io/badge/docker%20hub-gabrielwaschburger%2Fconversor--am-blue)](https://hub.docker.com/r/gabrielwaschburger/conversor-am)
[![Version](https://img.shields.io/badge/version-2.0.2-green)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Ferramenta interna de conversão de arquivos para escritório Andrade Maia - **Expansão Convertio-like**.

## ✨ Novidades v2.0.2

- ✅ **Publicado no Docker Hub**: Imagem pronta para produção
- 🔄 **GitHub Actions CI/CD**: Build, testes e deploy automáticos
- 🐳 **Docker Production Ready**: Gunicorn com 4 workers
- 📦 **Versioning Semântico**: Tags automáticas em releases
- 🎨 **Nova Interface**: Tema profissional preto e laranja
- 📊 **Barra de Progresso**: Visualização em tempo real
- ⬇️ **Download Integrado**: Botão direto para baixar conversões
- 📱 **Design Responsivo**: Otimizado para todos os dispositivos

## Visão Geral

Esta ferramenta fornece uma interface web completa para conversão de arquivos multimídia e documentos, similar ao Convertio. Suporta conversões entre os formatos mais usados na web, com arquitetura modular e escalável. A funcionalidade de PDF foi completamente separada e mantida na ferramenta I'AM.pdf existente.

## 🎯 Interface do Usuário

### Design e Tema
- **Cores**: Preto (#1a1a1a) e laranja (#ff6b35) do escritório Andrade Maia
- **Layout**: Design moderno com gradientes e sombras
- **Responsivo**: Adaptável para desktop, tablet e mobile

### Funcionalidades da Interface
- **Upload Inteligente**: Drag & drop com preview do arquivo selecionado
- **Seleção Categorizada**: Formatos organizados por tipo (áudio, vídeo, imagem, etc.)
- **Barra de Progresso**: Visualização em tempo real com etapas da conversão
- **Download Direto**: Botão integrado para baixar arquivo convertido
- **Feedback Visual**: Animações, transições e estados de loading
- **Tratamento de Erros**: Mensagens claras em caso de falha

### Experiência do Usuário
1. **Selecionar Arquivo**: Interface intuitiva com preview
2. **Escolher Formato**: Dropdown categorizado por tipo
3. **Converter**: Barra de progresso mostra andamento
4. **Baixar**: Download direto do arquivo convertido

## Tecnologias

- **Backend**: Python 3.10+ com Flask
- **Conversão de mídia**: ffmpeg-python (áudio/vídeo)
- **Imagens**: Pillow (PNG, JPG, WebP)
- **Documentos**: python-docx (DOCX), reportlab (PDF), pdf2docx (PDF→DOCX)
- **Planilhas**: pandas, openpyxl (XLSX, CSV)
- **Arquitetura**: modular, separando lógica de conversão em módulos específicos por tipo
- **Segurança**: validar caminhos de arquivo, sanitizar inputs, rodar em ambiente isolado

## Arquitetura

```
conversor-arquivos-am/
├── main.py                 # Aplicação principal com classes base
├── rotas/
│   └── app_routes.py       # Rotas Flask
├── conversores/            # (Para futuras expansões)
├── utils/                  # (Para futuras expansões)
├── templates/              # Templates HTML
├── static/                 # CSS/JS
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```

### Diagrama da Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   Conversores   │
│   (HTML/CSS/JS) │◄──►│   Flask Routes   │◄──►│   BaseConverter │
│                 │    │                  │    │                 │
│ - Form upload   │    │ - / (home)       │    │ - AudioConv.    │
│ - Seleção fmt   │    │ - /convert       │    │ - VideoConv.    │
│ - Categorias    │    │                  │    │ - ImageConv.    │
└─────────────────┘    │ - Validações     │    │ - DocConv.      │
                       │ - Tratamento err │    │ - TextConv.     │
                       └──────────────────┘    │ - SpreadConv.   │
                                                └─────────────────┘
```

**Conversores por Categoria:**
- **AudioConverter**: OGG→MP3, MP3→WAV
- **VideoConverter**: MP4→WAV, MP4→AVI
- **ImageConverter**: PNG→JPG, PNG/JPG→WebP
- **DocumentConverter**: DOCX↔PDF, DOCX→TXT
- **TextConverter**: TXT→PDF
- **SpreadsheetConverter**: XLSX↔CSV

## Conversões Suportadas (Expandido)

### 🎵 Áudio
- **OGG → MP3**: Conversão com qualidade 192kbps
- **MP3 → WAV**: Conversão para formato não comprimido

### 🎬 Vídeo
- **MP4 → WAV**: Extração de áudio para formato WAV
- **MP4 → AVI**: Conversão entre formatos de vídeo

### 🖼️ Imagem
- **PNG → JPG**: Otimização e conversão de formato
- **PNG/JPG → WebP**: Conversão para formato moderno e comprimido

### 📄 Documentos
- **DOCX → PDF**: Documentos Word para PDF
- **PDF → DOCX**: PDFs para documentos editáveis
- **DOCX → TXT**: Extração de texto puro

### 📊 Planilhas
- **XLSX → CSV**: Planilhas Excel para CSV
- **CSV → XLSX**: Arquivos CSV para Excel

### 📝 Texto
- **TXT → PDF**: Arquivos de texto para PDF

## Instalação e Configuração

### Pré-requisitos

- Python 3.10+
- FFmpeg instalado no sistema (para conversões de áudio/vídeo)
- Dependências Python

### Instalação

1. **Clone/criar diretório do projeto**:
   ```bash
   mkdir conversor-arquivos-am
   cd conversor-arquivos-am
   ```

2. **Instalar dependências Python**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Instalar FFmpeg**:
   - **Windows**: Baixe do site oficial ffmpeg.org
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

4. **Verificar instalação**:
   ```bash
   python -c "import ffmpeg; print('FFmpeg OK')"
   ```

### Execução

```bash
python main.py
```

Acesse: http://localhost:5000

## Integração com Infraestrutura RDS

### Ambiente de Desenvolvimento
- Execute localmente para testes
- Arquivos temporários em `/tmp` ou `%TEMP%`

### Ambiente de Produção (RDS)
```python
# Configurações para RDS
app.config.update(
    UPLOAD_FOLDER='/rds/shared/uploads',
    EXPORTS_DIR='/rds/shared/exports',
    MAX_CONTENT_LENGTH=500 * 1024 * 1024,  # 500MB
    SECRET_KEY=os.environ.get('FLASK_SECRET')
)
```

### Servidores Compartilhados
- Deploy como serviço Windows/Linux
- Configurar permissões de pasta
- Logs em `/var/log/conversor-am/`

## Segurança

- Validação de tipos de arquivo
- Limite de tamanho: 50MB por arquivo
- Sanitização de nomes de arquivo
- Ambiente isolado (venv recomendado)
- Logs de auditoria em `exports/`

## Estimativa de Tempo por Módulo

| Módulo | Tempo Estimado | Status |
|--------|----------------|--------|
| Classe Base Converter | 2h | ✅ Concluído |
| AudioConverter (OGG→MP3, MP3→WAV) | 4h | ✅ Concluído |
| VideoConverter (MP4→WAV, MP4→AVI) | 4h | ✅ Concluído |
| ImageConverter (PNG→JPG, →WebP) | 3h | ✅ Concluído |
| DocumentConverter (DOCX↔PDF, →TXT) | 6h | ✅ Concluído |
| TextConverter (TXT→PDF) | 2h | ✅ Concluído |
| SpreadsheetConverter (XLSX↔CSV) | 4h | ✅ Concluído |
| Rotas Flask | 4h | ✅ Concluído |
| Frontend HTML (categorias) | 3h | ✅ Concluído |
| Tratamento de Erros | 2h | ✅ Concluído |
| Validações de Segurança | 2h | ✅ Concluído |
| Configurações Multi-ambiente | 3h | ✅ Concluído |
| Documentação | 2h | ✅ Concluído |
| **Total Expandido** | **41h** | **100% Concluído** |

## Expansões Futuras

- Suporte a mais formatos
- Interface FastAPI
- Upload múltiplo
- Fila de processamento
- Integração com storage cloud
- API REST para outros sistemas

### Deploy em Ambiente RDS

Para deploy em produção (RDS/data center):

1. **Configurar variáveis de ambiente**:
   ```bash
   export FLASK_ENV=rds
   export FLASK_SECRET="sua-chave-secreta-aqui"
   export PORT=8000
   ```

2. **Executar script de deploy**:
   ```bash
   chmod +x deploy_rds.sh
   sudo ./deploy_rds.sh
   ```

3. **Verificar serviço**:
   ```bash
   sudo systemctl status conversor-am
   ```

### Load Balancer (Data Center)

Para múltiplos servidores, configurar load balancer:

```nginx
upstream conversor_am {
    server server01:8000;
    server server02:8000;
    server server03:8000;
}

server {
    listen 80;
    server_name conversor.andremaia.com;

    location / {
        proxy_pass http://conversor_am;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoramento

- **Logs**: `/rds/shared/logs/conversor_am.log`
- **Métricas**: Implementar endpoint `/health` (futuro)
- **Auditoria**: Arquivos convertidos salvos em `/rds/shared/exports/`

## Expansões Futuras

- [ ] Interface FastAPI para APIs REST
- [ ] Upload múltiplo e processamento em fila
- [ ] Integração com storage cloud (S3, Azure Blob)
- [ ] Autenticação e autorização
- [ ] Dashboard de administração
- [ ] Suporte a mais formatos (DOCX, XLSX, etc.)
- [ ] Compressão automática
- [ ] Notificações por email
- [ ] API de status de conversão

## Suporte

Para questões técnicas, consulte a documentação do I'AM.pdf como referência arquitetural.