#!/usr/bin/env python3
"""Базовый пример использования"""

from src.email_sender.client import EmailClient

def main():
    # Создаем клиент для Gmail
    client = EmailClient(
        email="your_email@gmail.com",
        password="your_app_password",  # Пароль приложения Gmail
        service="gmail"
    )
    
    # Отправляем письмо
    result = client.send(
        to_email="recipient@example.com",
        subject="Тестовое письмо",
        body="Привет! Это тестовое письмо.",
        html_body="<h1>Привет!</h1><p>Это HTML письмо</p>"
    )
    
    print(f"Результат: {result}")

if __name__ == "__main__":
    main()
