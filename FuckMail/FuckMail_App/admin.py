from django.contrib import admin
from django.utils.html import format_html

from .models import *

@admin.register(Emails)
class Emails(admin.ModelAdmin):
    fields = ["address", "password", "proxy_url", "create_at"]
    list_display = ["address", "password", "check_proxy_format", "create_at"]

    @admin.display(ordering='proxy_url')
    def check_proxy_format(self, obj):
        return format_html(
            '<span style="background-color: green; color: white; font-size: 15px; font-weight: bold;">%s</span>' % obj.proxy_url
        if len(obj.proxy_url.split(":")) == 4 else 
        '<span style="background-color: red; color: white; font-size: 15px; font-weight: bold;">%s</span>' % obj.proxy_url)