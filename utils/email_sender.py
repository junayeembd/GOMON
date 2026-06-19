import smtplib
from email.mime.text import MIMEText
import os 
from dotenv import load_dotenv

load_dotenv("no_open.env")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def send_otp(to_email, otp):

    msg = MIMEText(f"""
🔐 GOMON Verification Code
Your OTP is: {otp}

⏳ This code is valid for a short time.
Do not share it with anyone.
----------------------------------------
        -Team GOMON""")
    msg["Subject"] = "GOMON Email Verification"
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("OTP Email error:", e)
        return False

def send_welcome_email(to_email, user_id, username):

    msg = MIMEText(f"""
🎉 Welcome to GOMON 🚗

Your account has been successfully created!

🆔 User ID: {user_id}
👤 Username: {username}

Now you can enjoy:
✔ Easy ride booking
✔ Fast driver access
✔ Safe journey

Ride for Everyone 💚

— Team GOMON
""")

    msg["Subject"] = "Welcome to GOMON 🚗"
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Welcome Email Error:", e)
        return False

def send_admin_welcome_email(to_email, user_id, username,emp_id, dept, role, permission, password):

    msg = MIMEText(f"""
🎉 Welcome to GOMON Admin Panel

Your admin account has been created successfully.

━━━━━━━━━━━━━━━━━━━━━━
👤 Username: {username}
🆔 User ID: {user_id}
🔐Temporary Password: {password}
🏢 Employee ID: {emp_id}
📂 Department: {dept}
🛡 Admin Role: {role}
🔑 Permissions: {permission}
━━━━━━━━━━━━━━━━━━━━━━

⚠️Please login and chnage the password.
Please login and manage the system responsibly.

— Team GOMON
""")

    msg["Subject"] = "Admin Account Created - GOMON"
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Admin email error:", e)
        return False