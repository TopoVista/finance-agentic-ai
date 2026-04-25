from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from api.core.config import settings


def _get_mailer() -> FastMail | None:
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASS):
        return None

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.SMTP_USER,
        MAIL_PASSWORD=settings.SMTP_PASS,
        MAIL_FROM=settings.SMTP_FROM,
        MAIL_PORT=settings.SMTP_PORT,
        MAIL_SERVER=settings.SMTP_HOST,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )
    return FastMail(conf)


async def send_email(to: str, subject: str, body: str) -> bool:
    mailer = _get_mailer()
    if mailer is None:
        return False

    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=body,
        subtype="html",
    )
    await mailer.send_message(message)
    return True
