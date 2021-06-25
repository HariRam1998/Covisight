from urllib.parse import uses_query
from django.db.models.query_utils import Q
import requests
from blog.models import Post
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from newsapi import NewsApiClient
from django.contrib import messages
from users.models import profiledetails
from .models import Notification1, User, Contact
from django.conf import settings
from django.core.mail import send_mail
import pyrebase
import cloudinary.uploader
import cloudinary
import datetime

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

cloudinary.config(cloud_name='df4siptjs', api_key='727231952262334',
                  api_secret='f8WYhe1BrWJNwbE4lCq9pP0hpJM')

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'covidhome.html', {})

    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')
    japan = {
        'proimage': url12,
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request, 'covidhome.html', japan)


def news(request):
    newsapi = NewsApiClient(api_key='ffc32cc1b8e848ccbb0a24415c767eb3')
    top = newsapi.get_top_headlines(q='covid',language='en')
    l = top['articles']
    desc = []
    news = []
    img = []
    fulldetail = []
    pub = []
    pkk = []
    cont = []

    for i in range(len(l)):
        f = l[i]
        news.append(f['title'])
        desc.append(f['description'])
        img.append(f['urlToImage'])
        pub.append(f["publishedAt"])
        fulldetail.append(f['url'])
        cont.append(f["content"])
    
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')

    mylist = zip(news, desc, img,pub,fulldetail,cont)
    context = {
        "mylist": mylist,
        'notification': Notification1.objects.filter(receiver=request.user.username),
        'proimage': url12,
        }
    return render(request,'news.html', context)


def faq(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')
    context = {
        'proimage': url12,
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request,'faq.html',context)


def contact(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')
    context = {
        'proimage': url12,
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request,'contact.html',context)


def contactform(request):
    if request.POST.get('action') == 'post':
        body = request.POST.get('body1')
        try:
            user = request.user.username
            user = User.objects.get(username=user)
            username = request.user.username
            useremail = request.user.email
            contact = Contact(name=username, email=useremail, content=body)
            contact.save()
            subject = 'We have received your Contact Us request'
            message = f'We will come in contact with you as soon as possible'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [useremail, ]
            send_mail(subject, message, email_from, recipient_list)
            response = {
                'a': True
            }
            return JsonResponse(response)
        except:
            # messages.warning(request, "Please Login to use the contact us module!!!")
            response = {
                'b': 1
            }
            return JsonResponse(response)


def covidlung(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')

    if request.POST:
        return _extracted_from_covidlung_10(request, url12)
    context = {
        'proimage': url12,
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request, 'covidlung.html',context)

def _extracted_from_covidlung_10(request, url12):
    file = request.FILES['files']
    upload_result = cloudinary.uploader.upload(file)
    url = upload_result['url']
    URL = 'https://covidlungsdetection.herokuapp.com/?link=' + url
    response = requests.get(URL)
    data = response.json()
    print(data["predict"])
    context = {
        'proimage': url12,
        'predict': data["predict"],
        'url': url,
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request, 'prediction.html',context)


def prediction(request):
    context = {
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request, 'prediction.html',context)

def search(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    trends = Post.objects.filter(time_upload__gte=week_ago).order_by('-read')
    if request.method != "POST":
        params = {
            'proimage': url12,
            'trends': trends[:5],
            'pop_post': Post.objects.order_by('-read')[:5],
            'notification': Notification1.objects.filter(receiver=request.user.username),
        }
        return render(request, 'bloghome.html', params)
    query = request.POST.get('search_main')
    if len(query) > 78:
        all_posts = Post.objects.none()
    else:
        all_posts = Post.objects.filter(Q(title__icontains=query) | Q(body_text__icontains=query))
    params = {
        'proimage': url12,
        'posts': all_posts,
        'trends': trends[:5],
        'pop_post': Post.objects.order_by('-read')[:5],
        'notification': Notification1.objects.filter(receiver=request.user.username),
    }
    return render(request, 'bloghome.html', params)
    

def aboutus(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')
    params = {
        'proimage': url12,
    }
    return render(request, 'aboutus.html',params)
