from user import User
import tkinter as tk
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Client")
        self.root.geometry("800x600")

        self.login_screen()

    def login_screen(self):
        self.frame_login = tk.Frame(self.root, padx=20, pady=20)
        self.frame_login.pack(expand=True)

        # Email Label and Entry
        tk.Label(self.frame_login, text="Email:").grid(row=0, column=0, sticky="e")
        self.entry_email = tk.Entry(self.frame_login, width=30)
        self.entry_email.grid(row=0, column=1, pady=5)

        # Password Label and Entry
        tk.Label(self.frame_login, text="Password:").grid(row=1, column=0, sticky="e")
        self.entry_password = tk.Entry(self.frame_login, show="*", width=30)
        self.entry_password.grid(row=1, column=1, pady=5)

        # Login Button
        self.btn_login = tk.Button(self.frame_login, text="Login", command=self.handle_login)
        self.btn_login.grid(row=2, columnspan=2, pady=10)

    def handle_login(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        if not email or not password:
            print("Error", "Please enter both email and password.")
            return

        self.user = User(email, password)
        if self.user.login():
            print("Success, Logged in successfully!")
            #TODO: save account to local database
            self.frame_login.destroy()
            self.mailbox_screen()
      
    def mailbox_screen(self):
        self.frame_mailbox = tk.Frame(self.root, padx=20, pady=20)
        self.frame_mailbox.pack(expand=True)
        tk.Label(self.frame_mailbox, text="Inbox").pack()
        self.listbox_emails = tk.Listbox(self.frame_mailbox, width=100, height=30)
        self.listbox_emails.pack(pady=10)

        emails = self.user.list_emails()
        for email in emails:
            self.listbox_emails.insert(tk.END, email)