from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_cache = models.BooleanField(default=False)

    def __str__(self):
          return "%s's profile" % self.user

class Mails(models.Model):
    user_id = models.IntegerField()
    address = models.CharField(max_length=255, null=True, verbose_name="Email Address")
    password = models.CharField(max_length=255, null=True, verbose_name="Email Password")
    proxy_url = models.CharField(max_length=255, verbose_name="Proxy URL")
    count_messages = models.IntegerField(null=True, verbose_name="Count messages")
    create_at = models.DateTimeField(editable=True, auto_now_add=True)

    def __str__(self):
        return "%s" % self.address

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"

class CacheMessages(models.Model):
    user_id = models.IntegerField(null=True)
    message_id = models.CharField(max_length=255, null=True, verbose_name="Message ID")
    address = models.CharField(max_length=255, null=True, verbose_name="Email Address")
    from_user = models.CharField(max_length=255, null=True, verbose_name="From")
    subject = models.CharField(max_length=255, null=True, verbose_name="Subject")
    date = models.DateTimeField(editable=True)
    payload = models.TextField(null=True, verbose_name="Payload")
    visual = models.BooleanField(default=False)

    def __str__(self):
        return "<CacheMessage: %s>" % self.message_id

    class Meta:
        verbose_name = "CacheMessage"
        verbose_name_plural = "CacheMessages"

class DesktopSessions(models.Model):
    user_id = models.IntegerField()
    sessionid = models.CharField(max_length=255)

    def __str__(self):
        return "<DesktopSession %s>" % self.sessionid

    class Meta:
        verbose_name = "DesktopSession"
        verbose_name_plural = "DesktopSessions"