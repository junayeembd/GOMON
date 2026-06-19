import customtkinter as ctk
from pages.login_page import LoginPage
from database import connect_db


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GomonApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("GOMON - Ride for Everyone")
        self.geometry("900x600")
        self.resizable(True, True)

        self.conn = connect_db()
        self.show_login()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        LoginPage(self)

if __name__ == "__main__":
    app = GomonApp()
    app.mainloop()
    