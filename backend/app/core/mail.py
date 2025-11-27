from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailSchema(BaseModel):
    email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(email: List[EmailStr], subject: str, body: str):
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px; }}
            .header {{ background-color: #0d9488; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 30px 20px; background-color: #f9fafb; }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #0d9488; letter-spacing: 5px; text-align: center; margin: 20px 0; }}
            .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Med AI Security</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a request to reset your password for your Med AI account.</p>
                <p>Please use the following One-Time Password (OTP) to complete the process:</p>
                <div class="otp-code">{body.split('<b>')[1].split('</b>')[0] if '<b>' in body else body}</div>
                <p>This code will expire in 10 minutes.</p>
                <p>If you did not request this, please ignore this email or contact support.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Med AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=email,
        body=html_template,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        logger.info(f"Email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False
