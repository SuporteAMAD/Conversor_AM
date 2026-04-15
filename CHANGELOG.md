# Changelog - Conversor de Arquivos AM

## [2.0.2] - Publicação Docker (2026-04-15)

### ✨ Adicionado

#### 🐳 Publicação no Docker Hub
- **Imagem Docker**: `gabrielwaschburger/conversor-am:v2.0.1`
- **Arquivo Backup**: `conversor-am-v2.0.1.tar` (2.6GB)
- **Gunicorn**: Servidor WSGI com 4 workers para produção
- **Health Check**: Verificação automática de saúde do container
- **Documentação**: Guia completo de deploy (`DEPLOY_PUBLICADO.md`)

#### 📦 Distribuição Universal
- **Compatibilidade**: Qualquer servidor com Docker
- **Portabilidade**: Mesma imagem funciona localmente e em produção
- **Escalabilidade**: Fácil de replicar em múltiplos servidores
- **Backup**: Arquivo tar para distribuição offline

## [2.0.1] - Docker Production Ready (2026-04-15)

### ✨ Adicionado

#### 🐳 Suporte a Docker Production
- **Gunicorn**: Servidor WSGI para produção com 4 workers
- **Configuração Production**: Ambiente `FLASK_ENV=production` mapeado
- **Health Check**: Verificação automática de saúde do container
- **Volumes Persistentes**: Uploads, exports e logs mapeados

#### 🔧 Melhorias de Configuração
- **ProductionConfig**: Nova classe de configuração para produção
- **Debug Dinâmico**: `app.run()` usa configuração baseada no ambiente
- **Mapeamento de Ambientes**: Suporte para `production` e `prod`

### 📦 Dependências
- **gunicorn==22.0.0**: Servidor WSGI para produção

## [2.0.0] - Expansão Convertio-like (2026-04-14)

### ✨ Adicionado

#### � Interface do Usuário Renovada
- **Tema Visual**: Cores preto (#1a1a1a) e laranja (#ff6b35) do escritório
- **Barra de Progresso**: Visualização em tempo real das conversões
- **Download Integrado**: Botão direto para baixar arquivos convertidos
- **Design Responsivo**: Interface otimizada para todos os dispositivos
- **Experiência AJAX**: Conversões assíncronas sem recarregar página
- **Feedback Visual**: Animações, transições e estados de loading

#### �🎵 Conversões de Áudio Expandidas
- **OGG → MP3**: Conversão com qualidade 192kbps (existente)
- **MP3 → WAV**: Conversão para formato não comprimido (novo)

#### 🎬 Conversões de Vídeo Expandidas
- **MP4 → WAV**: Extração de áudio (existente)
- **MP4 → AVI**: Conversão entre formatos de vídeo (novo)

#### 🖼️ Conversões de Imagem Expandidas
- **PNG → JPG**: Otimização e conversão (existente)
- **PNG/JPG → WebP**: Conversão para formato moderno (novo)

#### 📄 Conversões de Documentos (NOVO)
- **DOCX → PDF**: Documentos Word para PDF
- **PDF → DOCX**: PDFs para documentos editáveis
- **DOCX → TXT**: Extração de texto puro

#### 📝 Conversões de Texto (NOVO)
- **TXT → PDF**: Arquivos de texto para PDF

#### 📊 Conversões de Planilhas (NOVO)
- **XLSX → CSV**: Planilhas Excel para CSV
- **CSV → XLSX**: Arquivos CSV para Excel

### � Corrigido

#### 🔧 Problema de Codificação em TextConverter
- **Bug**: TextConverter falhava com arquivos UTF-16/Unicode
- **Causa**: Codificação hardcoded como UTF-8 apenas
- **Solução**: Implementação de detecção automática de codificação
- **Codificações suportadas**: UTF-8, UTF-16 (LE/BE), Latin-1, CP1252
- **Fallback**: Tratamento de BOM e conversão forçada se necessário

### �🔧 Melhorias Técnicas

#### Interface do Usuário
- **Organização por categorias**: Áudio, Vídeo, Imagem, Documentos, Planilhas, Texto
- **Grupos optgroup**: Melhor organização visual no select
- **CSS responsivo**: Design moderno com categorias destacadas
- **Ícones por categoria**: 🎵 🎬 🖼️ 📄 📊 📝

#### Arquitetura
- **Novos conversores modulares**: DocumentConverter, TextConverter, SpreadsheetConverter
- **Factory pattern expandido**: Suporte a 6 tipos de arquivo
- **Validações robustas**: 11 extensões suportadas
- **Tratamento de erros**: Mensagens específicas por conversão

#### Bibliotecas Adicionadas
- `python-docx==1.1.0`: Manipulação de documentos Word
- `reportlab==4.0.7`: Geração de PDFs
- `pdf2docx==0.5.6`: Conversão PDF→DOCX
- `pandas>=2.0.0`: Manipulação de dados e planilhas
- `openpyxl==3.1.2`: Leitura/escrita Excel

### 📊 Estatísticas

- **Conversões suportadas**: 12 (era 3)
- **Formatos de entrada**: 11 (era 3)
- **Bibliotecas utilizadas**: 8 (era 3)
- **Tempo de desenvolvimento**: 41h (era 25h)
- **Linhas de código**: +200 linhas

### 🔄 Compatibilidade

- **Backward compatible**: Todas as conversões originais mantidas
- **API consistente**: Mesmo padrão de uso
- **Configuração**: Mesmas configurações de ambiente
- **Segurança**: Validações expandidas mantidas

### 🧪 Testes

- ✅ Validação de 11 tipos de arquivo
- ✅ Instanciação de 12 conversores
- ✅ Importação de todas as dependências
- ✅ Interface web funcional

### 📈 Comparação com Convertio

| Recurso | Antes | Agora | Convertio |
|---------|-------|-------|-----------|
| Áudio | 1 | 2 | 15+ |
| Vídeo | 1 | 2 | 20+ |
| Imagem | 1 | 2 | 10+ |
| Documentos | 0 | 3 | 15+ |
| Planilhas | 0 | 2 | 10+ |
| Texto | 0 | 1 | 5+ |
| **Total** | **3** | **12** | **75+** |

### 🎯 Status do MVP Expandido

- ✅ **Funcionalidades core**: Upload, conversão, download
- ✅ **Interface web**: Moderna e organizada
- ✅ **Segurança**: Validações e sanitização
- ✅ **Arquitetura**: Modular e extensível
- ✅ **Documentação**: Completa e atualizada
- ✅ **Testes**: Validação abrangente

### 🚀 Próximos Passos

1. **Mais formatos**: DOC, XLS, PPT, etc.
2. **Compressão**: ZIP, RAR, 7Z
3. **E-books**: EPUB, MOBI
4. **APIs REST**: Endpoints programáticos
5. **Fila de processamento**: Para arquivos grandes
6. **Dashboard**: Métricas e administração

---

## [1.0.0] - MVP Inicial (2026-04-14)

- ✅ Classe BaseConverter
- ✅ AudioConverter (OGG→MP3)
- ✅ VideoConverter (MP4→WAV)
- ✅ ImageConverter (PNG→JPG)
- ✅ Interface Flask básica
- ✅ Configurações multi-ambiente
- ✅ Separação completa de PDF