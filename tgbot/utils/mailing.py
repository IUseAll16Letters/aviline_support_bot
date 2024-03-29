__all__ = ("send_email_to_aviline", )

import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from config.settings import SMTP_MAIL_PARAMS, EMAIL_HOST_USER
from tgbot.logging_config import mailing


async def send_email_to_aviline(subject, text, warranty_card: bytes, warranty_basename: str):
    sender = EMAIL_HOST_USER
    to = [SMTP_MAIL_PARAMS['send_to']]
    msg = MIMEMultipart()
    msg.preamble = subject
    msg['subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    msg.attach(MIMEText(text, 'html'))

    host = SMTP_MAIL_PARAMS['host']
    is_ssl = SMTP_MAIL_PARAMS['ssl']
    is_tls = SMTP_MAIL_PARAMS['tls']
    port = SMTP_MAIL_PARAMS['port']

    image = MIMEApplication(warranty_card, basename=warranty_basename)
    image['Content-Disposition'] = f'attachment; filename={warranty_basename}'
    msg.attach(image)

    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=is_ssl)

    async with smtp as connection:
        if is_tls:
            await connection.starttls()
        if 'user' in SMTP_MAIL_PARAMS:
            await connection.login(SMTP_MAIL_PARAMS['user'], SMTP_MAIL_PARAMS['password'])
        response = await connection.send_message(msg)
        msg = f"Mail sent with response: {response = }. "
        mailing.info(msg=msg)
