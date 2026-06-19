import customtkinter as ctk
from tkinter import messagebox
from database import hash_password

class ChangePasswordPage(ctk.CTkFrame):

    def __init__(self, master, user_id):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.master = master
        self.conn = master.conn
        self.user_id = user_id

        ctk.CTkLabel(self, text="Change Password", font=("Arial",24)).pack(pady=20)
        p_frame = ctk.CTkFrame(self, fg_color="transparent")
        p_frame.pack(pady=5)
        ctk.CTkLabel(p_frame,text="New Password",font=("Arial",14,"bold")).pack(anchor="w")
        self.new = ctk.CTkEntry(p_frame, show="*", width=300)
        self.new.pack()

        ctk.CTkLabel(p_frame,text="Confirm Password",font=("Arial",14,"bold")).pack(anchor="w")
        self.re = ctk.CTkEntry(p_frame, show="*", width=300)
        self.re.pack()

        ctk.CTkButton(self, text="Update", command=self.update).pack(pady=20)

    def update(self):

        new = self.new.get()
        re = self.re.get()

        if new != re:
            messagebox.showerror("Error","Password mismatch")
            return

        hashed = hash_password(new)

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE accounts
        SET password=%s, is_first_login=FALSE
        WHERE id=%s
        """,(hashed,self.user_id))

        self.conn.commit()

        messagebox.showinfo("Success","Password updated")

        from pages.login_page import LoginPage
        self.master.clear_window()
        LoginPage(self.master)