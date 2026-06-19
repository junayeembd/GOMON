import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from database import check_password, hash_password
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AdminDashboard(ctk.CTkFrame):

    def __init__(self, master, admin_id):

        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.master = master
        self.conn = master.conn
        self.admin_id = admin_id
        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """ SELECT permissions, account_status FROM admin_info WHERE account_id=%s """,
            (self.admin_id,),
        )

        admin_info = cursor.fetchone()

        self.permissions = admin_info["permissions"].lower() if admin_info else ""
        if admin_info and admin_info["account_status"] == "suspended":
            messagebox.showerror(
                "Access Denied", "Your account has been suspended by Super Admin."
            )

            from pages.login_page import LoginPage

            self.master.clear_window()
            LoginPage(self.master)
            return

        self.build_ui()

    def build_ui(self):

        top = ctk.CTkFrame(self, height=60)
        top.pack(fill="x")

        ctk.CTkLabel(top, text="🛠 Admin Dashboard", font=("Arial", 22, "bold")).pack(
            side="left", padx=20
        )
        self.time = ctk.CTkLabel(top)
        self.time.pack(side="right", padx=20)

        self.update_time()
        main = ctk.CTkScrollableFrame(self)
        main.pack(fill="both", expand=True)
        sidebar = ctk.CTkFrame(main, width=200)
        sidebar.pack(side="left", fill="y")

        menus = [("🏠 Home", self.show_home)]
        if "users" in self.permissions:
            menus.append(("👥 Manage Users", self.show_users))
        if "drivers" in self.permissions:
            menus.append(("🚗 Manage Drivers", self.show_drivers))
        if "admins" in self.permissions:
            menus.append(("👤👤 Manage Admins", self.show_admins))
        if "rides" in self.permissions or "monitor" in self.permissions:
            menus.append(("📍 Ride Monitoring", self.show_rides))
        if "earnings" in self.permissions:
            menus.append(("💰 Earnings", self.show_earnings))
        if "reports" in self.permissions:
            menus.append(("📄 Reports", self.show_reports))
        if "analytics" in self.permissions:
            menus.append(("📊 Analytics", self.show_analytics))
        if "support" in self.permissions:
            menus.append(("🎧 Customer Support", self.show_support))
        if "driver_support" in self.permissions:
            menus.append(("🚗 Driver Support", self.show_driver_support))
        if "user_support" in self.permissions:
            menus.append(("👤 User Support", self.show_user_support))
        if "complaints" in self.permissions:
            menus.append(("⚠ Complaint Management", self.show_complaints))
        if "fraud" in self.permissions:
            menus.append(("🛡 Fraud Detection", self.show_fraud))
        if "security" in self.permissions:
            menus.append(("🔐 Security Control", self.show_security))
        if "system" in self.permissions:
            menus.append(("⚙ System Settings", self.show_system_settings))
        if "maintenance" in self.permissions:
            menus.append(("🛠 Maintenance", self.show_maintenance))

        menus.extend(
            [
                ("👤 My Profile", self.show_profile),
                ("🔒 Change Password", self.change_password_ui),
                ("🚪 Logout", self.logout),
            ]
        )

        for name, cmd in menus:
            ctk.CTkButton(sidebar, text=name, width=180, height=40, command=cmd).pack(
                pady=6
            )
        self.content = ctk.CTkScrollableFrame(main)
        self.content.pack(side="right", fill="both", expand=True)

        self.show_home()

    def update_time(self):
        now = datetime.now().strftime("%d %B %Y | %H:%M:%S")
        self.time.configure(text=now)

        self.after(1000, self.update_time)

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_home(self):

        self.clear()
        ctk.CTkLabel(
            self.content, text="Welcome Admin", font=("Arial", 28, "bold")
        ).pack(pady=(20, 10))
        ctk.CTkLabel(
            self.content,
            text="Only sections allowed by Super Admin are visible.",
            font=("Arial", 14),
        ).pack(pady=(0, 20))

        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role='user'")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM driver_info")
        total_drivers = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rides")
        total_rides = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM rides WHERE ride_status='completed'")
        completed = cursor.fetchone()[0]

        cards = []

        if "users" in self.permissions:
            cards.append(("👤 Users", total_users, "Manage all users"))
        if "drivers" in self.permissions:
            cards.append(("🚗 Drivers", total_drivers, "Manage all drivers"))
        if "rides" in self.permissions:
            cards.append(("📍 Total Rides", total_rides, "All ride records"))
        if "analytics" in self.permissions:
            cards.append(("✅ Completed", completed, "Finished rides"))

        card_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        card_frame.pack(pady=20)

        for i, (title, value, desc) in enumerate(cards):
            card = ctk.CTkFrame(card_frame, width=220, height=130)
            card.grid(row=i // 2, column=i % 2, padx=15, pady=15)
            ctk.CTkLabel(card, text=title, font=("Arial", 18, "bold")).pack(
                pady=(20, 5)
            )
            ctk.CTkLabel(card, text=str(value), font=("Arial", 28, "bold")).pack()
            ctk.CTkLabel(card, text=desc, font=("Arial", 12)).pack(pady=(5, 10))

        quick = ctk.CTkFrame(self.content)
        quick.pack(pady=25, padx=20, fill="x")
        ctk.CTkLabel(quick, text="Quick Access", font=("Arial", 20, "bold")).pack(
            pady=10
        )

        if "users" in self.permissions:
            ctk.CTkButton(quick, text="👥 Manage Users", command=self.show_users).pack(
                pady=5
            )

        if "drivers" in self.permissions:
            ctk.CTkButton(
                quick, text="🚗 Manage Drivers", command=self.show_drivers
            ).pack(pady=5)

        if "rides" in self.permissions:
            ctk.CTkButton(quick, text="📍 View Rides", command=self.show_rides).pack(
                pady=5
            )

        if "earnings" in self.permissions:
            ctk.CTkButton(
                quick, text="💰 View Earnings", command=self.show_earnings
            ).pack(pady=5)

    def show_users(self):
        if not self.has_permission("users"):
            return
        self.clear()

        ctk.CTkLabel(
            self.content, text="Manage Users", font=("Arial", 24, "bold")
        ).pack(pady=15)
        top = ctk.CTkFrame(self.content)
        top.pack(fill="x", padx=20, pady=10)
        self.user_search = ctk.CTkEntry(
            top, width=300, placeholder_text="Search name / username / email / phone"
        )
        self.user_search.pack(side="left", padx=10)
        ctk.CTkButton(top, text="Search", command=self.load_users).pack(
            side="left", padx=5
        )
        ctk.CTkButton(
            top,
            text="Refresh",
            command=lambda: [self.user_search.delete(0, "end"), self.load_users()],
        ).pack(side="left", padx=5)

        self.user_table = ctk.CTkScrollableFrame(self.content, width=1100, height=500)
        self.user_table.pack(padx=20, pady=10, fill="both", expand=True)
        self.load_users()

    def load_users(self):
        for w in self.user_table.winfo_children():
            w.destroy()

        search = self.user_search.get().strip()
        cursor = self.conn.cursor(dictionary=True)

        query = """ SELECT id, name, username, email, phone, address, status FROM accounts WHERE role='user' """

        params = []
        if search:
            query += """ AND (name LIKE %s OR username LIKE %s OR email LIKE %s OR phone LIKE %s)"""
            like = f"%{search}%"
            params.extend([like, like, like, like])

        query += " ORDER BY id DESC"

        cursor.execute(query, tuple(params))
        users = cursor.fetchall()

        headers = ["Name", "Username", "Email", "Phone", "Status", "Edit", "Delete"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(self.user_table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=10, pady=10
            )

        for r, row in enumerate(users, start=1):
            ctk.CTkLabel(self.user_table, text=row["name"]).grid(
                row=r, column=0, padx=10
            )
            ctk.CTkLabel(self.user_table, text=row["username"]).grid(
                row=r, column=1, padx=10
            )
            ctk.CTkLabel(self.user_table, text=row["email"]).grid(
                row=r, column=2, padx=10
            )
            ctk.CTkLabel(self.user_table, text=row["phone"]).grid(
                row=r, column=3, padx=10
            )
            ctk.CTkLabel(self.user_table, text=row["status"]).grid(
                row=r, column=4, padx=10
            )
            ctk.CTkButton(
                self.user_table,
                text="Edit",
                width=70,
                command=lambda uid=row["id"]: self.edit_user(uid),
            ).grid(row=r, column=5, padx=5)
            ctk.CTkButton(
                self.user_table,
                text="Delete",
                width=70,
                fg_color="red",
                command=lambda uid=row["id"]: self.delete_user(uid),
            ).grid(row=r, column=6, padx=5)

    def edit_user(self, user_id):

        if not self.has_permission("users"):
            return

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT id,name,username,email,phone,address,status
        FROM accounts
        WHERE id=%s AND role='user'
        """,
            (user_id,),
        )

        user = cursor.fetchone()

        ctk.CTkLabel(self.content, text="Edit User", font=("Arial", 24, "bold")).pack(
            pady=20
        )

        form = ctk.CTkFrame(self.content)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Name").pack(anchor="w")
        self.u_name = ctk.CTkEntry(form, width=350)
        self.u_name.insert(0, user["name"])
        self.u_name.pack(pady=5)

        ctk.CTkLabel(form, text="Username").pack(anchor="w")
        self.u_username = ctk.CTkEntry(form, width=350)
        self.u_username.insert(0, user["username"])
        self.u_username.pack(pady=5)

        ctk.CTkLabel(form, text="Email").pack(anchor="w")
        self.u_email = ctk.CTkEntry(form, width=350)
        self.u_email.insert(0, user["email"])
        self.u_email.pack(pady=5)

        ctk.CTkLabel(form, text="Phone").pack(anchor="w")
        self.u_phone = ctk.CTkEntry(form, width=350)
        self.u_phone.insert(0, user["phone"])
        self.u_phone.pack(pady=5)

        ctk.CTkLabel(form, text="Address").pack(anchor="w")
        self.u_address = ctk.CTkEntry(form, width=350)
        self.u_address.insert(0, user["address"])
        self.u_address.pack(pady=5)

        ctk.CTkLabel(form, text="Status").pack(anchor="w")
        self.u_status = ctk.CTkOptionMenu(
            form, width=350, values=["active", "inactive", "blocked"]
        )
        self.u_status.pack(pady=5)
        self.u_status.set(user["status"])

        ctk.CTkButton(
            form, text="Update User", command=lambda: self.update_user(user_id)
        ).pack(pady=20)

        ctk.CTkButton(form, text="⬅ Back", command=self.show_users).pack()

    def update_user(self, user_id):

        name = self.u_name.get().strip()
        username = self.u_username.get().strip()
        email = self.u_email.get().strip()
        phone = self.u_phone.get().strip()
        address = self.u_address.get().strip()
        status = self.u_status.get()

        if not all([name, username, email, phone]):
            messagebox.showerror("Error", "All fields are required")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT id,username,email,phone
        FROM accounts
        WHERE id!=%s
        AND (
        username=%s OR
        email=%s OR
        phone=%s
        )
        """,
            (user_id, username, email, phone),
        )

        duplicate = cursor.fetchone()

        if duplicate:

            if duplicate["username"] == username:
                messagebox.showerror("Error", "Username already exists")
                return

            if duplicate["email"] == email:
                messagebox.showerror("Error", "Email already exists")
                return

            if duplicate["phone"] == phone:
                messagebox.showerror("Error", "Phone number already exists")
                return

        cursor.execute(
            """
        UPDATE accounts
        SET name=%s,
        username=%s,
        email=%s,
        phone=%s,
        address=%s,
        status=%s
        WHERE id=%s
        """,
            (name, username, email, phone, address, status, user_id),
        )

        self.conn.commit()

        messagebox.showinfo("Success", "User updated successfully")

        self.show_users()

    def delete_user(self, user_id):

        confirm = messagebox.askyesno(
            "Delete User", "Are you sure you want to delete this user?"
        )

        if not confirm:
            return
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM accounts WHERE id=%s", (user_id,))
        self.conn.commit()
        messagebox.showinfo("Deleted", "User removed successfully")
        self.show_users()

    def show_drivers(self):

        self.clear()
        search_frame = ctk.CTkFrame(self.content)
        search_frame.pack(pady=10)
        self.search = ctk.CTkEntry(
            search_frame, placeholder_text="Search driver...", width=300
        )
        self.search.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Search", command=self.search_driver).pack(
            side="left"
        )
        ctk.CTkLabel(
            self.content, text="Manage Drivers", font=("Arial", 24, "bold")
        ).pack(pady=20)

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            """ SELECT a.id,a.name,a.username, d.vehicle_type,d.vehicle_number FROM accounts a JOIN driver_info d ON a.id=d.account_id """
        )

        drivers = cursor.fetchall()
        table = ctk.CTkScrollableFrame(self.content, width=900, height=400)
        table.pack()

        headers = ["Name", "Username", "Vehicle", "Vehicle No", "Edit", "Delete"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=20
            )
        for r, row in enumerate(drivers, start=1):

            ctk.CTkLabel(table, text=row["name"]).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["username"]).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["vehicle_type"]).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["vehicle_number"]).grid(row=r, column=3)
            ctk.CTkButton(
                table,
                text="Edit",
                width=70,
                command=lambda did=row["id"]: self.edit_driver(did),
            ).grid(row=r, column=4, padx=5)
            ctk.CTkButton(
                table,
                text="Delete",
                width=70,
                fg_color="red",
                command=lambda did=row["id"]: self.delete_driver(did),
            ).grid(row=r, column=5, padx=5)

    def search_driver(self):

        search = self.search.get().strip()

        cursor = self.conn.cursor(dictionary=True)

        query = """
        SELECT a.id,a.name,a.username,d.vehicle_type,d.vehicle_number
        FROM accounts a
        JOIN driver_info d ON a.id=d.account_id
        WHERE (
        a.name LIKE %s OR
        a.username LIKE %s OR
        d.vehicle_type LIKE %s OR
        d.vehicle_number LIKE %s
        )
        """

        like = f"%{search}%"

        cursor.execute(query, (like, like, like, like))
        drivers = cursor.fetchall()

        self.clear()

        ctk.CTkLabel(
            self.content, text="Manage Drivers", font=("Arial", 24, "bold")
        ).pack(pady=20)

        table = ctk.CTkScrollableFrame(self.content, width=1000, height=450)
        table.pack(pady=10)

        headers = ["Name", "Username", "Vehicle", "Vehicle No", "Edit", "Delete"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=15, pady=10
            )

        for r, row in enumerate(drivers, start=1):
            ctk.CTkLabel(table, text=row["name"]).grid(row=r, column=0, padx=10)
            ctk.CTkLabel(table, text=row["username"]).grid(row=r, column=1, padx=10)
            ctk.CTkLabel(table, text=row["vehicle_type"]).grid(row=r, column=2, padx=10)
            ctk.CTkLabel(table, text=row["vehicle_number"]).grid(
                row=r, column=3, padx=10
            )

            ctk.CTkButton(
                table,
                text="Edit",
                width=70,
                command=lambda did=row["id"]: self.edit_driver(did),
            ).grid(row=r, column=4, padx=5)

            ctk.CTkButton(
                table,
                text="Delete",
                width=70,
                fg_color="red",
                command=lambda did=row["id"]: self.delete_driver(did),
            ).grid(row=r, column=5, padx=5)

    def edit_driver(self, driver_id):

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT a.name,a.username,a.email,a.phone,a.address,d.nid,d.driving_license,
            d.vehicle_type,d.vehicle_number,d.work_time
            FROM accounts a
            JOIN driver_info d ON a.id=d.account_id
            WHERE a.id=%s
        """,
            (driver_id,),
        )

        driver = cursor.fetchone()

        ctk.CTkLabel(self.content, text="Edit Driver", font=("Arial", 24, "bold")).pack(
            pady=20
        )

        d_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        d_frame.pack(pady=5)
        ctk.CTkLabel(d_frame, text="Name").pack(anchor="w")
        self.d_name = ctk.CTkEntry(d_frame, width=350)
        self.d_name.insert(0, driver["name"])
        self.d_name.pack()

        ctk.CTkLabel(d_frame, text="Username").pack(anchor="w")
        self.d_username = ctk.CTkEntry(d_frame, width=350)
        self.d_username.insert(0, driver["username"])
        self.d_username.pack()

        ctk.CTkLabel(d_frame, text="Email").pack(anchor="w")
        self.d_email = ctk.CTkEntry(d_frame, width=350)
        self.d_email.insert(0, driver["email"])
        self.d_email.pack()

        ctk.CTkLabel(d_frame, text="Phone").pack(anchor="w")
        self.d_phone = ctk.CTkEntry(d_frame, width=350)
        self.d_phone.insert(0, driver["phone"])
        self.d_phone.pack()

        ctk.CTkLabel(d_frame, text="Address").pack(anchor="w")
        self.d_address = ctk.CTkEntry(d_frame, width=350)
        self.d_address.insert(0, driver["address"])
        self.d_address.pack()

        ctk.CTkLabel(d_frame, text="NID No").pack(anchor="w")
        self.d_nid = ctk.CTkEntry(d_frame, width=350)
        self.d_nid.insert(0, driver["nid"])
        self.d_nid.pack()

        ctk.CTkLabel(d_frame, text="Driving License").pack(anchor="w")
        self.d_license = ctk.CTkEntry(d_frame, width=350)
        self.d_license.insert(0, driver["driving_license"])
        self.d_license.pack()

        ctk.CTkLabel(d_frame, text="Vehicle Type").pack(anchor="w")
        self.vehicle = ctk.CTkOptionMenu(
            d_frame, width=350, values=["Bike", "CNG", "Private Car", "Micro"]
        )
        self.vehicle.pack()
        self.vehicle.set(driver["vehicle_type"])

        ctk.CTkLabel(d_frame, text="Vehicle Number").pack(anchor="w")
        self.vehicle_no = ctk.CTkEntry(d_frame, width=350)
        self.vehicle_no.insert(0, driver["vehicle_number"])
        self.vehicle_no.pack()

        ctk.CTkLabel(d_frame, text="Work Time").pack(anchor="w")
        self.d_work = ctk.CTkOptionMenu(
            d_frame, width=350, values=["Part Time", "Full Time"]
        )
        self.d_work.pack()
        self.d_work.set(driver["work_time"])

        ctk.CTkButton(
            self.content,
            text="Update Driver",
            command=lambda: self.update_driver(driver_id),
        ).pack(pady=20)

        ctk.CTkButton(self.content, text="⬅ Back", command=self.show_drivers).pack()

    def update_driver(self, driver_id):

        name = self.d_name.get().strip()
        username = self.d_username.get().strip()
        email = self.d_email.get().strip()
        phone = self.d_phone.get().strip()
        address = self.d_address.get().strip()
        nid = self.d_nid.get().strip()
        license_no = self.d_license.get().strip()
        vehicle_type = self.vehicle.get().strip()
        vehicle_no = self.vehicle_no.get().strip()
        work_time = self.d_work.get().strip()

        if not all(
            [name, username, email, phone, address, nid, license_no, vehicle_no]
        ):
            messagebox.showerror("Error", "All fields are required")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """
        SELECT id FROM accounts WHERE username=%s AND id!=%s """,
            (username, driver_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        cursor.execute(
            """SELECT id FROM accounts WHERE email=%s AND id!=%s """, (email, driver_id)
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Email already exists")
            return

        cursor.execute(
            """ SELECT id FROM accounts WHERE phone=%s AND id!=%s """,
            (phone, driver_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Phone number already exists")
            return

        cursor.execute(
            """SELECT account_id FROM driver_info WHERE nid=%s AND account_id!=%s """,
            (nid, driver_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "NID already exists")
            return

        cursor.execute(
            """SELECT account_id FROM driver_info WHERE driving_license=%s AND account_id!=%s """,
            (license_no, driver_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Driving license already exists")
            return

        cursor.execute(
            """SELECT account_id FROM driver_info WHERE vehicle_number=%s AND account_id!=%s """,
            (vehicle_no, driver_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Vehicle number already exists")
            return

        cursor.execute(
            """UPDATE accounts SET name=%s,username=%s,email=%s,phone=%s,address=%s WHERE id=%s""",
            (name, username, email, phone, address, driver_id),
        )

        cursor.execute(
            """UPDATE driver_info SET nid=%s,driving_license=%s,vehicle_type=%s,vehicle_number=%s,work_time=%s WHERE account_id=%s
            """,
            (nid, license_no, vehicle_type, vehicle_no, work_time, driver_id),
        )

        self.conn.commit()
        messagebox.showinfo("Success", "Driver updated successfully")
        self.show_drivers()

    def delete_driver(self, driver_id):

        confirm = messagebox.askyesno("Confirm", "Delete this driver?")
        if not confirm:
            return
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM driver_info WHERE account_id=%s", (driver_id,))
        cursor.execute("DELETE FROM accounts WHERE id=%s", (driver_id,))
        self.conn.commit()
        messagebox.showinfo("Deleted", "Driver removed")
        self.show_drivers()

    def show_admins(self):

        if not self.has_permission("admins"):
            return
        self.clear()
        ctk.CTkLabel(
            self.content, text="Manage Admins", font=("Arial", 24, "bold")
        ).pack(pady=15)
        top = ctk.CTkFrame(self.content)
        top.pack(fill="x", padx=20, pady=10)

        self.admin_search = ctk.CTkEntry(
            top, width=320, placeholder_text="Search name / username / email / role"
        )
        self.admin_search.pack(side="left", padx=10)

        ctk.CTkButton(top, text="Search", command=self.load_admins).pack(
            side="left", padx=5
        )
        ctk.CTkButton(
            top,
            text="Refresh",
            command=lambda: [self.admin_search.delete(0, "end"), self.load_admins()],
        ).pack(side="left", padx=5)

        self.admin_table = ctk.CTkScrollableFrame(self.content, width=1200, height=500)
        self.admin_table.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_admins()

    def load_admins(self):
        for w in self.admin_table.winfo_children():
            w.destroy()

        search = self.admin_search.get().strip()
        cursor = self.conn.cursor(dictionary=True)

        query = """ SELECT a.id, a.name, a.username, a.email,ai.admin_role, ai.department, ai.account_status
                FROM accounts a JOIN admin_info ai ON a.id=ai.account_id WHERE a.role='admin' """

        params = []

        if search:
            query += """AND (a.name LIKE %s OR a.username LIKE %s OR a.email LIKE %s OR ai.admin_role LIKE %s OR ai.department LIKE %s )"""

            like = f"%{search}%"
            params.extend([like, like, like, like, like])

        query += " ORDER BY a.id DESC"

        cursor.execute(query, tuple(params))
        admins = cursor.fetchall()

        headers = [
            "Name",
            "Username",
            "Email",
            "Role",
            "Department",
            "Status",
            "Edit",
            "Delete",
        ]

        for i, h in enumerate(headers):
            ctk.CTkLabel(self.admin_table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=10, pady=10
            )

        for r, row in enumerate(admins, start=1):
            ctk.CTkLabel(self.admin_table, text=row["name"]).grid(
                row=r, column=0, padx=10
            )
            ctk.CTkLabel(self.admin_table, text=row["username"]).grid(
                row=r, column=1, padx=10
            )
            ctk.CTkLabel(self.admin_table, text=row["email"]).grid(
                row=r, column=2, padx=10
            )
            ctk.CTkLabel(self.admin_table, text=row["admin_role"]).grid(
                row=r, column=3, padx=10
            )
            ctk.CTkLabel(self.admin_table, text=row["department"]).grid(
                row=r, column=4, padx=10
            )

            color = "green" if row["account_status"] == "active" else "red"

            ctk.CTkLabel(
                self.admin_table, text=row["account_status"], text_color=color
            ).grid(row=r, column=5, padx=10)
            ctk.CTkButton(
                self.admin_table,
                text="Edit",
                width=70,
                command=lambda aid=row["id"]: self.edit_admin(aid),
            ).grid(row=r, column=6, padx=5)
            ctk.CTkButton(
                self.admin_table,
                text="Delete",
                width=70,
                fg_color="red",
                command=lambda aid=row["id"]: self.delete_admin(aid),
            ).grid(row=r, column=7, padx=5)

    def edit_admin(self, admin_id):

        if not self.has_permission("admins"):
            return

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT a.name,a.username,a.email,a.phone,a.address,
           ai.employee_id,ai.department,ai.admin_role,ai.permissions,ai.account_status
        FROM accounts a
        JOIN admin_info ai ON a.id=ai.account_id
        WHERE a.id=%s
        """,
            (admin_id,),
        )

        admin = cursor.fetchone()

        ctk.CTkLabel(self.content, text="Edit Admin", font=("Arial", 24, "bold")).pack(
            pady=20
        )

        form = ctk.CTkFrame(self.content)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Name").pack(anchor="w")
        self.a_name = ctk.CTkEntry(form, width=350)
        self.a_name.insert(0, admin["name"])
        self.a_name.pack(pady=5)

        ctk.CTkLabel(form, text="Username").pack(anchor="w")
        self.a_username = ctk.CTkEntry(form, width=350)
        self.a_username.insert(0, admin["username"])
        self.a_username.pack(pady=5)

        ctk.CTkLabel(form, text="Email").pack(anchor="w")
        self.a_email = ctk.CTkEntry(form, width=350)
        self.a_email.insert(0, admin["email"])
        self.a_email.pack(pady=5)

        ctk.CTkLabel(form, text="Phone").pack(anchor="w")
        self.a_phone = ctk.CTkEntry(form, width=350)
        self.a_phone.insert(0, admin["phone"])
        self.a_phone.pack(pady=5)

        ctk.CTkLabel(form, text="Address").pack(anchor="w")
        self.a_address = ctk.CTkEntry(form, width=350)
        self.a_address.insert(0, admin["address"])
        self.a_address.pack(pady=5)

        ctk.CTkLabel(form, text="Employee ID").pack(anchor="w")
        self.a_emp = ctk.CTkEntry(form, width=350)
        self.a_emp.insert(0, admin["employee_id"])
        self.a_emp.pack(pady=5)

        ctk.CTkLabel(form, text="Department").pack(anchor="w")
        self.a_department = ctk.CTkOptionMenu(
            form,
            width=350,
            values=[
                "Operations",
                "Customer Support",
                "User Management",
                "Driver Management",
                "Ride Monitoring",
                "Finance",
                "Accounts",
                "Technical Support",
                "IT",
                "System Administration",
                "Security",
                "Fraud Detection",
                "Emergency Response",
                "Human Resources",
                "Marketing",
                "Analytics",
                "Complaint Management",
            ],
        )
        self.a_department.pack(pady=5)
        self.a_department.set(admin["department"])

        ctk.CTkLabel(form, text="Admin Role").pack(anchor="w")
        self.a_role = ctk.CTkOptionMenu(
            form,
            width=350,
            values=[
                "Manager",
                "Support",
                "Customer Support",
                "User Support",
                "Driver Support",
                "Finance",
                "Moderator",
                "Operations Manager",
                "Ride Monitoring",
                "User Manager",
                "Driver Manager",
                "Technical Support",
                "System Admin",
                "Security Officer",
                "Fraud Analyst",
                "HR",
                "Marketing",
                "Analytics",
            ],
        )
        self.a_role.pack(pady=5)
        self.a_role.set(admin["admin_role"])

        ctk.CTkLabel(form, text="Permissions").pack(anchor="w")

        perm_frame = ctk.CTkFrame(self.content)
        perm_frame.pack()

        self.user_perm = ctk.CTkCheckBox(perm_frame, text="Manage Users")
        self.user_perm.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.driver_perm = ctk.CTkCheckBox(perm_frame, text="Manage Drivers")
        self.driver_perm.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.admin_perm = ctk.CTkCheckBox(perm_frame, text="Manage Admins")
        self.admin_perm.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.ride_perm = ctk.CTkCheckBox(perm_frame, text="Manage Rides")
        self.ride_perm.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.monitor_perm = ctk.CTkCheckBox(perm_frame, text="Ride Monitoring")
        self.monitor_perm.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.earn_perm = ctk.CTkCheckBox(perm_frame, text="View Earnings")
        self.earn_perm.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.payment_perm = ctk.CTkCheckBox(perm_frame, text="Manage Payments")
        self.payment_perm.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.report_perm = ctk.CTkCheckBox(perm_frame, text="View Reports")
        self.report_perm.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.analytics_perm = ctk.CTkCheckBox(perm_frame, text="View Analytics")
        self.analytics_perm.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        self.support_perm = ctk.CTkCheckBox(perm_frame, text="Customer Support Access")
        self.support_perm.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.driver_support_perm = ctk.CTkCheckBox(
            perm_frame, text="Driver Support Access"
        )
        self.driver_support_perm.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.user_support_perm = ctk.CTkCheckBox(perm_frame, text="User Support Access")
        self.user_support_perm.grid(row=3, column=2, padx=10, pady=5, sticky="w")

        self.complaint_perm = ctk.CTkCheckBox(perm_frame, text="Complaint Management")
        self.complaint_perm.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.fraud_perm = ctk.CTkCheckBox(perm_frame, text="Fraud Detection")
        self.fraud_perm.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self.security_perm = ctk.CTkCheckBox(perm_frame, text="Security Control")
        self.security_perm.grid(row=4, column=2, padx=10, pady=5, sticky="w")

        self.system_perm = ctk.CTkCheckBox(perm_frame, text="System Settings")
        self.system_perm.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.maintenance_perm = ctk.CTkCheckBox(perm_frame, text="Maintenance Mode")
        self.maintenance_perm.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        if "users" in admin["permissions"]:
            self.user_perm.select()

        if "drivers" in admin["permissions"]:
            self.driver_perm.select()

        if "admins" in admin["permissions"]:
            self.admin_perm.select()

        if "rides" in admin["permissions"]:
            self.ride_perm.select()

        if "monitor" in admin["permissions"]:
            self.monitor_perm.select()

        if "earnings" in admin["permissions"]:
            self.earn_perm.select()

        if "payments" in admin["permissions"]:
            self.payment_perm.select()

        if "reports" in admin["permissions"]:
            self.report_perm.select()

        if "analytics" in admin["permissions"]:
            self.analytics_perm.select()

        if "support" in admin["permissions"]:
            self.support_perm.select()

        if "driver_support" in admin["permissions"]:
            self.driver_support_perm.select()

        if "user_support" in admin["permissions"]:
            self.user_support_perm.select()

        if "complaints" in admin["permissions"]:
            self.complaint_perm.select()

        if "fraud" in admin["permissions"]:
            self.fraud_perm.select()

        if "security" in admin["permissions"]:
            self.security_perm.select()

        if "system" in admin["permissions"]:
            self.system_perm.select()

        if "maintenance" in admin["permissions"]:
            self.maintenance_perm.select()

        ctk.CTkLabel(form, text="Account Status").pack(anchor="w")

        self.a_status = ctk.CTkOptionMenu(
            form, width=350, values=["active", "suspended"]
        )
        self.a_status.pack(pady=5)
        self.a_status.set(admin["account_status"])

        ctk.CTkButton(
            form, text="Update Admin", command=lambda: self.update_admin(admin_id)
        ).pack(pady=20)

        ctk.CTkButton(
            self.content, text="⬅ Back", fg_color="gray", command=self.show_admins
        ).pack(pady=5)

    def update_admin(self, admin_id):

        name = self.a_name.get().strip()
        username = self.a_username.get().strip()
        email = self.a_email.get().strip()
        phone = self.a_phone.get().strip()
        address = self.a_address.get().strip()
        employee_id = self.a_emp.get().strip()
        department = self.a_department.get().strip()
        role = self.a_role.get().strip()
        status = self.a_status.get()

        permissions = []

        if self.user_perm.get():
            permissions.append("users")

        if self.driver_perm.get():
            permissions.append("drivers")

        if self.admin_perm.get():
            permissions.append("admins")

        if self.ride_perm.get():
            permissions.append("rides")

        if self.monitor_perm.get():
            permissions.append("monitor")

        if self.earn_perm.get():
            permissions.append("earnings")

        if self.payment_perm.get():
            permissions.append("payments")

        if self.report_perm.get():
            permissions.append("reports")

        if self.analytics_perm.get():
            permissions.append("analytics")

        if self.support_perm.get():
            permissions.append("support")

        if self.driver_support_perm.get():
            permissions.append("driver_support")

        if self.user_support_perm.get():
            permissions.append("user_support")

        if self.complaint_perm.get():
            permissions.append("complaints")

        if self.fraud_perm.get():
            permissions.append("fraud")

        if self.security_perm.get():
            permissions.append("security")

        if self.system_perm.get():
            permissions.append("system")

        if self.maintenance_perm.get():
            permissions.append("maintenance")

        perm_text = " | ".join(permissions)

        if not all([name, username, email, phone]):
            messagebox.showerror("Error", "All required fields must be filled")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT id
        FROM accounts
        WHERE id != %s
        AND (
        username=%s OR
        email=%s OR
        phone=%s
        )
        """,
            (admin_id, username, email, phone),
        )

        duplicate = cursor.fetchone()

        if duplicate:
            messagebox.showerror("Duplicate", "Username, email or phone already exists")
            return
        cursor.execute(
            """ SELECT account_id FROM admin_info WHERE employee_id=%s AND account_id!=%s """,
            (employee_id, admin_id),
        )

        if cursor.fetchone():
            messagebox.showerror("Error", "Employee ID already exists")
            return

        cursor.execute(
            """
        UPDATE accounts
        SET name=%s, username=%s, email=%s, phone=%s, address=%s
        WHERE id=%s
        """,
            (name, username, email, phone, address, admin_id),
        )

        cursor.execute(
            """
        UPDATE admin_info
        SET employee_id=%s,department=%s,
        admin_role=%s,
        permissions=%s,
        account_status=%s
        WHERE account_id=%s
        """,
            (employee_id, department, role, perm_text, status, admin_id),
        )

        self.conn.commit()

        messagebox.showinfo("Success", "Admin updated successfully")

        self.show_admins()

    def delete_admin(self, admin_id):

        if not self.has_permission("admins"):
            return
        if admin_id == self.admin_id:
            messagebox.showerror("Error", "You cannot delete your own account")
            return
        confirm = messagebox.askyesno(
            "Delete Admin", "Are you sure you want to delete this admin?"
        )
        if not confirm:
            return

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM admin_info WHERE account_id=%s", (admin_id,))
        cursor.execute("DELETE FROM accounts WHERE id=%s", (admin_id,))

        self.conn.commit()
        messagebox.showinfo("Success", "Admin deleted successfully")
        self.load_admins()

    def show_rides(self):

        self.clear()
        ctk.CTkLabel(
            self.content, text="Ride Monitoring", font=("Arial", 24, "bold")
        ).pack(pady=15)
        top = ctk.CTkFrame(self.content)
        top.pack(fill="x", padx=20, pady=10)

        self.ride_status_filter = ctk.CTkOptionMenu(
            top,
            values=[
                "All",
                "searching",
                "accepted",
                "started",
                "completed",
                "cancelled",
            ],
        )
        self.ride_status_filter.pack(side="left", padx=10)
        self.ride_status_filter.set("All")
        ctk.CTkButton(top, text="Apply", command=self.load_rides).pack(side="left")

        self.ride_table = ctk.CTkScrollableFrame(self.content, width=1150, height=500)
        self.ride_table.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_rides()

    def load_rides(self):

        for w in self.ride_table.winfo_children():
            w.destroy()

        status = self.ride_status_filter.get()

        cursor = self.conn.cursor(dictionary=True)

        query = """ SELECT id, pickup, drop_location, vehicle_type, fare, ride_status FROM rides """

        params = []

        if status != "All":
            query += " WHERE ride_status=%s"
            params.append(status)

        query += " ORDER BY id DESC"
        cursor.execute(query, tuple(params))
        rides = cursor.fetchall()
        headers = ["ID", "Pickup", "Destination", "Vehicle", "Fare", "Status"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(self.ride_table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=10, pady=10
            )
        for r, row in enumerate(rides, start=1):
            ctk.CTkLabel(self.ride_table, text=row["id"]).grid(row=r, column=0)
            ctk.CTkLabel(self.ride_table, text=row["pickup"]).grid(row=r, column=1)
            ctk.CTkLabel(self.ride_table, text=row["drop_location"]).grid(
                row=r, column=2
            )
            ctk.CTkLabel(self.ride_table, text=row["vehicle_type"]).grid(
                row=r, column=3
            )
            ctk.CTkLabel(self.ride_table, text=row["fare"]).grid(row=r, column=4)
            ctk.CTkLabel(self.ride_table, text=row["ride_status"]).grid(row=r, column=5)

    def show_earnings(self):
        if not self.has_permission("earnings"):
            return

        self.clear()
        ctk.CTkLabel(
            self.content, text="Earnings Dashboard", font=("Arial", 26, "bold")
        ).pack(pady=15)
        top = ctk.CTkFrame(self.content)
        top.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(top, text="Filter:").pack(side="left", padx=10)
        self.earn_filter = ctk.CTkOptionMenu(
            top,
            values=["Today", "This Week", "This Month", "All Time"],
            command=lambda x: self.load_earnings(),
        )
        self.earn_filter.pack(side="left")
        self.earn_filter.set("All Time")
        self.earn_summary = ctk.CTkFrame(self.content)
        self.earn_summary.pack(fill="x", padx=20, pady=10)

        self.earn_graph = ctk.CTkFrame(self.content)
        self.earn_graph.pack(fill="x", padx=20, pady=10)
        self.earn_table = ctk.CTkScrollableFrame(self.content, width=1100, height=300)
        self.earn_table.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_earnings()

    def load_earnings(self):
        for w in self.earn_summary.winfo_children():
            w.destroy()
        for w in self.earn_graph.winfo_children():
            w.destroy()
        for w in self.earn_table.winfo_children():
            w.destroy()
        cursor = self.conn.cursor(dictionary=True)
        condition = ""
        value = self.earn_filter.get()

        if value == "Today":
            condition = "AND DATE(created_at)=CURDATE()"
        elif value == "This Week":
            condition = "AND YEARWEEK(created_at,1)=YEARWEEK(CURDATE(),1)"
        elif value == "This Month":
            condition = "AND MONTH(created_at)=MONTH(CURDATE()) AND YEAR(created_at)=YEAR(CURDATE())"
        cursor.execute(
            f""" SELECT fare, created_at FROM rides WHERE ride_status='completed' {condition} ORDER BY created_at DESC """
        )

        rides = cursor.fetchall()

        total = sum(float(r["fare"]) for r in rides)
        trips = len(rides)
        avg = round(total / trips, 2) if trips else 0

        stats = [
            ("💰 Total Earnings", f"{total:.2f} BDT"),
            ("🚕 Total Trips", trips),
            ("📊 Average Fare", f"{avg} BDT"),
        ]

        for i, (title, val) in enumerate(stats):
            card = ctk.CTkFrame(self.earn_summary, width=220, height=100)
            card.grid(row=0, column=i, padx=15, pady=10)
            ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold")).pack(
                pady=(15, 5)
            )
            ctk.CTkLabel(card, text=str(val), font=("Arial", 22, "bold")).pack()

        if rides:
            latest = rides[:7][::-1]
            x = [r["created_at"].strftime("%d %b") for r in latest]
            y = [float(r["fare"]) for r in latest]

            fig, ax = plt.subplots(figsize=(7, 3))
            ax.plot(x, y, marker="o")
            ax.set_title("Recent Earnings")
            ax.set_xlabel("Date")
            ax.set_ylabel("Fare")

            canvas = FigureCanvasTkAgg(fig, self.earn_graph)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x")

        headers = ["Date", "Fare", "Status"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(self.earn_table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=20, pady=10
            )

        for r, row in enumerate(rides, start=1):

            ctk.CTkLabel(
                self.earn_table, text=row["created_at"].strftime("%d %b %Y %I:%M %p")
            ).grid(row=r, column=0, padx=10, pady=5)
            ctk.CTkLabel(self.earn_table, text=f"{row['fare']} BDT").grid(
                row=r, column=1, padx=10
            )
            ctk.CTkLabel(self.earn_table, text="Completed", text_color="green").grid(
                row=r, column=2, padx=10
            )

    def show_analytics(self):

        if not self.has_permission("analytics"):
            return

        self.clear()
        ctk.CTkLabel(
            self.content, text="Analytics Dashboard", font=("Arial", 24, "bold")
        ).pack(pady=20)
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM rides WHERE ride_status='completed'")
        completed = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM rides WHERE ride_status='cancelled'")
        cancelled = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(fare) FROM rides WHERE ride_status='completed'")
        avg_fare = cursor.fetchone()[0] or 0

        analytics = [
            ("Completed Rides", completed),
            ("Cancelled Rides", cancelled),
            ("Average Fare", round(avg_fare, 2)),
        ]

        frame = ctk.CTkFrame(self.content)
        frame.pack(pady=20)

        for i, (title, value) in enumerate(analytics):
            card = ctk.CTkFrame(frame, width=220, height=120)
            card.grid(row=0, column=i, padx=15)
            ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold")).pack(
                pady=(20, 10)
            )
            ctk.CTkLabel(card, text=str(value), font=("Arial", 28, "bold")).pack()

    def show_reports(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Reports Section", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_support(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Customer Support Section", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_driver_support(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Driver Support Section", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_user_support(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="User Support Section", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_complaints(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Complaint Management", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_fraud(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Fraud Detection", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_security(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Security Control", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_system_settings(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="System Settings", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_maintenance(self):
        self.clear()
        ctk.CTkLabel(
            self.content, text="Maintenance Panel", font=("Arial", 24, "bold")
        ).pack(pady=20)

    def show_profile(self):

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT a.*, ai.employee_id, ai.department,
                ai.admin_role, ai.permissions, ai.account_status
            FROM accounts a
            JOIN admin_info ai ON a.id = ai.account_id
            WHERE a.id=%s""",
            (self.admin_id,),
        )

        admin = cursor.fetchone()

        ctk.CTkLabel(self.content, text="My Profile", font=("Arial", 24, "bold")).pack(
            pady=20
        )

        form = ctk.CTkFrame(self.content)
        form.pack(pady=10, padx=20)

        ctk.CTkLabel(form, text="Name").pack(anchor="w")
        self.name = ctk.CTkEntry(form, width=350)
        self.name.insert(0, admin["name"])
        self.name.pack(pady=(0, 10))

        ctk.CTkLabel(form, text="Username").pack(anchor="w")
        self.username = ctk.CTkEntry(form, width=350)
        self.username.insert(0, admin["username"])
        self.username.pack(pady=(0, 10))

        ctk.CTkLabel(form, text="Email").pack(anchor="w")
        self.email = ctk.CTkEntry(form, width=350)
        self.email.insert(0, admin["email"])
        self.email.pack(pady=(0, 10))

        ctk.CTkLabel(form, text="Phone Number").pack(anchor="w")
        self.phone = ctk.CTkEntry(form, width=350)
        self.phone.insert(0, admin["phone"])
        self.phone.pack(pady=(0, 10))

        ctk.CTkLabel(form, text="Address").pack(anchor="w")
        self.address = ctk.CTkEntry(form, width=350)
        self.address.insert(0, admin["address"])
        self.address.pack(pady=(0, 20))

        readonly = ctk.CTkFrame(form, fg_color="transparent")
        readonly.pack(fill="x", pady=10)

        def make_readonly(label, value):
            ctk.CTkLabel(readonly, text=label).pack(anchor="w")

            entry = ctk.CTkEntry(readonly, width=350)
            entry.insert(0, value if value else "")
            entry.configure(state="disabled")
            entry.pack(pady=(0, 10))

        make_readonly("Employee ID", admin["employee_id"])
        make_readonly("Department", admin["department"])
        make_readonly("Admin Role", admin["admin_role"])
        make_readonly("Permissions", admin["permissions"])
        make_readonly("Account Status", admin["account_status"])

        ctk.CTkLabel(form, text="Current Password").pack(anchor="w")
        self.profile_password = ctk.CTkEntry(form, width=350, show="*")
        self.profile_password.pack(pady=(0, 20))

        ctk.CTkButton(form, text="Save Changes", command=self.update_profile).pack(
            pady=10
        )

    def update_profile(self):

        name = self.name.get().strip()
        username = self.username.get().strip()
        email = self.email.get().strip()
        phone = self.phone.get().strip()
        address = self.address.get().strip()
        password = self.profile_password.get().strip()

        if not name or not username or not email or not phone:
            messagebox.showerror("Error", "All editable fields are required")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        if not password:
            messagebox.showerror("Error", "Enter your current password to save changes")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT password FROM accounts
            WHERE id=%s""",
            (self.admin_id,),
        )

        admin = cursor.fetchone()

        if not check_password(password, admin["password"]):
            messagebox.showerror("Wrong Password", "Current password is incorrect")
            return

        cursor.execute(
            """
            SELECT id, username, email, phone
            FROM accounts
            WHERE id != %s
            AND (
                username=%s OR
                email=%s OR
                phone=%s
            )""",
            (self.admin_id, username, email, phone),
        )

        duplicate = cursor.fetchone()

        if duplicate:

            if duplicate["username"] == username:
                messagebox.showerror("Username already exists")
                return

            if duplicate["email"] == email:
                messagebox.showerror("Email already exists")
                return

            if duplicate["phone"] == phone:
                messagebox.showerror("Phone number already exists")
                return

        cursor.execute(
            """
            UPDATE accounts
            SET name=%s,username=%s,email=%s,phone=%s,address=%s
            WHERE id=%s""",
            (name, username, email, phone, address, self.admin_id),
        )

        self.conn.commit()

        messagebox.showinfo("Profile updated successfully")

        self.show_profile()

    def change_password_ui(self):

        self.clear()

        ctk.CTkLabel(
            self.content, text="Change Password", font=("Arial", 24, "bold")
        ).pack(pady=20)

        ctk.CTkLabel(self.content, text="Current Password").pack()
        self.old_pass = ctk.CTkEntry(self.content, width=350, show="*")
        self.old_pass.pack(pady=5)

        ctk.CTkLabel(self.content, text="New Password").pack()
        self.new_pass = ctk.CTkEntry(self.content, width=350, show="*")
        self.new_pass.pack(pady=5)

        ctk.CTkLabel(self.content, text="Confirm Password").pack()
        self.confirm_pass = ctk.CTkEntry(self.content, width=350, show="*")
        self.confirm_pass.pack(pady=5)

        ctk.CTkButton(
            self.content, text="Update Password", command=self.update_password
        ).pack(pady=20)

        ctk.CTkButton(
            self.content, text="⬅ Back", fg_color="gray", command=self.show_profile
        ).pack()

    def update_password(self):

        old_password = self.old_pass.get()
        new_password = self.new_pass.get()
        confirm_password = self.confirm_pass.get()

        if not old_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return

        if len(new_password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute("   SELECT password FROM accounts WHERE id=%s", (self.admin_id,))

        admin = cursor.fetchone()

        if not check_password(old_password, admin["password"]):
            messagebox.showerror("Error", "Current password is incorrect")
            return

        new_hashed = hash_password(new_password)

        cursor.execute(
            """
            UPDATE accounts
            SET password=%s WHERE id=%s """,
            (new_hashed, self.admin_id),
        )

        self.conn.commit()

        messagebox.showinfo("Success", "Password updated successfully")

        self.show_profile()

    def has_permission(self, permission):
        permissions = [p.strip() for p in self.permissions.split("|")]

        if permission not in permissions:
            messagebox.showerror(
                "Access Denied", "You do not have permission to access this section."
            )
            return False
        return True

    def logout(self):

        from pages.login_page import LoginPage

        self.master.clear_window()

        LoginPage(self.master)
