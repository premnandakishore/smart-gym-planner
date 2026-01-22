import os
import smtplib
from email.message import EmailMessage

def send_login_alert(user_name, user_email):
    sender = os.getenv("GYM_EMAIL")
    password = os.getenv("GYM_EMAIL_PASS")

    if not sender or not password:
        return  # fail silently if not configured

    msg = EmailMessage()
    msg["Subject"] = "Gym Planner Login Alert"
    msg["From"] = sender
    msg["To"] = sender
    msg.set_content(
        f"Login Alert 🚨\n\n"
        f"User: {user_name}\n"
        f"Email: {user_email}\n"
        f"Status: Logged in successfully."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
def send_otp(email, otp):
    sender = os.getenv("GYM_EMAIL")
    password = os.getenv("GYM_EMAIL_PASS")

    subject = "Gym Planner Password Reset OTP"
    body = f"Your OTP is: {otp}"

    msg = f"Subject:{subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, email, msg)
    server.quit()
