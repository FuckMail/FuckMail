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


class API:
    class AuthUserView(ListAPIView):
        serializer_class = User
        def get(self, request, username, password, sessionid):
            queryset: QuerySet = User.objects.filter(username=username, password=password)
            if queryset.exists():
                init_queryset = queryset.get()
                session_queryset: QuerySet = DesktopSessions.objects.filter(user_id=init_queryset.pk)
                if not session_queryset.exists():
                    DesktopSessions.objects.create(user_id=init_queryset.pk, sessionid=sessionid)
                else:
                    desktop_session = DesktopSessions.objects.filter(user_id=init_queryset.pk).update(sessionid=sessionid)
            return HttpResponse(dumps({"response": queryset.exists()}), content_type='application/json')


    class AddressesView(ListAPIView):
        serializer_class = Mails
        def get(self, request, username):
            addresses = list()
            try:
                user_id: QuerySet = User.objects.get(username=username)
                queryset: QuerySet = Mails.objects.filter(user_id=user_id.pk).order_by("address").all()
                addresses = [address.address for address in queryset]
            except Exception as e:
                logger.error(e)
            return HttpResponse(dumps({"addresses": addresses}), content_type='application/json')


    class AddressDataView(ListAPIView):
        serializer_class = Mails
        def get(self, request, username, address):
            data = dict()
            try:
                user_id: QuerySet = User.objects.get(username=username)
                queryset: QuerySet = Mails.objects.get(user_id=user_id.pk, address=address)
                data = dict(
                    address=queryset.address, password=queryset.password,
                    proxy_url=queryset.proxy_url
                )
            except Exception as e:
                logger.error(e)
            return HttpResponse(dumps(dict(data=data)), content_type='application/json')


    class AddAddressView(ListAPIView):
        serializers = Mails
        def get(self, request, username, sessionID, address, password, proxy_url):
            is_session: QuerySet = DesktopSessions.objects.filter(sessionid=sessionID)
            if is_session.exists():
                is_address: QuerySet = Mails.objects.filter(address=address)
                if not is_address.exists():
                    user_id: QuerySet = User.objects.get(username=username)
                    Mails.objects.create(
                        user_id=user_id.pk, address=address,
                        password=password, proxy_url=proxy_url)
                    return HttpResponse(dumps({"response": True}), content_type='application/json')
            return HttpResponse(dumps({"response": False}), content_type='application/json')

    def render_page(request, message_id):
        username, message_id = message_id.split("user")
        message_id, address = message_id.split("address")
        user_id = User.objects.get(username=username)
        mail = MailsCore(user_id=user_id.pk, mail_address=address)
        message = mail.get_message_by_id(message_id)
        data = dict(message=message)
        return render(request, "message_more_info.html", data)

class Web:
    def index(request):
        """The main function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            render or redirect
        """

        if request.user.is_authenticated:
            return redirect("profile") # Redirect to 'profile' page.
        else:
            if request.POST:
                data: dict = dict() # Init data dictionary.
                username: str = request.POST["username"] # Get username from request response.
                password: str = request.POST["password"] # Get password from request response.
                recaptcha_response = request.POST.get("g-recaptcha-response") # Get recaptcha-response from request response.
                content = requests.post('https://www.google.com/recaptcha/api/siteverify',
                    data={'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}).text
                hash_password: str = md5(password.encode("utf-8")).hexdigest() # Convert password to md5 hash.
                if not username or not password:
                    message: str = "Поля не должны оставаться пустыми!" # Set message.
                    data: dict = dict(message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY) # Convert data to dict object.
                    return render(request, "login.html", data) # Render login page with data.
                elif not loads(content)["success"]:
                    message: str = "Неверная reCAPTCHA! Попробуйте снова." # Set message.
                    data: dict = dict(message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY) # Convert data to dict object.
                    return render(request, "login.html", data) # Render login page with data.

                if "register-button" in request.POST:
                    user = User.objects.filter(username=username).exists() # Check user.
                    if not user:
                        user: QuerySet = User.objects.create(username=username, password=hash_password, is_staff=True) # Create new user.
                        login(request, user) # Auth user in the system.
                        return redirect("profile") # Redirect to 'profile' page.
                    else:
                        message: str = "Пользователь с таким юзернейм существует!" # Set message.
                        data: dict = dict(message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY) # Convert data to dict object.
                        return render(request, "login.html", data) # Render login page with data.
                elif "login-button" in request.POST:
                    user: QuerySet = User.objects.filter(username=username, password=hash_password) # Create user object from db.
                    if user.exists():
                        user: QuerySet = user.get() # Get user object from db.
                        user.last_login = datetime.now() # Update datetime in last_login.
                        user.save() # Save changes.
                        login(request, user) # Auth user in the system.
                        return redirect("profile") # Redirect to 'profile' page.
                    else:
                        message: str = "Пользователь не существует!" # Set message.
                        data: dict = dict(message=message, GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY) # Convert data to dict object.
                        return render(request, "login.html", data) # Render login page with data.
            data: dict = dict(GOOGLE_RECAPTCHA_PUBLIC_KEY=settings.GOOGLE_RECAPTCHA_PUBLIC_KEY) # Convert data to dict object.
            return render(request, "login.html", data) # Render login page with data.

    def profile(request):
        """The 'profile' function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            If user auth then 'render'.
            If user is not auth then 'redirect'.
        """

        if request.user.is_authenticated:
            try:
                is_new_account: dict = request.session["add_new_account"] # Get new account data from request session.
            except KeyError:
                is_new_account: dict = {"status": False} # Set false status if is not new account data.
            request.session["add_new_account"] = {"status": False}
            user_id = request.session["_auth_user_id"] # Get user id.
            username: str = User.objects.get(pk=user_id).username # Get username from db by user id.
            mails: QuerySet = Mails.objects.filter(user_id=int(user_id)).all() # Get mails from db.
            if request.POST:
                data: dict = dict() # Init dict object.
                if "have_mail" in request.POST: # Is have mail.
                    address: str = request.POST["have_mail"] # Get mail address from request.
                    try:
                        mails_core: dict = MailsCore(user_id=user_id, mail_address=address).all() # Get all mails from MailsCore object.
                    except Exception as e:
                        if str(e) == "Mails matching query does not exist.":
                            data: dict = dict(mails=mails, username=username, is_new_account=is_new_account)
                            return render(request, "index.html", data)
                        else:
                            data: dict = dict(message=str(e), address=address)
                            return render(request, "500.html", data)
                    # Check mails status.
                    if mails_core["status"] == "error":
                        data: dict = dict(message=mails_core["message"], address=address)
                        return render(request, "500.html", data)
                    elif mails_core["status"] == "success":
                        messages: list = list(reversed(mails_core["messages"])) # Reversed messages from MailsCore object in the 'all' function.
                elif "search_mail" in request.POST: # Is search mail.
                    mail = Mails.objects.filter(user_id=user_id, address=request.POST["search_mail"]) # Get mail object from db.
                    if mail.exists():
                        address: str = request.POST["search_mail"] # Get mail address from request response.
                        messages: list = list(reversed(
                            CacheMessages.objects.filter(user_id=user_id, address=address).order_by("date").all())) # Get all messages from CacheMessages object by date.
                    else:
                        message: str = "Account is not found!"
                        data: dict = dict(message=message)
                        return render(request, "500.html", data)
                mails: list = [mail.address for mail in mails]
                mails.remove(address)
                data: dict = dict(mails=mails, messages=messages, address=address, username=username,
                    is_new_account=is_new_account, first_mail=address, mails_length=len(mails)+1) # Convert data to dict object.
                return render(request, "index.html", data)
            else:
                data: dict = dict(mails=mails, username=username,
                    is_new_account=is_new_account, mails_length=len(mails)) # Convert data to dict object.
                return render(request, "index.html", data)
        else:
            return redirect("index") # Redirect to 'index' page.

    def add_account(request):
        """The 'add account' function.\n
        If user auth then before redirect to set a new account data in the request session.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect
        """

        if request.user.is_authenticated:
            mail_address: str = request.POST["mail-address"] # Get mail address from request response.
            mail_password: str = request.POST["mail-password"] # Get mail password from request response.
            proxy_url: str = request.POST["proxy-url"] # Get proxy url from request response.

            # Check proxy format (alert message)
            if len(proxy_url.split(":")) != 4:
                message_text: str = "Неверный формат адреса proxy!" # Set message text.
                message_type: str = "Error" # Set message type.
            else:
                # Check mail format (alert message)
                if len(mail_address.split("@")) != 2:
                    message_text: str = "Неверный формат адреса от почты!" # Set message text.
                    message_type: str = "Error" # Set message type.
                else:
                    user_id = request.session["_auth_user_id"] # Get user id from request session.
                    mail = Mails.objects.filter(user_id=user_id, address=mail_address) # Get mail object from db.
                    if not mail.exists():
                        Mails.objects.create(user_id=request.session["_auth_user_id"], address=mail_address,
                            password=mail_password, proxy_url=proxy_url) # Create new mail object in the db.
                        message_text: str = f"Аккаунт <b>{mail_address}</b> был успешно добавлен!" # Set message text.
                        message_type: str = "Success" # Set message type.
                    else:
                        message_text: str = "Адресс уже существует!" # Set message text.
                        message_type: str = "Error" # Set message type.
            data: dict = dict(status=True, type=message_type, message=message_text) # Convert data to dict object.
            request.session["add_new_account"] = data # Set data in request session.
            return redirect("profile") # Redirect to 'profile' page.
        else:
            return redirect("index") # Redirect to 'index' page.

    def add_few_accounts(self, request):
        """The 'add few accounts' function.\n
        Read txt file and set data to HttpResponse at js.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect or HttpResponse
        """

        if request.user.is_authenticated:
            user_id = request.session["_auth_user_id"] # Get user id from request response.
            content = request.POST["content"] # Get content from request response.
            content_array = content.split("\n") # Seperation content.
            for i in range(0, len(content_array), 3):
                mail_address = content_array[i].strip()
                if not Mails.objects.filter(user_id=user_id, address=mail_address).exists(): # Check mail address in the db.
                    password = content_array[i+1].strip()
                    proxy = content_array[i+2].strip()
                    Mails.objects.create(user_id=user_id, address=mail_address,
                        password=password, proxy_url=proxy) # Create new mail object.
            return HttpResponse(dumps(True), content_type="application/json")
        else:
            return redirect("index") # Redirect to 'index' page.

    def del_all_accounts(request):
        """The 'delete all accounts' function.\n
        Delete all accounts from db.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect or HttpResponse
        """

        if request.user.is_authenticated:
            user_id = request.session["_auth_user_id"] # Get user id from request session.
            Mails.objects.filter(user_id=user_id).delete() # Delete all accounts.
            return HttpResponse(dumps(True), content_type="application/json")
        else:
            return redirect("index")

    def read_message(request):
        """The 'read message' function.\n

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect or HttpResponse
        """

        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.session["_auth_user_id"] # Get user id from request session.
                mail_address: QuerySet = CacheMessages.objects.filter(user_id=user_id, message_id=request.POST["message_id"]).get() # Get mail address object.
                mail_address.visual = True # Set value for mail address visual => True.
                mail_address.save() # Save changes.
            return HttpResponse(dumps(True), content_type="application/json")
        else:
            return redirect("index") # Redirect to 'index' page.

    def del_mail(request):
        """The 'delete mail' function.\n
        Delete mail from db.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            If user is not auth then redirect else HttpResponse
        """

        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.session["_auth_user_id"] # Get user id from request session.
                Mails.objects.filter(user_id=user_id, address=request.POST["mail_address"]).delete() # Delete mail object from db (Mails model).
                CacheMessages.objects.filter(user_id=user_id, address=request.POST["mail_address"]).delete() # Delete messages from db (CacheMessages model).
            return HttpResponse(dumps(True), content_type="application/json")
        else:
            return redirect("index") # Redirect to 'index' page.

    def del_mail_from_list(request):
        """The 'delete mail from list' function.\n
        Delete mail address from list by right click.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect or HttpResponse
        """

        if request.user.is_authenticated:
            user_id = request.session["_auth_user_id"] # Get user id from request session.
            mail_address = request.POST["mail_address"] # Get mail address from request response.
            Mails.objects.filter(user_id=user_id, address=mail_address).delete() # Delete mail object from db (Mails model).
            CacheMessages.objects.filter(user_id=user_id, address=request.POST["mail_address"]).delete() # Delete messages from db (CacheMessages model).
            return HttpResponse(dumps(True), content_type="application/json")
        else:
            return redirect("index") # Redirect to 'index' page.

    def get_new_messages(request):
        """The 'get new messages' function.\n
        Get new messages from imap server.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            HttpResponse
        """

        user_id = request.session["_auth_user_id"] # Get user id from request session.
        mails = MailsCore(user_id=user_id, mail_address=request.POST["mail_address"])
        new_messages = mails.get_new_messages()
        if new_messages:
            return HttpResponse(dumps({"messages": new_messages}), content_type="application/json")
        return HttpResponse(dumps({"messages": ""}), content_type="application/json")

    def help(request, fileName):
        """The 'help' function.\n
        Get help.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            if user auth then HttpResponse else redirect
        """

        if request.user.is_authenticated:
            return render(request, f"help/{fileName}")
        else:
            return redirect("index") # Redirect to 'index' page.

    def download_help_file(request, filename="accounts.txt"):
        """The 'download help file' function.\n
        Download file which to give help of user. In the file example correct and incorrect format.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            HttpResponse
        """

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + r"/FuckMail_App/media/" + filename
        path = open(filepath, "rb")
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response

    def message_more_info(request, payload):
        """The 'delete all accounts' function.\n
        Delete all accounts from db.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect or HttpResponse
        """

        if request.user.is_authenticated:
            user_id = request.session["_auth_user_id"]
            data: dict = dict(zip(["message"], [CacheMessages.objects.get(user_id=user_id, message_id=payload).payload]))
            return render(request, "message_more_info.html", data)
        else:
            return redirect("index") # Redirect to 'index' page.

    def logout_user(request):
        """The 'logout user' function.\n

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect
        """

        logout(request)
        return redirect("index") # Redirect to 'index' page.