import os

from home.models import Notification, Notification1
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
config = {
    "apiKey": "AIzaSyAMWjY5lH-ZpxTW9TXAw22eKFPsiuKHHrQ",
    "authDomain": "diary-2e61a.firebaseapp.com",
    "databaseURL": "https://diary-2e61a-default-rtdb.firebaseio.com",
    "projectId": "diary-2e61a",
    "storageBucket": "diary-2e61a.appspot.com",
    "messagingSenderId": "863445861576",
    "appId": "1:863445861576:web:557866a3d6e6f1b4bf11fd",
    "measurementId": "G-Q97XVVVFR2"
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

valp = None


@login_required
def createpost(request):
    p = profiledetails.objects.filter(usermail=request.user.email).first()
    url12 = p.proimage
    if profiledetails.objects.filter(usermail__iexact=request.user.email).exists():
        if request.method == 'POST':
            url = None
            try:
                file = request.FILES['image']
                upload_result = cloudinary.uploader.upload(file)
                url = upload_result['url']
            except:
                auth = firebase.auth()
                email = str(os.getenv('EMAIL_HOST_USER'))
                password = str(os.getenv('EMAIL_HOST_PASSWORD'))
                user = auth.sign_in_with_email_and_password(email, password)
                url = storage.child(
                    "files/" + "safety-suit.png").get_url(user['idToken'])
                print(url)

            post_title = request.POST.get('post_title')
            post_description = request.POST.get('post_description')
            photoornot = request.POST.get('custId')
            pt = post_title
            pd = post_description
            if pt and pd:
                userg = request.user
                pro = profiledetails.objects.get(usermail=request.user.email)
                pro = pro.proimage
                Post(title=post_title, body_text=post_description, uprofile=pro, photo=url, author=userg).save()
                post = Post.objects.get(
                    title=post_title, body_text=post_description, uprofile=pro, photo=url, author=userg)
                message = "created a post"
                Notification1(post=post, sender=request.user, receiver=request.user.username, message=message,
                              photo=pro).save()
                return redirect('view_post')
            else:
                messages.warning(request, "Please Enter Title and Description!!")
        response = {
            'proimage': url12,
            "data": True,
            'notification': Notification1.objects.filter(receiver=request.user.username),
        }
        return render(request, "post-create.html", response)
    response = {
        'proimage': url12,
        "data": False,
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request, "post-create.html", response)


@login_required
def viewpost(request):
    user = request.user
    p = profiledetails.objects.filter(usermail=request.user.email).first()
    url = p.proimage
    response = {
        'posts': Post.objects.filter(author=user).order_by('time_upload'),
        'notification': Notification1.objects.filter(receiver=request.user.username),
        'proimage': url,
    }
    return render(request, 'viewpost.html', response)


def fullviewpost(request, id, slug):
    global valp

    def valp():
        return id

    post = Post.objects.get(pk=id, slug=slug)
    post.read += 1
    post.save()
    url = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url = p.proimage
    except:
        url = None

    if request.method == 'POST':
        comm = request.POST.get('comm')
        comm_id = request.POST.get('comm_id')  # None
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url = p.proimage
        a = post.author.username

        if comm_id:
            SubComment(post=post,
                       user=request.user,
                       comm=comm,
                       scimage=url,
                       comment=Comment.objects.get(id=int(comm_id))
                       ).save()
        elif comm:
            Comment(post=post, user=request.user, comm=comm, cimage=url).save()
            message = 'posted a comment on your'
            Notification1(post=post, sender=request.user,
                          receiver=a, message=message, photo=url).save()

    comments = []
    for c in Comment.objects.filter(post=post):
        comments.append([c, SubComment.objects.filter(comment=c)])

    parms = {
        'notification': Notification1.objects.filter(receiver=request.user.username),
        # Post.objects.filter(author=user).order_by('time_upload')
        'comments': comments,
        'post': post,
        'proimage': url,
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
    url = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url = p.proimage
    except:
        url = None
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    trends = Post.objects.filter(time_upload__gte=week_ago).order_by('-read')
    all_post = Paginator(Post.objects.filter(publish=True), 5)
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
        'notification': Notification1.objects.filter(receiver=request.user.username),
        'proimage': url,
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
    p = profiledetails.objects.filter(
        usermail=request.user.email).first()
    url = p.proimage
    message = 'liked your post'
    Notification1(post=post, sender=request.user,
                  receiver=post.author.username, message=message, photo=url).save()

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
    p = profiledetails.objects.filter(
        usermail=request.user.email).first()
    url = p.proimage
    message = 'Disliked your post'
    Notification1(post=post, sender=request.user,
                  receiver=post.author.username, message=message, photo=url).save()

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
    p = profiledetails.objects.filter(usermail=request.user.email).first()
    url12 = p.proimage
    try:
        if (profiledetails.objects.filter(usermail__iexact=request.user.email).exists() == True and Post.objects.filter(
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
                    pro = profiledetails.objects.get(usermail=request.user.email)
                    pro = pro.proimage
                    if repeat == 0:
                        Post.objects.filter(pk=id, slug=slug, author=request.user).update(title=post_title,
                                                                                          body_text=post_description,
                                                                                          uprofile=pro, photo=url)
                    else:
                        Post.objects.filter(pk=id, slug=slug, author=request.user).update(
                            title=post_title, body_text=post_description, uprofile=pro)
                    post = Post.objects.get(pk=id)

                    message = 'Post Has Been Updated'
                    Notification1(post=post, sender=request.user,
                                  receiver=request.user.username, message=message, photo=pro).save()
                    # Post(title=post_title, body_text=post_description,
                    #      uprofile=pro, photo=url, author=userg).save()
                    return redirect('view_post')

                else:
                    messages.warning(request, "Please Enter Title and Description!!")
            response = {
                'proimage': url12,
                "postt": Post.objects.get(pk=id, slug=slug),
                "data": True,
                'notification': Notification1.objects.filter(receiver=request.user.username),
            }
            return render(request, "edit.html", response)

        else:
            response = {
                'proimage': url12,
                "data": False,
                'notification': Notification1.objects.filter(receiver=request.user.username),
            }
        return render(request, "edit.html", response)
    except:
        response = {
            'proimage': url12,
            "data": True,
            'notification': Notification1.objects.filter(receiver=request.user.username),
        }
        return render(request, "edit.html", response)
