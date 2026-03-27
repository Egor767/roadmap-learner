from app.clients import AIClient, EmailClient


def get_ai_client():
    return AIClient()


def get_email_client():
    return EmailClient()
