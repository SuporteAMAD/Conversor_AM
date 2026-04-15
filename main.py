"""
Conversor de Arquivos AM v2.0.0 - Expansão Convertio-like
Ferramenta interna de conversão de arquivos para escritório Andrade Maia.

MELHORIAS v2.0.0:
- 🎨 Interface renovada com tema preto/laranja do escritório
- 📊 Barra de progresso em tempo real
- ⬇️ Download integrado via AJAX
- 📱 Design responsivo
- ⚡ Feedback visual aprimorado

IMPORTANTE: Esta aplicação NÃO inclui funcionalidade de PDF.
A ferramenta PDF (I'AM.pdf) é mantida completamente separada.

Arquitetura modular inspirada no I'AM.pdf, reutilizando padrões de:
- Helpers genéricos (file_sha1, cache_path, save_converted_copy)
- Tratamento de uploads/downloads
- Validações de segurança
- Estrutura Flask com rotas modulares

Módulos:
- conversores/: Classes específicas para cada tipo de conversão (áudio, vídeo, imagem)
- rotas/: Rotas Flask/FastAPI
- utils/: Funções utilitárias reutilizáveis
- templates/: HTML frontend
- static/: CSS/JS
"""

import os
import tempfile
import hashlib
import re
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from datetime import datetime
import sys
from pathlib import Path

from flask import Flask
from config import get_config

# Configurações
config = get_config()

app = Flask(__name__)
app.config.from_object(config)

# ========== CONFIGURAÇÃO DE FFmpeg ==========

def setup_ffmpeg_path():
    """Detecta e configura o caminho do FFmpeg."""
    ffmpeg_paths = [
        # Procurar localmente em ./ffmpeg/bin/
        os.path.join(os.path.dirname(__file__), "ffmpeg", "bin"),
        # Procurar em ./ffmpeg-master-latest-win64-gpl/bin/
        os.path.join(os.path.dirname(__file__), "ffmpeg-master-latest-win64-gpl", "bin"),
    ]
    
    # Adicionar ao PATH se existir
    for path in ffmpeg_paths:
        if os.path.exists(path):
            if path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
            return True
    
    return False

# Configurar FFmpeg ao iniciar
setup_ffmpeg_path()

# ========== CLASSE BASE PARA CONVERSORES ==========

class BaseConverter(ABC):
    """
    Classe base abstrata para conversores de arquivo.
    Segue padrão similar ao I'AM.pdf, com métodos utilitários compartilhados.
    """

    def __init__(self, input_path: str, output_format: str):
        self.input_path = input_path
        self.output_format = output_format
        self.temp_files = []  # Para limpeza

    @abstractmethod
    def convert(self) -> bytes:
        """
        Método abstrato para conversão.
        Deve retornar os bytes do arquivo convertido.
        """
        pass

    def _get_output_filename(self, original_name: str) -> str:
        """Gera nome do arquivo de saída baseado no original."""
        stem, _ = os.path.splitext(original_name)
        return f"{stem}_convertido.{self.output_format}"

    def _create_temp_file(self, suffix: str = "") -> str:
        """Cria arquivo temporário e registra para limpeza."""
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        self.temp_files.append(path)
        return path

    def cleanup(self):
        """Remove arquivos temporários."""
        for path in self.temp_files:
            try:
                os.remove(path)
            except:
                pass
        self.temp_files = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

# ========== CONVERSORES ESPECÍFICOS ==========

class AudioConverter(BaseConverter):
    """Conversor de áudio: OGG → MP3"""

    def convert(self) -> bytes:
        try:
            import ffmpeg
        except ImportError:
            raise RuntimeError("ffmpeg-python não instalado. Instale com: pip install ffmpeg-python")

        output_path = self._create_temp_file(".mp3")

        # Conversão usando ffmpeg
        stream = ffmpeg.input(self.input_path)
        stream = ffmpeg.output(stream, output_path, acodec='mp3', audio_bitrate='192k')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        with open(output_path, 'rb') as f:
            return f.read()

class VideoConverter(BaseConverter):
    """Conversor de vídeo: MP4 → WAV"""

    def convert(self) -> bytes:
        try:
            import ffmpeg
        except ImportError:
            raise RuntimeError("ffmpeg-python não instalado. Instale com: pip install ffmpeg-python")

        output_path = self._create_temp_file(".wav")

        # Extrair áudio do vídeo para WAV
        stream = ffmpeg.input(self.input_path)
        stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ar='44100')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        with open(output_path, 'rb') as f:
            return f.read()

class ImageConverter(BaseConverter):
    """Conversor de imagem: PNG → JPG"""

    def convert(self) -> bytes:
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError("Pillow não instalado. Instale com: pip install Pillow")

        # Abrir imagem e converter
        with Image.open(self.input_path) as img:
            # Converter para RGB se necessário (para JPG)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            output_path = self._create_temp_file(".jpg")
            img.save(output_path, 'JPEG', quality=90)

            with open(output_path, 'rb') as f:
                return f.read()

class DocumentConverter(BaseConverter):
    """Conversor de documentos: DOCX → PDF"""

    def convert(self) -> bytes:
        try:
            from docx import Document
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        except ImportError:
            raise RuntimeError("python-docx e reportlab não instalados")

        if self.output_format == 'pdf':
            # DOCX → PDF
            doc = Document(self.input_path)
            output_path = self._create_temp_file(".pdf")

            # Criar PDF
            pdf = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            for para in doc.paragraphs:
                if para.text.strip():
                    story.append(Paragraph(para.text, styles['Normal']))
                    story.append(Spacer(1, 12))

            pdf.build(story)

            with open(output_path, 'rb') as f:
                return f.read()

        elif self.output_format == 'docx':
            # PDF → DOCX
            try:
                from pdf2docx import Converter
            except ImportError:
                raise RuntimeError("pdf2docx não instalado")

            output_path = self._create_temp_file(".docx")

            cv = Converter(self.input_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()

            with open(output_path, 'rb') as f:
                return f.read()

        elif self.output_format == 'txt':
            # DOCX → TXT
            doc = Document(self.input_path)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

            return text.encode('utf-8')

class TextConverter(BaseConverter):
    """Conversor de texto: TXT → PDF"""

    def convert(self) -> bytes:
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        except ImportError:
            raise RuntimeError("reportlab não instalado")

        # Tentar ler com diferentes codificações
        encodings_to_try = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1', 'cp1252']
        text = None

        for encoding in encodings_to_try:
            try:
                with open(self.input_path, 'r', encoding=encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            # Se nenhuma codificação funcionou, tentar como bytes e decodificar
            with open(self.input_path, 'rb') as f:
                raw_bytes = f.read()
                # Remover BOM se existir
                if raw_bytes.startswith(b'\xff\xfe'):
                    raw_bytes = raw_bytes[2:]  # UTF-16 LE BOM
                elif raw_bytes.startswith(b'\xfe\xff'):
                    raw_bytes = raw_bytes[2:]  # UTF-16 BE BOM

                try:
                    text = raw_bytes.decode('utf-16-le')
                except:
                    try:
                        text = raw_bytes.decode('latin-1')
                    except:
                        raise ValueError("Não foi possível decodificar o arquivo de texto")

        output_path = self._create_temp_file(".pdf")

        # Criar PDF
        pdf = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        for line in text.split('\n'):
            if line.strip():
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))

        pdf.build(story)

        with open(output_path, 'rb') as f:
            return f.read()

class SpreadsheetConverter(BaseConverter):
    """Conversor de planilhas: XLSX → CSV"""

    def convert(self) -> bytes:
        try:
            import pandas as pd
        except ImportError:
            raise RuntimeError("pandas não instalado")

        if self.output_format == 'csv':
            # XLSX → CSV
            df = pd.read_excel(self.input_path)
            csv_content = df.to_csv(index=False)
            return csv_content.encode('utf-8')

        elif self.output_format == 'xlsx':
            # CSV → XLSX
            df = pd.read_csv(self.input_path)
            output_path = self._create_temp_file(".xlsx")
            df.to_excel(output_path, index=False)

            with open(output_path, 'rb') as f:
                return f.read()

class ImageWebPConverter(BaseConverter):
    """Conversor de imagem para WebP"""

    def convert(self) -> bytes:
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError("Pillow não instalado")

        with Image.open(self.input_path) as img:
            # Converter para RGB se necessário
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            output_path = self._create_temp_file(".webp")
            img.save(output_path, 'WEBP', quality=85)

            with open(output_path, 'rb') as f:
                return f.read()

class AudioWAVConverter(BaseConverter):
    """Conversor de áudio: MP3 → WAV"""

    def convert(self) -> bytes:
        try:
            import ffmpeg
        except ImportError:
            raise RuntimeError("ffmpeg-python não instalado")

        output_path = self._create_temp_file(".wav")

        # MP3 → WAV
        stream = ffmpeg.input(self.input_path)
        stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ar='44100')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        with open(output_path, 'rb') as f:
            return f.read()

class VideoAVIConverter(BaseConverter):
    """Conversor de vídeo: MP4 → AVI"""

    def convert(self) -> bytes:
        try:
            import ffmpeg
        except ImportError:
            raise RuntimeError("ffmpeg-python não instalado")

        output_path = self._create_temp_file(".avi")

        # MP4 → AVI
        stream = ffmpeg.input(self.input_path)
        stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='mp3')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        with open(output_path, 'rb') as f:
            return f.read()

class VideoM4VConverter(BaseConverter):
    """Conversor de vídeo: M4V → MP4"""

    def convert(self) -> bytes:
        try:
            import ffmpeg
        except ImportError:
            raise RuntimeError("ffmpeg-python não instalado")

        output_path = self._create_temp_file(".mp4")

        # M4V → MP4 (re-encode com H.264/AAC)
        stream = ffmpeg.input(self.input_path)
        stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='aac', preset='medium')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        with open(output_path, 'rb') as f:
            return f.read()

# ========== REGISTRO DE CONVERSORES ==========

CONVERTERS = {
    # Áudio
    ('audio', 'mp3'): AudioConverter,
    ('audio', 'wav'): AudioWAVConverter,

    # Vídeo
    ('video', 'wav'): VideoConverter,
    ('video', 'avi'): VideoAVIConverter,
    ('video', 'mp4'): VideoM4VConverter,

    # Imagem
    ('image', 'jpg'): ImageConverter,
    ('image', 'webp'): ImageWebPConverter,

    # Documentos
    ('document', 'pdf'): DocumentConverter,
    ('document', 'docx'): DocumentConverter,
    ('document', 'txt'): DocumentConverter,

    # Texto
    ('text', 'pdf'): TextConverter,

    # Planilhas
    ('spreadsheet', 'csv'): SpreadsheetConverter,
    ('spreadsheet', 'xlsx'): SpreadsheetConverter,
}

def get_converter(file_type: str, target_format: str, input_path: str) -> Optional[BaseConverter]:
    """Factory para obter conversor apropriado."""
    key = (file_type.lower(), target_format.lower())
    converter_class = CONVERTERS.get(key)
    if converter_class:
        return converter_class(input_path, target_format)
    return None

# ========== HELPERS REUTILIZADOS DO I'AM.pdf ==========

def file_sha1(path: str) -> str:
    """Calcula SHA1 do arquivo."""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def cache_path(suffix: str, key: str) -> str:
    """Gera caminho de cache."""
    base = tempfile.gettempdir()
    fname = f"am_cache_{key}{suffix}"
    return os.path.join(base, fname)

def save_converted_copy(filename: str, data: bytes) -> None:
    """Salva cópia do arquivo convertido no diretório exports."""
    try:
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", filename.strip()) or "convertido.bin"
        stem, ext = os.path.splitext(safe)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        target = os.path.join(EXPORTS_DIR, f"{stem}_{stamp}{ext}")
        with open(target, "wb") as f:
            f.write(data)
    except Exception:
        pass

def save_upload_to_temp(storage, per_file_limit_bytes: int = None) -> str:
    """Salva upload em arquivo temporário com limite de tamanho."""
    if per_file_limit_bytes is None:
        per_file_limit_bytes = config.PER_FILE_LIMIT

    fd, path = tempfile.mkstemp(); os.close(fd)
    wrote = 0
    try:
        storage.stream.seek(0)
    except Exception:
        pass
    with open(path, "wb") as f:
        while True:
            chunk = storage.stream.read(1024 * 1024)
            if not chunk:
                break
            wrote += len(chunk)
            if per_file_limit_bytes is not None and wrote > per_file_limit_bytes:
                try: os.remove(path)
                except: pass
                raise ValueError(f"Arquivo excede {config.PER_FILE_LIMIT_MB} MB.")
            f.write(chunk)
    return path

# ========== VALIDAÇÕES DE SEGURANÇA ==========

def validate_file_type(filename: str) -> Tuple[str, str]:
    """Valida tipo de arquivo baseado na extensão."""
    ext = filename.lower().split('.')[-1]

    # Mapeamento de extensões para tipos
    type_map = {
        # Áudio
        'ogg': 'audio',
        'mp3': 'audio',
        'wav': 'audio',

        # Vídeo
        'mp4': 'video',
        'avi': 'video',
        'm4v': 'video',

        # Imagem
        'png': 'image',
        'jpg': 'image',
        'jpeg': 'image',
        'gif': 'image',
        'bmp': 'image',
        'tiff': 'image',
        'webp': 'image',

        # Documentos
        'docx': 'document',
        'doc': 'document',
        'pdf': 'document',

        # Texto
        'txt': 'text',

        # Planilhas
        'xlsx': 'spreadsheet',
        'xls': 'spreadsheet',
        'csv': 'spreadsheet',
    }

    file_type = type_map.get(ext)
    if not file_type:
        raise ValueError(f"Tipo de arquivo não suportado: .{ext}")

    return file_type, ext

def sanitize_filename(filename: str) -> str:
    """Sanitiza nome do arquivo."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", filename.strip()) or "arquivo"

# ========== VARIÁVEIS GLOBAIS ==========
EXPORTS_DIR = config.EXPORTS_DIR
PER_FILE_LIMIT_MB = config.PER_FILE_LIMIT_MB

# ========== IMPORTAR ROTAS ==========
# Importar rotas para registrar no app (FORA do if __name__ para funcionar com WSGI)
try:
    from rotas.app_routes import *
except ImportError as e:
    print(f"⚠️  Aviso ao importar rotas: {e}")

if __name__ == "__main__":
    app.run(debug=getattr(config, 'DEBUG', False), host=config.HOST, port=config.PORT)