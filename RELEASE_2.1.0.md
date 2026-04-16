# 🎉 Release v2.1.0 - Expansão para 100+ Formatos

**Data de Lançamento:** 16 de Abril de 2026  
**Status:** ✅ Produção - Docker Hub  
**Versão Docker:** `gabrielwaschburger/conversor-am:v2.1.0` (ou `latest`)

---

## 📊 O que mudou?

Expandimos o **Conversor AM** de ~7 formatos para **100+ formatos** em todas as categorias!

### 🎵 Áudio (20 formatos)
✅ MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, AIFF, WebA, AC3, DTS, EAC3, F32, F64, S16, S24, S32, U8, WMA, Vorbis

### 🎬 Vídeo (20 formatos)
✅ MP4, AVI, MKV, MOV, FLV, WebM, 3GP, WMV, ASF, MOD, MTS, TS, VOB, M2TS, OGV, M4V, F4V, INSV, QT

### 🖼️ Imagem (20 formatos)
✅ JPG, PNG, BMP, GIF, TIFF, ICO, WebP, TGA, PNM, PPM, XBM, XPM, SVG, CUR, HEIC, HEIF, JFIF, JP2, JP2K

### 📄 Documentos
✅ PDF, DOCX, DOC, TXT, ODT, RTF

### 📊 Planilhas
✅ CSV, XLSX, XLS, ODS, TSV

---

## 🏗️ Mudanças Técnicas

**Arquivo:** `main.py`
- ✅ Adicionadas classes genéricas reutilizáveis
  - `GenericAudioConverter` - Suporta 20+ formatos de áudio com codec FFmpeg
  - `GenericVideoConverter` - Suporta 20+ formatos de vídeo com codec FFmpeg
  - `GenericImageConverter` - Suporta 20+ formatos de imagem com Pillow

**Arquivo:** `rotas/app_routes.py`
- ✅ Dropdown expandido para 80+ opções com descrições
- ✅ Cards de conversões atualizados com novos formatos
- ✅ Versão do footer atualizada para v2.0.2

**Versão:** 2.1.0 (tag no GitHub e Docker Hub)

---

## 🧪 TESTE OS NOVOS FORMATOS!

Pedimos gentilmente que **vocês testem** os novos formatos e nos avisem sobre:

### ✅ Por favor, teste:
1. **Pelo menos 2-3 conversões de áudio** (ex: MP3 → FLAC, WAV → AAC)
2. **Pelo menos 2-3 conversões de vídeo** (ex: MP4 → MKV, AVI → WebM)
3. **Pelo menos 2-3 conversões de imagem** (ex: PNG → WebP, JPG → BMP)
4. **Conversões de documento** (ex: DOCX → PDF, PDF → DOCX)
5. **Conversões de planilha** (ex: XLSX → CSV, CSV → XLSX)

### 🐛 Se encontrar problemas, nos avise:
- ❌ Conversão falhou?
- ❌ Arquivo corrompido?
- ❌ Qualidade ruim?
- ❌ Erro na interface?
- ❌ Performance lenta?

**Envie um relatório com:**
- Formato origem → destino (ex: MP3 → FLAC)
- Tamanho do arquivo
- Mensagem de erro (se houver)
- Seu computador/navegador

---

## 🚀 Como testar?

### Local (Desenvolvimento):
```bash
docker pull gabrielwaschburger/conversor-am:v2.1.0
docker run -p 5000:5000 gabrielwaschburger/conversor-am:v2.1.0
# Acesse: http://localhost:5000
```

### Rede Interna:
```
http://172.16.100.152:5000
# ou seu_ip:5000
```

### Produção:
```bash
docker pull gabrielwaschburger/conversor-am:latest
docker-compose up -d
```

---

## 📈 Próximas Melhorias

- [ ] Suportar conversão em lote (múltiplos arquivos)
- [ ] Adicionar compressão de arquivo (ZIP)
- [ ] Histórico de conversões
- [ ] Presets de qualidade (baixa, média, alta)
- [ ] Integração com cloud (Google Drive, OneDrive)

---

## 📝 Changelog

### v2.1.0 (16/04/2026)
- ✨ Expansão para 100+ formatos
- 🎵 Audio: 20 formatos com codecs FFmpeg
- 🎬 Video: 20 formatos com codecs FFmpeg
- 🖼️ Image: 20 formatos com PIL/Pillow
- 📄 Documentos: 6 formatos mantidos
- 📊 Planilhas: 5 formatos mantidos
- 🏗️ Arquitetura: Classes genéricas reutilizáveis
- 🐳 Docker: Tags v2.1.0 e latest no Docker Hub

### v2.0.1 (Anterior)
- Conversões básicas de 7 formatos
- Interface responsiva
- Docker multi-stage

---

## 🔗 Links Úteis

- **GitHub:** https://github.com/SuporteAMAD/Conversor_AM
- **Docker Hub:** https://hub.docker.com/r/gabrielwaschburger/conversor-am
- **Release v2.1.0:** https://github.com/SuporteAMAD/Conversor_AM/releases/tag/v2.1.0

---

## 📞 Contato / Feedback

Envie relatórios de teste para a equipe de desenvolvimento. Seu feedback é essencial para melhorar o conversor!

**Status:** 🟢 Produção - Aguardando feedback dos usuários para validação

---

*Conversor AM v2.1.0 - 100+ Formatos - Escritório Andrade Maia*
