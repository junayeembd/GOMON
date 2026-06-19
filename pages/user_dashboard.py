import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from database import check_password, hash_password
from tkintermapview import TkinterMapView
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import geocoder



FARE_PER_KM = {
"Bike":23,
"CNG":26,
"Private Car":30,
"Micro":33
}

RENT_PER_HOUR = {
"Bike":200,
"CNG":250,
"Private Car":450,
"Micro":500,
"Bus":850,
"Truck":700,
"Mini Truck":650
}
class UserDashboard(ctk.CTkFrame):

    def __init__(self, master, user):

        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.master = master
        self.user = user
        self.conn = master.conn
        self.current_page = "home"
        self.build_ui()

    def build_ui(self):

        top = ctk.CTkFrame(self, height=60)
        top.pack(fill="x")

        ctk.CTkLabel(top,text="GOMON", font=("Arial",24,"bold")).pack(side="left",padx=20)
        ctk.CTkLabel(top, text=f"Hello {self.user['name']}").pack(side="left")

        self.time = ctk.CTkLabel(top)
        self.time.pack(side="right",padx=20)
        self.update_time()

        main = ctk.CTkFrame(self)
        main.pack(fill="both",expand=True)

        sidebar = ctk.CTkFrame(main,width=200)
        sidebar.pack(side="left",fill="y")

        menus = [
        ("🏠Home",self.show_home),
        ("🚘Active Ride",self.show_active),
        ("💬Message",self.show_message),
        ("🖼️Ride History",self.show_history),
        ("👤Profile",self.show_profile),
        ("🚕Rent Vehicle",self.show_rent),
        ("🔔Notifications", self.show_notifications),
        ("✂️Logout",self.logout)]

        for name,cmd in menus:
            ctk.CTkButton(sidebar,text=name,width=180,height=40,corner_radius=8,font=("Arial",14),command=cmd).pack(pady=6)

        self.content = ctk.CTkScrollableFrame(main)
        self.content.pack(side="right",fill="both",expand=True)
        self.show_home()


    def update_time(self):

        now = datetime.now().strftime("%d %B %Y | %H:%M:%S")
        self.time.configure(text=now)
        self.after(1000,self.update_time)


    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_home(self):
        self.current_page ="home"
        self.clear()

        container=ctk.CTkFrame(self.content, corner_radius=10)
        container.pack(pady=20)

        ctk.CTkLabel(container,text="🚕 Book a Ride",font=("Arial",26,"bold")).pack(pady=20)

        self.pickup = ctk.CTkEntry(container,placeholder_text="Pickup location",width=300)
        self.pickup.pack(pady=5)

        self.drop = ctk.CTkEntry(container,placeholder_text="Drop location",width=300)
        self.drop.pack(pady=5)

        self.distance = ctk.CTkEntry(container,placeholder_text="Distance KM",width=300)
        self.distance.pack(pady=5)

        self.vehicle = ctk.CTkOptionMenu(container,values=["Select","Bike","CNG","Private Car","Micro","Truck","Pickup"])
        self.vehicle.pack(pady=10)

        fare_card=ctk.CTkFrame(container)
        fare_card.pack(pady=10)
        self.fare_label = ctk.CTkLabel(fare_card,text="Estimated Fare:--",font=("Arial",16,"bold"))
        self.fare_label.pack()

        self.time_label = ctk.CTkLabel(fare_card,text="Estimated Time:--")
        self.time_label.pack()

        btn_frame = ctk.CTkFrame(container)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame,text="💰 Calculate Fare",width=140,command=self.calculate_fare).grid(row=0,column=0,padx=10)

        ctk.CTkButton(btn_frame,text="🚗 Request Ride",fg_color="#16a34a",width=140,command=self.request_ride).grid(row=0,column=1,padx=10)

        map_frame = ctk.CTkFrame(container)
        map_frame.pack(pady=15)

        self.user_map = TkinterMapView(map_frame,width=700,height=300)
        self.user_map.pack()

        if not self.detect_live_location():
            self.user_map.set_position(23.8103, 90.4125)
            self.user_map.set_zoom(12)

    def calculate_fare(self):

        self.user_map.delete_all_marker()
        self.user_map.delete_all_path()

        pickup = self.pickup.get().strip()
        drop = self.drop.get().strip()
        vehicle = self.vehicle.get()

        if not pickup or not drop:
            messagebox.showerror("Error","Enter pickup and drop location")
            return

        if vehicle == "Select":
            messagebox.showerror("Error","Select vehicle type")
            return

        pickup_coord = self.get_coordinates(pickup)
        drop_coord = self.get_coordinates(drop)

        if not pickup_coord or not drop_coord:
            messagebox.showerror("Error","Location not found")
            return

        distance = geodesic(pickup_coord, drop_coord).km
        self.distance.delete(0, "end")
        self.distance.insert(0, f"{distance:.2f}")

        fare = round(distance * FARE_PER_KM[vehicle])
        est_time = int(distance * 5)
        self.fare_label.configure(text=f"Estimated Fare: {fare} BDT")

        self.time_label.configure(text=f"Estimated Time: {est_time} minute")

        self.user_map.delete_all_marker()

        self.user_map.set_position(pickup_coord[0],pickup_coord[1])
        self.user_map.set_zoom(12)

        self.user_map.set_marker(pickup_coord[0],pickup_coord[1],text="Pickup")

        self.user_map.set_marker(drop_coord[0],drop_coord[1],text="Drop")
        self.user_map.set_path([pickup_coord,drop_coord])

    def request_ride(self):

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(""" SELECT id FROM rides WHERE user_id=%s AND ride_status IN ('searching','accepted','started')""",
                       (self.user["id"],))

        if cursor.fetchone():
            messagebox.showerror("Ride","You already have an active ride")
            return

        pickup = self.pickup.get()
        drop = self.drop.get()
        distance = self.distance.get()
        vehicle = self.vehicle.get()

        if vehicle == "Select":
            messagebox.showerror("Error","Select vehicle")
            return

        if not pickup or not drop or not distance:
            messagebox.showerror("Error","Fill all fields")
            return
        
        try:
            km = float(distance)
        except:
            messagebox.showerror("Error","Invalid distance")
            return

        fare = km * FARE_PER_KM[vehicle]

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO rides
        (user_id,pickup,drop_location,distance,vehicle_type,fare,ride_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s) """,(self.user["id"],pickup,drop,km,vehicle,fare,'searching'))

        self.conn.commit()

        messagebox.showinfo("Ride","Ride request sent")

    def show_active(self):
        self.current_page = "active"
        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT * FROM rides
        WHERE user_id=%s AND ride_status IN ('searching','accepted','started')
        ORDER BY id DESC LIMIT 1 """,(self.user["id"],))

        ride = cursor.fetchone()

        if not ride:

            cursor.execute("""SELECT * FROM rides WHERE user_id=%s AND ride_status='completed' AND (rating IS NULL OR rating=0)
                            ORDER BY id DESC LIMIT 1""", (self.user["id"],))

            ride = cursor.fetchone()

            if not ride:
                ctk.CTkLabel(self.content,text="No active ride").pack(pady=30)
                return

        ctk.CTkLabel(self.content,
        text=f"Pickup: {ride['pickup']}").pack()

        ctk.CTkLabel(self.content,
        text=f"Drop: {ride['drop_location']}").pack()

        ctk.CTkLabel(self.content,
        text=f"Vehicle: {ride['vehicle_type']}").pack()

        ctk.CTkLabel(self.content,
        text=f"Fare: {ride['fare']}").pack()

        map_frame = ctk.CTkFrame(self.content)
        map_frame.pack(pady=20)

        ride_map = TkinterMapView(
            map_frame,
            width=700,
            height=300
        )
        ride_map.pack()

        pickup_coord = self.get_coordinates(ride["pickup"])
        drop_coord = self.get_coordinates(ride["drop_location"])

        cursor.execute("""
        SELECT di.latitude, di.longitude
        FROM driver_info di
        JOIN rides r ON di.account_id = r.driver_id WHERE r.id=%s""",(ride["id"],))

        driver_loc = cursor.fetchone()

        if driver_loc and driver_loc["latitude"] and driver_loc["longitude"]:
            ride_map.set_marker(
                driver_loc["latitude"],
                driver_loc["longitude"],
                text="Driver"
            )

        if pickup_coord and drop_coord:

            ride_map.set_position(
                pickup_coord[0],
                pickup_coord[1])
            ride_map.set_zoom(12)

            ride_map.set_marker(
                pickup_coord[0],
                pickup_coord[1],
                text="Pickup")

            ride_map.set_marker(drop_coord[0],drop_coord[1],text="Drop")

            ride_map.set_path([pickup_coord,drop_coord])

        status = ride["ride_status"]

        if status == "accepted":
            color = "#f59e0b"
        elif status == "started":
            color = "#3b82f6"
        elif status == "searching":
            color = "gray"
        else:
            color = "#16a34a"

        ctk.CTkLabel(self.content, text=f"Status: {status}", text_color=color, font=("Arial",16,"bold")).pack()

        state = "disabled" if ride["ride_status"] == "started" else "normal"

        ctk.CTkButton(self.content,text="Cancel Ride",fg_color="red",state=state,command=lambda: self.cancel_ride
                      (ride["id"])).pack()

        if (ride["ride_status"] == "completed" and (ride["rating"] is None or ride["rating"] == 0)):

            ctk.CTkLabel(self.content,text="Rate Your Ride").pack(pady=10)

            self.rating_menu = ctk.CTkOptionMenu(self.content,values=["1","2","3","4","5"])
            self.rating_menu.pack()

            self.review_box = ctk.CTkTextbox(self.content,width=400,height=100)
            self.review_box.pack(pady=10)

            ctk.CTkButton(self.content,text="Submit Review",command=lambda: self.submit_review(ride["id"])).pack()

        if self.current_page == "active":
            self.after(10000, self.show_active)
    
    def submit_review(self, ride_id):

        try:
            rating = int(self.rating_menu.get())
        except:
            messagebox.showerror("Error", "Select rating")
            return

        review = self.review_box.get("1.0", "end").strip()
        if rating < 1 or rating > 5:
            messagebox.showerror("Error", "Rating must be between 1 and 5")
            return
        if len(review) > 300:
            messagebox.showerror("Error", "Review too long")
            return

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(""" SELECT rating FROM rides WHERE id=%s """, (ride_id,))

        ride = cursor.fetchone()
        if ride and ride["rating"] is not None:
            messagebox.showerror("Error", "You already submitted review")
            return
        cursor.execute(""" UPDATE rides SET rating=%s, review=%s WHERE id=%s """, (rating, review, ride_id))

        cursor.execute(""" SELECT driver_id FROM rides WHERE id=%s """, (ride_id,))

        data = cursor.fetchone()
        if data and data["driver_id"]:
            cursor.execute(""" INSERT INTO notifications(user_id, message) VALUES(%s,%s) """, ( data["driver_id"], f"You received {rating}⭐ rating from passenger"))
        self.conn.commit()
        messagebox.showinfo("Success", "Review submitted successfully")
        self.show_active()

    def show_message(self):
        self.current_page = "message"
        self.clear()

        ctk.CTkLabel(self.content, text="Driver Chat / Contact",font=("Arial",24,"bold")).pack(pady=20)

        chat_frame = ctk.CTkFrame(self.content)
        chat_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.chat_box = ctk.CTkTextbox(chat_frame,width=700, height=350 )
        self.chat_box.pack(padx=10, pady=10, fill="both", expand=True)

        self.chat_box.configure(state="normal")

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(""" SELECT id FROM rides WHERE user_id=%s ORDER BY id DESC LIMIT 1 """,(self.user["id"],))

        ride = cursor.fetchone()

        if ride:

            cursor.execute(""" SELECT sender_role, message, created_at FROM messages WHERE ride_id=%s ORDER BY id ASC """,(ride
            ["id"],))

            messages = cursor.fetchall()

            if not messages:
                self.chat_box.insert("end", "No messages yet.\n")
            else:
                for m in messages:

                    sender = "You" if m["sender_role"] == "user" else "Driver"
                    time = m["created_at"].strftime("%H:%M")
                    self.chat_box.insert("end", f"[{time}] {sender}: {m['message']}\n")

        else:
            self.chat_box.insert("end","No active ride found.\n")

        self.chat_box.see("end")

        msg_frame = ctk.CTkFrame(self.content)
        msg_frame.pack(pady=10)

        self.chat_input = ctk.CTkEntry(msg_frame, width=500, placeholder_text="Type your message...")
        self.chat_input.pack(side="left", padx=10)

        ctk.CTkButton( msg_frame, text="Send", width=100, command=self.send_message).pack(side="left")

        if self.current_page == "message":
            self.after(10000, self.show_message)

    def show_history(self):

        self.clear()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(""" SELECT pickup, drop_location, fare, ride_status, rating, review FROM rides WHERE user_id=%s ORDER BY id DESC """,(self.user["id"],))
        
        rides = cursor.fetchall()
        table = ctk.CTkFrame(self.content)
        table.pack(pady=20)
        headers=["Pickup","Drop","Fare","Status","Rating","Review"]

        for i,h in enumerate(headers):
            ctk.CTkLabel(table, text=h, font=("Arial",14,"bold") ).grid(row=0,column=i,padx=10,pady=5)

        for r,row in enumerate(rides,start=1):
            ctk.CTkLabel(table,text=row["pickup"]).grid(row=r,column=0,padx=10)
            ctk.CTkLabel(table,text=row["drop_location"]).grid(row=r,column=1,padx=10)
            ctk.CTkLabel(table,text=row["fare"]).grid(row=r,column=2,padx=10)
            ctk.CTkLabel(table,text=row["ride_status"]).grid(row=r,column=3,padx=10)
            ctk.CTkLabel(table,text=row["rating"] or "-").grid(row=r,column=4,padx=10)
            ctk.CTkLabel(table,text=row["review"] or "-").grid(row=r,column=5,padx=10)
    
    def show_notifications(self):

        self.clear()

        ctk.CTkLabel(self.content,text="Notifications",font=("Arial",24,"bold")).pack(pady=20)

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute("""SELECT message, created_at FROM notifications WHERE user_id=%s ORDER BY id DESC """,(self.user["id"],))

        notes = cursor.fetchall()

        for n in notes:
            box = ctk.CTkFrame(self.content)
            box.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(box,text=n["message"],anchor="w").pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(box,text=str(n["created_at"]),text_color="gray").pack(anchor="e", padx=10)


    def show_rent(self):

        self.clear()

        ctk.CTkLabel( self.content, text="Rent Vehicle", font=("Arial",24,"bold")).pack(pady=20)

        self.rent_pickup = ctk.CTkEntry( self.content, placeholder_text="Pickup location", width=350)
        self.rent_pickup.pack(pady=5)

        self.rent_destination = ctk.CTkEntry( self.content, placeholder_text="Destination", width=350)
        self.rent_destination.pack(pady=5)

        ctk.CTkLabel(self.content,text="Vehicle Type").pack()

        self.rent_vehicle = ctk.CTkOptionMenu(
            self.content,
            values=[
            "Select",
            "Bike",
            "Private Car",
            "CNG",
            "Micro",
            "Bus",
            "Truck",
            "Mini Truck"])
        self.rent_vehicle.pack(pady=5)
        ctk.CTkLabel(self.content,text="Rent Date").pack()

        self.rent_date = DateEntry( self.content,
            width=18,
            background="darkblue",
            foreground="white",
            borderwidth=2)
        self.rent_date.pack(pady=5)

        ctk.CTkLabel(self.content,text="Rent Time").pack()

        self.rent_time = ctk.CTkEntry(
            self.content,
            placeholder_text="HH:MM (example 14:30)",
            width=350 )
        self.rent_time.pack(pady=5)
        self.rent_hours = ctk.CTkEntry(
            self.content,
            placeholder_text="How many hours?",
            width=350)   
        self.rent_hours.pack(pady=5)

        ctk.CTkButton(
            self.content,
            text="Calculate Rent",
            command=self.calculate_rent
        ).pack(pady=10)

        ctk.CTkButton(
            self.content,
            text="Confirm Rent",
            fg_color="green",
            command=self.confirm_rent
        ).pack(pady=10)

    def calculate_rent(self):

        try:
            hours = float(self.rent_hours.get())
        except:
            messagebox.showerror("Error","Enter valid hours")
            return

        vehicle = self.rent_vehicle.get()
        if vehicle == "Select":
            messagebox.showerror("Error", "Select vehicle type")
            return

        rate = RENT_PER_HOUR[vehicle]

        total = hours * rate

        messagebox.showinfo(
            "Rent Cost",
            f"Total Rent: {total} BDT"
        )
    
    def confirm_rent(self):

        pickup = self.rent_pickup.get()
        destination = self.rent_destination.get()
        vehicle = self.rent_vehicle.get()
        hours = self.rent_hours.get()
        date = self.rent_date.get_date()
        time = self.rent_time.get()

        if not pickup or not destination or not hours or not time:
            messagebox.showerror("Error","Fill all fields")
            return

        hours = float(hours)

        price = hours * RENT_PER_HOUR[vehicle]

        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO rentals
            (user_id,pickup,destination,vehicle_type,hours,price,rent_date,rent_time)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,(
            self.user["id"],
            pickup,
            destination,
            vehicle,
            hours,
            price,
            date,time
        ))

        self.conn.commit()

        messagebox.showinfo(
            "Success","Vehicle rented successfully")

    def show_profile(self):

        self.clear()

        ctk.CTkLabel(
        self.content,
        text="Edit Profile",
        font=("Arial",24,"bold")
        ).pack(pady=20)

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
        "SELECT * FROM accounts WHERE id=%s",
        (self.user["id"],)
        )

        user = cursor.fetchone()

        self.name = ctk.CTkEntry(self.content,width=350)
        self.name.insert(0,user["name"])
        self.name.pack(pady=5)

        self.username = ctk.CTkEntry(self.content,width=350)
        self.username.insert(0,user["username"])
        self.username.pack(pady=5)

        self.email = ctk.CTkEntry(self.content,width=350)
        self.email.insert(0,user["email"])
        self.email.pack(pady=5)

        self.phone = ctk.CTkEntry(self.content,width=350)
        self.phone.insert(0,user["phone"])
        self.phone.pack(pady=5)

        self.address = ctk.CTkEntry(self.content,width=350)
        self.address.insert(0,user["address"])
        self.address.pack(pady=5)

        ctk.CTkLabel(self.content,text="Enter Password to Save Changes").pack(pady=(20,5))

        self.password_confirm = ctk.CTkEntry(
        self.content,
        show="*",
        placeholder_text="Current Password",
        width=350
        )
        self.password_confirm.pack(pady=5)

        ctk.CTkButton(
        self.content,
        text="Save Changes",
        command=self.update_profile
        ).pack(pady=20)

        ctk.CTkButton(
        self.content,
        text="Change Password",
        fg_color="orange",
        command=self.change_password_ui
        ).pack()
        

    def update_profile(self):

        name = self.name.get()
        username = self.username.get()
        email = self.email.get()
        phone = self.phone.get()
        address = self.address.get()
        password = self.password_confirm.get()

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT password FROM accounts WHERE id=%s",
            (self.user["id"],)
        )

        result = cursor.fetchone()

        if not check_password(password,result["password"]):
            messagebox.showerror("Error","Password incorrect")
            return

        
        cursor.execute(
            "SELECT id FROM accounts WHERE username=%s AND id!=%s",
            (username,self.user["id"]))

        if cursor.fetchone():
            messagebox.showerror("Error","Username already exists")
            return

        cursor.execute("SELECT id FROM accounts WHERE email=%s AND id!=%s",
        (email,self.user["id"]))

        if cursor.fetchone():
            messagebox.showerror("Error","Email already exists")
            return

        cursor.execute(
            "SELECT id FROM accounts WHERE phone=%s AND id!=%s",
            (phone,self.user["id"])
        )

        if cursor.fetchone():
            messagebox.showerror("Error","Phone already exists")
            return

        if username != username.lower():
            messagebox.showerror("Error","Username must contain only small letters")
            return

        cursor.execute("""
            UPDATE accounts
            SET name=%s,
            username=%s,
            email=%s,
            phone=%s,
            address=%s
            WHERE id=%s
            """,(name,username,email,phone,address,self.user["id"]))

        self.conn.commit()

        messagebox.showinfo("Success","Profile updated successfully")

    def change_password_ui(self):

        self.clear()

        ctk.CTkLabel(self.content,text="Change Password",font=("Arial",24)).pack(pady=20)

        self.old_pass = ctk.CTkEntry(self.content,show="*",placeholder_text="Old Password",width=350)
        self.old_pass.pack(pady=5)

        self.new_pass = ctk.CTkEntry(self.content,show="*",placeholder_text="New Password",width=350)
        self.new_pass.pack(pady=5)

        self.retype_pass = ctk.CTkEntry(self.content,show="*",placeholder_text="Retype Password",width=350)
        self.retype_pass.pack(pady=5)

        ctk.CTkButton(
            self.content,
            text="Update Password",
            command=self.update_password
        ).pack(pady=20)

        ctk.CTkButton(
            self.content,
            text="⬅ Back",
            fg_color="gray",
            command=self.show_profile
        ).pack(pady=5)

    def update_password(self):

        old = self.old_pass.get()
        new = self.new_pass.get()
        retype = self.retype_pass.get()

        if new != retype:
            messagebox.showerror("Error","Passwords do not match")
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT password FROM accounts WHERE id=%s",
            (self.user["id"],)
        )

        result = cursor.fetchone()

        if not check_password(old,result["password"]):
            messagebox.showerror("Error","Old password incorrect")
            return

        hashed = hash_password(new)

        cursor.execute(
            "UPDATE accounts SET password=%s WHERE id=%s",
            (hashed,self.user["id"])
        )

        self.conn.commit()

        messagebox.showinfo("Success","Password updated")
    
    def cancel_ride(self, ride_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE rides SET ride_status='cancelled' WHERE id=%s",
            (ride_id,)
        )
        self.conn.commit()
        messagebox.showinfo("Ride","Ride cancelled")
        self.show_active()

    def send_message(self):

        msg = self.chat_input.get().strip()

        if msg == "":
            return

        cursor = self.conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT id
        FROM rides
        WHERE user_id=%s
        AND ride_status IN ('accepted','started')
        ORDER BY id DESC
        LIMIT 1
        """,(self.user["id"],))

        ride = cursor.fetchone()

        if not ride:
            messagebox.showerror(
                "Message",
                "No active ride found"
            )
            return

        cursor.execute("""
        INSERT INTO messages(ride_id, sender_role, message)
        VALUES(%s,%s,%s)
        """,(ride["id"], "user", msg))

        self.conn.commit()

        self.chat_box.insert(
            "end",
            f"[{datetime.now().strftime('%H:%M')}] You: {msg}\n")

        self.chat_box.see("end")

        self.chat_input.delete(0, "end")

    def get_coordinates(self, place):

        geolocator = Nominatim(user_agent="gomon")

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

                self.user_map.set_position(lat, lon)
                self.user_map.set_zoom(14)

                self.user_map.set_marker(
                    lat,
                    lon,
                    text="Your Live Location"
                )

                return True
        except:
            pass

        return False

    def logout(self):

        from pages.login_page import LoginPage

        self.master.clear_window()
        LoginPage(self.master)