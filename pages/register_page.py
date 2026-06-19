import customtkinter as ctk
from tkinter import messagebox
import re
from pages.verify_otp import VerifyOTPPage
from utils.email_sender import send_otp
import random
from datetime import datetime, timedelta


class RegisterPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.master = master
        self.conn = master.conn
        

        self.show_role_selection()

    def show_role_selection(self):

        for w in self.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self,
            text="Create Account",
            font=("Arial", 30, "bold")
        ).pack(pady=40)

        ctk.CTkButton(
            self,
            text="Register as User",
            width=300,
            command=lambda: self.build_form("user")
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="Register as Driver",
            width=300,
            command=lambda: self.build_form("driver")
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="Back",
            command=self.go_back
        ).pack(pady=30)

    def build_form(self, role):

        for w in self.winfo_children():
            w.destroy()

        self.role = role

        container = ctk.CTkScrollableFrame(self, width=500, height=600)
        container.pack(pady=20)

        self.entries = {}

        fields = {
            "Name": "Example: Full Name",
            "Username": "Example: gomon123",
            "Email": "Example: user@gmail.com",
            "Phone": "Example: 017XXXXXXXX",
            "Address": "Example: Mirpur-2, Dhaka"
        }

        for field, example in fields.items():

            ctk.CTkLabel(container, text=field).pack(anchor="w", padx=70)

            entry = ctk.CTkEntry(
                container,
                placeholder_text=example,
                width=350
            )

            entry.pack(pady=5)

            self.entries[field] = entry

        ctk.CTkLabel(container, text="Password").pack(anchor="w", padx=70)
        pass_frame=ctk.CTkFrame(container,fg_color="transparent")
        pass_frame.pack(pady=5)

        self.password = ctk.CTkEntry(
            pass_frame,
            show="*",
            placeholder_text="Minimum 8 characters",
            width=300
        )
        self.password.pack(side="left", padx=(0,5))
        ctk.CTkButton(
            pass_frame,
            text="👁",
            width=45,
            command=self.toggle_password
        ).pack(side="left")

        ctk.CTkLabel(container, text="Confirm Password").pack(anchor="w", padx=70)
        confirm_frame=ctk.CTkFrame(container, fg_color="transparent")
        confirm_frame.pack(pady=5)

        self.confirm_password = ctk.CTkEntry(
            confirm_frame,
            show="*",
            placeholder_text="Retype password",
            width=300
        )
        self.confirm_password.pack(side="left", padx=(0,5))

        self.show_pass = False
        ctk.CTkButton(
            confirm_frame,
            text="👁",
            width=45,
            command=self.toggle_password
        ).pack(side="left")

        if role == "driver":

            driver_fields = {
                "NID": "Example: 11/13/17 digit must",
                "Driving License": "Example: DL12AB3456CD789",
                "Vehicle Number": "Example: Dhaka Metro-Ga 11-9999"
            }

            for field, example in driver_fields.items():

                ctk.CTkLabel(container, text=field).pack(anchor="w", padx=70)

                entry = ctk.CTkEntry(
                    container,
                    placeholder_text=example,
                    width=350
                )

                entry.pack(pady=5)

                self.entries[field] = entry

            ctk.CTkLabel(container, text="Vehicle Type").pack(anchor="w", padx=70)

            self.vehicle_type = ctk.CTkComboBox(
                container,
                values=[
                    "Select",
                    "Bike",
                    "Private Car",
                    "CNG",
                    "Micro",
                    "Bus",
                    "Truck",
                    "Pickup"
                ],
                width=350
            )

            self.vehicle_type.pack(pady=5)

            # WORK TIME

            ctk.CTkLabel(container, text="Work Time").pack(anchor="w", padx=70)

            self.work_time = ctk.CTkComboBox(
                container,
                values=[
                    "Select",
                    "Part Time",
                    "Full Time"
                ],
                width=350
            )

            self.work_time.pack(pady=5)

        ctk.CTkButton(
            container,
            text="Register",
            width=350,
            command=self.register_account
        ).pack(pady=20)

        ctk.CTkButton(
            container,
            text="Back",
            width=350,
            command=self.show_role_selection
        ).pack(pady=10)

    def toggle_password(self):

        self.show_pass = not self.show_pass

        if self.show_pass:
            self.password.configure(show="")
            self.confirm_password.configure(show="")
        else:
            self.password.configure(show="*")
            self.confirm_password.configure(show="*")

    def valid_email(self, email):

        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(pattern, email):
            return False
        
        blocked=[
            "gmial.com",
            "gamil.com",
            "gmail,com",
            "yaho.com",
            "hotmial.com"
        ]
        domain= email.split("@")[1].lower()
        if domain in blocked:
            return False
        
        return True

    def valid_nid(self, nid):

        return nid.isdigit() and len(nid) in [11, 13, 17]

    def valid_license(self, code):

        pattern = r'^[A-Za-z0-9]{15}$'

        return re.match(pattern, code)

    def valid_vehicle(self, number):

        pattern = r'^[A-Za-z\s\-]+ \d{2}-\d{4}$'

        return re.match(pattern, number)

    def register_account(self):

        data = {k: v.get().strip() for k, v in self.entries.items()}

        password = self.password.get()
        confirm = self.confirm_password.get()
        for key, value in data.items():
            if not value:
                messagebox.showerror("Error", f"{key} is required")
                return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be minimum 8 characters")
            return

        if not self.valid_email(data["Email"]):
            messagebox.showerror("Error", "Enter a vaild email address")
            return

        if not data["Phone"].isdigit() or len(data["Phone"]) != 11:
            messagebox.showerror("Error", "Phone must be 11 digits")
            return
        
        if data["Username"] != data["Username"].lower():
            messagebox.showerror("Error","Username must contain only small letters")
            return
        if self.role == "driver":

            required_driver = ["NID", "Driving License", "Vehicle Number"]

            for field in required_driver:
                if not data.get(field):
                    messagebox.showerror("Error", f"{field} is required")
                    return

            if not self.valid_nid(data["NID"]):
                messagebox.showerror("Error", "Invalid NID")
                return

            if not self.valid_license(data["Driving License"]):
                messagebox.showerror("Error", "License must be 15 characters")
                return

            if not self.valid_vehicle(data["Vehicle Number"]):
                messagebox.showerror("Error", "Invalid vehicle number")
                return

            if self.vehicle_type.get() == "Select" or self.work_time.get() == "Select":
                messagebox.showerror("Error", "Select vehicle & work time")
                return
            
        cursor = self.conn.cursor()

        cursor.execute("SELECT id FROM accounts WHERE username=%s", (data["Username"],))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return
        
        cursor.execute("SELECT id, is_verified FROM accounts WHERE email=%s", (data["Email"],))
        row = cursor.fetchone()

        if row:
            if row[1] == 1:
                messagebox.showerror("Error", "Email already registered")
                return
        
        cursor.execute("SELECT id FROM accounts WHERE phone=%s", (data["Phone"],))
        if cursor.fetchone():
            messagebox.showerror("Error", "Phone already registered")
            return

        if self.role == "driver":

            cursor.execute(
                "SELECT id FROM driver_info WHERE nid=%s",
                (data["NID"],))

            if cursor.fetchone():
                messagebox.showerror(
                    "Error",
                "NID already registered")
                return

            cursor.execute(
                "SELECT id FROM driver_info WHERE driving_license=%s",(data["Driving License"],))

            if cursor.fetchone():
                messagebox.showerror(
                "Error",
                "Driving license already registered")
                return

            cursor.execute(
            "SELECT id FROM driver_info WHERE vehicle_number=%s",(data["Vehicle Number"],))

            if cursor.fetchone():
                messagebox.showerror(
                "Error",
                "Vehicle number already registered")
                return

        otp = str(random.randint(100000, 999999))
        expire_time = datetime.now() + timedelta(minutes=2)
        if self.role == "driver":
            data["vehicle_type"] = self.vehicle_type.get()
            data["work_time"] = self.work_time.get()
            
        self.temp_data = data
        self.temp_password = password
        self.temp_otp = otp

        cursor.execute("""
            INSERT INTO accounts (email, otp, otp_expire, otp_count, is_verified)
            VALUES (%s,%s,%s,0,FALSE)
            ON DUPLICATE KEY UPDATE
            otp=%s,
            otp_expire=%s,
            otp_count=0
            """, (data["Email"], otp, expire_time, otp, expire_time))

        self.conn.commit()

        if not send_otp(data["Email"], otp):
            messagebox.showerror("Error", "OTP send failed")
            return
        
        if row:
            if row[1] == 0:
                messagebox.showinfo("OTP", "OTP resent to your email")
        else:
            messagebox.showinfo("OTP", "OTP sent successfully")
        self.master.clear_window()
        VerifyOTPPage(self.master, self)

    def go_back(self):
        self.master.clear_window()
        from pages.login_page import LoginPage
        LoginPage(self.master)
    