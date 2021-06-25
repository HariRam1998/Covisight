from django.contrib import admin
from .models import Like, Post, Comment, SubComment

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(SubComment)
admin.site.register(Like)
# Register your models here.
