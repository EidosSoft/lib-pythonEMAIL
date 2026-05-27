"""
Email Sender - простая библиотека для отправки email
"""

from .client import EmailClient
from .models import EmailMessage
from .attachments import Attachment
from .exceptions import (
    EmailSenderError,
    AuthenticationError,
    SendError,
    ConfigurationError
)

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    "EmailClient",
    "EmailMessage",
    "Attachment",
    "EmailSenderError",
    "AuthenticationError",
    "SendError",
    "ConfigurationError",
]
