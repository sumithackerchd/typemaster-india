from flask_mail import Message
from flask import current_app
from extensions import mail

def send_otp_email(receiver_email, otp):

    msg = Message(
        subject="TypeMaster India Password Reset OTP",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[receiver_email]
    )

    msg.body = f"""
Hello,

Your OTP is:

{otp}

This OTP is valid for 10 minutes.

Regards,
TypeMaster India
"""

    mail.send(msg)