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
from loguru import logger
from dataclasses import dataclass

from ..models import *

IMAP_SERVERS = {
    "hotmail.com": "imap.outlook.com",
    "outlook.com": "imap.outlook.com",
    "gmail.com": "imap.gmail.com"
}

class MailsCore:
    def __init__(self, user_id: int = 0, mail_address: str = ""):
        """Initialzation.

        Parameters
        ----------
            user_id : int
                This is user id. Default 0.
            mail_address : str:
                This is mail address. Default is empty string.
        """

        if bool(user_id) and mail_address:
            self.user_id: int = user_id
            self.mail_address: str = mail_address
            self.mail_data = self.get_mail_data(user_id=user_id, mail_address=self.mail_address) # Call for receive mail data.
            self.proxy_address = self.get_proxy_url(user_id=user_id, mail_address=self.mail_address) # Call for receive proxy address.

    #@logger.catch
    def all(self):
        """This is function get all messages.

        Returns
        -------
            Dictionary with data. Data structure is status, proxy, messages.
            Status type is error or success. If status is error then return one message\n
            else return more messages from imap server.
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
        """This is function check last message.\n
        Get all data from imap server and save in the database. After return CacheMessages instance.

        Parameters
        ----------
            user_id : int
                This is user id.
            mail_address : str:
                This is mail address.

        Returns
        -------
            The messages. CacheMessages instance.
        """

        custom_user = CustomUser.objects.filter(user_id=user_id).get()
        if not custom_user.is_cache:
            return self.is_not_cache_messages(user_id=user_id, mail_address=mail_address)
        else:
            return self.cache_messages(user_id=user_id, mail_address=mail_address)

        """mails = CacheMessages.objects.filter(user_id=user_id, address=mail_address) # Get all message from CacheMessages model.
        host = self.get_host(mail_address=mail_address) # Get imap host.
        mail = imaplib.IMAP4_SSL(host) # Init IMAP4_SSL class.
        mail.login(self.mail_data[0], self.mail_data[1]) # Auth mail address.
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
            code, data = mail.search(None, '(SINCE "%s")' % last_date)
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
                                    message_id=message_id, address=mail_address,
                                    from_user=self.decode_format(message["from"]), subject=self.decode_format(message["subject"]),
                                    date=self.date_format(message["date"]), payload=decode_message_payload, user_id=user_id
                                )
            _messages = CacheMessages.objects.filter(user_id=user_id, address=mail_address).order_by("date").all()
            return _messages"""

    def cache_messages(self, user_id: int, mail_address: str):
        cache_messages = CacheMessages.objects.filter(user_id=user_id, address=mail_address)
        if not cache_messages.exists():
            host = self.get_host(mail_address=mail_address) # Get imap host.
            mail = imaplib.IMAP4_SSL(host) # Init IMAP4_SSL class.
            mail.login(self.mail_data[0], self.mail_data[1]) # Auth mail address.
            mail.select("INBOX")
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
                            is_mail = CacheMessages.objects.filter(user_id=self.user_id, address=self.mail_address, message_id=message_id)
                            if not is_mail.exists():
                                CacheMessages.objects.create(
                                    message_id=message_id, address=mail_address,
                                    from_user=self.decode_format(message["from"]), subject=self.decode_format(message["subject"]),
                                    date=self.date_format(message["date"]), payload=decode_message_payload, user_id=user_id
                                )
        _messages = CacheMessages.objects.filter(user_id=user_id, address=mail_address).order_by("date").all()
        return _messages

    def is_not_cache_messages(self, user_id: int, mail_address: str) -> dict:
        _messages = list()
        host = self.get_host(mail_address=mail_address) # Get imap host.
        mail = imaplib.IMAP4_SSL(host) # Init IMAP4_SSL class.
        mail.login(self.mail_data[0], self.mail_data[1]) # Auth mail address.
        mail.select("INBOX")

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

                        @dataclass
                        class IsNotCacheMessage:
                            message_id: str
                            from_user: str
                            subject: str
                            date: str
                            payload: str

                        isNotCacheMessage = IsNotCacheMessage(message_id=message_id, from_user=self.decode_format(message["from"]),
                            subject=self.decode_format(message["subject"]), date=self.date_format(message["date"]),
                            payload=decode_message_payload)
                        _messages.append(isNotCacheMessage)
        return _messages

    def get_new_messages(self):
        """This is function get new messages.\n
        Get new messages from imap server. Function check messages each 5 seconds.

        Returns
        -------
            The new messages. Dictionary instance(message id, from, subject, date, payload).
        """

        _messages = dict() # Init new dictionary instance.
        host = self.get_host(mail_address=self.mail_address)
        mail = imaplib.IMAP4_SSL(host)
        mail.login(self.mail_data[0], self.mail_data[1])
        mail.select("INBOX")
        last_mail_date = CacheMessages.objects.filter(user_id=self.user_id, address=self.mail_address).order_by("-date")[0] # Get last message by date.
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
    
    def get_message_by_id(self, messageId: str):
        """The function get message by message id.

        Parameters
        ----------
            messageId : str
                This is message id.

        Returns
        -------
            Decode message payload. Decode paylod need for view in the desktop program.
        """

        host = self.get_host(mail_address=self.mail_address)
        mail = imaplib.IMAP4_SSL(host)
        mail.login(self.mail_data[0], self.mail_data[1])
        mail.select("INBOX")
        typ, data = mail.search(None, '(HEADER Message-ID "%s")' % messageId)
        if typ == "OK" and bool(data[0].decode("utf-8")):
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
        return decode_message_payload

    def get_mail_data(self, user_id: int, mail_address: str):
        """This is function get mail data (address and password).

        Parameters
        ----------
            user_id : int
                This is user id.
            mail_address : str
                This is mail address.

        Returns
        -------
            address : str
            password : str
        """

        data = Mails.objects.filter(user_id=user_id, address=mail_address).get()
        return data.address, data.password

    def get_proxy_url(self, user_id: int, mail_address: str):
        """This is function get proxy from mail data.

        Parameters
        ----------
            user_id : int
                This is user id.
            mail_address : str
                This is mail address.

        Returns
        -------
            proxy url : str
        """

        mail = Mails.objects.filter(user_id=user_id, address=mail_address).get()
        return mail.proxy_url

    def get_host(self, mail_address: str):
        """This is function get mail host from mail data.

        Parameters
        ----------
            mail_address : str
                This is mail address.

        Returns
        -------
            imap server : str
        """

        return IMAP_SERVERS[mail_address.split("@")[1]]

    def check_proxy(self, protocol_type=socks.HTTP, proxy_address: str = ""):
        """This is function check proxy address.

        Parameters
        ----------
            protocol_type : HTTP
                This is HTTP type from socks HTTP class.

        Returns
        -------
            0 or 1 : int\n
            0 is incorrect proxy url, 1 is correct proxy url.
        """

        if len(proxy_address.split(":")) != 4:
            return 0
        else:
            ip, port, username, password = proxy_address.split(":")
            socks.set_default_proxy(protocol_type, ip, int(port), True, username, password)
            socket.socket = socks.socksocket
            return 1

    def date_format(self, datetime: str):
        """This is function formats got date from message.

        Parameters
        ----------
            datetime : str
                The datetime from mail message.

        Returns
        -------
            date_format : str
        """

        date_format = dt.strftime(parser.parse(datetime), "%Y-%m-%d %H:%M:%S")
        return date_format

    def decode_format(self, subject):
        """This is function decode subject format receive subject param and return decode subject.

        Parameters
        ----------
        subject : str
            The subject from mail message.

        Returns
        -------
            subject : str
                Formated subject.
        """

        subject = subject.split("=?UTF-8?")[0]
        if not subject:
            return "Unknow"
        return subject