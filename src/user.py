
import email
from email.header import decode_header
import imaplib
import smtplib


class User:
    def __init__(self, email: str, password: str, smtp_server: str, smtp_port: int,
                 imap_server: str, imap_port: int):
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port

    def login(self) -> bool:
        try:
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.email, self.password)
            server.quit()
            return True
        except smtplib.SMTPAuthenticationError as e:
            print("Failed to login. Check your email and password.")
            print(e)
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def list_emails(self, limit=10):
        mails = []
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            mail.select("inbox")

            status, messages = mail.search(None, "ALL")

            if not messages or not messages[0]:
                return []

            mail_ids = messages[0].split()
            latest_ids = mail_ids[-limit:]
            latest_ids.reverse()

            for mail_id in latest_ids:
                status, msg_data = mail.fetch(mail_id, "(RFC822)")
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject_header = msg["Subject"]
                        if subject_header:
                            decoded_list = decode_header(subject_header)
                            subject, encoding = decoded_list[0]
                            
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                        else:
                            subject = "(Brak tematu)"
                        
                        mails.append(subject)

            mail.close()
            mail.logout()
            
        except Exception:
            return []
        
        return mails 