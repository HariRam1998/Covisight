from django.db import models
# Create your models here.

class resetcode(models.Model):
    user_mail = models.CharField(max_length=50)
    passcode = models.CharField(max_length=10)

    def __str__(self):
        return self.user_mail

class profiledetails(models.Model):
    usermail = models.CharField(max_length=50)
    tagline = models.CharField(max_length=50)
    description = models.TextField()
    phoneno =  models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    region = models.CharField(max_length=20)
    proimage =  models.TextField()
    occupation = models.CharField(max_length=20)
    covid = models.CharField(max_length=20,null=True, blank=True)

    def __str__(self):
        return self.usermail



