"""Основной клиент для отправки email"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import json

from .models import EmailMessage
from .attachments import Attachment
from .exceptions import AuthenticationError, SendError, ConfigurationError


class EmailClient:
    """
    Клиент для отправки email через SMTP
    Поддерживает Gmail, Yahoo, Outlook и другие сервисы
    """
    
    # Предустановленные конфигурации
    SMTP_CONFIGS = {
        'gmail': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True
        },
        'yahoo': {
            'host': 'smtp.mail.yahoo.com',
            'port': 587,
            'use_tls': True
        },
        'outlook': {
            'host': 'smtp-mail.outlook.com',
            'port': 587,
            'use_tls': True
        },
        'mailru': {
            'host': 'smtp.mail.ru',
            'port': 587,
            'use_tls': True
        },
        'yandex': {
            'host': 'smtp.yandex.ru',
            'port': 587,
            'use_tls': True
        }
    }
    
    def __init__(
        self,
        email: str,
        password: str,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        service: Optional[str] = None,
        use_tls: bool = True
    ):
        self.email = email
        self.password = password
        
        # Определяем SMTP настройки
        if smtp_host and smtp_port:
            self.smtp_host = smtp_host
            self.smtp_port = smtp_port
        elif service and service.lower() in self.SMTP_CONFIGS:
            config = self.SMTP_CONFIGS[service.lower()]
            self.smtp_host = config['host']
            self.smtp_port = config['port']
            use_tls = config.get('use_tls', True)
        else:
            # Автоопределение по домену
            domain = email.split('@')[-1].lower()
            for svc_name, config in self.SMTP_CONFIGS.items():
                if domain in svc_name:
                    self.smtp_host = config['host']
                    self.smtp_port = config['port']
                    break
            else:
                raise ConfigurationError(f"Не удалось определить SMTP сервер для {domain}")
        
        self.use_tls = use_tls
        self._server = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def connect(self):
        """Подключение к SMTP серверу"""
        try:
            if self.use_tls:
                self._server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                self._server.starttls(context=ssl.create_default_context())
            else:
                self._server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            self._server.login(self.email, self.password)
            return self
        except smtplib.SMTPAuthenticationError as e:
            raise AuthenticationError(f"Ошибка аутентификации: {e}")
        except Exception as e:
            raise AuthenticationError(f"Не удалось подключиться: {e}")
    
    def close(self):
        """Закрытие соединения"""
        if self._server:
            self._server.quit()
            self._server = None
    
    def _build_message(self, message: EmailMessage) -> MIMEMultipart:
        """Создание MIME сообщения"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["From"] = self.email
        msg["To"] = ", ".join(message.to_emails)
        
        if message.cc_emails:
            msg["Cc"] = ", ".join(message.cc_emails)
        
        if message.body:
            msg.attach(MIMEText(message.body, "plain", "utf-8"))
        
        if message.html_body:
            msg.attach(MIMEText(message.html_body, "html", "utf-8"))
        
        # Добавляем вложения
        for attachment in message.attachments:
            if isinstance(attachment, (str, Path)):
                attachment = Attachment(attachment)
            
            with open(attachment.file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment.filename}"
                )
                msg.attach(part)
        
        return msg
    
    def send(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        body: str = "",
        html_body: Optional[str] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        auto_connect: bool = True
    ) -> Dict[str, Any]:
        """
        Отправка email (простой способ)
        """
        message = EmailMessage(
            subject=subject,
            body=body,
            html_body=html_body
        )
        
        # Добавляем получателей
        if isinstance(to_email, str):
            message.to_emails = [to_email]
        else:
            message.to_emails = to_email
        
        if cc:
            message.cc_emails = [cc] if isinstance(cc, str) else cc
        
        if bcc:
            message.bcc_emails = [bcc] if isinstance(bcc, str) else bcc
        
        if attachments:
            for att in attachments:
                message.add_attachment(att)
        
        return self.send_message(message, auto_connect)
    
    def send_message(
        self,
        message: EmailMessage,
        auto_connect: bool = True
    ) -> Dict[str, Any]:
        """Отправка email через объект EmailMessage"""
        result = {
            "success": False,
            "message": "",
            "recipients": message.to_emails
        }
        
        try:
            if auto_connect and not self._server:
                self.connect()
            
            msg = self._build_message(message)
            all_recipients = message.to_emails + message.cc_emails + message.bcc_emails
            self._server.send_message(msg, to_addrs=all_recipients)
            
            result["success"] = True
            result["message"] = "Email успешно отправлен"
            
        except Exception as e:
            result["message"] = str(e)
            raise SendError(f"Ошибка при отправке: {e}")
        
        finally:
            if auto_connect:
                self.close()
        
        return result
    
    def send_bulk(
        self,
        recipients: List[Dict[str, Any]],
        template_subject: str,
        template_body: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Массовая рассылка с персонализацией"""
        results = []
        
        for recipient in recipients:
            subject = template_subject.format(**recipient)
            body = template_body.format(**recipient)
            
            try:
                result = self.send(
                    to_email=recipient["email"],
                    subject=subject,
                    body=body,
                    **kwargs
                )
                result["recipient"] = recipient["email"]
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "recipient": recipient["email"],
                    "message": str(e)
                })
        
        return results
    
    @classmethod
    def from_config(cls, config_path: Union[str, Path]):
        """Загрузка конфигурации из JSON файла"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return cls(
            email=config['email'],
            password=config['password'],
            smtp_host=config.get('smtp_host'),
            smtp_port=config.get('smtp_port'),
            service=config.get('service'),
            use_tls=config.get('use_tls', True)
        )
    
    def test_connection(self) -> bool:
        """Тестирование подключения"""
        try:
            self.connect()
            self.close()
            return True
        except Exception:
            return False
