from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class resetcode(models.Model):
    user_mail = models.CharField(max_length=50)
    passcode = models.CharField(max_length=10)

    def __str__(self):
        return self.user_mail


class profiledetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tagline = models.CharField(max_length=50)
    description = models.TextField()
    phoneno = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    region = models.CharField(max_length=20)
    occupation = models.CharField(max_length=20)
    covid = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.email
