import customtkinter as ctk
from tkinter import messagebox
from database import hash_password
from utils.email_sender import send_welcome_email, send_otp
import random
from datetime import datetime, timedelta


class VerifyOTPPage(ctk.CTkFrame):

    def __init__(self, master, register_page):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.master = master
        self.conn = master.conn
        self.reg = register_page

        self.otp_boxes = []
        self.time_left = 120

        self.build_ui()
        self.start_timer()

    def build_ui(self):

        main = ctk.CTkScrollableFrame(self)
        main.pack(fill="both", expand=True)

        container = ctk.CTkFrame(main, width=400, corner_radius=15)
        container.pack(pady=80, ipadx=20, ipady=20)
        container.configure(width=400, height=450)
        container.pack_propagate(False)

        self.car = ctk.CTkLabel(container, text="🚗", font=("Arial", 38))
        self.car.place(x=0, y=20)

        ctk.CTkLabel(container, text="━━━━━━━━━━━━━━━━━━━━━━", text_color="gray").pack(pady=(50, 5))
        self.after(300, self.animate_car)

        ctk.CTkLabel(container, text="🔐 Verify OTP", font=("Arial", 26, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(container, text="Enter 6-digit code", text_color="gray").pack(pady=(0, 20))

        box_frame = ctk.CTkFrame(container)
        box_frame.pack(pady=10)

        for i in range(6):
            entry = ctk.CTkEntry(box_frame, width=40, height=45, font=("Arial", 18), justify="center")
            entry.grid(row=0, column=i, padx=5)
            entry.bind("<KeyRelease>", lambda e, i=i: self.move_next(e, i))
            self.otp_boxes.append(entry)

        self.timer_label = ctk.CTkLabel(container, text="Time left: 60s", text_color="orange")
        self.timer_label.pack(pady=10)
        ctk.CTkButton(container, text="Verify", width=250, fg_color="#16a34a", command=self.verify).pack(pady=10)

        self.resend_btn = ctk.CTkButton(container, text="Resend OTP", state="disabled", command=self.resend_otp)
        self.resend_btn.pack(pady=5)

    def move_next(self, event, index):

        text = event.widget.get()
        if len(text) > 1:
            event.widget.delete(1, "end")
        if text and index < 5:
            self.otp_boxes[index + 1].focus()
        elif event.keysym == "BackSpace" and index > 0:
            self.otp_boxes[index - 1].focus()

    def get_otp(self):
        otp = "".join(box.get() for box in self.otp_boxes)

        if not otp.isdigit():
            return ""
        return otp

    def verify(self):

        otp_input = self.get_otp()

        if len(otp_input) != 6:
            messagebox.showerror("Error", "Enter full 6-digit OTP")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(""" SELECT otp, otp_expire FROM accounts WHERE email=%s """, (self.reg.temp_data["Email"],),)
        row = cursor.fetchone()

        if not row:
            messagebox.showerror("Error", "No OTP found")
            return

        if otp_input != row["otp"]:
            messagebox.showerror("Error", "Invalid OTP")
            return

        if datetime.now() > row["otp_expire"]:
            messagebox.showerror("Error", "OTP expired")
            return

        data = self.reg.temp_data
        hashed = hash_password(self.reg.temp_password)
        role = self.reg.role

        cursor = self.conn.cursor()
        cursor.execute( """ UPDATE accounts SET name=%s, username=%s, phone=%s, address=%s, password=%s, role=%s,
                       is_verified=TRUE, is_first_login= FALSE WHERE email=%s """, ( data["Name"], data["Username"], data["Phone"],data["Address"],hashed,role,data["Email"],),)

        cursor.execute("SELECT id FROM accounts WHERE email=%s", (data["Email"],))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Account not found")
            return

        account_id = result[0]
        if role == "driver":
            cursor.execute(
                """
            INSERT INTO driver_info
            (account_id,nid,driving_license,vehicle_number,vehicle_type,work_time,online_status)
            VALUES (%s,%s,%s,%s,%s,%s,'offline')
            """, ( account_id, data["NID"], data["Driving License"], data["Vehicle Number"], data.get("vehicle_type"),
                   data.get("work_time"),),)
            
        cursor.execute( """ UPDATE accounts SET otp=NULL, otp_expire=NULL, otp_count=0 WHERE email=%s """, (data["Email"],),)
        self.conn.commit()

        send_welcome_email(data["Email"], account_id, data["Username"])
        from pages.login_page import LoginPage
        self.master.clear_window()
        LoginPage(self.master)

    def start_timer(self):
        if self.time_left > 0:
            self.timer_label.configure(text=f"Time left: {self.time_left}s")
            self.time_left -= 1
            self.after(1000, self.start_timer)
        else:
            self.timer_label.configure(text="OTP expired ❌")
            self.resend_btn.configure(state="normal")

    def resend_otp(self):

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute( """ SELECT otp_count FROM accounts WHERE email=%s """, (self.reg.temp_data["Email"],),)

        row = cursor.fetchone()
        if row and row["otp_count"] >= 3:
            messagebox.showerror("Limit", "Max resend limit reached")
            return

        new_otp = str(random.randint(100000, 999999))
        expire_time = datetime.now() + timedelta(minutes=2)

        cursor.execute(
            """ UPDATE accounts SET otp=%s, otp_expire=%s, otp_count=otp_count+1 WHERE email=%s """,
              (new_otp, expire_time, self.reg.temp_data["Email"]),)
        self.conn.commit()

        if send_otp(self.reg.temp_data["Email"], new_otp):
            messagebox.showinfo("Success", "New OTP sent")
            self.time_left = 120
            self.resend_btn.configure(state="disabled")
            self.start_timer()

            for box in self.otp_boxes:
                box.delete(0, "end")

        else:
            messagebox.showerror("Error", "Failed to resend OTP")

    def animate_car(self):
        if not hasattr(self, "car"):
            return

        x = self.car.winfo_x()
        width = self.car.master.winfo_width()
        if x > width:
            return

        self.car.place(x=x + 1, y=20)

        # smooth speed
        self.after(40, self.animate_car)
