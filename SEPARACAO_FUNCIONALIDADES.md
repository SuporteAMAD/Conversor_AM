# Separação de Funcionalidades - Conversor de Arquivos AM

## Histórico da Decisão

A funcionalidade de PDF foi **completamente removida** desta aplicação para manter uma separação clara entre ferramentas:

### ✅ Mantido na Aplicação Atual
- **Conversões multimídia**:
  - Áudio: OGG → MP3
  - Vídeo: MP4 → WAV (extração de áudio)
  - Imagem: PNG → JPG

### ❌ Removido da Aplicação Atual
- **Qualquer funcionalidade de PDF**:
  - PDF → TXT
  - Qualquer referência a PyPDF2
  - Qualquer reutilização de lógica do I'AM.pdf

### 🔄 Mantido na Ferramenta I'AM.pdf
- Todas as funcionalidades de manipulação de PDF
- Conversão PDF → DOCX
- Extração de texto com OCR
- Compressão, mesclagem, divisão de PDFs
- Todas as outras operações PDF

## Motivos da Separação

1. **Responsabilidade Única**: Cada ferramenta tem um propósito claro
2. **Manutenibilidade**: Evita conflitos entre diferentes tipos de conversão
3. **Escalabilidade**: Permite evoluir cada ferramenta independentemente
4. **Segurança**: Reduz a superfície de ataque focando em tipos específicos

## Arquitetura Resultante

### Conversor de Arquivos AM (Esta Aplicação)
- Foco: Conversões multimídia
- Tecnologias: Flask, ffmpeg-python, Pillow
- Arquivos suportados: OGG, MP4, PNG, JPG, JPEG

### I'AM.pdf (Ferramenta Separada)
- Foco: Manipulação de PDFs
- Tecnologias: Flask, PyPDF2, pdf2image, pytesseract, etc.
- Arquivos suportados: PDF (várias operações)

## Migração

Se você estava usando funcionalidades de PDF nesta aplicação:

1. **Mova para I'AM.pdf**: Todas as operações PDF devem ser feitas na ferramenta dedicada
2. **Atualize bookmarks/scripts**: Aponte referências de PDF para a ferramenta I'AM.pdf
3. **Reconfigure infraestrutura**: As duas ferramentas podem rodar em paralelo

## Suporte

- **Conversões multimídia**: Use esta ferramenta (Conversor de Arquivos AM)
- **Operações PDF**: Use a ferramenta I'AM.pdf
- **Integração**: Ambas podem compartilhar infraestrutura RDS, mas são aplicações independentes