from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("message_more_info/<str:payload>", message_more_info, name="message_more_info"),
    path("profile", profile, name="profile"),
    path("logout", logout_user, name="logout"),
    path("add_account", add_account, name="add_account")
]