import re
import email
import socket
import imaplib
from json import loads
from hashlib import md5
from datetime import datetime as dt
from dateutil import parser

import socks
import requests

from ..models import *

IMAP_SERVERS = {
    "hotmail.com": "imap.outlook.com",
    "outlook.com": "imap.outlook.com",
    "gmail.com": "imap.gmail.com"
}

class MailsCore:
    def __init__(self, user_id: int, mail_address: str):
        """Initialzation
        Call functions: get_mail_data; get_proxy_url
        :param: mail_address
        :type: str
        """
        self.user_id = user_id
        self.mail_address = mail_address
        self.mail_data = self.get_mail_data(user_id=user_id, mail_address=self.mail_address)
        self.proxy_address = self.get_proxy_url(user_id=user_id, mail_address=self.mail_address)

    def all(self):
        """This is function get all messages
        :return: Dictionary with data
        Data structure -> Own: status, message; Another: proxy, messages
        """

        check_proxy = self.check_proxy(proxy_address=self.proxy_address)
        if not check_proxy:
            return {"status": "error", "message": "Is not correct proxy address!"}
        else:
            try:
                proxy = loads(requests.post("https://api.myip.com").text)
            except Exception as e:
                return {"status": "error", "message": str(e)}
            messages = self.check_last_messages(self.user_id, self.mail_address)
            return {"status": "success", "proxy": proxy, "messages": messages}

    def check_last_messages(self, user_id: int, mail_address: str):
        """This is function check last message
        :param: mail_address
        :type: str
        :return: All cache messages
        :rtype: CacheMessages
        """

        mails = CacheMessages.objects.filter(user_id=user_id, address=mail_address)
        host = self.get_host(mail_address=mail_address)
        mail = imaplib.IMAP4_SSL(host)
        mail.login(self.mail_data[0], self.mail_data[1])
        mail.select("INBOX")

        if not mails.exists():
            code, data = mail.search(None, "ALL")
            if code == "OK" and bool(data[0].decode("utf-8")):
                mail_ids = data[0].split()
                for i in mail_ids:
                    data = mail.fetch(i.decode("utf-8"), "(RFC822)")
                    for response in data:
                        message_array = response[0]
                        if isinstance(message_array, tuple):
                            message = email.message_from_string(str(message_array[1], "utf-8"))
                            if host == "imap.outlook.com":
                                try:
                                    decode_message_payload = message.get_payload(decode=True).decode("utf-8")
                                except:
                                    try:
                                        decode_message_payload = message.get_payload(1).get_payload(decode=True).decode("utf-8")
                                    except:
                                        decode_message_payload = None
                            else:
                                decode_message_payload = message.get_payload().get_payload(decode=True).decode("utf-8")

                            message_id = md5(re.sub('[^0-9a-zA-Z]+', '', message["Message-Id"]).encode("utf-8")).hexdigest()
                            CacheMessages.objects.create(
                                message_id=message_id, address=mail_address,
                                from_user=self.decode_format(message["from"]), subject=self.decode_format(message["subject"]),
                                date=self.date_format(message["date"]), payload=decode_message_payload, user_id=user_id
                            )
            _messages = CacheMessages.objects.filter(user_id=user_id, address=mail_address).order_by("date").all()
            return _messages
        else:
            last_mail_date = CacheMessages.objects.filter(user_id=user_id, address=mail_address).order_by("-date")[0]
            last_date = dt.strftime(last_mail_date.date, "%d-%b-%Y")
            code, data = mail.search(None, '(SINCE "%s" UNSEEN)' % last_date)
            if code == "OK" and bool(data[0].decode("utf-8")):
                mail_ids = data[0].split()

                for i in mail_ids:
                    data = mail.fetch(i.decode("utf-8"), "(RFC822)")
                    for response_part in data:
                        arr = response_part[0]
                        if isinstance(arr, tuple):
                            message = email.message_from_string(str(arr[1], "utf-8"))
                            if host == "imap.outlook.com":
                                try:
                                    decode_message_payload = message.get_payload(decode=True).decode("utf-8")
                                except:
                                    try:
                                        decode_message_payload = message.get_payload(1).get_payload(decode=True).decode("utf-8")
                                    except:
                                        decode_message_payload = None
                            else:
                                decode_message_payload = message.get_payload().get_payload(decode=True).decode("utf-8")

                            message_id = md5(re.sub('[^0-9a-zA-Z]+', '', message["Message-Id"]).encode("utf-8")).hexdigest()
                            CacheMessages.objects.create(
                                message_id=message_id, address=mail_address,
                                from_user=self.decode_format(message["from"]), subject=self.decode_format(message["subject"]),
                                date=self.date_format(message["date"]), payload=decode_message_payload, user_id=user_id
                            )
            _messages = CacheMessages.objects.filter(user_id=user_id, address=mail_address).order_by("date").all()
            return _messages

    def get_new_messages(self):
        _messages = dict()
        host = self.get_host(mail_address=self.mail_address)
        mail = imaplib.IMAP4_SSL(host)
        mail.login(self.mail_data[0], self.mail_data[1])
        mail.select("INBOX")
        last_mail_date = CacheMessages.objects.filter(user_id=self.user_id, address=self.mail_address).order_by("-date")[0]
        last_date = dt.strftime(last_mail_date.date, "%d-%b-%Y")
        code, data = mail.search(None, '(SINCE "%s" UNSEEN)' % last_date)
        if code == "OK" and bool(data[0].decode("utf-8")):
            mail_ids = data[0].split()

            for i in mail_ids:
                data = mail.fetch(i.decode("utf-8"), "(RFC822)")
                for response_part in data:
                    arr = response_part[0]
                    if isinstance(arr, tuple):
                        message = email.message_from_string(str(arr[1], "utf-8"))
                        if host == "imap.outlook.com":
                            try:
                                decode_message_payload = message.get_payload(decode=True).decode("utf-8")
                            except:
                                try:
                                    decode_message_payload = message.get_payload(1).get_payload(decode=True).decode("utf-8")
                                except:
                                    decode_message_payload = None
                        else:
                            decode_message_payload = message.get_payload().get_payload(decode=True).decode("utf-8")

                        message_id = md5(re.sub('[^0-9a-zA-Z]+', '', message["Message-Id"]).encode("utf-8")).hexdigest()
                        is_mail = CacheMessages.objects.filter(user_id=self.user_id, address=self.mail_address, message_id=message_id)
                        if not is_mail.exists():
                            CacheMessages.objects.create(
                                message_id=message_id, address=self.mail_address,
                                from_user=self.decode_format(message["from"]), subject=self.decode_format(message["subject"]),
                                date=self.date_format(message["date"]), payload=decode_message_payload, user_id=self.user_id
                            )
                            _messages["message_id"] = message_id
                            _messages["from_user"] = self.decode_format(message["from"])
                            _messages["subject"] = self.decode_format(message["subject"])
                            _messages["date"] = self.date_format(message["date"])
                            _messages["payload"] = decode_message_payload
        return _messages

    def get_mail_data(self, user_id: int, mail_address: str):
        """This is function get mail data (address and password)
        :param: mail_address
        :type: str
        :return: address and password
        :rtype: tuple
        """

        data = Mails.objects.filter(user_id=user_id, address=mail_address).get()
        return data.address, data.password

    def get_proxy_url(self, user_id: int, mail_address: str):
        """This is function get proxy from mail data
        :param: mail_address
        :type: str
        :return: Mail proxy url
        :rtype: str
        """

        mail = Mails.objects.filter(user_id=user_id, address=mail_address).get()
        return mail.proxy_url

    def get_host(self, mail_address: str):
        """This is function get mail host from mail data
        :param: mail_address
        :type: str
        :return: IMAP host
        :rtype: str
        """

        return IMAP_SERVERS[mail_address.split("@")[1]]

    def check_proxy(self, protocol_type=socks.HTTP, proxy_address: str = ""):
        """This is function check proxy address
        :param: protocol_type (default: socks.HTTP)
        :type: None
        :param: proxy_address
        :type: str
        :return: code (0 - false, 1 - true)
        :rtype: int
        """

        if len(proxy_address.split(":")) != 4:
            return 0
        else:
            ip, port, username, password = proxy_address.split(":")
            socks.set_default_proxy(protocol_type, ip, int(port), True, username, password)
            socket.socket = socks.socksocket
            return 1

    def date_format(self, datetime: str):
        """This is function formats got date from message
        :param: datetime
        :type: str
        :return: date_format
        :rtype: str
        """

        date_format = dt.strftime(parser.parse(datetime), "%Y-%m-%d %H:%M:%S")
        return date_format

    def decode_format(self, subject):
        """This is function decode subject format
            receive subject param and return decode subject
        :param: subject
        :type: str
        :return: subject
        :rtype: str
        """

        subject = subject.split("=?UTF-8?")[0]
        if not subject:
            return "Unknow"
        return subject