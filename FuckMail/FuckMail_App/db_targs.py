import re
import imaplib
import socket
from hashlib import md5
from datetime import datetime, timedelta

import psycopg2
import socks
from dateutil import parser

IMAP_SERVERS = {
    "hotmail.com":"imap.outlook.com",
    "outlook.com":"imap.outlook.com",
    "gmail.com":"imap.gmail.com"
}


class IMAP:
    def __init__(self):
        """Inizializate"""

        self.conn = None
        self.cursor = None
        self.db_connect()

    def db_connect(self):
        self.conn = psycopg2.connect(
            dbname="postgres", user="postgres",
            password="fG11xztk", host="localhost")

        self.cursor = self.conn.cursor()

    def set_proxy(self, *args):
        ip, port, username, password = args[0]
        socks.set_default_proxy(socks.HTTP, ip, int(port), True, username, password)
        socket.socket = socks.socksocket

    def get_smtp_server(self, mail_address):
        try:
            return IMAP_SERVERS[mail_address.split("@")[1]]
        except KeyError:
            return None

    def get_all_mails(self):
        self.cursor.execute('SELECT * FROM "FuckMail_App_emails"')
        return self.cursor.fetchall()

    def update_count_messages(self):
        for mail in self.get_all_mails():
            if len(mail[3].split(":")) == 4:
                if self.get_smtp_server(mail[1]) is not None:
                    self.set_proxy(mail[3].split(":"))
                    imap = imaplib.IMAP4_SSL(self.get_smtp_server(mail[1]))
                    imap.login(mail[1], mail[2])
                    imap.select("inbox")
                    #count_messages = res[1][0].decode("utf-8")
                    data = imap.search(None, "ALL")
                    mail_ids = data[1]
                    id_list = mail_ids[0].split()
                    first_email_id = int(id_list[0])
                    latest_email_id = int(id_list[-1])
                    messages = dict()

                    for i in range(latest_email_id,first_email_id, -1):
                        data = imap.fetch(str(i), "(RFC822)")
                        for response_part in data:
                            arr = response_part[0]
                            if isinstance(arr, tuple):
                                msg = imap.message_from_string(str(arr[1], "utf-8"))
                                if self.get_smtp_server() == "imap.outlook.com":
                                    try:
                                        decode_msg_payload = msg.get_payload(decode=True).decode("utf-8")
                                    except:
                                        try:
                                            decode_msg_payload = msg.get_payload(1).get_payload(decode=True).decode("utf-8")
                                        except:
                                            decode_msg_payload = None
                                else:
                                    decode_msg_payload = msg.get_payload(1).get_payload(decode=True).decode("utf-8")

                                # Hash message_id (simple good looks)
                                message_id = md5(re.sub('[^0-9a-zA-Z]+', '', msg["Message-Id"]).encode("utf-8")).hexdigest()
                                # Set message_id and payload for state
                                messages[message_id] = {
                                        "from": msg["from"], "subject": msg["subject"],
                                        "date": self.date_format(msg["date"]), "payload": decode_msg_payload
                                        }
                    print(messages)

    def date_format(self, date_time):
        """This is function take date from email message and formating his."""

        date_time = datetime.strftime(parser.parse(date_time) +  timedelta(hours=3), "%Y-%m-%d %H:%M:%S")
        return date_time

if __name__ == "__main__":
    imap_obj = IMAP()
    imap_obj.update_count_messages()