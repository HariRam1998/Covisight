import os
from home.models import Notification
import json
from django.http.response import HttpResponse
import requests
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect
import pyrebase
from django.contrib import messages
import datetime
import cloudinary.uploader
import cloudinary

from django.template.loader import render_to_string

from users.models import profiledetails
from .models import Like, Post, SubComment, Comment

cloudinary.config(cloud_name='df4siptjs', api_key='727231952262334',
                  api_secret='f8WYhe1BrWJNwbE4lCq9pP0hpJM')

valp = None


@login_required
def createpost(request):
    if request.method == 'POST':
        url = None
        try:
            file = request.FILES['image']
            upload_result = cloudinary.uploader.upload(file)
            url = upload_result['url']
        except:
            url = 'https://res.cloudinary.com/df4siptjs/image/upload/v1624263393/jm0iqbnbijwdhqoxzoz2.png'

        post_title = request.POST.get('post_title')
        post_description = request.POST.get('post_description')
        pt = post_title
        pd = post_description
        if pt and pd:
            userg = request.user
            Post(title=post_title, body_text=post_description, photo=url, author=userg).save()
            post = Post.objects.get(
                title=post_title, body_text=post_description, photo=url, author=userg)
            message = "created a post"
            Notification(post=post, sender=request.user, receiver=request.user.username, message=message).save()
            return redirect('view_post')
        else:
            messages.warning(request, "Please Enter Title and Description!!")
    response = {
        'proimage': request.user.first_name,
        "data": True,
        'notification': Notification.objects.filter(receiver=request.user.username),
        'pagetitle': 'Create post',

    }
    return render(request, "post-create.html", response)


@login_required
def viewpost(request):
    response = {
        'posts': Post.objects.filter(author=request.user).order_by('time_upload'),
        'notification': Notification.objects.filter(receiver=request.user.username),
        'proimage': request.user.first_name,
        'pagetitle': 'View post',
    }
    return render(request, 'viewpost.html', response)


def fullviewpost(request, id, slug):
    global valp

    def valp():
        return id

    try:
        post = Post.objects.get(pk=id, slug=slug)
        post.read += 1
        post.save()
    except:
        return render(request, '404.html')

    if request.method == 'POST':
        comm = request.POST.get('comm')
        comm_id = request.POST.get('comm_id')  # None
        a = post.author.username

        if comm_id:
            SubComment(post=post,
                       user=request.user,
                       comm=comm,
                       comment=Comment.objects.get(id=int(comm_id))
                       ).save()
        elif comm:
            Comment(post=post, user=request.user, comm=comm).save()
            message = 'posted a comment on your'
            Notification(post=post, sender=request.user,
                         receiver=a, message=message).save()

    comments = []
    for c in Comment.objects.filter(post=post):
        comments.append([c, SubComment.objects.filter(comment=c)])

    url12 = None
    if request.user.is_authenticated:
        url12 = request.user.first_name

    parms = {
        'notification': Notification.objects.filter(receiver=request.user.username),
        # Post.objects.filter(author=user).order_by('time_upload')
        'comments': comments,
        'post': post,
        'proimage': url12,
        'pagetitle': 'Full post view',
    }

    if request.is_ajax():
        html = render_to_string('comments.html', parms, request=request)
        # print(html)
        # html = render_to_string('blog/comments.html', context, request=request)
        # return JsonResponse({'form': html})
        print("hello")
        return JsonResponse({'form': html})

    return render(request, 'fullviewpost.html', parms)


def bloghome(request):
    url12 = None
    if request.user.is_authenticated:
        url12 = request.user.first_name
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    trends = Post.objects.filter(time_upload__gte=week_ago).order_by('-read')
    all_post = Paginator(Post.objects.filter(publish=1), 5)
    page = request.GET.get('page')
    try:
        posts = all_post.page(page)
    except PageNotAnInteger:
        posts = all_post.page(1)
    except EmptyPage:
        posts = all_post.page(all_post.num_pages)

    parms = {
        'posts': posts,
        'trends': trends[:5],
        'pop_post': Post.objects.order_by('-read')[:5],
        'notification': Notification.objects.filter(receiver=request.user.username),
        'proimage': url12,
        'pagetitle': 'Blog home',
    }
    return render(request, 'bloghome.html', parms)


def likepost(request):
    if request.method == 'GET':
        id = request.GET['likes']
        post = Post.objects.get(pk=id)

        is_liked = _extracted_from_likepost_10(post, request)
        context = {
            'is_liked': is_liked,
        }
    return JsonResponse(context)


def _extracted_from_likepost_10(post, request):
    abd = Like.objects.filter(post=post, user=request.user)
    a = None
    if abd:
        Like.objects.filter(post=post, user=request.user).delete()
        a = "False"
    else:
        Like(post=post, user=request.user, like=1).save()
        a = "True"
    message = 'liked your post'
    Notification(post=post, sender=request.user,
                 receiver=post.author.username, message=message).save()

    return a


def dislikepost(request):
    if request.method == 'GET':
        id = request.GET['dislike']
        post = Post.objects.get(pk=id)
        is_disliked = _extracted_from_dislikepost_10(post, request)
        context = {
            'is_disliked': is_disliked,
        }
    return JsonResponse(context)


def _extracted_from_dislikepost_10(post, request):
    abd = Like.objects.filter(post=post, user=request.user)
    a = None
    if abd:
        Like.objects.filter(post=post, user=request.user).delete()
        a = "False"
    else:
        Like(post=post, user=request.user, dislike=1).save()
        a = "True"
    message = 'Disliked your post'
    Notification(post=post, sender=request.user,
                 receiver=post.author.username, message=message).save()

    return a


def checklike(request):
    try:
        is_disliked = "False"
        is_liked = "False"
        ok = valp()
        id1 = ok
        print(id1)
        post = Post.objects.get(pk=id1)
        if Like.objects.filter(post=post, user=request.user, dislike=1).exists():
            is_disliked = "True"
        elif Like.objects.filter(post=post, user=request.user, like=1).exists():
            is_liked = "True"
    except:
        is_disliked = "False"
        is_liked = "False"
    context = {
        'is_disliked': is_disliked,
        'is_liked': is_liked,
    }
    return JsonResponse(context)


@login_required
def deletepost(request):
    if request.POST.get('action') == 'post':
        id = request.POST.get('id')
        Post.objects.filter(id=id).delete()
        context = {
            'hi': 'hello',
        }
    return JsonResponse(context)


@login_required
def editpost(request, id, slug):  # sourcery no-metrics
    url12 = request.user.first_name
    try:
        if (profiledetails.objects.filter(user=request.user).exists() == True and Post.objects.filter(
                pk=id, slug=slug, author=request.user).exists()):
            if request.method == 'POST':
                url = None
                repeat = 0
                try:
                    file = request.FILES['image']
                    upload_result = cloudinary.uploader.upload(file)
                    url = upload_result['url']
                except:
                    repeat = 1

                post_title = request.POST.get('post_title')
                post_description = request.POST.get('post_description')
                pt = post_title
                pd = post_description
                if pt and pd:
                    if repeat == 0:
                        Post.objects.filter(pk=id, slug=slug, author=request.user).update(title=post_title,
                                                                                          body_text=post_description,
                                                                                          photo=url)
                    else:
                        Post.objects.filter(pk=id, slug=slug, author=request.user).update(
                            title=post_title, body_text=post_description)
                    post = Post.objects.get(pk=id)

                    message = 'Post Has Been Updated'
                    Notification(post=post, sender=request.user,
                                 receiver=request.user.username, message=message).save()
                    # Post(title=post_title, body_text=post_description,
                    #      uprofile=pro, photo=url, author=userg).save()
                    return redirect('view_post')

                else:
                    messages.warning(request, "Please Enter Title and Description!!")
            response = {
                'proimage': url12,
                "postt": Post.objects.get(pk=id, slug=slug),
                "data": True,
                'notification': Notification.objects.filter(receiver=request.user.username),
                'pagetitle': 'Edit post',
            }
            return render(request, "edit.html", response)

        else:
            response = {
                'proimage': url12,
                "data": False,
                'notification': Notification.objects.filter(receiver=request.user.username),
                'pagetitle': 'Edit post',
            }
        return render(request, "edit.html", response)
    except:
        return redirect('view_post')
