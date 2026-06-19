import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from database import check_password, hash_password
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
import geocoder
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import timedelta, date


class DriverDashboard(ctk.CTkFrame):

    def __init__(self, master, driver_id):

        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.master = master
        self.driver_id = driver_id
        self.conn = master.conn

        self.status = "offline"
        self.auto_job = None
        self.time_job = None
        self.location_job = None
        self.current_page = "home"
        self.build_ui()
        
        self.location_job = self.after(10000, self.update_live_location)

    def build_ui(self):

        top = ctk.CTkFrame(self, height=60)
        top.pack(fill="x")

        self.page_title = ctk.CTkLabel(top, text="🏠 Home", font=("Arial", 22, "bold"))
        self.page_title.pack(side="left", padx=20)

        self.notify_btn = ctk.CTkButton(
            top, text="🔔 Notifications", width=120, command=self.show_notifications
        )
        self.notify_btn.pack(side="right", padx=10)

        self.time_label = ctk.CTkLabel(top)
        self.time_label.pack(side="right", padx=20)

        self.update_time()

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(main, width=200)
        sidebar.pack(side="left", fill="y")

        menus = [
            ("🏠 Home", self.show_home),
            ("📩 Ride Requests", self.show_requests),
            ("🚗 Active Ride", self.show_active),
            ("📜 Ride History", self.show_history),
            ("💰 Earnings", self.show_earnings),
            ("⭐ Rating", self.show_rating),
            ("💬 Messages", self.show_message),
            ("👤 Profile", self.show_profile),
            ("🚨 SOS", self.sos_alert),
            ("🚪 Logout", self.logout),
        ]

        for name, cmd in menus:
            ctk.CTkButton(
                sidebar,
                text=name,
                width=180,
                height=40,
                corner_radius=8,
                font=("Arial", 14),
                command=cmd,
            ).pack(pady=6)

        self.content = ctk.CTkScrollableFrame(main)
        self.content.pack(side="right", fill="both", expand=True)

        self.show_home()

    def update_time(self):
        if not self.winfo_exists():
            return

        now = datetime.now().strftime("%d %B %Y | %H:%M:%S")
        self.time_label.configure(text=now)

        self.time_job = self.after(1000, self.update_time)

    def clear(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home(self):

        if self.auto_job:
            self.after_cancel(self.auto_job)
            self.auto_job = None

        self.current_page = "home"
        self.page_title.configure(text="🏠 Home")
        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT a.name,a.username,d.vehicle_type,
        d.driving_license,d.vehicle_number,d.online_status
        FROM accounts a
        JOIN driver_info d ON a.id=d.account_id
        WHERE a.id=%s
        """,
            (self.driver_id,),
        )

        driver = cursor.fetchone()
        if not driver:
            ctk.CTkLabel(self.content, text="Driver data not found").pack()
            return

        self.status = driver["online_status"]

        cursor.execute(
            """
        SELECT SUM(fare) AS total
        FROM rides
        WHERE driver_id=%s
        AND ride_status='completed'
        """,
            (self.driver_id,),
        )

        result = cursor.fetchone()
        earn = result["total"] or 0

        if not driver:
            ctk.CTkLabel(self.content, text="Driver data not found").pack()
            return

        ctk.CTkLabel(
            self.content, text="Driver Dashboard", font=("Arial", 26, "bold")
        ).pack(pady=20)

        card = ctk.CTkFrame(self.content, corner_radius=10)
        card.pack(pady=10)

        info = [
            ("Name", driver["name"]),
            ("Username", driver["username"]),
            ("Vehicle", driver["vehicle_type"]),
            ("License No", driver["driving_license"]),
            ("Vehicle No", driver["vehicle_number"]),
        ]

        for i, (label, value) in enumerate(info):
            ctk.CTkLabel(card, text=f"{label}:", width=120, anchor="w").grid(
                row=i, column=0, padx=10, pady=4
            )
            ctk.CTkLabel(card, text=value, font=("Arial", 13, "bold")).grid(
                row=i, column=1, padx=10, pady=4
            )

        stats_frame = ctk.CTkFrame(self.content)
        stats_frame.pack(pady=20)

        cursor.execute(
            """
            SELECT COUNT(*) AS trips
            FROM rides
            WHERE driver_id=%s AND ride_status='completed'
        """,
            (self.driver_id,),
        )

        trip_result = cursor.fetchone()
        trips = trip_result["trips"]

        cards = [
            ("💰 Earnings", f"{earn} BDT"),
            ("🚗 Trips", trips),
            ("⭐ Rating", "0.0"),
            ("📍 Status", self.status.upper()),
        ]

        for i, (title, value) in enumerate(cards):

            card_box = ctk.CTkFrame(stats_frame, width=150, height=80, corner_radius=10)
            card_box.grid(row=0, column=i, padx=10)

            ctk.CTkLabel(card_box, text=title, font=("Arial", 12)).pack(pady=5)
            ctk.CTkLabel(card_box, text=value, font=("Arial", 18, "bold")).pack()

        earn_card = ctk.CTkFrame(self.content)
        earn_card.pack(pady=10)

        ctk.CTkLabel(
            earn_card, text=f"Total Earnings: {earn} BDT", font=("Arial", 18, "bold")
        ).pack(padx=20, pady=10)

        self.status_label = ctk.CTkLabel(
            self.content,
            text=f"Status: {self.status.upper()}",
            font=("Arial", 16, "bold"),
        )
        self.status_label.pack(pady=10)

        self.animate_status()
        btn_frame = ctk.CTkFrame(self.content)
        btn_frame.pack(pady=10)
        state_online = "disabled" if self.status == "online" else "normal"
        state_offline = "disabled" if self.status == "offline" else "normal"
        ctk.CTkButton(
            btn_frame,
            text="🟢 Go Online",
            state=state_online,
            width=140,
            fg_color="#16a34a",
            command=self.go_online,
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            btn_frame,
            text="🔴 Go Offline",
            state=state_offline,
            width=140,
            fg_color="#dc2626",
            command=self.go_offline,
        ).grid(row=0, column=1, padx=10)

        # MAP PLACEHOLDER
        map_frame = ctk.CTkFrame(self.content, corner_radius=10)
        map_frame.pack(pady=20, fill="both", expand=True, padx=20)

        ctk.CTkLabel(
            map_frame, text="🗺 Driver Location Map", font=("Arial", 18, "bold")
        ).pack(pady=10)

        self.map_widget = TkinterMapView(
            map_frame, width=900, height=350, corner_radius=10
        )
        self.map_widget.pack(padx=10, pady=10)

        if not self.detect_live_location():

            self.map_widget.set_position(23.8103, 90.4125)
            self.map_widget.set_zoom(12)

            self.map_widget.set_marker(23.8103, 90.4125, text="You")



    def go_online(self):
        self.status = "online"

        cursor = self.conn.cursor()
        cursor.execute(
            """
        UPDATE driver_info
        SET online_status='online'
        WHERE account_id=%s
        """,
            (self.driver_id,),
        )
        self.conn.commit()

        self.show_home()

    def go_offline(self):
        self.status = "offline"

        cursor = self.conn.cursor()
        cursor.execute(
            """
        UPDATE driver_info
        SET online_status='offline'
        WHERE account_id=%s
        """,
            (self.driver_id,),
        )
        self.conn.commit()

        self.show_home()

    def show_requests(self):

        self.current_page = "requests"
        self.page_title.configure(text="📩 Ride / Rental Requests")
        self.clear()

        if self.status != "online":
            ctk.CTkLabel(
                self.content, text="Go Online to see ride requests", font=("Arial", 16)
            ).pack(pady=30)
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT
            id,
            pickup,
            drop_location AS destination,
            distance,
            fare AS price,
            vehicle_type,
            'ride' AS request_type
        FROM rides
        WHERE ride_status='searching'
        AND vehicle_type = (
            SELECT vehicle_type
            FROM driver_info
            WHERE account_id=%s
        )

        UNION ALL

        SELECT
            id,
            pickup,
            destination,
            hours AS distance,
            price,
            vehicle_type,
            'rental' AS request_type
        FROM rentals
        WHERE status='searching'
        AND vehicle_type = (
            SELECT vehicle_type
            FROM driver_info
            WHERE account_id=%s
        )
        ORDER BY id DESC
        """,
            (self.driver_id, self.driver_id),
        )

        requests = cursor.fetchall()

        if not requests:
            ctk.CTkLabel(
                self.content,
                text="No ride or rental requests available",
                font=("Arial", 16),
            ).pack(pady=30)
            return

        for req in requests:

            frame = ctk.CTkFrame(self.content, corner_radius=12)
            frame.pack(fill="x", padx=20, pady=10)

            if req["request_type"] == "ride":
                title = "🚕 Ride Request"
                title_color = "#22c55e"
                details = f"Distance: {req['distance']} km"
                button_text = "Accept Ride"
                button_color = "#16a34a"
            else:
                title = "📅 Rental Request"
                title_color = "#f59e0b"
                details = f"Duration: {req['distance']} Hour"
                button_text = "Accept Rental"
                button_color = "#f59e0b"

            ctk.CTkLabel(
                frame, text=title, font=("Arial", 16, "bold"), text_color=title_color
            ).pack(anchor="w", padx=15, pady=(10, 5))

            ctk.CTkLabel(
                frame,
                text=f"{req['pickup']} ➜ {req['destination']}",
                font=("Arial", 15, "bold"),
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(frame, text=details, font=("Arial", 13)).pack(
                anchor="w", padx=15, pady=2
            )

            ctk.CTkLabel(
                frame, text=f"Vehicle: {req['vehicle_type']}", font=("Arial", 13)
            ).pack(anchor="w", padx=15, pady=2)

            ctk.CTkLabel(
                frame, text=f"Fare: {req['price']} BDT", font=("Arial", 13, "bold")
            ).pack(anchor="w", padx=15, pady=(2, 10))

            if req["request_type"] == "ride":
                ctk.CTkButton(
                    frame,
                    text=button_text,
                    fg_color=button_color,
                    command=lambda r=req: self.accept_ride(r),).pack(pady=(0, 10))
            else:
                ctk.CTkButton(
                    frame,
                    text=button_text,
                    fg_color=button_color,
                    command=lambda r=req: self.accept_rental(r),).pack(pady=(0, 10))

        if self.current_page == "requests" and self.winfo_exists():
            self.auto_refresh(self.show_requests)
    def accept_rental(self, rental):

        cursor = self.conn.cursor()

        cursor.execute(
            """
        SELECT id
        FROM rentals
        WHERE driver_id=%s
        AND status IN ('accepted','started')
        """,
            (self.driver_id,),
        )

        if cursor.fetchone():
            messagebox.showerror("Rental", "Finish current rental first")
            return

        cursor.execute(
            """
        UPDATE rentals
        SET driver_id=%s,
            status='accepted'
        WHERE id=%s
        AND status='searching'
        """,
            (self.driver_id, rental["id"]),
        )

        self.conn.commit()

        if cursor.rowcount == 0:
            messagebox.showerror("Rental", "This rental already accepted")
            return

        messagebox.showinfo("Rental", "Rental request accepted")

        self.show_requests()

    def start_ride(self, ride_id):

        cursor = self.conn.cursor()

        cursor.execute(
            """
        UPDATE rides
        SET ride_status='started'
        WHERE id=%s
        """,
            (ride_id,),
        )

        self.conn.commit()

        self.add_notification(ride_id, "Your ride has started.")

        self.show_active()

    def accept_ride(self, ride):

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id
            FROM rides
            WHERE driver_id=%s
            AND ride_status IN ('accepted','started')
        """,
            (self.driver_id,),
        )

        if cursor.fetchone():
            messagebox.showerror("Ride", "Finish current ride first")
            return

        cursor = self.conn.cursor()

        cursor.execute(
            """
        UPDATE rides
        SET driver_id=%s, ride_status='accepted'
        WHERE id=%s AND ride_status='searching'
        """,
            (self.driver_id, ride["id"]),
        )

        self.conn.commit()
        if cursor.rowcount == 0:
            messagebox.showerror("Ride", "This ride already accepted by another driver")
            return

        self.show_active()

    def show_active(self):

        self.current_page = "active"
        self.page_title.configure(text="🚗 Active Ride")
        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT * FROM rides
        WHERE driver_id=%s
        AND ride_status IN ('accepted','started')
        """,
            (self.driver_id,),
        )

        ride = cursor.fetchone()

        if not ride:
            ctk.CTkLabel(self.content, text="No active ride").pack(pady=30)
            return

        ctk.CTkLabel(self.content, text=f"Pickup: {ride['pickup']}").pack()
        ctk.CTkLabel(self.content, text=f"Drop: {ride['drop_location']}").pack()
        ctk.CTkLabel(self.content, text=f"Fare: {ride['fare']}").pack()

        map_frame = ctk.CTkFrame(self.content)
        map_frame.pack(pady=20)

        ride_map = TkinterMapView(map_frame, width=850, height=300)
        ride_map.pack()

        ride_map.delete_all_marker()
        ride_map.delete_all_path()
        pickup_coord = self.get_coordinates(ride["pickup"])
        drop_coord = self.get_coordinates(ride["drop_location"])

        if pickup_coord and drop_coord:

            ride_map.set_position(pickup_coord[0], pickup_coord[1])
            ride_map.set_zoom(12)

            ride_map.set_marker(pickup_coord[0], pickup_coord[1], text="Pickup")

            ride_map.set_marker(drop_coord[0], drop_coord[1], text="Drop")

            ride_map.set_path([pickup_coord, drop_coord])
        else:
            ctk.CTkLabel(map_frame, text="Unable to load route").pack()

        status = ride["ride_status"]

        if status == "accepted":
            ctk.CTkButton(
                self.content,
                text="Start Ride",
                fg_color="#3b82f6",
                command=lambda: self.update_status(ride["id"], "started"),
            ).pack(pady=5)
        elif status == "started":
            ctk.CTkButton(
                self.content,
                text="End Ride",
                fg_color="#16a34a",
                command=lambda: self.update_status(ride["id"], "completed"),
            ).pack()
        if self.current_page == "active" and self.winfo_exists():
            self.auto_refresh(self.show_active)

    def update_status(self, ride_id, status):

        cursor = self.conn.cursor()

        cursor.execute(
            """
        UPDATE rides
        SET ride_status=%s
        WHERE id=%s
        """,
            (status, ride_id),
        )

        self.conn.commit()

        if status == "started":
            self.add_notification(ride_id, "Driver has started the ride.")

        messagebox.showinfo("Ride", f"Ride {status}")
        if status == "completed":
            self.add_notification(ride_id, "Your ride has been completed successfully.")
        self.show_active()

    def show_earnings(self):
        if self.auto_job:
            self.after_cancel(self.auto_job)
            self.auto_job = None

        self.page_title.configure(text="💰 Earnings")
        self.clear()

        ctk.CTkLabel(
            self.content, text="Driver Earnings", font=("Arial", 24, "bold")
        ).pack(pady=15)

        filter_frame = ctk.CTkFrame(self.content)
        filter_frame.pack(pady=10)
        ctk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=5)
        self.earning_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["Today", "This Week", "This Month", "All Time"],
            command=self.load_earnings,
        )
        self.earning_filter.pack(side="left", padx=5)
        self.earning_filter.set("All Time")

        self.earning_summary = ctk.CTkLabel(
            self.content, text="", font=("Arial", 18, "bold")
        )
        self.earning_summary.pack(pady=10)
        self.graph_frame = ctk.CTkFrame(self.content)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.history_frame = ctk.CTkScrollableFrame(self.content, width=900, height=250)
        self.history_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self.load_earnings("All Time")

        

    def load_earnings(self, value):
        for w in self.graph_frame.winfo_children():
            w.destroy()
        for w in self.history_frame.winfo_children():
            w.destroy()

        cursor = self.conn.cursor(dictionary=True)
        condition = ""
        params = [self.driver_id]
        today = date.today()

        if value == "Today":
            condition = "AND DATE(created_at)=%s"
            params.append(today)
        elif value == "This Week":
            start = today - timedelta(days=today.weekday())
            condition = "AND DATE(created_at)>=%s"
            params.append(start)
        elif value == "This Month":
            condition = "AND MONTH(created_at)=%s AND YEAR(created_at)=%s"
            params.append(today.month)
            params.append(today.year)

        cursor.execute(
            f""" SELECT created_at, fare FROM rides WHERE driver_id=%s AND ride_status='completed' {condition} ORDER BY created_at ASC """,
            tuple(params),
        )

        rides = cursor.fetchall()
        total = sum(float(r["fare"]) for r in rides)
        self.earning_summary.configure(
            text=f"Total Earnings: {total:.2f} BDT | Total Trips: {len(rides)}"
        )

        if not rides:
            ctk.CTkLabel(self.graph_frame, text="No earnings data found").pack(pady=30)
            return
        x = []
        y = []
        for r in rides:
            x.append(r["created_at"].strftime("%d %b"))
            y.append(float(r["fare"]))

        fig, ax = plt.subplots(figsize=(7, 3))
        ax.plot(x, y, marker="o")
        ax.set_title("Earnings Graph")
        ax.set_xlabel("Date")
        ax.set_ylabel("BDT")
        plt.xticks(rotation=30)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        headers = ["Date", "Fare"]

        for i, h in enumerate(headers):
            ctk.CTkLabel(self.history_frame, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=20, pady=10
            )

        for row, r in enumerate(rides, start=1):
            ctk.CTkLabel(
                self.history_frame, text=r["created_at"].strftime("%d %b %Y %I:%M %p")
            ).grid(row=row, column=0, padx=20, pady=5)

            ctk.CTkLabel(self.history_frame, text=f"{r['fare']} BDT").grid(
                row=row, column=1, padx=20, pady=5
            )

    def show_rating(self):
        if self.auto_job:
            self.after_cancel(self.auto_job)
            self.auto_job = None

        self.page_title.configure(text="⭐ Rating & Reviews")
        self.clear()

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            """ SELECT ROUND(AVG(rating),1) AS avg_rating, COUNT(rating) AS total_reviews FROM rides WHERE driver_id=%s AND rating IS NOT
                       NULL """,
            (self.driver_id,),
        )

        stats = cursor.fetchone()
        avg_rating = stats["avg_rating"] or 0
        total_reviews = stats["total_reviews"] or 0

        top = ctk.CTkFrame(self.content)
        top.pack(pady=20)

        ctk.CTkLabel(
            top, text=f"⭐ Average Rating: {avg_rating}/5", font=("Arial", 24, "bold")
        ).pack(pady=5)
        ctk.CTkLabel(
            top, text=f"Total Reviews: {total_reviews}", font=("Arial", 16)
        ).pack()

        cursor.execute(
            """SELECT a.name, r.rating, r.review, r.created_at FROM rides r JOIN accounts a ON r.user_id = a.id
                        WHERE r.driver_id=%s AND r.rating IS NOT NULL ORDER BY r.id DESC """,
            (self.driver_id,),
        )

        reviews = cursor.fetchall()
        if not reviews:
            ctk.CTkLabel(self.content, text="No reviews yet", font=("Arial", 16)).pack(
                pady=20
            )
            return
        review_frame = ctk.CTkScrollableFrame(self.content, width=900, height=450)
        review_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for row in reviews:
            card = ctk.CTkFrame(review_frame, corner_radius=12)
            card.pack(fill="x", padx=10, pady=8)
            date = row["created_at"].strftime("%d %b %Y")

            ctk.CTkLabel(
                card, text=f"{row['name']}   •   {date}", font=("Arial", 15, "bold")
            ).pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(
                card,
                text=f"{'⭐' * int(row['rating'])} ({row['rating']}/5)",
                text_color="#f59e0b",
                font=("Arial", 14),
            ).pack(anchor="w", padx=15)
            ctk.CTkLabel(
                card,
                text=row["review"] if row["review"] else "NO written review",
                wraplength=700,
                justify="left",
            ).pack(anchor="w", padx=15, pady=(5, 10))

    def show_message(self):

        self.current_page = "message"
        self.page_title.configure(text="💬 Passenger Messages")
        self.clear()
        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """ SELECT r.id, a.name FROM rides r JOIN accounts a ON r.user_id = a.id WHERE r.driver_id=%s AND r.ride_status IN ('accepted','started') ORDER BY r.id DESC LIMIT 1 """,
            (self.driver_id,),
        )

        ride = cursor.fetchone()

        if not ride:
            ctk.CTkLabel(self.content, text="No active ride message available").pack(
                pady=40
            )
            return

        self.current_ride_id = ride["id"]
        ctk.CTkLabel(
            self.content, text=f"Chat with {ride['name']}", font=("Arial", 24, "bold")
        ).pack(pady=20)

        self.chat_box = ctk.CTkTextbox(self.content, width=800, height=400)
        self.chat_box.pack(padx=20, pady=10)
        cursor.execute(
            """ SELECT sender_role, message, created_at FROM messages WHERE ride_id=%s ORDER BY id ASC """,
            (ride["id"],),
        )

        messages = cursor.fetchall()

        for m in messages:

            sender = "You" if m["sender_role"] == "driver" else ride["name"]
            time = m["created_at"].strftime("%H:%M")

            self.chat_box.insert("end", f"[{time}] {sender}: {m['message']}\n")

        self.chat_box.see("end")
        bottom = ctk.CTkFrame(self.content)
        bottom.pack(pady=10)
        self.msg_input = ctk.CTkEntry(
            bottom, width=600, placeholder_text="Type message..."
        )
        self.msg_input.pack(side="left", padx=10)
        ctk.CTkButton(bottom, text="Send", command=self.send_message).pack(side="left")

        if self.current_page == "message" and self.winfo_exists():
            self.auto_refresh(self.show_message)

    def send_message(self):

        msg = self.msg_input.get().strip()

        if not msg:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """ INSERT INTO messages(ride_id, sender_role, message) VALUES(%s,%s,%s) """,
            (self.current_ride_id, "driver", msg),
        )

        self.conn.commit()
        self.msg_input.delete(0, "end")
        self.show_message()

    def refresh_messages(self):
        if hasattr(self, "page_title"):
            if self.page_title.cget("text") == "💬 Passenger Messages":
                self.show_message()

    def show_profile(self):
        if self.auto_job:
            self.after_cancel(self.auto_job)
            self.auto_job = None

        self.page_title.configure(text="👤 Profile")
        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT a.*,d.*
        FROM accounts a
        JOIN driver_info d ON a.id=d.account_id
        WHERE a.id=%s
        """,
            (self.driver_id,),
        )

        driver = cursor.fetchone()

        if not driver:
            messagebox.showerror("Error", "Driver data not found")
            return

        self.name = ctk.CTkEntry(self.content, width=300)
        self.name.insert(0, driver["name"])
        self.name.pack(pady=5)

        self.username = ctk.CTkEntry(self.content, width=300)
        self.username.insert(0, driver["username"])
        self.username.pack(pady=5)

        self.email = ctk.CTkEntry(self.content, width=300)
        self.email.insert(0, driver["email"])
        self.email.pack(pady=5)

        self.phone = ctk.CTkEntry(self.content, width=300)
        self.phone.insert(0, driver["phone"])
        self.phone.pack(pady=5)

        ctk.CTkLabel(self.content, text=f"NID: {driver['nid']}").pack()
        ctk.CTkLabel(self.content, text=f"License: {driver['driving_license']}").pack()
        ctk.CTkLabel(self.content, text=f"Vehicle: {driver['vehicle_type']}").pack()
        ctk.CTkLabel(
            self.content, text=f"Vehicle No: {driver['vehicle_number']}"
        ).pack()
        ctk.CTkLabel(self.content, text=f"Work Time: {driver['work_time']}").pack()

        self.password = ctk.CTkEntry(self.content, show="*", width=300)
        self.password.pack(pady=10)

        ctk.CTkButton(
            self.content, text="Save Profile", command=self.update_profile
        ).pack(pady=10)

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
        password = self.password.get()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM accounts WHERE username=%s AND id!=%s",
            (username, self.driver_id),
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        cursor.execute(
            "SELECT id FROM accounts WHERE email=%s AND id!=%s", (email, self.driver_id)
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Email already exists")
            return

        cursor.execute(
            "SELECT id FROM accounts WHERE phone=%s AND id!=%s", (phone, self.driver_id)
        )
        if cursor.fetchone():
            messagebox.showerror("Error", "Phone number already exists")
            return

        cursor.execute("SELECT password FROM accounts WHERE id=%s", (self.driver_id,))
        result = cursor.fetchone()

        if not check_password(password, result["password"]):
            messagebox.showerror("Error", "Password incorrect")
            return

        if username != username.lower():
            messagebox.showerror("Error", "Username must contain only small letters")
            return

        cursor.execute(
            """
        UPDATE accounts
        SET name=%s, username=%s, email=%s, phone=%s
        WHERE id=%s
        """,
            (name, username, email, phone, self.driver_id), )

        self.conn.commit()

        messagebox.showinfo("Success", "Profile updated")

    def sos_alert(self):

        messagebox.showwarning("Emergency", "SOS Alert Sent to Admin!")

    def show_notifications(self):
        if self.auto_job:
            self.after_cancel(self.auto_job)
            self.auto_job = None
        cursor = self.conn.cursor()

        cursor.execute(
            """
                SELECT COUNT(*)
                FROM rides
                WHERE driver_id=%s
            """,
            (self.driver_id,),
        )

        count = cursor.fetchone()[0]

        self.page_title.configure(text=f"🔔 Notifications ({count})")
        self.clear()

        ctk.CTkLabel(
            self.content, text="Notifications", font=("Arial", 24, "bold")
        ).pack(pady=20)

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
        SELECT * FROM rides
        WHERE driver_id=%s
        ORDER BY id DESC
        LIMIT 5
        """,
            (self.driver_id,),
        )

        rides = cursor.fetchall()

        if not rides:
            ctk.CTkLabel(self.content, text="No notifications").pack()
            return

        for r in rides:

            text = f"Ride {r['ride_status']} | {r['pickup']} ➜ {r['drop_location']}"

            ctk.CTkLabel(self.content, text=text).pack(pady=5)

    def animate_status(self):

        colors = ["red", "#22c55e", "#16a34a", "#15803d"]

        def loop(i=0):
            if not hasattr(self, "status_label"):
                return

            if not self.status_label.winfo_exists():
                return

            self.status_label.configure(text_color=colors[i])
            self.after(400, loop, (i + 1) % len(colors))

        loop()

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
        self.new_pass.pack(side="left", pady=5)
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
        self.re_pass.pack(side="left", pady=5)
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

        cursor.execute("SELECT password FROM accounts WHERE id=%s", (self.driver_id,))

        result = cursor.fetchone()

        if not check_password(old, result["password"]):
            messagebox.showerror("Error", "Old password incorrect")
            return

        hashed = hash_password(new)

        cursor.execute(
            "UPDATE accounts SET password=%s WHERE id=%s", (hashed, self.driver_id)
        )

        self.conn.commit()

        messagebox.showinfo("Success", "Password changed")

    def toggle_password(self, entry):

        if entry.cget("show") == "":
            entry.configure(show="*")
        else:
            entry.configure(show="")

    def show_history(self):
        if self.auto_job:
            self.after_cancel(self.auto_job)
            self.auto_job = None

        self.page_title.configure(text="📜 Ride History")
        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT r.pickup,
            r.drop_location,
            r.distance,
            r.fare,
            r.ride_status,
            r.created_at,
            a.name AS passenger
            FROM rides r
            JOIN accounts a ON r.user_id = a.id
            WHERE r.driver_id=%s
            ORDER BY r.id DESC
        """,
            (self.driver_id,),
        )

        rides = cursor.fetchall()

        if not rides:
            ctk.CTkLabel(
                self.content, text="No ride history found", font=("Arial", 16)
            ).pack(pady=40)
            return

        total_trips = len(rides)
        total_earn = sum(r["fare"] for r in rides if r["ride_status"] == "completed")

        stats = ctk.CTkFrame(self.content)
        stats.pack(pady=20)

        cards = [
            ("🚗 Total Trips", total_trips),
            ("💰 Total Earnings", f"{total_earn} BDT"),
        ]

        for i, (title, val) in enumerate(cards):

            card = ctk.CTkFrame(stats, width=180, height=80, corner_radius=10)
            card.grid(row=0, column=i, padx=10)

            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=5)
            ctk.CTkLabel(card, text=val, font=("Arial", 18, "bold")).pack()

        table = ctk.CTkScrollableFrame(self.content, width=1000, height=450)
        table.pack(pady=20)

        headers = ["Date", "Passenger", "Pickup", "Drop", "Distance", "Fare", "Status"]

        for i, h in enumerate(headers):

            ctk.CTkLabel(table, text=h, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=15, pady=10
            )

        for r, row in enumerate(rides, start=1):

            date = row["created_at"].strftime("%d %b %Y")

            ctk.CTkLabel(table, text=date).grid(row=r, column=0, padx=15, pady=5)

            ctk.CTkLabel(table, text=row["passenger"]).grid(
                row=r, column=1, padx=15, pady=5
            )

            ctk.CTkLabel(table, text=row["pickup"]).grid(
                row=r, column=2, padx=15, pady=5
            )

            ctk.CTkLabel(table, text=row["drop_location"]).grid(
                row=r, column=3, padx=15, pady=5
            )

            ctk.CTkLabel(table, text=f"{row['distance']} km").grid(
                row=r, column=4, padx=15, pady=5
            )

            ctk.CTkLabel(table, text=f"{row['fare']} BDT").grid(
                row=r, column=5, padx=15, pady=5)

            status = row["ride_status"]

            if status == "completed":
                color = "green"
            elif status == "accepted":
                color = "orange"
            else:
                color = "red"

            ctk.CTkLabel(
                table, text=status, text_color=color, font=("Arial", 13, "bold")
            ).grid(row=r, column=6, padx=15, pady=5)

    def get_coordinates(self, place):

        geolocator = Nominatim(user_agent="gomon_driver")

        try:
            location = geolocator.geocode(place)

            if location:
                return (location.latitude, location.longitude)
        except:
            pass

        return None

    def detect_live_location(self):

        try:
            g = geocoder.ip("me")

            if g.latlng:
                lat, lon = g.latlng

                self.map_widget.set_position(lat, lon)
                self.map_widget.set_zoom(14)

                self.map_widget.set_marker(lat, lon, text="Your Live Location")

                return True
        except:
            pass

        return False

    def add_notification(self, ride_id, message):

        cursor = self.conn.cursor()

        cursor.execute(
            """
        SELECT user_id
        FROM rides
        WHERE id=%s
        """,
            (ride_id,),
        )

        row = cursor.fetchone()

        if row:
            user_id = row[0]

            cursor.execute(
                """
            INSERT INTO notifications(user_id,message)
            VALUES(%s,%s)
            """,
                (user_id, message),
            )

            self.conn.commit()

    def update_live_location(self):
        if not self.winfo_exists():
            return

        cursor = self.conn.cursor()
        g = geocoder.ip("me")

        if g.latlng:
            lat, lon = g.latlng

            cursor.execute(
                "UPDATE driver_info SET latitude=%s, longitude=%s WHERE account_id=%s",
                (lat, lon, self.driver_id),)
            self.conn.commit()

        self.location_job = self.after(10000, self.update_live_location)

    def auto_refresh(self, func):
        if not self.winfo_exists():
            return

        if self.auto_job:
            self.after_cancel(self.auto_job)

        self.auto_job = self.after(5000, func)
    
    def destroy(self):

        if self.auto_job:
            self.after_cancel(self.auto_job)

        if self.time_job:
            self.after_cancel(self.time_job)

        if self.location_job:
            self.after_cancel(self.location_job)

        super().destroy()

    def logout(self):

        if self.auto_job:
            self.after_cancel(self.auto_job)

        if self.time_job:
            self.after_cancel(self.time_job)

        if self.location_job:
            self.after_cancel(self.location_job)

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE driver_info SET online_status='offline' WHERE account_id=%s",
            (self.driver_id,),)
        self.conn.commit()

        from pages.login_page import LoginPage
        self.master.clear_window()
        LoginPage(self.master)
