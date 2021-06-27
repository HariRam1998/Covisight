from home.models import Notification
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
import cloudinary.uploader
import cloudinary

cloudinary.config(cloud_name='df4siptjs', api_key='727231952262334',
                  api_secret='f8WYhe1BrWJNwbE4lCq9pP0hpJM')



def login1(request):
    if (request.POST):
        username = request.POST.get('login_username')
        password = request.POST.get('login_password')
        if User.objects.filter(username__iexact=username).exists():
            user = authenticate(request, username=username, password=password)
            if user is not None:
                user_login(request, user)
                return redirect('user-home')
            else:
                messages.warning(request, "Password is Wrong!!")
        else:
            messages.warning(request, "Username is Wrong!!")

    return render(request, 'index.html', {})


def logoutfun(request):
    print("hey")
    logout(request)
    return redirect('user-home')


def register(request):
    if request.POST:
        username = request.POST.get('register_username')
        email = request.POST.get('register_email')
        password = request.POST.get('register_password')
        cpassword = request.POST.get('register_password_repeat')

        if (password == cpassword):
            if (User.objects.filter(username__iexact=username).exists() == False and User.objects.filter(
                    email__iexact=email).exists() == False):
                return _extracted_from_register_10(username, email, password, request)
            elif User.objects.filter(username__iexact=username).exists():
                messages.warning(request, "Username Already exists!!")

            elif User.objects.filter(email__iexact=email).exists():
                messages.warning(request, "Email Already exists!!")
        else:
            messages.warning(request, "Confirm Password is not matching!!")

    return render(request, 'index.html')


def _extracted_from_register_10(username, email, password, request):
    url = 'https://res.cloudinary.com/df4siptjs/image/upload/v1624261801/qyetxxsgfkrfgxfwi8td.png'
    user = User.objects.create_user(username=username, email=email, password=password, first_name=url)
    user.save()
    user = User.objects.get(username=username)
    abc = profiledetails(user=user)
    abc.save()
    message = 'You have sucessfully registered!!!'
    return redirect('user_login')


@login_required
def useraccount(request):
    p = profiledetails.objects.filter(user=request.user).first()
    response = {
        'proimage': request.user.first_name,
        'phoneno': p.phoneno,
        'covidsatus': p.covid,
        'notification': Notification.objects.filter(receiver=request.user.username),
        'pagetitle': 'Account info',

    }
    return render(request, 'account.html', response)


@login_required
def useraccountcp(request):
    if request.POST.get('action') == 'post':
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        if password == cpassword:
            if request.user.is_authenticated:
                username12 = request.user.username
                u = User.objects.get(username=username12)
                u.set_password(password)
                u.save()
                user = authenticate(request, username=username12, password=password)
                user_login(request, user)
                response = {
                    'a': True
                }
                return JsonResponse(response)
        else:
            response = {
                'a': False
            }
            return JsonResponse(response)

    response = {
        'proimage': request.user.first_name,
        'notification': Notification.objects.filter(receiver=request.user.username),
        'pagetitle': 'Change Password',
    }
    return render(request, 'account-password.html', response)


@login_required
def userprofile(request):
    if request.method == 'POST':
        url = None
        try:
            file = request.FILES['image']
            upload_result = cloudinary.uploader.upload(file)
            url = upload_result['url']
            user12 = User.objects.get(email=request.user.email)
            user12.first_name = url
            user12.save()

        except:
            url = 'https://res.cloudinary.com/df4siptjs/image/upload/v1624263393/jm0iqbnbijwdhqoxzoz2.png'

        old_user = profiledetails.objects.get(user=request.user)
        old_user.tagline = request.POST.get('profile_tagline')
        old_user.description = request.POST.get('profile_description')
        old_user.phoneno = request.POST.get('profile_public_website')
        if request.POST.get('profile_country'):
            old_user.country = request.POST.get('profile_country')
        if request.POST.get('profile_city'):
            old_user.region = request.POST.get('profile_city')
        old_user.occupation = request.POST.get('profile_occupation')
        old_user.covid = request.POST.get('profile_covid')
        old_user.save()
        return redirect('user_profile')

    p = profiledetails.objects.filter(user=request.user).first()
    japan = {
        'tagline': p.tagline,
        'description': p.description,
        'phoneno': p.phoneno,
        'country': p.country,
        'region': p.region,
        'proimage': request.user.first_name,
        'occupation': p.occupation,
        'covidsatus': p.covid,
        'notification': Notification.objects.filter(receiver=request.user.username),
        'pagetitle': 'Profile',

    }
    return render(request, 'profile.html', japan)


def validate_fpassword(request):
    username = request.GET.get('forgot_email')
    response = {
        'is_taken3': User.objects.filter(email__iexact=username).exists()
    }
    return JsonResponse(response)


def fpassword(request):
    if request.POST:
        email = request.POST.get('forgot_email')
        if User.objects.filter(email__iexact=email).exists():
            rad = str(random.randrange(100000, 1000000))
            subject = 'Reset Password From Coronainsight'
            message = f'This is Your Reset Code ' + rad + ' enter this code correctly'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ]
            try:
                send_mail(subject, message, email_from, recipient_list)
                if resetcode.objects.filter(user_mail__iexact=email).exists():
                    resetcode.objects.filter(user_mail=email).delete()
                fpass = resetcode.objects.create(user_mail=email, passcode=rad)
                fpass.save()
                return redirect('ccfpassword')
            except:
                print("wrong")
        else:
            messages.warning(request, "Email is not present!!")

    return render(request, 'forgetpassword.html')


def cfpassword(request):
    if request.POST:
        pin = request.POST.get('reset_passcode')
        pass0 = request.POST.get('reset_password')
        pass1 = request.POST.get('reset_password_repeat')
        if pass0 == pass1:
            if resetcode.objects.filter(passcode__iexact=pin).exists():
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
    print(response)
    return JsonResponse(response)


def validate_loginemail(request):
    """Check username availability"""
    username = request.GET.get('login_username', None)
    response = {
        'is_taken2': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)


def notification(request):
    context = {
        'notification': Notification.objects.filter(receiver=request.user.username),
        'notifi': Notification.objects.filter(receiver=request.user.username),
    }
    return render(request, 'notification.html', context)
