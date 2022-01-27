from django.urls import path, include
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("message_more_info/<str:payload>", message_more_info, name="message_more_info"),
    path("profile", profile, name="profile"),
    path("logout", logout_user, name="logout"),
    path("add_account", add_account, name="add_account"),

    path("api/auth/<str:username>/<str:password>", AuthUserView.as_view(), name="auth_user"),
    path("api/addresses/<str:username>", AddressesView.as_view(), name="addresses"),
    path("api/address_data/<str:username>/<str:address>", AddressDataView.as_view(), name="address_data"),

    path("read_message/", read_message, name="add_account"),
    path("del_mail/", del_mail, name="del_mail"),

    path("add_few_accounts/", add_few_accounts, name="add_few_accounts"),
    path("del_all_accounts/", del_all_accounts, name="del_all_accounts"),
    path("del_mail_from_list/", del_mail_from_list, name="del_mail_from_list"),
    path("get_new_messages/", get_new_messages, name="get_new_messages"),

    path("help/<str:fileName>", help, name="help"),
    path("download_help_file/", download_help_file, name="download_help_file")
]