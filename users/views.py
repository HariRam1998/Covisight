import random
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from .models import resetcode, profiledetails
from django.contrib.auth import authenticate
from django.contrib.auth import login as user_login
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
import pyrebase
from django.core.files.storage import default_storage
from newsapi import NewsApiClient

# https://github.com/bhattbhavesh91/cowin-vaccination-slot-availability

config={
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



def login1(request):
    if (request.POST):
        username = request.POST.get('login_username')
        password = request.POST.get('login_password')
        if (User.objects.filter(username__iexact=username).exists() == True):
            user = authenticate(request, username=username, password=password)
            if user is not None:
                user_login(request, user)
                return redirect('user-home')
            else:
                messages.warning(request, "Password is Wrong!!")
        else:
            messages.warning(request, "Username is Wrong!!")

    return render(request, 'index.html',{})



def logoutfun(request):
    print("hey")
    logout(request)
    return redirect('user-home')

def register(request):
    if (request.POST):
        username = request.POST.get('register_username')
        email = request.POST.get('register_email')
        password = request.POST.get('register_password')
        cpassword = request.POST.get('register_password_repeat')

        if(password == cpassword):
            if(User.objects.filter(username__iexact=username).exists() == False and User.objects.filter(email__iexact=email).exists() == False):
                user = User.objects.create_user(username, email, password)
                user.save()
                return redirect('user-home')
            elif(User.objects.filter(username__iexact=username).exists()):
                messages.warning(request, "Username Already exists!!")
                # response = {
                #     'is_taken3':'hey'
                # }
                # return JsonResponse(response)
            elif(User.objects.filter(email__iexact=email).exists()):
                messages.warning(request, "Email Already exists!!")
                # response = {
                #     'is_taken3': 'hey'
                # }
                # return JsonResponse(response)
        else:
            messages.warning(request, "Confirm Password is not matching!!")

    return render(request, 'index.html')

@login_required
def useraccount(request):
    p = profiledetails.objects.filter(usermail=request.user.email).first()
    username = request.user.username
    email = request.user.email
    response={
        'user1' : User.objects.filter(email = email),
        'proimage': p.proimage,
        'phoneno': p.phoneno,
        'covidsatus': p.covid,

    }
    return render(request, 'account.html',response)

@login_required
def useraccountcp(request):
    p = profiledetails.objects.filter(usermail=request.user.email).first()
    response = {
        'proimage': p.proimage,
    }
    if request.POST.get('action') == 'post':
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        if(password == cpassword):
            if request.user.is_authenticated:
                username12 = request.user.username
                u = User.objects.get(username=username12)
                u.set_password(password)
                u.save()
                response = {
                'a': True
                }
                return JsonResponse(response)
        else:
            response = {
                'a': True
            }
            return JsonResponse(response)

    return render(request, 'account-password.html',response)

@login_required
def userprofile(request):
    if request.method == 'POST':
        tagline = request.POST.get('profile_tagline')
        description = request.POST.get('profile_description')
        phoneno = request.POST.get('profile_public_website')
        country = request.POST.get('profile_country')
        region = request.POST.get('profile_city')
        occupation = request.POST.get('profile_occupation')
        covid = request.POST.get('profile_covid')
        auth = firebase.auth()
        email = "haritheharry94@gmail.com"
        password = "hariram@007"
        username12 = request.user.username
        user = auth.sign_in_with_email_and_password(email, password)
        url = storage.child("users/" + username12).get_url(user['idToken'])
        if url == "":
            url = storage.child("files/" + "safety-suit.png").get_url(user['idToken'])

        if(profiledetails.objects.filter(usermail__iexact=request.user.email).exists()):
            old_user = profiledetails.objects.get(usermail=request.user.email)
            old_user.tagline=tagline
            old_user.description=description
            old_user.phoneno=phoneno
            old_user.country=country
            old_user.region=region
            old_user.occupation = occupation
            old_user.covid = covid
            old_user.proimage = url
            old_user.save()
        else:
            abc = profiledetails(usermail= request.user.email , tagline =  tagline, description=description,phoneno=phoneno, country = country,  region = region,proimage=url,occupation = occupation,covid = covid)
            abc.save()
    if(profiledetails.objects.filter(usermail__iexact=request.user.email).exists() == True):
        p = profiledetails.objects.filter(usermail = request.user.email).first()
        url = p.proimage
        if p.proimage == "":
            url = storage.child("files/" + "safety-suit.png").get_url(user['idToken'])
        japan = {
        'tagline' : p.tagline,
        'description' : p.description,
        'phoneno' : p.phoneno,
        'country' : p.country,
        'region' : p.region,
        'proimage' : url,
        'occupation' : p.occupation,
        'covidsatus' : p.covid,
        }
        return render(request, 'profile.html', japan)
    return render(request, 'profile.html',{})

def validate_fpassword(request):
    username = request.GET.get('forgot_email')
    response = {
        'is_taken3': User.objects.filter(email__iexact=username).exists()
    }
    return JsonResponse(response)

def fpassword(request):
    if (request.POST):
        email = request.POST.get('forgot_email')
        if (User.objects.filter(email__iexact=email).exists() == True):
            rad = str(random.randrange(100000, 1000000))
            subject = 'Reset Password From Coronainsight'
            message = f'This is Your Reset Code '+ rad +' enter this code correctly'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ]
            try:
                send_mail(subject, message, email_from, recipient_list)
                if(resetcode.objects.filter(user_mail__iexact=email).exists() == True):
                    resetcode.objects.filter(user_mail=email).delete()
                    fpass = resetcode.objects.create(user_mail=email, passcode=rad)
                    fpass.save()
                else:
                    fpass = resetcode.objects.create(user_mail=email, passcode=rad)
                    fpass.save()
                return redirect('ccfpassword')
            except:
                print("wrong")
        else:
            messages.warning(request, "Email is not present!!")

    return render(request, 'forgetpassword.html')


def cfpassword(request):
    if (request.POST):
        pin = request.POST.get('reset_passcode')
        pass0 = request.POST.get('reset_password')
        pass1 = request.POST.get('reset_password_repeat')
        if(pass0 == pass1):
            if (resetcode.objects.filter(passcode__iexact=pin).exists() == True):
                ab = resetcode.objects.get(passcode__iexact=pin)
                u = User.objects.get(email=ab)
                u.set_password(pass0)
                u.save()
                return redirect('user_login')
            else:
                messages.warning(request, "Passcode is not matching!!")
        else:
            messages.warning(request, "Confirm Password is not matching!!")

    return render(request, 'changeforgetpassword.html')



def validate_username(request):
    """Check username availability"""
    username = request.GET.get('register_username')
    # a = User.objects.filter(username__iexact=username).exists()
    # print(username)
    # print(a)
    response = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)


def validate_email(request):
    """Check username availability"""
    email = request.GET.get('register_email', None)
    response = {
        'is_taken1': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(response)

def validate_loginemail(request):
    """Check username availability"""
    username = request.GET.get('login_username', None)
    response = {
        'is_taken2': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)

