import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

from database import authenticate_user
import pages

from style import (
    BG_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    TEXT_COLOR,
    FONT
)


class Sidebar(tk.Frame):
    def __init__(self, parent, on_navigate, on_logout, active_page="Dashboard"):
        super().__init__(
            parent,
            bg=CARD_COLOR,
            width=230
        )

        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.active_page = active_page
        self.nav_buttons = {}

        # Prevent the sidebar from shrinking
        self.pack_propagate(False)

        # LOGO SECTION
        logo_frame = tk.Frame(self, bg=CARD_COLOR)
        logo_frame.pack(fill="x", pady=(20, 10))

        logo_path = Path(__file__).parent / "assets" / "alaga_logo.png"

        try:
            image = Image.open(logo_path).convert("RGBA")
            image.thumbnail((170, 100), Image.Resampling.LANCZOS)

            self.logo_image = ImageTk.PhotoImage(image)

            tk.Label(
                logo_frame,
                image=self.logo_image,
                bg=CARD_COLOR,
                borderwidth=0
            ).pack(pady=(0, 5))

        except FileNotFoundError:
            tk.Label(
                logo_frame,
                text="ALAGA",
                font=(FONT, 22, "bold"),
                bg=CARD_COLOR,
                fg=PRIMARY_COLOR
            ).pack()

        except Exception as error:
            print("Unable to load ALAGA logo:", error)

            tk.Label(
                logo_frame,
                text="ALAGA",
                font=(FONT, 22, "bold"),
                bg=CARD_COLOR,
                fg=PRIMARY_COLOR
            ).pack()

        tk.Label(
            logo_frame,
            text="LIVESTOCK MANAGEMENT",
            font=(FONT, 8, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=(3, 0))

        # Divider
        tk.Frame(
            self,
            bg=BG_COLOR,
            height=2
        ).pack(fill="x", padx=15, pady=12)

        # NAVIGATION SECTION
        nav_frame = tk.Frame(self, bg=CARD_COLOR)
        nav_frame.pack(fill="both", expand=True, padx=10)

        navigation_items = [
            ("Dashboard", "Dashboard"),
            ("Animals", "Animals"),
            ("Vaccination", "Vaccination"),
            ("Feeding", "Feeding"),
            ("Health Records", "Health Records"),
            ("Breeding", "Breeding"),
            ("Profile", "Profile"),
        ]

        for label, page_name in navigation_items:
            self.create_nav_button(
                nav_frame,
                label,
                page_name
            )

        # LOGOUT SECTION
        logout_frame = tk.Frame(self, bg=CARD_COLOR)
        logout_frame.pack(fill="x", padx=10, pady=15)

        tk.Frame(
            logout_frame,
            bg=BG_COLOR,
            height=1
        ).pack(fill="x", pady=(0, 12))

        self.logout_button = tk.Button(
            logout_frame,
            text="↪  Logout",
            font=(FONT, 10, "bold"),
            bg=CARD_COLOR,
            fg="#D9534F",
            activebackground="#FCE8E6",
            activeforeground="#C0392B",
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            padx=15,
            pady=10,
            command=self.logout
        )
        self.logout_button.pack(fill="x")

    # CREATE NAVIGATION BUTTON
    def create_nav_button(self, parent, label, page_name):
        is_active = page_name == self.active_page

        button = tk.Button(
            parent,
            text=f"   {label}",
            font=(FONT, 10, "bold" if is_active else "normal"),
            bg=PRIMARY_COLOR if is_active else CARD_COLOR,
            fg="white" if is_active else TEXT_COLOR,
            activebackground=PRIMARY_COLOR,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            padx=12,
            pady=11,
            command=lambda: self.navigate(page_name)
        )

        button.pack(fill="x", pady=3)
        self.nav_buttons[page_name] = button

    # NAVIGATION FUNCTION
    def navigate(self, page_name):
        self.set_active_page(page_name)
        self.on_navigate(page_name)

    # UPDATE ACTIVE BUTTON
    def set_active_page(self, page_name):
        self.active_page = page_name

        for name, button in self.nav_buttons.items():
            if name == page_name:
                button.configure(
                    bg=PRIMARY_COLOR,
                    fg="white",
                    font=(FONT, 10, "bold")
                )
            else:
                button.configure(
                    bg=CARD_COLOR,
                    fg=TEXT_COLOR,
                    font=(FONT, 10, "normal")
                )

    # LOGOUT FUNCTION
    def logout(self):
        if messagebox.askyesno(
            "Logout",
            "Are you sure you want to log out?"
        ):
            self.on_logout()

# MAIN APPLICATION

class AlagaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ALAGA | Livestock Management System")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        self.current_user = None
        self.sidebar = None
        self.content_frame = None
        self.app_frame = None

        self.show_login()

    # CLEAR ROOT WINDOW
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # LOGIN PAGE
    def show_login(self):
        self.clear_window()

        self.root.configure(bg=BG_COLOR)

        login_container = tk.Frame(
            self.root,
            bg=BG_COLOR
        )
        login_container.pack(
            expand=True,
            fill="both"
        )

        login_card = tk.Frame(
            login_container,
            bg=CARD_COLOR,
            padx=45,
            pady=35,
            highlightthickness=1,
            highlightbackground="#E0E0E0"
        )
        login_card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        tk.Label(
            login_card,
            text="ALAGA",
            font=(FONT, 28, "bold"),
            fg=PRIMARY_COLOR,
            bg=CARD_COLOR
        ).pack(pady=(0, 5))

        tk.Label(
            login_card,
            text="LIVESTOCK MANAGEMENT SYSTEM",
            font=(FONT, 10, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(pady=(0, 25))

        tk.Label(
            login_card,
            text="Welcome Back!",
            font=(FONT, 18, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(pady=(0, 5))

        tk.Label(
            login_card,
            text="Log in to manage your livestock records.",
            font=(FONT, 10),
            fg=TEXT_COLOR,
            bg=CARD_COLOR
        ).pack(pady=(0, 25))

        tk.Label(
            login_card,
            text="Username",
            font=(FONT, 10, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.username_entry = ttk.Entry(
            login_card,
            width=35,
            font=(FONT, 11)
        )
        self.username_entry.pack(
            fill="x",
            ipady=6,
            pady=(0, 15)
        )

        tk.Label(
            login_card,
            text="Password",
            font=(FONT, 10, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.password_entry = ttk.Entry(
            login_card,
            width=35,
            font=(FONT, 11),
            show="*"
        )
        self.password_entry.pack(
            fill="x",
            ipady=6,
            pady=(0, 20)
        )

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        tk.Button(
            login_card,
            text="LOG IN",
            font=(FONT, 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            activebackground=PRIMARY_COLOR,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.login
        ).pack(
            fill="x",
            ipady=8
        )

        tk.Label(
            login_card,
            text="ALAGA | Care for Every Animal",
            font=(FONT, 9),
            fg="#777777",
            bg=CARD_COLOR
        ).pack(pady=(20, 0))

        self.username_entry.focus_set()

    # AUTHENTICATE USER
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your username and password."
            )
            return

        try:
            user = authenticate_user(username, password)

            if not user:
                messagebox.showerror(
                    "Login Failed",
                    "Invalid username or password."
                )
                return

            self.current_user = user
            self.show_dashboard()

        except Exception as error:
            messagebox.showerror(
                "Login Error",
                f"Unable to log in.\n\n{error}"
            )

    # MAIN APPLICATION LAYOUT
    def show_dashboard(self):
        self.clear_window()

        self.root.configure(bg=BG_COLOR)

        self.app_frame = tk.Frame(
            self.root,
            bg=BG_COLOR
        )
        self.app_frame.pack(
            fill="both",
            expand=True
        )

        # Sidebar with custom logo
        self.sidebar = Sidebar(
            parent=self.app_frame,
            on_navigate=self.navigate,
            on_logout=self.logout,
            active_page="Dashboard"
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        # Main content area
        self.content_frame = tk.Frame(
            self.app_frame,
            bg=BG_COLOR
        )
        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.navigate("Dashboard")

    # PAGE NAVIGATION
    def navigate(self, page_name):
        if self.content_frame is None:
            return

        # Clear the previous page
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        try:
            # Update the selected sidebar button
            if self.sidebar:
                self.sidebar.set_active_page(page_name)

            # Load the selected page from pages.py
            pages.show_page(
                self.content_frame,
                page_name,
                user=self.current_user
            )

        except Exception as error:
            messagebox.showerror(
                "Page Loading Error",
                f"Unable to load {page_name}.\n\n{error}"
            )

    # LOGOUT
    def logout(self):
        self.current_user = None
        self.sidebar = None
        self.content_frame = None
        self.app_frame = None

        self.show_login()

# RUN APPLICATION
if __name__ == "__main__":
    root = tk.Tk()
    app = AlagaApp(root)
    root.mainloop()
