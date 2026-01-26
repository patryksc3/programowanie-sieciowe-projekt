
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import smtplib
import sqlite3


class User:
    def __init__(self, email: str, password: str, smtp_server: str, smtp_port: int,
                 imap_server: str, imap_port: int):
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.current_ids = []

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
            mail.select("INBOX")

            status, messages = mail.search(None, "ALL")

            if not messages or not messages[0]:
                return []

            mail_ids = messages[0].split()
            latest_ids = mail_ids[-limit:]
            latest_ids.reverse()

            self.current_ids = latest_ids

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
                                if encoding == "unknown-8bit":
                                    encoding = "utf-8"
                                try:
                                    subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                                except LookupError:
                                    subject = subject.decode("utf-8", errors="ignore")
                        else:
                            subject = "(Brak tematu)"
                        
                        mails.append(subject)

            mail.close()
            mail.logout()

        except Exception as e:
            print(f"Błąd pobierania listy: {e}")
            return []
        
        return mails 

    def save_to_db(self):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    smtp_server TEXT NOT NULL,
                    smtp_port INTEGER NOT NULL,
                    imap_server TEXT NOT NULL,
                    imap_port INTEGER NOT NULL
                )
            ''')
            
            # Check if email exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (self.email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET password = ?, smtp_server = ?, smtp_port = ?, imap_server = ?, imap_port = ?
                    WHERE email = ?
                ''', (self.password, self.smtp_server, self.smtp_port, self.imap_server, self.imap_port, self.email))
            else:
                # Insert new user
                cursor.execute('''
                    INSERT INTO users (email, password, smtp_server, smtp_port, imap_server, imap_port)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.email, self.password, self.smtp_server, self.smtp_port, self.imap_server, self.imap_port))
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}") 

    @staticmethod
    def load_saved_users():
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    smtp_server TEXT NOT NULL,
                    smtp_port INTEGER NOT NULL,
                    imap_server TEXT NOT NULL,
                    imap_port INTEGER NOT NULL
                )
            ''')

            cursor.execute('''
                SELECT email, password, smtp_server, smtp_port, imap_server, imap_port
                FROM users
                ORDER BY id DESC
            ''')
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "email": row[0],
                    "password": row[1],
                    "smtp_server": row[2],
                    "smtp_port": row[3],
                    "imap_server": row[4],
                    "imap_port": row[5],
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def delete_from_db(email: str):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE email = ?', (email,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def get_email_body(self, index):
        if index >= len(self.current_ids):
            return "Błąd: Nie znaleziono wiadomości.", "Nieznany nadawca"

        mail_id = self.current_ids[index]
        body = ""
        sender = ""

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email, self.password)
            mail.select("inbox")

            status, msg_data = mail.fetch(mail_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = msg.get("From", "Nieznany nadawca")

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if "attachment" not in content_disposition:
                                if content_type == "text/plain":
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                        break
                                    except:
                                        pass
                                elif content_type == "text/html" and not body:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                    except:
                                        pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            mail.close()
            mail.logout()

        except Exception as e:
            return f"Błąd pobierania treści: {e}", "Błąd"

        return body, sender

    def send_email(self, to_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()

            return True, "Wiadomość wysłana pomyślnie."
        except Exception as e:
            print(f"Błąd wysyłania: {e}")
            return False, f"Błąd: {e}"