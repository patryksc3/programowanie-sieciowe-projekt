from user import User
import tkinter as tk
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Client")
        self.root.geometry("800x600")
        self.saved_users = []

        self.login_screen()

    def login_screen(self):
        self.frame_container = tk.Frame(self.root, padx=20, pady=20)
        self.frame_container.pack(fill="both", expand=True)
        self.frame_container.columnconfigure(0, weight=1)
        self.frame_container.columnconfigure(1, weight=1)

        self.frame_login = tk.Frame(self.frame_container, padx=10, pady=10)
        self.frame_login.grid(row=0, column=0, sticky="nsew")

        # Email Label and Entry
        tk.Label(self.frame_login, text="Email:").grid(row=0, column=0, sticky="e")
        self.entry_email = tk.Entry(self.frame_login, width=30)
        self.entry_email.grid(row=0, column=1, pady=5)

        # Password Label and Entry
        tk.Label(self.frame_login, text="Password:").grid(row=1, column=0, sticky="e")
        self.entry_password = tk.Entry(self.frame_login, show="*", width=30)
        self.entry_password.grid(row=1, column=1, pady=5)

        #smtp server and port
        tk.Label(self.frame_login, text="SMTP Server:").grid(row=2, column=0, sticky="e")
        self.entry_smtp_server = tk.Entry(self.frame_login, width=30)
        self.entry_smtp_server.grid(row=2, column=1, pady=5)

        tk.Label(self.frame_login, text="SMTP Port:").grid(row=3, column=0, sticky="e")
        self.entry_smtp_port = tk.Entry(self.frame_login, width=30)
        self.entry_smtp_port.grid(row=3, column=1, pady=5)

        #imap server and port
        tk.Label(self.frame_login, text="IMAP Server:").grid(row=4, column=0, sticky="e")
        self.entry_imap_server = tk.Entry(self.frame_login, width=30)
        self.entry_imap_server.grid(row=4, column=1, pady=5)

        tk.Label(self.frame_login, text="IMAP Port:").grid(row=5, column=0, sticky="e")
        self.entry_imap_port = tk.Entry(self.frame_login, width=30)
        self.entry_imap_port.grid(row=5, column=1, pady=5)

        # Login Button
        self.btn_login = tk.Button(self.frame_login, text="Login", command=self.handle_login)
        self.btn_login.grid(row=6, columnspan=2, pady=10)

        # Saved Logins Listbox and Button
        self.frame_saved = tk.Frame(self.frame_container, padx=10, pady=10)
        self.frame_saved.grid(row=0, column=1, sticky="nsew")
        tk.Label(self.frame_saved, text="Saved logins").pack(anchor="w")
        self.listbox_saved = tk.Listbox(self.frame_saved, width=40, height=18)
        self.listbox_saved.pack(fill="both", expand=True, pady=5)
        self.listbox_saved.bind("<Double-Button-1>", lambda _: self.handle_saved_login())
        self.btn_login_saved = tk.Button(self.frame_saved, text="Login selected", command=self.handle_saved_login)
        self.btn_login_saved.pack(pady=(5, 0))

        self.saved_users = User.load_saved_users()
        for saved in self.saved_users:
            self.listbox_saved.insert(tk.END, saved["email"])


    def handle_login(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        smtp_server = self.entry_smtp_server.get()
        imap_server = self.entry_imap_server.get()
        smtp_port = self.entry_smtp_port.get()
        imap_port = self.entry_imap_port.get()
        if not email or not password or not smtp_server or not imap_server or not smtp_port or not imap_port:
            print("Error", "Please fill in all fields.")
            return

        self.user = User(email, password, smtp_server, smtp_port, imap_server, imap_port)
        if self.user.login():
            print("Success, Logged in successfully!")
            self.user.save_to_db()
            self.frame_container.destroy()
            self.mailbox_screen()

    def handle_saved_login(self):
        if not self.saved_users:
            print("Error", "No saved logins found.")
            return

        selection = self.listbox_saved.curselection()
        if not selection:
            print("Error", "Select a saved login first.")
            return

        saved = self.saved_users[selection[0]]

        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, saved["email"])

        self.entry_password.delete(0, tk.END)
        self.entry_password.insert(0, saved["password"])

        self.entry_smtp_server.delete(0, tk.END)
        self.entry_smtp_server.insert(0, saved["smtp_server"])

        self.entry_smtp_port.delete(0, tk.END)
        self.entry_smtp_port.insert(0, str(saved["smtp_port"]))

        self.entry_imap_server.delete(0, tk.END)
        self.entry_imap_server.insert(0, saved["imap_server"])

        self.entry_imap_port.delete(0, tk.END)
        self.entry_imap_port.insert(0, str(saved["imap_port"]))

        self.handle_login()
      
    def mailbox_screen(self):
        self.frame_mailbox = tk.Frame(self.root, padx=20, pady=20)
        self.frame_mailbox.pack(expand=True)
        tk.Label(self.frame_mailbox, text="Inbox").pack()
        self.listbox_emails = tk.Listbox(self.frame_mailbox, width=100, height=30)
        self.listbox_emails.pack(pady=10)

        emails = self.user.list_emails()
        for email in emails:
            self.listbox_emails.insert(tk.END, email)