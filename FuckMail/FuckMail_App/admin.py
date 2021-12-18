from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import *

@admin.register(Mails)
class Emails(admin.ModelAdmin):
    fields = ["address", "password", "proxy_url", "create_at"]
    list_display = ["address", "password", "check_proxy_format", "create_at"]

    @admin.display(ordering="proxy_url")
    def check_proxy_format(self, obj):
        return format_html(
            '<span style="background-color: green; color: white; font-size: 15px; font-weight: bold;">%s</span>' % obj.proxy_url
        if len(obj.proxy_url.split(":")) == 4 else 
        '<span style="background-color: red; color: white; font-size: 15px; font-weight: bold;">%s</span>' % obj.proxy_url)

@admin.register(CacheMessages)
class CacheMessages(admin.ModelAdmin):
    fields = ["message_id", "address", "from_user", "subject", "date", "visual"]
    list_display = ["address", "from_user", "subject"]
    readonly_fields = ["visual"]