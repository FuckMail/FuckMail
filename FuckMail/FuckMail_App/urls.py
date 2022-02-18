from django.urls import path, include
from .views import *

urlpatterns = [
    path("", Web.index, name="index"),
    path("message_more_info/<str:payload>", Web.message_more_info, name="message_more_info"),
    path("profile", Web.profile, name="profile"),
    path("logout", Web.logout_user, name="logout"),

    path("add_account", Web.add_account, name="add_account"),
    path("read_message/", Web.read_message, name="read_message"),
    path("del_mail/", Web.del_mail, name="del_mail"),
    path("add_few_accounts/", Web.add_few_accounts, name="add_few_accounts"),
    path("del_all_accounts/", Web.del_all_accounts, name="del_all_accounts"),
    path("del_mail_from_list/", Web.del_mail_from_list, name="del_mail_from_list"),
    path("get_new_messages/", Web.get_new_messages, name="get_new_messages"),

    path("change_checkbox_value/", Web.change_checkbox_value, name="chnage_checkbox_value"),
    path("help/<str:fileName>", Web.help, name="help"),
    path("download_help_file/", Web.download_help_file, name="download_help_file"),

    path("api/auth/<str:username>/<str:password>/<str:sessionid>", API.AuthUserView.as_view(), name="auth_user"),
    path("api/addresses/<str:username>", API.AddressesView.as_view(), name="addresses"),
    path("api/address_data/<str:username>/<str:address>", API.AddressDataView.as_view(), name="address_data"),
    path("api/show_message/<str:message_id>", API.render_page, name="render_page"),
    path("api/add_address/<str:username>/<str:sessionID>/<str:address>/<str:password>/<str:proxy_url>", API.AddAddressView.as_view(), name="add_account_desktop"),
]