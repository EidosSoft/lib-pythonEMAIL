"""Модели данных для email сообщений"""

from typing import List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field

from .attachments import Attachment


@dataclass
class EmailMessage:
    """Модель email сообщения"""
    subject: str
    body: str = ""
    html_body: Optional[str] = None
    to_emails: List[str] = field(default_factory=list)
    cc_emails: List[str] = field(default_factory=list)
    bcc_emails: List[str] = field(default_factory=list)
    attachments: List[Union[str, Path, Attachment]] = field(default_factory=list)
    
    def add_recipient(self, email: str):
        """Добавить получателя"""
        self.to_emails.append(email)
        return self
    
    def add_cc(self, email: str):
        """Добавить копию"""
        self.cc_emails.append(email)
        return self
    
    def add_bcc(self, email: str):
        """Добавить скрытую копию"""
        self.bcc_emails.append(email)
        return self
    
    def add_attachment(self, file_path: Union[str, Path], filename: Optional[str] = None):
        """Добавить вложение"""
        self.attachments.append(Attachment(file_path, filename))
        return self
