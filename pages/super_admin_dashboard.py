import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from database import check_password, hash_password
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.email_sender import send_admin_welcome_email
import random, string


class SuperAdminDashboard(ctk.CTkFrame):

    def __init__(self, master, admin_id):

        super().__init__(master)

        self.pack(fill="both", expand=True)

        self.master = master
        self.conn = master.conn
        self.admin_id = admin_id

        self.build_ui()

    def build_ui(self):

        top = ctk.CTkFrame(self, height=60)
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text="👑 Super Admin Dashboard", font=("Arial", 22, "bold")
        ).pack(side="left", padx=20)

        self.time = ctk.CTkLabel(top)
        self.time.pack(side="right", padx=20)

        self.update_time()

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(main, width=200)
        sidebar.pack(side="left", fill="y")

        menus = [
            ("🏠 Home", self.show_home),
            ("👤 My Profile", self.show_profile),
            ("👥 Manage Users", self.show_users),
            ("🚗 Manage Drivers", self.show_drivers),
            ("📍 Ride Monitoring", self.show_rides),
            ("💰 Earnings Analytics", self.show_earnings),
            ("⚙️ System Control", self.system_control_panel),
            ("➕ Create Admin", self.create_admin_ui),
            ("👥 Manage Admins", self.show_admins),
            ("📊 System Status", self.show_stats),
            ("🚪 Logout", self.logout),
        ]

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

        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role='user'")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM driver_info")
        drivers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role='admin'")
        admins = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM rides")
        rides = cursor.fetchone()[0]

        title = ctk.CTkLabel(
            self.content, text="Super Admin Control Panel", font=("Arial", 28, "bold")
        )
        title.pack(pady=20)
        ctk.CTkLabel(
            self.content, text=f"Welcome Super Admin", font=("Arial", 16)
        ).pack(pady=5)

        cards_frame = ctk.CTkFrame(self.content)
        cards_frame.pack(pady=20)

        stats = [
            ("👤 Users", users),
            ("🚗 Drivers", drivers),
            ("🛠 Admins", admins),
            ("🧾 Total Rides", rides),
        ]

        for i, (text, value) in enumerate(stats):

            card = ctk.CTkFrame(cards_frame, width=180, height=100)
            card.grid(row=0, column=i, padx=15)

            ctk.CTkLabel(card, text=text, font=("Arial", 14)).pack(pady=10)
            ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold")).pack()
        self.show_graphs()

    def show_graphs(self):

        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role='user'")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role='driver'")
        drivers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role='admin'")
        admins = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT ride_status, COUNT(*)
            FROM rides
            GROUP BY ride_status
        """
        )

        ride_data = cursor.fetchall()

        statuses = [r[0] for r in ride_data]
        counts = [r[1] for r in ride_data]

        cursor.execute(
            """
            SELECT DATE(created_at), SUM(fare)
            FROM rides
            WHERE ride_status='completed'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """
        )

        earnings = cursor.fetchall()

        dates = [e[0] for e in earnings]
        amounts = [e[1] for e in earnings]

        graph_frame = ctk.CTkFrame(self.content)
        graph_frame.pack(pady=20)

        fig1 = plt.Figure(figsize=(4, 3), dpi=100)
        ax1 = fig1.add_subplot(111)

        labels = ["Users", "Drivers", "Admins"]
        values = [users, drivers, admins]

        ax1.bar(labels, values)
        ax1.set_title("System Users Overview")

        canvas1 = FigureCanvasTkAgg(fig1, graph_frame)
        canvas1.get_tk_widget().grid(row=0, column=0, padx=20)

        fig2 = plt.Figure(figsize=(4, 3), dpi=100)
        ax2 = fig2.add_subplot(111)

        if counts:
            ax2.pie(counts, labels=statuses, autopct="%1.1f%%")
            ax2.set_title("Ride Status Distribution")

        canvas2 = FigureCanvasTkAgg(fig2, graph_frame)
        canvas2.get_tk_widget().grid(row=0, column=1, padx=20)

        fig3 = plt.Figure(figsize=(6, 3), dpi=100)
        ax3 = fig3.add_subplot(111)

        if amounts:
            ax3.plot(dates, amounts, marker="o")
            ax3.set_title("Earnings Trend")
            ax3.set_ylabel("BDT")

        canvas3 = FigureCanvasTkAgg(fig3, self.content)
        canvas3.get_tk_widget().pack(pady=20)

    def create_admin_ui(self):

        self.clear()

        ctk.CTkLabel(
            self.content, text="Create Admin", font=("Arial", 24, "bold")
        ).pack(pady=20)

        a_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        a_frame.pack(pady=5)

        ctk.CTkLabel(a_frame, text="Name").pack(anchor="w")
        self.name = ctk.CTkEntry(a_frame, placeholder_text="Name", width=350)
        self.name.pack()

        ctk.CTkLabel(a_frame, text="Username").pack(anchor="w")
        self.username = ctk.CTkEntry(a_frame, placeholder_text="Username", width=350)
        self.username.pack()

        ctk.CTkLabel(a_frame, text="Email Address").pack(anchor="w")
        self.email = ctk.CTkEntry(a_frame, placeholder_text="Email", width=350)
        self.email.pack()

        ctk.CTkLabel(a_frame, text="Phone Number").pack(anchor="w")
        self.phone = ctk.CTkEntry(a_frame, placeholder_text="Phone", width=350)
        self.phone.pack()

        ctk.CTkLabel(a_frame, text="Address").pack(anchor="w")
        self.address = ctk.CTkEntry(a_frame, placeholder_text="Address", width=350)
        self.address.pack()

        ctk.CTkLabel(a_frame, text="Employee ID").pack(anchor="w")
        self.emp_id = ctk.CTkEntry(a_frame, placeholder_text="Employee ID", width=350)
        self.emp_id.pack()

        ctk.CTkLabel(self.content, text="Department", font=("Arial", 14, "bold")).pack()
        self.department = ctk.CTkOptionMenu(
            self.content,
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
        self.department.pack(pady=5)

        ctk.CTkLabel(self.content, text="Admin Role", font=("Arial", 14, "bold")).pack()

        self.role = ctk.CTkOptionMenu(
            self.content,
            values=[
                "Select",
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
        self.role.pack(pady=5)

        ctk.CTkLabel(self.content, text="Permissions", font=("Arial", 14, "bold")).pack(
            pady=10
        )

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

        ctk.CTkButton(
            self.content,
            text="Create Admin",
            fg_color="green",
            command=self.create_admin,
        ).pack(pady=20)

    def create_admin(self):

        name = self.name.get()
        username = self.username.get()
        email = self.email.get()
        phone = self.phone.get()
        address = self.address.get()

        emp = self.emp_id.get()
        dept = self.department.get()

        def generate_password(length=8):
            chars = string.ascii_letters + string.digits
            return "".join(random.choice(chars) for _ in range(length))

        plain_password = generate_password()
        hashed = hash_password(plain_password)
        role = self.role.get()

        if (
            not name
            or not username
            or not email
            or not phone
            or not address
            or not emp
            or not dept
        ):
            messagebox.showerror("Error", "All fields are required")
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM accounts WHERE username=%s", (username,))

        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        cursor.execute("SELECT id FROM accounts WHERE email=%s", (email,))

        if cursor.fetchone():
            messagebox.showerror("Error", "Email already exists")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        permissions = []

        perm_map = {
            "users": self.user_perm,
            "drivers": self.driver_perm,
            "admins": self.admin_perm,
            "rides": self.ride_perm,
            "monitor": self.monitor_perm,
            "earnings": self.earn_perm,
            "payments": self.payment_perm,
            "reports": self.report_perm,
            "analytics": self.analytics_perm,
            "support": self.support_perm,
            "driver_support": self.driver_support_perm,
            "user_support": self.user_support_perm,
            "complaints": self.complaint_perm,
            "fraud": self.fraud_perm,
            "security": self.security_perm,
            "system": self.system_perm,
            "maintenance": self.maintenance_perm,
        }

        for perm_name, var in perm_map.items():
            if var.get():
                permissions.append(perm_name)

        if not permissions:
            messagebox.showerror("Error", "Select at least one permission")
            return

        perm_text = ",".join(permissions)
        perm_text = perm_text.replace(",", " |")

        hashed = hash_password(plain_password)

        cursor.execute(
            """
            INSERT INTO accounts
            (name,username,email,phone,address,password,role,is_verified,is_first_login)
            VALUES(%s,%s,%s,%s,%s,%s,'admin', TRUE, TRUE)
        """,
            (name, username, email, phone, address, hashed),
        )

        account_id = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO admin_info
            (account_id,employee_id,department,admin_role,permissions,account_status)
            VALUES(%s,%s,%s,%s,%s,'active')
        """,
            (account_id, emp, dept, role, perm_text),
        )

        self.conn.commit()
        send_admin_welcome_email(
            email, account_id, username, emp, dept, role, perm_text, plain_password
        )

        messagebox.showinfo("Success", f"Admin created successfully!")
        self.create_admin_ui()

    def show_admins(self):

        self.clear()

        search_frame = ctk.CTkFrame(self.content)
        search_frame.pack(pady=10)

        self.admin_search = ctk.CTkEntry(
            search_frame, placeholder_text="Search admin....", width=300
        )
        self.admin_search.pack(side="left", padx=5)
        ctk.CTkButton(
            search_frame, text="Search admin", command=self.search_admin
        ).pack(side="left")

        ctk.CTkLabel(self.content, text="Admin List", font=("Arial", 24, "bold")).pack(
            pady=20
        )

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT a.id,a.name,a.username,a.email,
            ai.admin_role,ai.department,
            ai.account_status
            FROM accounts a
            JOIN admin_info ai ON a.id = ai.account_id
            WHERE a.role='admin'
        """
        )

        admins = cursor.fetchall()

        table = ctk.CTkScrollableFrame(self.content, width=800, height=400)
        table.pack()

        headers = ["Name", "Username", "Email", "Role", "Department", "Status"]

        for i, h in enumerate(headers):

            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=20, pady=10
            )

        for r, row in enumerate(admins, start=1):

            ctk.CTkLabel(table, text=row["name"]).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["username"]).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["email"]).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["admin_role"]).grid(row=r, column=3)
            ctk.CTkLabel(table, text=row["department"]).grid(row=r, column=4)
            ctk.CTkLabel(table, text=row["account_status"]).grid(row=r, column=5)

    def search_admin(self):

        keyword = self.admin_search.get().strip()
        query = f"%{keyword}%"

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT a.id,a.name,a.username,a.email,a.phone,a.address,
            ai.employee_id,ai.department,ai.admin_role,
            ai.permissions,ai.account_status
            FROM accounts a
            JOIN admin_info ai ON a.id=ai.account_id
            WHERE a.role='admin'
            AND (
                a.name LIKE %s OR
                a.username LIKE %s OR
                a.email LIKE %s OR
                ai.employee_id LIKE %s OR
                ai.department LIKE %s OR
                ai.admin_role LIKE %s
        )
    """,
            (query, query, query, query, query, query),
        )

        admins = cursor.fetchall()

        self.render_admin_table(admins)

    def render_admin_table(self, admins):

        self.clear()

        ctk.CTkLabel(
            self.content, text="Manage Admins", font=("Arial", 24, "bold")
        ).pack(pady=20)

        outer = ctk.CTkFrame(self.content)
        outer.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = ctk.CTkCanvas(outer, bg="#2b2b2b", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        v_scroll = ctk.CTkScrollbar(outer, orientation="vertical", command=canvas.yview)
        v_scroll.pack(side="right", fill="y")

        h_scroll = ctk.CTkScrollbar(
            self.content, orientation="horizontal", command=canvas.xview
        )
        h_scroll.pack(fill="x")

        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        table = ctk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=table, anchor="nw")

        table.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        headers = [
            "Name",
            "Username",
            "Email",
            "Phone",
            "Employee ID",
            "Department",
            "Role",
            "Permissions",
            "Status",
            "Edit",
            "Delete",
        ]
        col_widths = [140, 140, 220, 140, 130, 140, 120, 220, 100, 100, 100]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=h,
                width=col_widths[i],
                anchor="center",
                font=("Arial", 14, "bold"),
            ).grid(row=0, column=i, padx=5, pady=10)

        for r, row in enumerate(admins, start=1):

            ctk.CTkLabel(table, text=row["name"], width=140).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["username"], width=140).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["email"], width=220).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["phone"], width=140).grid(row=r, column=3)
            ctk.CTkLabel(table, text=row["employee_id"], width=130).grid(
                row=r, column=4
            )
            ctk.CTkLabel(table, text=row["department"], width=140).grid(row=r, column=5)
            ctk.CTkLabel(table, text=row["admin_role"], width=120).grid(row=r, column=6)
            ctk.CTkLabel(
                table,
                text=row["permissions"],
                width=220,
                wraplength=200,
                justify="left",
            ).grid(row=r, column=7)
            ctk.CTkLabel(table, text=row["account_status"], width=100).grid(
                row=r, column=8, padx=10
            )

            ctk.CTkButton(
                table,
                text="Edit",
                width=90,
                command=lambda id=row["id"]: self.edit_admin(id),
            ).grid(row=r, column=9, padx=5)

            ctk.CTkButton(
                table,
                text="Delete",
                width=80,
                fg_color="red",
                command=lambda id=row["id"]: self.delete_admin(id),
            ).grid(row=r, column=10, padx=5)

        ctk.CTkButton(
            self.content, text="⬅ Back", fg_color="gray", command=self.show_admins
        ).pack(pady=5)

    def edit_admin(self, admin_id):

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT a.*, ai.employee_id, ai.department,
            ai.admin_role, ai.permissions
            FROM accounts a
            JOIN admin_info ai ON a.id = ai.account_id
            WHERE a.id=%s
        """,
            (admin_id,),
        )

        admin = cursor.fetchone()

        ctk.CTkLabel(self.content, text="Edit Admin", font=("Arial", 24, "bold")).pack(
            pady=20
        )
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.pack(pady=5)

        ctk.CTkLabel(frame, text="Name").pack(anchor="w")
        self.a_name = ctk.CTkEntry(frame, width=350)
        self.a_name.insert(0, admin["name"])
        self.a_name.pack()

        ctk.CTkLabel(frame, text="Username").pack(anchor="w")
        self.a_username = ctk.CTkEntry(frame, width=350)
        self.a_username.insert(0, admin["username"])
        self.a_username.pack()

        ctk.CTkLabel(frame, text="Email").pack(anchor="w")
        self.a_email = ctk.CTkEntry(frame, width=350)
        self.a_email.insert(0, admin["email"])
        self.a_email.pack()

        ctk.CTkLabel(frame, text="Phone No").pack(anchor="w")
        self.a_phone = ctk.CTkEntry(frame, width=350)
        self.a_phone.insert(0, admin["phone"])
        self.a_phone.pack()

        ctk.CTkLabel(frame, text="Address").pack(anchor="w")
        self.a_address = ctk.CTkEntry(frame, width=350)
        self.a_address.insert(0, admin["address"])
        self.a_address.pack()

        ctk.CTkLabel(frame, text="Employee ID").pack(anchor="w")
        self.a_emp = ctk.CTkEntry(frame, width=350)
        self.a_emp.insert(0, admin["employee_id"])
        self.a_emp.pack()

        ctk.CTkLabel(frame, text="Department", font=("Arial", 14, "bold")).pack(
            anchor="w"
        )
        self.a_dept = ctk.CTkOptionMenu(
            frame,
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
        self.a_dept.set(admin["department"])
        self.a_dept.pack()

        ctk.CTkLabel(frame, text="Admin Role", font=("Arial", 14, "bold")).pack(
            anchor="w"
        )

        self.a_role = ctk.CTkOptionMenu(
            frame,
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
        self.a_role.pack()

        self.a_role.set(admin["admin_role"])

        ctk.CTkLabel(frame, text="Permissions").pack(anchor="w")

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

        ctk.CTkButton(
            self.content,
            text="Update Admin",
            command=lambda: self.update_admin(admin_id),
        ).pack(pady=20)

        ctk.CTkButton(
            self.content, text="⬅ Back", fg_color="gray", command=self.show_admins
        ).pack()

    def update_admin(self, admin_id):

        name = self.a_name.get().strip()
        username = self.a_username.get().strip()
        email = self.a_email.get().strip()
        phone = self.a_phone.get().strip()
        address = self.a_address.get().strip()
        employee_id = self.a_emp.get().strip()
        department = self.a_dept.get().strip()
        admin_role = self.a_role.get().strip()

        if not all([name, username, email, phone, address, employee_id]):
            messagebox.showerror("Error", "All fields are required")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        permissions = []
        perm_map = {
            "users": self.user_perm,
            "drivers": self.driver_perm,
            "admins": self.admin_perm,
            "rides": self.ride_perm,
            "monitor": self.monitor_perm,
            "earnings": self.earn_perm,
            "payments": self.payment_perm,
            "reports": self.report_perm,
            "analytics": self.analytics_perm,
            "support": self.support_perm,
            "driver_support": self.driver_support_perm,
            "user_support": self.user_support_perm,
            "complaints": self.complaint_perm,
            "fraud": self.fraud_perm,
            "security": self.security_perm,
            "system": self.system_perm,
            "maintenance": self.maintenance_perm,
        }

        for perm_name, checkbox in perm_map.items():
            if checkbox.get():
                permissions.append(perm_name)

        perm_text = " | ".join(permissions)

        cursor = self.conn.cursor()
        cursor.execute(
            """ SELECT id FROM accounts WHERE username=%s AND id!=%s """,
            (username, admin_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        cursor.execute(
            """ SELECT id FROM accounts WHERE email=%s AND id!=%s """, (email, admin_id)
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Email already exists")
            return

        cursor.execute(
            """ SELECT id FROM accounts WHERE phone=%s AND id!=%s """, (phone, admin_id)
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Phone number already exists")
            return

        cursor.execute(
            """ SELECT account_id FROM admin_info WHERE employee_id=%s AND account_id!=%s """,
            (employee_id, admin_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Employee ID already exists")
            return

        cursor.execute(
            """ UPDATE accounts SET name=%s,username=%s,email=%s,phone=%s,address=%s WHERE id=%s""",
            (name, username, email, phone, address, admin_id),
        )

        cursor.execute(
            """ UPDATE admin_info SET employee_id=%s, department=%s, admin_role=%s, permissions=%s WHERE account_id=%s""",
            (employee_id, department, admin_role, perm_text, admin_id),
        )

        self.conn.commit()
        messagebox.showinfo("Success", "Admin updated successfully")
        self.show_admins()

    def delete_admin(self, admin_id):

        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM admin_info WHERE account_id=%s", (admin_id,))
        cursor.execute("DELETE FROM accounts WHERE id=%s", (admin_id,))

        self.conn.commit()

        messagebox.showinfo("Deleted", "Admin removed")

        self.show_admins()

    def show_stats(self):

        self.clear()

        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM accounts")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM driver_info")
        drivers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM rides")
        rides = cursor.fetchone()[0]

        stats = [("Users", users), ("Drivers", drivers), ("Rides", rides)]

        frame = ctk.CTkFrame(self.content)
        frame.pack(pady=30)

        for i, (title, val) in enumerate(stats):

            box = ctk.CTkFrame(frame, width=180, height=100)
            box.grid(row=0, column=i, padx=20)

            ctk.CTkLabel(box, text=title, font=("Arial", 14)).pack(pady=10)
            ctk.CTkLabel(box, text=val, font=("Arial", 20, "bold")).pack()

    def show_profile(self):

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT * FROM accounts
            WHERE id=%s
        """,
            (self.admin_id,),
        )

        admin = cursor.fetchone()

        ctk.CTkLabel(
            self.content, text="Super Admin Profile", font=("Arial", 24, "bold")
        ).pack(pady=20)

        self.name = ctk.CTkEntry(self.content, width=350)
        self.name.insert(0, admin["name"])
        self.name.pack(pady=5)

        self.username = ctk.CTkEntry(self.content, width=350)
        self.username.insert(0, admin["username"])
        self.username.pack(pady=5)

        self.email = ctk.CTkEntry(self.content, width=350)
        self.email.insert(0, admin["email"])
        self.email.pack(pady=5)

        self.phone = ctk.CTkEntry(self.content, width=350)
        self.phone.insert(0, admin["phone"])
        self.phone.pack(pady=5)

        self.address = ctk.CTkEntry(self.content, width=350)
        self.address.insert(0, admin["address"])
        self.address.pack(pady=5)

        ctk.CTkButton(
            self.content, text="Update Profile", command=self.update_profile
        ).pack(pady=20)

        ctk.CTkButton(
            self.content,
            text="Change Password",
            fg_color="orange",
            command=self.change_password_ui,
        ).pack(pady=10)

    def update_profile(self):

        name = self.name.get()
        username = self.username.get()
        email = self.email.get()
        phone = self.phone.get()
        address = self.address.get()

        if not name or not username:
            messagebox.showerror("Error", "Name and Username required")
            return

        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT id FROM accounts WHERE username=%s AND id!=%s",
            (username, self.admin_id),
        )

        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        cursor.execute(
            """
            UPDATE accounts
            SET name=%s,
            username=%s,
            email=%s,
            phone=%s,
            address=%s
            WHERE id=%s
        """,
            (name, username, email, phone, address, self.admin_id),
        )

        self.conn.commit()

        messagebox.showinfo("Success", "Profile updated")

    def change_password_ui(self):

        self.clear()

        ctk.CTkLabel(self.content, text="Change Password", font=("Arial", 24)).pack(
            pady=20
        )

        frame1 = ctk.CTkFrame(self.content)
        frame1.pack(pady=5)

        self.old_pass = ctk.CTkEntry(
            frame1, show="*", width=250, placeholder_text="Old Password"
        )
        self.old_pass.pack(side="left", padx=5)

        ctk.CTkButton(
            frame1,
            text="👁",
            width=40,
            command=lambda: self.toggle_password(self.old_pass),
        ).pack(side="left")

        frame2 = ctk.CTkFrame(self.content)
        frame2.pack(pady=5)

        self.new_pass = ctk.CTkEntry(
            frame2, show="*", width=250, placeholder_text="New Password"
        )
        self.new_pass.pack(side="left", padx=5)

        ctk.CTkButton(
            frame2,
            text="👁",
            width=40,
            command=lambda: self.toggle_password(self.new_pass),
        ).pack(side="left")

        frame3 = ctk.CTkFrame(self.content)
        frame3.pack(pady=5)

        self.re_pass = ctk.CTkEntry(
            frame3, show="*", width=250, placeholder_text="Retype Password"
        )
        self.re_pass.pack(side="left", padx=5)

        ctk.CTkButton(
            frame3,
            text="👁",
            width=40,
            command=lambda: self.toggle_password(self.re_pass),
        ).pack(side="left")

        ctk.CTkButton(
            self.content, text="Update Password", command=self.update_password
        ).pack(pady=20)

        ctk.CTkButton(self.content, text="⬅ Back", command=self.show_profile).pack()

    def update_password(self):

        old = self.old_pass.get()
        new = self.new_pass.get()
        re = self.re_pass.get()

        if len(new) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return

        if new != re:
            messagebox.showerror("Error", "Password mismatch")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute("SELECT password FROM accounts WHERE id=%s", (self.admin_id,))

        result = cursor.fetchone()

        if not check_password(old, result["password"]):
            messagebox.showerror("Error", "Old password incorrect")
            return

        hashed = hash_password(new)

        cursor.execute(
            "UPDATE accounts SET password=%s WHERE id=%s", (hashed, self.admin_id)
        )

        self.conn.commit()

        messagebox.showinfo("Success", "Password changed")

    def toggle_password(self, entry):

        if entry.cget("show") == "":
            entry.configure(show="*")
        else:
            entry.configure(show="")

    def show_users(self):

        self.clear()
        search_frame = ctk.CTkFrame(self.content)
        search_frame.pack(pady=10)
        self.search = ctk.CTkEntry(
            search_frame, placeholder_text="Search user...", width=300
        )
        self.search.pack(side="left", padx=5)

        ctk.CTkButton(search_frame, text="Search", command=self.search_user).pack(
            side="left"
        )

        ctk.CTkLabel(
            self.content, text="Manage Users", font=("Arial", 24, "bold")
        ).pack(pady=20)

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id,name,username,email,phone,address
            FROM accounts
            WHERE role='user'
        """
        )

        users = cursor.fetchall()

        table = ctk.CTkScrollableFrame(self.content, width=900, height=400)
        table.pack()

        headers = ["Name", "Username", "Email", "Phone", "Address"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=20
            )

        for r, row in enumerate(users, start=1):

            ctk.CTkLabel(table, text=row["name"]).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["username"]).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["email"]).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["phone"]).grid(row=r, column=3)
            ctk.CTkLabel(table, text=row["address"]).grid(row=r, column=4)

    def edit_user(self, user_id):

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM accounts WHERE id=%s", (user_id,))

        user = cursor.fetchone()

        ctk.CTkLabel(self.content, text="Edit User", font=("Arial", 24, "bold")).pack(
            pady=20
        )
        u_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        u_frame.pack(pady=5)
        ctk.CTkLabel(u_frame, text="Name").pack(anchor="w")
        self.edit_name = ctk.CTkEntry(u_frame, width=350)
        self.edit_name.insert(0, user["name"])
        self.edit_name.pack()

        ctk.CTkLabel(u_frame, text="Username").pack(anchor="w")
        self.edit_username = ctk.CTkEntry(u_frame, width=350)
        self.edit_username.insert(0, user["username"])
        self.edit_username.pack()

        ctk.CTkLabel(u_frame, text="Email").pack(anchor="w")
        self.edit_email = ctk.CTkEntry(u_frame, width=350)
        self.edit_email.insert(0, user["email"])
        self.edit_email.pack()

        ctk.CTkLabel(u_frame, text="Phone").pack(anchor="w")
        self.edit_phone = ctk.CTkEntry(u_frame, width=350)
        self.edit_phone.insert(0, user["phone"])
        self.edit_phone.pack()

        ctk.CTkLabel(u_frame, text="Address").pack(anchor="w")
        self.edit_address = ctk.CTkEntry(u_frame, width=350)
        self.edit_address.insert(0, user["address"])
        self.edit_address.pack()

        ctk.CTkButton(
            self.content, text="Update", command=lambda: self.update_user(user_id)
        ).pack(pady=20)

        ctk.CTkButton(
            self.content, text="⬅ Back", fg_color="gray", command=self.show_users
        ).pack(pady=5)

    def update_user(self, user_id):

        name = self.edit_name.get()
        username = self.edit_username.get()
        email = self.edit_email.get()
        phone = self.edit_phone.get()
        address = self.edit_address.get()

        cursor = self.conn.cursor()

        cursor.execute(
            """SELECT id FROM accounts WHERE username=%s AND id!=%s """,
            (username, user_id),
        )

        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        cursor.execute(
            """ SELECT id FROM accounts WHERE email=%s AND id!=%s """, (email, user_id)
        )

        if cursor.fetchone():
            messagebox.showerror("Error", "Email already exists")
            return

        cursor.execute(
            """ SELECT id FROM accounts WHERE phone=%s AND id!=%s """, (phone, user_id)
        )

        if cursor.fetchone():
            messagebox.showerror("Error", "Phone number already exists")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        cursor.execute(
            """
            UPDATE accounts
            SET name=%s,username=%s,email=%s,phone=%s,address=%s
            WHERE id=%s
        """,
            (name, username, email, phone, address, user_id),
        )

        self.conn.commit()

        messagebox.showinfo("Success", "User updated")

        self.show_users()

    def delete_user(self, user_id):

        confirm = messagebox.askyesno("Confirm", "Delete this user?")

        if not confirm:
            return

        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM accounts WHERE id=%s", (user_id,))

        self.conn.commit()
        messagebox.showinfo("Deleted", "User removed")
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
            """
            SELECT a.id,a.name,a.username,
            d.vehicle_type,d.vehicle_number
            FROM accounts a
            JOIN driver_info d ON a.id=d.account_id
        """
        )

        drivers = cursor.fetchall()

        table = ctk.CTkScrollableFrame(self.content, width=900, height=400)
        table.pack()

        headers = ["Name", "Username", "Vehicle", "Vehicle No"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=20
            )

        for r, row in enumerate(drivers, start=1):

            ctk.CTkLabel(table, text=row["name"]).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["username"]).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["vehicle_type"]).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["vehicle_number"]).grid(row=r, column=3)

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

    def show_rides(self):

        self.clear()

        ctk.CTkLabel(
            self.content, text="Ride Monitoring", font=("Arial", 24, "bold")
        ).pack(pady=20)

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT pickup,drop_location,
            vehicle_type,fare,ride_status
            FROM rides
            ORDER BY id DESC
        """
        )

        rides = cursor.fetchall()

        table = ctk.CTkScrollableFrame(self.content, width=900, height=400)
        table.pack()

        headers = ["Pickup", "Drop", "Vehicle", "Fare", "Status"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=20
            )

        for r, row in enumerate(rides, start=1):

            ctk.CTkLabel(table, text=row["pickup"]).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["drop_location"]).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["vehicle_type"]).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["fare"]).grid(row=r, column=3)

            status = row["ride_status"]

            color = "green" if status == "completed" else "orange"

            ctk.CTkLabel(table, text=status, text_color=color).grid(row=r, column=4)

    def show_earnings(self):

        self.clear()

        ctk.CTkLabel(
            self.content, text="Earnings Analytics", font=("Arial", 24, "bold")
        ).pack(pady=20)

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT SUM(fare)
            FROM rides
            WHERE ride_status='completed'
        """
        )

        total = cursor.fetchone()[0] or 0

        ctk.CTkLabel(
            self.content,
            text=f"Total Platform Earnings: {total} BDT",
            font=("Arial", 22, "bold"),
        ).pack(pady=30)

    def search_user(self):

        keyword = self.search.get().strip()

        cursor = self.conn.cursor(dictionary=True)

        query = f"%{keyword}%"

        cursor.execute(
            """
            SELECT id,name,username,email,phone,address
            FROM accounts
            WHERE role='user'
            AND (
                name LIKE %s OR
                username LIKE %s OR
                email LIKE %s OR
                phone LIKE %s OR
                address LIKE %s
            )
        """,
            (query, query, query, query, query),
        )

        users = cursor.fetchall()

        self.clear()

        ctk.CTkLabel(
            self.content, text="User Search Result", font=("Arial", 24, "bold")
        ).pack(pady=20)

        table = ctk.CTkScrollableFrame(self.content, width=1100, height=450)
        table.pack()

        headers = ["Name", "Username", "Email", "Phone", "Address", "Edit", "Delete"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=15, pady=10
            )

        for r, row in enumerate(users, start=1):

            ctk.CTkLabel(table, text=row["name"]).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["username"]).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["email"]).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["phone"]).grid(row=r, column=3)
            ctk.CTkLabel(table, text=row["address"]).grid(row=r, column=4)

            ctk.CTkButton(
                table, text="Edit", command=lambda id=row["id"]: self.edit_user(id)
            ).grid(row=r, column=5, padx=5)

            ctk.CTkButton(
                table,
                text="Delete",
                fg_color="red",
                command=lambda id=row["id"]: self.delete_user(id),
            ).grid(row=r, column=6, padx=5)

    def search_driver(self):

        keyword = self.search.get().strip()
        query = f"%{keyword}%"

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT a.id,a.name,a.username,a.email,a.phone,a.address,
            d.nid,d.driving_license,d.vehicle_type,
            d.vehicle_number,d.work_time,d.online_status
            FROM accounts a
            JOIN driver_info d ON a.id=d.account_id
            WHERE a.role='driver'
            AND (
                a.name LIKE %s OR
                a.username LIKE %s OR
                a.email LIKE %s OR
                a.phone LIKE %s OR
                d.vehicle_type LIKE %s OR
                d.vehicle_number LIKE %s OR
                d.driving_license LIKE %s OR
                d.nid LIKE %s
            )
        """,
            (query, query, query, query, query, query, query, query),
        )

        drivers = cursor.fetchall()

        self.clear()

        ctk.CTkLabel(
            self.content, text="Driver Search Result", font=("Arial", 24, "bold")
        ).pack(pady=20)

        table = ctk.CTkScrollableFrame(self.content, width=1300, height=450)
        table.pack()

        headers = [
            "Name",
            "Username",
            "Email",
            "Phone",
            "Vehicle",
            "Vehicle No",
            "License",
            "Status",
            "Edit",
            "Delete",
        ]

        for i, h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=10, pady=10
            )

        for r, row in enumerate(drivers, start=1):

            ctk.CTkLabel(table, text=row["name"]).grid(row=r, column=0)
            ctk.CTkLabel(table, text=row["username"]).grid(row=r, column=1)
            ctk.CTkLabel(table, text=row["email"]).grid(row=r, column=2)
            ctk.CTkLabel(table, text=row["phone"]).grid(row=r, column=3)
            ctk.CTkLabel(table, text=row["vehicle_type"]).grid(row=r, column=4)
            ctk.CTkLabel(table, text=row["vehicle_number"]).grid(row=r, column=5)
            ctk.CTkLabel(table, text=row["driving_license"]).grid(row=r, column=6)
            ctk.CTkLabel(table, text=row["online_status"]).grid(row=r, column=7)

            ctk.CTkButton(
                table, text="Edit", command=lambda id=row["id"]: self.edit_driver(id)
            ).grid(row=r, column=8)

            ctk.CTkButton(
                table,
                text="Delete",
                fg_color="red",
                command=lambda id=row["id"]: self.delete_driver(id),
            ).grid(row=r, column=9)

        ctk.CTkButton(
            self.content, text="⬅ Back", fg_color="gray", command=self.show_drivers
        ).pack(pady=5)

    def system_control_panel(self):

        self.clear()

        ctk.CTkLabel(
            self.content, text="⚙️ System Control Panel", font=("Arial", 26, "bold")
        ).pack(pady=20)

        frame = ctk.CTkFrame(self.content)
        frame.pack(pady=20)

        # Maintenance Mode
        ctk.CTkButton(
            frame,
            text="🛠 Enable Maintenance Mode",
            width=250,
            command=self.enable_maintenance,
        ).grid(row=0, column=0, padx=20, pady=10)

        ctk.CTkButton(
            frame,
            text="✅ Disable Maintenance Mode",
            width=250,
            command=self.disable_maintenance,
        ).grid(row=0, column=1, padx=20, pady=10)

        # Registration control
        ctk.CTkButton(
            frame,
            text="🚫 Disable New Registration",
            width=250,
            command=self.disable_registration,
        ).grid(row=1, column=0, padx=20, pady=10)

        ctk.CTkButton(
            frame,
            text="✔ Enable Registration",
            width=250,
            command=self.enable_registration,
        ).grid(row=1, column=1, padx=20, pady=10)

        # Suspend user system
        ctk.CTkButton(
            frame, text="👤 Suspend All Users", width=250, command=self.suspend_users
        ).grid(row=2, column=0, padx=20, pady=10)

        ctk.CTkButton(
            frame,
            text="🚗 Suspend All Drivers",
            width=250,
            command=self.suspend_drivers,
        ).grid(row=2, column=1, padx=20, pady=10)

        # Reset rides
        ctk.CTkButton(
            frame,
            text="🗑 Reset Ride History",
            width=250,
            fg_color="red",
            command=self.reset_rides,
        ).grid(row=3, column=0, padx=20, pady=10)

        # System info
        ctk.CTkButton(
            frame, text="📊 System Info", width=250, command=self.system_info
        ).grid(row=3, column=1, padx=20, pady=10)

    def enable_maintenance(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE system_settings
            SET maintenance_mode=1
        """
        )

        self.conn.commit()

        messagebox.showinfo("System", "Maintenance Mode Enabled")

    def disable_maintenance(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE system_settings
            SET maintenance_mode=0
        """
        )

        self.conn.commit()

        messagebox.showinfo("System", "Maintenance Mode Disabled")

    def disable_registration(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE system_settings
            SET registration_enabled=0
        """
        )

        self.conn.commit()

        messagebox.showinfo("System", "New Registration Disabled")

    def enable_registration(self):

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE system_settings
            SET registration_enabled=1
        """
        )

        self.conn.commit()

        messagebox.showinfo("System", "Registration Enabled")

    def suspend_users(self):

        confirm = messagebox.askyesno("Warning", "Suspend ALL users?")

        if not confirm:
            return

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE accounts
            SET status='suspended'
            WHERE role='user'
        """
        )

        self.conn.commit()

        messagebox.showinfo("System", "All users suspended")

    def suspend_drivers(self):

        confirm = messagebox.askyesno("Warning", "Suspend ALL drivers?")

        if not confirm:
            return
        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE accounts
            SET status='suspended'
            WHERE role='driver'
        """
        )

        self.conn.commit()

        messagebox.showinfo("System", "All drivers suspended")

    def reset_rides(self):

        confirm = messagebox.askyesno("Danger", "Delete all ride history?")

        if not confirm:
            return

        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM rides")

        self.conn.commit()

        messagebox.showinfo("System", "Ride history cleared")

    def system_info(self):

        self.clear()

        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM accounts")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM rides")
        rides = cursor.fetchone()[0]

        ctk.CTkLabel(
            self.content, text="System Information", font=("Arial", 24, "bold")
        ).pack(pady=20)

        ctk.CTkLabel(
            self.content, text=f"Total Accounts : {users}", font=("Arial", 18)
        ).pack(pady=10)

        ctk.CTkLabel(
            self.content, text=f"Total Rides : {rides}", font=("Arial", 18)
        ).pack(pady=10)

        ctk.CTkLabel(
            self.content, text="Version : GOMON v1.0.pack r1.1", font=("Arial", 18)
        ).pack(pady=10)

    def logout(self):

        from pages.login_page import LoginPage

        self.master.clear_window()

        LoginPage(self.master)
