from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from newsapi import NewsApiClient
from django.contrib import messages
from users.models import profiledetails
from .models import User, Contact
from django.conf import settings
from django.core.mail import send_mail

def home(request):
    if request.user.is_authenticated:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        japan = {
            'proimage': 'hey',
        }
        return render(request, 'covidhome.html', japan)
    else:
        return render(request, 'covidhome.html', {})


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

    mylist = zip(news, desc, img,pub,fulldetail,cont)
    context = {"mylist": mylist}
    return render(request,'news.html', context)


def faq(request):
    return render(request,'faq.html')


def contact(request):
    return render(request,'contact.html',{})


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