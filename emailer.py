#!/usr/bin/env python3
"""
Emailer class
"""
import smtplib
from email.mime.text import MIMEText


class Emailer:
    """
    Class that sends an email from sender with password
    """

    def __init__(self, sender="", pword="") -> None:
        self.sender = sender
        self.pword = pword

    def setSenderData(self, sender, pword):
        """
        sets the sender info
        """
        self.sender = sender
        self.pword = pword

    def sendEmail(self, subject="", body="", recipients=""):
        """
        Sends an email
        """
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.sender
        if isinstance(recipients, list):
            msg["To"] = ", ".join(recipients)
        else:
            msg["To"] = recipients
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(self.sender, self.pword)
                smtp_server.sendmail(self.sender, recipients, msg.as_string())
            print("Message sent!")
            return True
        except Exception as e:
            print(f"Failed to send {e}")
            return False
