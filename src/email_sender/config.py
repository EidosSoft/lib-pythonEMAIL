"""Управление конфигурацией"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class EmailConfig:
    """Конфигурация email клиента"""
    email: str
    password: str
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    service: Optional[str] = None
    use_tls: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def save(self, filepath: Union[str, Path]):
        """Сохранение в файл"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: Union[str, Path]):
        """Загрузка из файла"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    @classmethod
    def from_env(cls):
        """Загрузка из переменных окружения"""
        return cls(
            email=os.environ.get('EMAIL_SENDER_EMAIL', ''),
            password=os.environ.get('EMAIL_SENDER_PASSWORD', ''),
            smtp_host=os.environ.get('EMAIL_SENDER_SMTP_HOST'),
            smtp_port=int(os.environ.get('EMAIL_SENDER_SMTP_PORT', 0)) or None,
            service=os.environ.get('EMAIL_SENDER_SERVICE'),
            use_tls=os.environ.get('EMAIL_SENDER_USE_TLS', 'true').lower() == 'true'
        )
