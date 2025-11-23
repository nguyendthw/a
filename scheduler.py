import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from app import db, Schedule

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["From"] = "your_email@gmail.com"
    msg["To"] = to
    msg["Subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your_email@gmail.com", "your_app_password")
        server.send_message(msg)

while True:
    now = datetime.utcnow()
    schedules = Schedule.query.filter_by(is_sent=False).all()

    for s in schedules:
        if now >= s.remind_at:
            send_email(s.email, s.title, s.description)
            s.is_sent = True
            db.session.commit()
            print(f"Đã gửi email: {s.title}")

    time.sleep(30)
