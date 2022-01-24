import mimetypes
import os
import traceback
from json import dumps, loads
from hashlib import md5
from datetime import datetime

from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from rest_framework.generics import ListAPIView
from loguru import logger
import requests

from .models import *
from .serializers import *
from .mails.utils import MailsCore


class HttpJavascriptResponse(HttpResponse):
    def __init__(self,content):
       HttpResponse.__init__(self,content,mimetype="text/javascript")


class EmailsView(ListAPIView):
    serializer_class = EmailsSerializer
    def get(self, request):
        queryset: QuerySet = Mails.objects.all()
        serializer = EmailsSerializer(queryset, many=True)
        return HttpResponse(dumps({"data": serializer.data}), content_type='application/json')


class CacheMessagesView(ListAPIView):
    serializer_class = CacheMessages
    def get(self, request, mail_address):
        queryset: QuerySet = CacheMessages.objects.filter(address=mail_address).all()
        serializer = CacheMessagesSerializer(queryset, many=True)
        return HttpResponse(dumps({"cachemessages": serializer.data}), content_type='application/json')


def index(request):
    if request.user.is_authenticated:
        return redirect("profile")
    else:
        if request.POST:
            data: dict = dict()
            username: str = request.POST["username"]
            password: str = request.POST["password"]
            recaptcha_response = request.POST.get("g-recaptcha-response")
            content = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response
                }).text
            hash_password: str = md5(password.encode("utf-8")).hexdigest()
            if not username or not password:
                message: str = "Поля не должны оставаться пустыми!"
                data: dict = dict(
                    message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY)
                return render(request, "login.html", data)
            elif not loads(content)["success"]:
                message: str = "Неверная reCAPTCHA! Попробуйте снова."
                data: dict = dict(
                    message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY)
                return render(request, "login.html", data)

            if "register-button" in request.POST:
                user = User.objects.filter(username=username).exists()
                if not user:
                    user: QuerySet = User.objects.create(username=username, password=hash_password, is_staff=True)
                    login(request, user)
                    return redirect("profile")
                else:
                    message: str = "Пользователь с таким юзернейм существует!"
                    data: dict = dict(
                        message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY)
                    return render(request, "login.html", data)
            elif "login-button" in request.POST:
                user: QuerySet = User.objects.filter(username=username, password=hash_password)
                if user.exists():
                    user: QuerySet = user.get()
                    user.last_login = datetime.now()
                    user.save()
                    login(request, user)
                    return redirect("profile")
                else:
                    message: str = "Пользователь не существует!"
                    data: dict = dict(
                        message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY)
                    return render(request, "login.html", data)
        data: dict = dict(
            GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY)
        return render(request, "login.html", data)

def profile(request):
    if request.user.is_authenticated:
        try:
            is_new_account: dict = request.session["add_new_account"]
        except KeyError:
            is_new_account: dict = {"status": False}
        request.session["add_new_account"] = {"status": False}
        user_id = request.session["_auth_user_id"]
        username: str = User.objects.get(pk=user_id).username
        emails: QuerySet = Mails.objects.filter(user_id=int(user_id)).all()
        if request.POST:
            data: dict = dict()
            if "have_mail" in request.POST:
                address: str = request.POST["have_mail"]
                try:
                    mails: dict = MailsCore(user_id=user_id, mail_address=address).all()
                except Exception as e:
                    logger.error(traceback.format_exc())
                    if str(e) == "Mails matching query does not exist.":
                        data: dict = dict(
                            emails=emails, username=username,
                            is_new_account=is_new_account)
                        return render(request, "index.html", data)
                    else:
                        data: dict = dict(
                            message=str(e), address=address)
                        return render(request, "500.html", data)
                if mails["status"] == "error":
                    data: dict = dict(
                        message=mails["message"], address=address)
                    return render(request, "500.html", data)
                elif mails["status"] == "success":
                    messages: list = list(reversed(mails["messages"]))
            elif "search_mail" in request.POST:
                mail = Mails.objects.filter(user_id=user_id, address=request.POST["search_mail"])
                if mail.exists():
                    address: str = request.POST["search_mail"]
                    messages: list = list(reversed(CacheMessages.objects.filter(user_id=user_id, address=address).order_by("date").all()))
                else:
                    message: str = "Account is not found!"
                    data: dict = dict(
                        message=message)
                    return render(request, "500.html", data)
            emails: list = [mail.address for mail in emails]
            emails.remove(address)
            data: dict = dict(
                emails=emails, messages=messages,
                address=address, username=username,
                is_new_account=is_new_account, first_mail=address,
                mails_length=len(emails)+1)
            return render(request, "index.html", data)
        else:
            data: dict = dict(
                emails=emails, username=username,
                is_new_account=is_new_account, mails_length=len(emails))
            return render(request, "index.html", data)
    else:
        return redirect("index")

def add_account(request):
    if request.user.is_authenticated:
        mail_address: str = request.POST["mail-address"]
        mail_password: str = request.POST["mail-password"]
        proxy_url: str = request.POST["proxy-url"]

        # Check proxy format (alert message)
        if len(proxy_url.split(":")) != 4:
            # Set data for new account before redirect
            data: dict = dict(status=True, type="Error", message="Неверный формат адреса proxy!")
            request.session["add_new_account"] = data
        else:
            # Check mail format (alert message)
            if len(mail_address.split("@")) != 2:
                # Set data for new account before redirect
                data: dict = dict(status=True, type="Error", message="Неверный формат адреса от почты!")
                request.session["add_new_account"] = data
            else:
                Mails.objects.create(
                    user_id=request.session["_auth_user_id"], address=mail_address,
                    password=mail_password, proxy_url=proxy_url)
                # Set data for new account before redirect (alert message)
                data: dict = dict(status=True, type="Success",
                    message=f"Аккаунт <b>{mail_address}</b> был успешно добавлен!")
                request.session["add_new_account"] = data
        return redirect("profile")
    else:
        return redirect("index")

def add_few_accounts(request):
    if request.user.is_authenticated:
        print(request.POST)
        user_id = request.session["_auth_user_id"]
        content = request.POST["content"]
        content_array = content.split("\n")
        for i in range(0, len(content_array), 3):
            mail_address = content_array[i].strip()
            if not Mails.objects.filter(user_id=user_id, address=mail_address).exists():
                password = content_array[i+1].strip()
                proxy = content_array[i+2].strip()
                Mails.objects.create(
                    user_id=user_id, address=mail_address,
                    password=password, proxy_url=proxy)
        return HttpResponse(dumps(True), content_type="application/json")
    else:
        return redirect("index")

def del_all_accounts(request):
    if request.user.is_authenticated:
        user_id = request.session["_auth_user_id"]
        Mails.objects.filter(user_id=user_id).delete()
        return HttpResponse(dumps(True), content_type="application/json")
    else:
        return redirect("index")

def message_more_info(request, payload):
    if request.user.is_authenticated:
        user_id = request.session["_auth_user_id"]
        data: dict = dict(zip(["message"], [CacheMessages.objects.get(user_id=user_id, message_id=payload).payload]))
        return render(request, "message_more_info.html", data)
    else:
        return redirect("index")

def read_message(request):
    if request.user.is_authenticated:
        if request.is_ajax():
            user_id = request.session["_auth_user_id"]
            mail_address: QuerySet = CacheMessages.objects.filter(user_id=user_id, message_id=request.POST["message_id"]).get()
            mail_address.visual = True
            mail_address.save()
        return HttpResponse(dumps(True), content_type="application/json")
    else:
        return redirect("index")

def del_mail(request):
    if request.user.is_authenticated:
        if request.is_ajax():
            user_id = request.session["_auth_user_id"]
            Mails.objects.filter(user_id=user_id, address=request.POST["mail_address"]).delete()
            CacheMessages.objects.filter(user_id=user_id, address=request.POST["mail_address"]).delete()
        return HttpResponse(dumps(True), content_type="application/json")
    else:
        return redirect("index")

def del_mail_from_list(request):
    if request.user.is_authenticated:
        user_id = request.session["_auth_user_id"]
        mail_address = request.POST["mail_address"]
        Mails.objects.filter(user_id=user_id, address=mail_address).delete()
        return HttpResponse(dumps(True), content_type="application/json")
    else:
        return redirect("index")

def get_new_messages(request):
    user_id = request.session["_auth_user_id"]
    mails = MailsCore(user_id=user_id, mail_address=request.POST["mail_address"])
    new_messages = mails.get_new_messages()
    if new_messages:
        return HttpResponse(dumps({"messages": new_messages}), content_type="application/json")
    return HttpResponse(dumps({"messages": ""}), content_type="application/json")

def help(request, fileName):
    if request.user.is_authenticated:
        return render(request, f"help/{fileName}")
    else:
        return redirect("index")

def download_help_file(request, filename="accounts.txt"):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = BASE_DIR + r"/FuckMail_App/media/" + filename
    path = open(filepath, "rb")
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type=mime_type)
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response

def logout_user(request):
    logout(request)
    return redirect("index")