
import smtplib


class User:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.smtp_server = "smtp-mail.outlook.com"
        self.smtp_port = 587
        self.imap_server = "outlook.office365.com"
        self.imap_port = 993

    def login(self) -> bool:
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            return True
        except smtplib.SMTPAuthenticationError:
            print("Failed to login. Check your email and password.")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            server.quit()