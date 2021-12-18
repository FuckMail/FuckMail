from hashlib import md5
from datetime import datetime

from json import dumps

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import login, logout

from rest_framework.generics import ListAPIView

from .models import *
from django.contrib.auth.models import User

from .serializers import *

from .mails.utils import MailsCore


class HttpJavascriptResponse(HttpResponse):
    def __init__(self,content):
       HttpResponse.__init__(self,content,mimetype="text/javascript")


class EmailsView(ListAPIView):
    serializer_class = EmailsSerializer
    def get(self, request):
        queryset = Mails.objects.all()
        serializer = EmailsSerializer(queryset, many=True)
        return HttpResponse(dumps({"data": serializer.data}), content_type='application/json')
    #return Response({"articles": serializer.data})


class CacheMessagesView(ListAPIView):
    serializer_class = CacheMessages
    def get(self, request, mail_address):
        queryset = CacheMessages.objects.filter(address=mail_address).all()
        serializer = CacheMessagesSerializer(queryset, many=True)
        return HttpResponse(dumps({"cachemessages": serializer.data}), content_type='application/json')


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

        username = User.objects.get(pk=request.session["_auth_user_id"]).username
        emails = Mails.objects.filter(user_id=int(request.session["_auth_user_id"])).all()
        if request.POST:
            if "have_mail" in request.POST:
                address = request.POST["have_mail"]
                mails = MailsCore(mail_address=address).all()
                if mails["status"] == "error":
                    return render(request, "500.html", {"message": mails["message"]})
                elif mails["status"] == "success":
                    messages = list(reversed(mails["messages"]))
            elif "search_mail" in request.POST:
                mail = Mails.objects.filter(address=request.POST["search_mail"])
                if mail.exists():
                    address = request.POST["search_mail"]
                    messages = CacheMessages.objects.filter(address=address).order_by("date").all()
                else:
                    return render(request, "500.html", {"message": "Account is not found!"})
            return render(request, "index.html", {"emails": emails, "messages": messages,
                    "address":address, "username":username,
                    "is_new_account":is_new_account})
        else:
            return render(request, "index.html", {"emails":emails, "username":username, "is_new_account":is_new_account})
    else:
        return redirect("index")

def add_account(request):
    mail_address = request.POST["mail-address"]
    mail_password = request.POST["mail-password"]
    proxy_url = request.POST["proxy-url"]

    # Check proxy format
    if len(proxy_url.split(":")) != 4:
        # Set data for new account before redirect
        request.session["add_new_account"] = {"status":True, "type": "Error",
            "message": "Неверный формат адреса proxy!"}
    else:
         # Check mail format
        if len(mail_address.split("@")) != 2:
            # Set data for new account before redirect
            request.session["add_new_account"] = {"status":True, "type": "Error",
                "message": "Неверный формат адреса от почты!"}
        else:
            Mails.objects.create(
                user_id=request.session["_auth_user_id"], address=mail_address,
                password=mail_password, proxy_url=proxy_url)
            # Set data for new account before redirect
            request.session["add_new_account"] = {"status":True, "type": "Success",
                "message": "Аккаунт <b>%s</b> был успешно добавлен!" % mail_address}
    return redirect("profile")

def message_more_info(request, payload):
    return render(request, "message_more_info.html", {"message": CacheMessages.objects.get(message_id=payload).payload})

def read_message(request):
    if request.is_ajax():
        mail_address = CacheMessages.objects.filter(message_id=request.POST["message_id"]).get()
        mail_address.visual = True
        mail_address.save()
    return HttpResponse(dumps(True), content_type="application/json")

def logout_user(request):
    logout(request)
    return redirect("index")