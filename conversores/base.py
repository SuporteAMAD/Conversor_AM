import os
import tempfile
from abc import ABC, abstractmethod
from typing import List


class BaseConverter(ABC):
    """Contrato base para estratégias de conversão orientadas a arquivo."""

    def __init__(self, input_path: str, output_format: str):
        self.input_path = input_path
        self.output_format = output_format.lower()
        self.temp_files: List[str] = []

    @abstractmethod
    def convert(self) -> str:
        """Executa a conversão e retorna o caminho do arquivo gerado."""

    def get_output_filename(self, original_name: str) -> str:
        stem, _ = os.path.splitext(original_name)
        return f"{stem}_convertido.{self.output_format}"

    def _create_temp_file(self, suffix: str = "") -> str:
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        self.temp_files.append(path)
        return path

    def cleanup(self):
        for path in self.temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass
        self.temp_files = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
