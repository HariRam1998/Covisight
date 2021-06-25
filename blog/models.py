from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.db import models
from django.conf import settings
from django.utils import timezone


# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True)
    body_text = models.TextField()
    time_upload = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.TextField()
    uprofile = models.TextField()
    publish = models.IntegerField(default=1)
    read = models.IntegerField(default=0)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cimage = models.TextField()
    time = models.DateTimeField(default=timezone.now)
    comm = models.TextField()


class SubComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    scimage = models.TextField()
    comm = models.TextField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
