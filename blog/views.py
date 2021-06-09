import requests
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
import pyrebase
from django.contrib import messages
import datetime
from users.models import profiledetails
from .models import Post, SubComment, Comment

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


@login_required
def createpost(request):
    if (profiledetails.objects.filter(usermail__iexact=request.user.email).exists() == True):
        if request.method == 'POST':
            post_title = request.POST.get('post_title')
            post_description = request.POST.get('post_description')
            photoornot = request.POST.get('custId')
            pt = post_title
            pd = post_description
            if pt and pd:
                auth = firebase.auth()
                email = "haritheharry94@gmail.com"
                password = "hariram@007"
                userg = request.user
                username12 = post_title
                user = auth.sign_in_with_email_and_password(email, password)
                if photoornot == 'succeess':
                    url = storage.child("posts/" + username12).get_url(user['idToken'])
                else:
                    url = storage.child("files/" + "safety-suit.png").get_url(user['idToken'])
                pro = profiledetails.objects.get(usermail=request.user.email)
                pro = pro.proimage

                print(pro)
                Post(title=post_title, body_text=post_description, uprofile=pro, photo=url, author=userg).save()

            else:
                messages.warning(request, "Please Enter Title and Description!!")
        response = {
            "data": True,
        }
        return render(request, "post-create.html", response)
    response = {
        "data": False,
    }
    return render(request, "post-create.html", response)

@login_required
def viewpost(request):
    user = request.user
    response = {
        'posts': Post.objects.filter(author=user).order_by('time_upload')
    }
    print(response)
    return render(request, 'viewpost.html', response)


def fullviewpost(request, id, slug):
    try:
        post = Post.objects.get(pk=id, slug=slug)
    except:
        print('not working')

    post.read += 1
    post.save()
    if request.method == 'POST':
        comm = request.POST.get('comm')
        comm_id = request.POST.get('comm_id')  # None
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url = p.proimage

        if comm_id:
            SubComment(post=post,
                       user=request.user,
                       comm=comm,
                       scimage=url,
                       comment=Comment.objects.get(id=int(comm_id))
                       ).save()
        elif comm:
            Comment(post=post, user=request.user, comm=comm, cimage=url).save()

    comments = []
    for c in Comment.objects.filter(post=post):
        comments.append([c, SubComment.objects.filter(comment=c)])
    parms = {
        'comments': comments,
        'post': post,
    }

    return render(request, 'fullviewpost.html', parms)


def bloghome(request):
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
        }
    return render(request, 'bloghome.html',parms)