from .models import *
from rest_framework import serializers

class EmailsSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    user_id = serializers.IntegerField()
    address = serializers.CharField(max_length=255)

    class Meta:
        model = Emails
        fields = ["pk", "user_id", "address"]


class CacheMessagesSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    subject = serializers.CharField(max_length=255)

    class Meta:
        model = CacheMessages
        fields = ["pk", "subject"]