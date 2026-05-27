import pytest
from src.email_sender.client import EmailClient
from src.email_sender.exceptions import ConfigurationError


def test_smtp_auto_detect():
    # Gmail
    client = EmailClient("test@gmail.com", "pass", service="gmail")
    assert client.smtp_host == "smtp.gmail.com"
    
    # Yahoo
    client = EmailClient("test@yahoo.com", "pass", service="yahoo")
    assert client.smtp_host == "smtp.mail.yahoo.com"
    
    # Outlook
    client = EmailClient("test@outlook.com", "pass", service="outlook")
    assert client.smtp_host == "smtp-mail.outlook.com"


def test_invalid_service():
    with pytest.raises(ConfigurationError):
        EmailClient("test@unknown.com", "pass")
