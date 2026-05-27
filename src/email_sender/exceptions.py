"""Исключения библиотеки"""


class EmailSenderError(Exception):
    """Базовое исключение"""
    pass


class AuthenticationError(EmailSenderError):
    """Ошибка аутентификации"""
    pass


class SendError(EmailSenderError):
    """Ошибка отправки"""
    pass


class ConfigurationError(EmailSenderError):
    """Ошибка конфигурации"""
    pass
