import re
import socket
import imaplib
import email
from hashlib import md5
from datetime import datetime, timedelta

import socks
from dateutil import parser
from django.urls import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout

from .models import *
from django.contrib.auth.models import User


# Myself imap servers
IMAP_SERVERS = {
    "hotmail.com":"imap.outlook.com",
    "outlook.com":"imap.outlook.com",
    "gmail.com":"imap.gmail.com"
}

# Myself error codes
ERRORS_CODE = {
    1132016//1:"Invalid proxy format! (Example: ip:port:username:password)",
    1132016//2:"Invalid proxy port!",
    1132016//3:"Invalid mail address!",
    1132016//4:"Invalid mail domen!"
}

class EmailStruct:
    def __init__(self, mail_data: Emails):
        """Inizializate all params"""

        self.mail = None
        self.mail_data = mail_data
        self.smtp_server = self.get_smtp_server()

    def auth(self):
        res = self.proxyauth()
        if isinstance(res, int):
            return ERRORS_CODE[res]
        else:
            smtp_server_res = self.smtp_server
            if isinstance(smtp_server_res, int):
                return ERRORS_CODE[smtp_server_res]
            try:
                self.mail = imaplib.IMAP4_SSL(smtp_server_res)
                self.mail.login(self.mail_data.address, self.mail_data.password)
                self.get_message_type()
            except Exception as e:
                return str(e)

    def read_all_messages(self):
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
                    #PAYLOAD_STATES[message_id] = decode_msg_payload
                    messages[message_id] = {
                            "from": msg["from"], "subject": msg["subject"],
                            "date": self.date_format(msg["date"]), "payload": decode_msg_payload
                            }
        return messages

    def get_smtp_server(self):
        """This is function set smtp server."""

        try:
            imap_server = IMAP_SERVERS[self.mail_data.address.split("@")[1]]
            return imap_server
        except IndexError:
            return 1132016//3
        except KeyError:
            return 1132016//4

    def get_message_type(self):
        """Function set message type"""

        return self.mail.select("inbox")

    def proxyauth(self, protocol_type=socks.HTTP):
        """This is function authorizate proxy server.
        If function get error then return myself error code ;)
        """

        if len(self.mail_data.proxy_url.split(":")) != 4:
            return 1132016//1
        else:
            try:
                ip, port, username, password = self.mail_data.proxy_url.split(":")
                socks.set_default_proxy(protocol_type, ip, int(port), True, username, password)
                socket.socket = socks.socksocket
            except ValueError:
                return 1132016//2

    def date_format(self, date_time):
        """This is function take date from email message and formating his."""

        date_time = datetime.strftime(parser.parse(date_time) +  timedelta(hours=3), "%Y-%m-%d %H:%M:%S")
        return date_time


class HttpJavascriptResponse(HttpResponse):
    def __init__(self,content):
       HttpResponse.__init__(self,content,mimetype="text/javascript")

def index(request):
    if request.user.is_authenticated:
        return redirect("profile")
    else:
        if request.POST:
            username = request.POST["username"]
            password = request.POST["password"]
            hash_password = md5(password.encode("utf-8")).hexdigest()
            if not username or not password:
                return render(request, "login.html", {"message":"Поля не должны оставаться пустыми!"})

            if "register-button" in request.POST:
                    user = User.objects.filter(username=username).exists()
                    if not user:
                        user = User.objects.create(username=username, password=hash_password, is_staff=True)
                        login(request, user)
                        return redirect("profile")
                    else:
                        return render(request, "login.html", {"message":"Пользователь с таким юзернейм существует!"})
            elif "login-button" in request.POST:
                user = User.objects.filter(username=username, password=hash_password)
                if user.exists():
                    user = user.get()
                    user.last_login = datetime.now()
                    user.save()
                    login(request, user)
                    return redirect("profile")
                else:
                    return render(request, "login.html", {"message":"Пользователь не существует!"})
        return render(request, "login.html")

def profile(request):
    if request.user.is_authenticated:
        try:
            is_new_account = request.session["add_new_account"]
        except KeyError:
            is_new_account = {"status": False}
        request.session["add_new_account"] = {"status": False}
        data = None
        check_auth = None
        emailStruct = None
        username = User.objects.get(pk=request.session["_auth_user_id"]).username
        emails = Emails.objects.all()

        if request.POST:
            if "email" in request.POST:
                mail = Emails.objects.filter(address=request.POST["email"])
                if mail.exists():
                    address = request.POST["email"]
                    cache_messages = CacheMessages.objects.filter(address=address).all()
                else:
                    return render(request, "500.html", {"message": "Account is not found!"})
            elif "email_address" in request.POST:
                mail = Emails.objects.filter(address=request.POST["email_address"])
                if mail.exists():
                    address = request.POST["email_address"]
                    cache_messages = CacheMessages.objects.filter(address=address).all()
                else:
                    return render(request, "500.html", {"message": "Account is not found!"})

            if isinstance(check_auth, str):
                return render(request, "500.html", {"message": check_auth})
            #data = emailStruct.read_all_messages()
            return render(request, "index.html", {"emails": emails, "messages": cache_messages, 
                    "address":address, "count_messages":len(cache_messages), "username":username,
                    "is_new_account":is_new_account})
        else:
            return render(request, "index.html", {"emails":emails, "username":username, "is_new_account":is_new_account})
    else:
        return redirect("index")

def add_account(request):
    mail_address = request.POST["mail-address"]
    mail_password = request.POST["mail-password"]
    proxy_url = request.POST["proxy-url"]

    if len(proxy_url.split(":")) != 4:
        request.session["add_new_account"] = {"status":True, "type": "Error",
            "message": "Неверный формат proxy!"}
    else:
        if len(mail_address.split("@")) != 2:
            request.session["add_new_account"] = {"status":True, "type": "Error",
                "message": "Неверный формат адреса от почты!"}
        else:
            Emails.objects.create(
                user_id=request.session["_auth_user_id"], address=mail_address,
                password=mail_password, proxy_url=proxy_url
            )
            request.session["add_new_account"] = {"status":True, "type": "Success",
                "message": "Аккаунт <b>%s</b> был успешно добавлен!" % mail_address}
    return redirect("profile")

def message_more_info(request, payload):
    return render(request, "message_more_info.html", {"message": CacheMessages.objects.get(message_id=payload).payload})

def logout_user(request):
    logout(request)
    return redirect("index")