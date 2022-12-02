from rest_framework import serializers
from .models import UrlEntry

class UrlEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlEntry
        fields = ['id', 'url_name', 'url_link', 'url_desc', 'user']
