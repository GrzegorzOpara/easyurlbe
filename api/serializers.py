from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UrlEntry

class UrlEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlEntry
        fields = ['id', 'url_name', 'url_link', 'url_desc', 'user']

class UserGetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']