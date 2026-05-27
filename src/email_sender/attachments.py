"""Работа с вложениями"""

from pathlib import Path
from typing import Union, Optional
import mimetypes


class Attachment:
    """Класс для работы с вложениями"""
    
    def __init__(self, file_path: Union[str, Path], filename: Optional[str] = None):
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        self.filename = filename or self.file_path.name
        self.mime_type = mimetypes.guess_type(self.file_path)[0] or "application/octet-stream"
    
    def __repr__(self):
        return f"Attachment({self.filename})"
