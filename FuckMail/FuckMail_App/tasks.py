import re
import imaplib
import socket
import email
from hashlib import md5
from datetime import timedelta

from dateutil import parser
from loguru import logger
import socks
from celery import shared_task

from .models import *

IMAP_SERVERS = {
    "hotmail.com":"imap.outlook.com",
    "outlook.com":"imap.outlook.com",
    "gmail.com":"imap.gmail.com"
}

class UpdateMessages:
    def __init__(self, mails: Emails, cache_messages: CacheMessages):
        self.mail = None
        self.mails = mails.objects.all()

    def update_messages_ins(self):
        for mail in self.mails:
            self.auth_proxy(mail.proxy_url)
            self.auth_mail(mail.address, mail.password)
            #if isinstance(res_proxy, str):
            #    return logger.error("Proxy -> " + res_proxy, "Mail -> " + res_mail)
            data = self.mail.search(None, "ALL")
            mail_ids = data[1]
            id_list = mail_ids[0].split()
            first_email_id = int(id_list[0])
            latest_email_id = int(id_list[-1])

            messages = dict()

            for i in range(latest_email_id,first_email_id, -1):
                data = self.mail.fetch(str(i), "(RFC822)")
                for response_part in data:
                    arr = response_part[0]
                    if isinstance(arr, tuple):
                        msg = email.message_from_string(str(arr[1], "utf-8"))
                        if self.get_smtp_server(mail.address) == "imap.outlook.com":
                            try:
                                decode_msg_payload = msg.get_payload(decode=True).decode("utf-8")
                            except:
                                try:
                                    decode_msg_payload = msg.get_payload(1).get_payload(decode=True).decode("utf-8")
                                except:
                                    decode_msg_payload = None
                        else:
                            decode_msg_payload = msg.get_payload(1).get_payload(decode=True).decode("utf-8")

                        message_id = md5(re.sub('[^0-9a-zA-Z]+', '', msg["Message-Id"]).encode("utf-8")).hexdigest()
                        cache_obj = CacheMessages.objects.filter(message_id=message_id)

                        if not cache_obj.exists():
                            CacheMessages.objects.create(message_id=message_id, address=mail.address,
                                from_user=msg["from"], subject=msg["subject"],
                                date=self.date_format(msg["date"]), payload=decode_msg_payload,
                                visual=False)

    def auth_mail(self, address, password):
        smtp_server = self.get_smtp_server(address)
        if isinstance(smtp_server, int):
            return logger.error("Invalid proxy format!")

        try:
            self.mail = imaplib.IMAP4_SSL(smtp_server)
            self.mail.login(address, password)
            self.mail.select("inbox")
        except Exception as e:
            return str(e)

    def auth_proxy(self, proxy_url):
        try:
            if len(proxy_url.split(":")) != 4:
                return "Invalid proxy format!"
            ip, port, username, password = proxy_url.split(":")
            socks.set_default_proxy(socks.HTTP, ip, int(port), True, username, password)
            socket.socket = socks.socksocket
        except Exception as e:
            return logger.error(e)

    def get_smtp_server(self, address):
        """This is function set smtp server."""

        try:
            imap_server = IMAP_SERVERS[address.split("@")[1]]
            return imap_server
        except IndexError:
            return 1132016//3
        except KeyError:
            return 1132016//4

    def date_format(self, date_time):
        """This is function take date from email message and formating his."""

        date_time = datetime.strftime(parser.parse(date_time) +  timedelta(hours=3), "%Y-%m-%d %H:%M:%S")
        return date_time


@shared_task
def update_messages():
    updateMessages = UpdateMessages(Emails, CacheMessages)
    updateMessages.update_messages_ins()

# celery --app FuckMail worker -l INFO
# celery -A FuckMail beat -l INFO
# celery --app FuckMail worker -l INFO --pool=solo