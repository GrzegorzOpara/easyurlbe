from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UrlEntry(models.Model):
    url_name = models.CharField(max_length = 200)
    url_link = models.TextField()
    url_desc = models.TextField(null = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)

    def __str__(self) -> str:
        return self.url_name