# Conversor de Arquivos AM

[![Build Status](https://github.com/gabrielwaschburger/conversor-am/workflows/%F0%9F%90%B3%20Build%20e%20Push%20Docker/badge.svg)](https://github.com/gabrielwaschburger/conversor-am/actions)
[![Docker Hub](https://img.shields.io/badge/docker%20hub-gabrielwaschburger%2Fconversor--am-blue)](https://hub.docker.com/r/gabrielwaschburger/conversor-am)
[![Version](https://img.shields.io/badge/version-2.1.0-green)](./RELEASE_2.1.0.md)
[![Formatos](https://img.shields.io/badge/formatos-100%2B-orange)](./GUIA_USUARIO_v2.1.0.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Ferramenta interna de conversão de arquivos para escritório Andrade Maia - **100+ Formatos Suportados** 🚀

## ✨ Novidades v2.1.0 (16/04/2026)

- 🎉 **100+ Formatos Suportados**: Expansão massiva de capacidades
  - 🎵 **Áudio**: 20 formatos (MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, AIFF, AC3, DTS, EAC3, F32, F64, S16, S24, S32, U8, WMA, Vorbis)
  - 🎬 **Vídeo**: 20 formatos (MP4, AVI, MKV, MOV, FLV, WebM, 3GP, WMV, ASF, MOD, MTS, TS, VOB, M2TS, OGV, M4V, F4V, INSV, QT)
  - 🖼️ **Imagem**: 20 formatos (JPG, PNG, BMP, GIF, TIFF, ICO, WebP, TGA, PNM, PPM, XBM, XPM, SVG, CUR, HEIC, HEIF, JFIF, JP2, JP2K)
  - 📄 **Documentos**: 6 formatos (PDF, DOCX, DOC, TXT, ODT, RTF)
  - 📊 **Planilhas**: 5 formatos (CSV, XLSX, XLS, ODS, TSV)
- 🏗️ **Arquitetura Genérica**: Classes reutilizáveis com mapeamento de codecs FFmpeg
- 📱 **Dropdown Expandido**: 80+ opções com descrições amigáveis
- 🧪 **Pronto para Testes**: Versão em produção aguardando feedback dos usuários

## 🚀 Início Rápido

### Para Usuários (Testes dos 100+ Formatos)

1. **Acesse o conversor:**
   ```
   http://localhost:5000  ou  http://seu_ip:5000
   ```

2. **Selecione um arquivo** e **escolha entre 100+ formatos**
   
3. **Clique em "Converter"** e **baixe o resultado**

📖 **Documentação completa:** [GUIA_USUARIO_v2.1.0.md](./GUIA_USUARIO_v2.1.0.md)

### Para Desenvolvedores

```bash
# Clone o repositório
git clone https://github.com/SuporteAMAD/Conversor_AM.git
cd Conversor_AM

# Instale dependências
pip install -r requirements.txt

# Execute a aplicação
python main.py

# Ou use Docker
docker-compose up -d
```

🔗 **Links úteis:**
- 📄 [Release Notes v2.1.0](./RELEASE_2.1.0.md) - Changelog completo
- 📚 [Guia do Usuário](./GUIA_USUARIO_v2.1.0.md) - Tutorial com exemplos
- 🐳 [Docker Hub](https://hub.docker.com/r/gabrielwaschburger/conversor-am) - Imagens prontas
- 📦 [GitHub Releases](https://github.com/SuporteAMAD/Conversor_AM/releases) - Todas as versões

## Visão Geral

Esta ferramenta fornece uma interface web completa para conversão de arquivos multimídia e documentos, com suporte a **100+ formatos**. Funciona de forma similar ao Convertio, com arquitetura modular e escalável. A funcionalidade de PDF foi completamente separada e mantida na ferramenta I'AM.pdf existente. Suporta conversões entre os formatos mais usados na web, com arquitetura modular e escalável. A funcionalidade de PDF foi completamente separada e mantida na ferramenta I'AM.pdf existente.

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

## Conversões Suportadas (100+ Formatos)

### 🎵 Áudio (20 formatos)
MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, AIFF, WebA, AC3, DTS, EAC3, F32, F64, S16, S24, S32, U8, WMA, Vorbis

**Exemplos:**
- OGG → MP3, MP3 ↔ WAV, WAV → FLAC, MP3 → AAC
- Todas as combinações com codec FFmpeg otimizado

### 🎬 Vídeo (20 formatos)
MP4, AVI, MKV, MOV, FLV, WebM, 3GP, WMV, ASF, MOD, MTS, TS, VOB, M2TS, OGV, M4V, F4V, INSV, QT

**Exemplos:**
- MP4 ↔ AVI, MP4 → MKV, AVI → WebM, MOV → MP4
- Todas as combinações com codec H.264/VP9

### 🖼️ Imagem (20 formatos)
JPG, PNG, BMP, GIF, TIFF, ICO, WebP, TGA, PNM, PPM, XBM, XPM, SVG, CUR, HEIC, HEIF, JFIF, JP2, JP2K

**Exemplos:**
- PNG ↔ JPG, PNG → WebP, JPG → BMP, TIFF → PNG
- Todas as combinações com Pillow/PIL

### 📄 Documentos (6 formatos)
PDF, DOCX, DOC, TXT, ODT, RTF

**Exemplos:**
- DOCX ↔ PDF, DOCX → TXT, DOC → PDF, RTF → DOCX

### 📊 Planilhas (5 formatos)
CSV, XLSX, XLS, ODS, TSV

**Exemplos:**
- XLSX ↔ CSV, CSV → XLSX, XLS → ODS, TSV → CSV

### 📝 Texto (Suplementar)
- TXT → PDF, TXT → DOCX

**Para documentação detalhada sobre todos os formatos**, veja [GUIA_USUARIO_v2.1.0.md](./GUIA_USUARIO_v2.1.0.md)

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