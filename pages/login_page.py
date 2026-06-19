import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from pages.register_page import RegisterPage
from database import check_password
from pages.forgot_password import ForgotPasswordPage
from pages.user_dashboard import UserDashboard
from pages.driver_dashboard import DriverDashboard
from pages.super_admin_dashboard import SuperAdminDashboard
from pages.admin_dashboard import AdminDashboard
from pages.change_password_page import ChangePasswordPage


class LoginPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.master = master
        self.conn = master.conn
        self.build_ui()

    def build_ui(self):
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True)

        container = ctk.CTkFrame(
            scroll,
            corner_radius=10,
            fg_color="#393737",
            border_width=1,
            border_color="#323030",
        )

        container.pack(expand=True, padx=50, pady=50)

        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")

        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            logo = ctk.CTkImage(img, size=(140, 140))
            logo_label = ctk.CTkLabel(container, image=logo, text="")
            logo_label.image = logo
            logo_label.pack(pady=10)

        ctk.CTkLabel(container, text="GOMON", font=("Arial", 28, "bold")).pack(
            pady=(10, 0)
        )

        ctk.CTkLabel(
            container,
            text="Ride for Everyone",
            font=("Arial", 12),
            text_color="#f97316",
        ).pack(pady=(0, 10))

        self.username = ctk.CTkEntry(
            container,
            placeholder_text="Username or Email",
            width=300,
            height=40,
            corner_radius=10,
        )
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(
            container,
            placeholder_text="Password",
            show="*",
            width=300,
            height=40,
            corner_radius=10,
        )
        self.password.pack(pady=10)

        ctk.CTkButton(
            container, text="Login", width=300, height=30, command=self.login
        ).pack(pady=10)

        ctk.CTkButton(
            container,
            text="Create New Account",
            width=300,
            height=30,
            fg_color="green",
            command=self.go_register,
        ).pack(pady=5)

        ctk.CTkButton(
            container,
            text="Forgot Password?",
            fg_color="transparent",
            text_color="orange",
            hover=False,
            command=self.go_forgot,
        ).pack(pady=10)

    def go_register(self):
        self.master.clear_window()
        RegisterPage(self.master)

    def login(self):

        username_input = self.username.get().strip()
        password_input = self.password.get().strip()

        if not username_input or not password_input:
            messagebox.showerror("Error", "All fields are required!")
            return

        if self.conn is None:
            messagebox.showerror("Error", "Database not connected!")
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, password, role, is_verified, is_first_login
            FROM accounts 
            WHERE username=%s OR email=%s
        """,
            (username_input, username_input),
        )

        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Username or Email not found!")
            return

        user_id, hashed_password, role, is_verified, first_login = result

        if not is_verified:
            messagebox.showerror("Error", "Please verify your email first!")
            return

        if not check_password(password_input, hashed_password):
            messagebox.showerror("Error", "Incorrect password!")
            return

        if first_login == 1:
            self.master.clear_window()
            ChangePasswordPage(self.master, user_id)
            return

        if role == "user":
            self.open_user_dashboard(user_id)

        elif role == "driver":
            self.open_driver_dashboard(user_id)

        elif role == "admin":
            self.open_admin_dashboard(user_id)

        elif role == "superadmin":
            self.open_superadmin_dashboard(user_id)

    def go_forgot(self):
        self.master.clear_window()
        ForgotPasswordPage(self.master)

    def open_user_dashboard(self, user_id):

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT id, name, username, email, phone, address
        FROM accounts
        WHERE id=%s
        """,
            (user_id,),
        )

        user = cursor.fetchone()

        self.master.clear_window()

        UserDashboard(self.master, user)

    def open_driver_dashboard(self, user_id):

        self.master.clear_window()

        DriverDashboard(self.master, user_id)

    def open_admin_dashboard(self, user_id):
        self.master.clear_window()
        AdminDashboard(self.master, user_id)

    def open_superadmin_dashboard(self, user_id):

        self.master.clear_window()

        SuperAdminDashboard(self.master, user_id)
