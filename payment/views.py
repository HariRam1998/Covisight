from users.models import profiledetails
from home.models import Notification1
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Transaction
from .models import User
from .paytm import generate_checksum, verify_checksum
from django.contrib import messages


def initiate_payment(request):
    Transaction.objects.filter(success=0).delete()
    abc = Transaction.objects.values('donation_id').order_by('donation_id').annotate(amount=Sum('amount'))
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')

    ja, jb, jc, jd = 0, 0, 0, 0
    a, b, c, d = 0, 0, 0, 0
    for i in abc:
        for donation, amount in i.items():
            if amount == 1 or ja == 1:
                ja += 1
                a = amount
            elif amount == 2 or jb == 1:
                jb += 1
                b = amount
            elif amount == 3 or jc == 1:
                jc += 1
                c = amount
            elif amount == 4 or jd == 1:
                jd += 1
                d = amount

    response = {
        'a': a,
        'ra': (a / 100000) * 100,
        'b': b,
        'rb': (b / 100000) * 100,
        'c': c,
        'rc': (c / 100000) * 100,
        'd': d,
        'rd': (d / 100000) * 100,
        'notification': Notification1.objects.filter(receiver=request.user.username),
        'proimage': url12,
    }
    if request.method == "POST":
        return _extracted_from_initiate_payment_41(request, response)
    return render(request, 'payments/donation.html', response)


def _extracted_from_initiate_payment_41(request, response):
    try:
        radam = request.POST.get('name')
        otheram = request.POST.get('otherAmount')
        uploadto = int(request.POST.get('cust'))
        amount = int(otheram) if otheram != '' else int(radam)
    except:
        messages.warning(request, "Enter Valid Data!!")
        return render(request, 'payments/donation.html', response)

    try:
        user = request.user.username
        user = User.objects.get(username=user)
    except:
        messages.warning(request, "Please Login so we can keep track of all donations!!")
        return render(request, 'payments/donation.html', response)

    transaction = Transaction.objects.create(made_by=user, amount=amount, donation_id=uploadto, success=0)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    return render(request, 'payments/redirect.html', context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method != 'POST':
        return
    received_data = dict(request.POST)
    paytm_params = {}
    paytm_checksum = received_data['CHECKSUMHASH'][0]
    for key, value in received_data.items():
        if key == 'CHECKSUMHASH':
            paytm_checksum = value[0]
        else:
            paytm_params[key] = str(value[0])
    # Verify checksum
    is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
    if is_valid_checksum:
        received_data['message'] = "Checksum Matched"
    else:
        received_data['message'] = "Checksum Mismatched"

    return render(request, 'payments/callback.html', context=received_data)


@csrf_exempt
def databasedel(request):
    if request.method != 'POST':
        return render(request, 'payments/callback.html')
    orderid = request.POST.get('ORDERID')
    status = request.POST.get('STATUS')
    status = status[2:13]
    id1 = str(orderid[2:-2])
    if status == "TXN_FAILURE":
        Transaction.objects.filter(order_id=id1).delete()
    else:
        Transaction.objects.filter(order_id=id1).update(success=1)
    return redirect('pay')
