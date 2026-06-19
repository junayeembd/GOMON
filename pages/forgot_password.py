import customtkinter as ctk
from tkinter import messagebox
import random
import string
from database import hash_password
from utils.email_sender import send_admin_welcome_email


class ForgotPasswordPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.master = master
        self.conn = master.conn

        self.build_ui()

    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="Forgot Password",
            font=("Arial",24,"bold")
        ).pack(pady=20)

        self.email = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Enter your email"
        )
        self.email.pack(pady=10)

        ctk.CTkButton(
            self,
            text="Send Temporary Password",
            command=self.reset_password
        ).pack(pady=20)

        ctk.CTkButton(
            self,
            text="⬅ Back to Login",
            command=self.back
        ).pack()

    # ✅ FIXED FUNCTION
    def reset_password(self):

        email = self.email.get().strip()

        if not email:
            messagebox.showerror("Error","Enter email")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, username FROM accounts WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            messagebox.showerror("Error","Email not found")
            return

        # 🔥 temp password generate
        temp_pass = ''.join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )

        hashed = hash_password(temp_pass)

        cursor.execute("""
        UPDATE accounts
        SET password=%s,
            is_first_login=TRUE
        WHERE email=%s
        """, (hashed, email))

        self.conn.commit()
        send_admin_welcome_email(
            email,
            user["id"],
            user["username"],
            "N/A",
            "User",
            "User",
            "Login",
            temp_pass
        )

        messagebox.showinfo(
            "Success",
            "Temporary password sent to your email"
        )
        from pages.login_page import LoginPage
        self.master.clear_window()
        LoginPage(self.master)

    def back(self):

        from pages.login_page import LoginPage
        self.master.clear_window()
        LoginPage(self.master)