import re

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import datetime
import json
import numpy as np
import requests
from copy import deepcopy
import pandas as pd



val=None

# Create your views here.
def cowin(request):
    if request.method == 'POST':
        dist_inp = request.POST.get('mySelect')
        url = 'https://raw.githubusercontent.com/bhattbhavesh91/cowin-vaccination-slot-availability/main/district_mapping.csv'
        df = pd.read_csv(url, index_col=0)
        df1 = pd.read_csv(url, index_col=0)
        mapping_dict = pd.Series(df["district id"].values,
                                 index=df["district name"].values).to_dict()
        DIST_ID = mapping_dict[dist_inp]
        base = datetime.datetime.today()
        date_list = [base]
        date_str = [x.strftime("%d-%m-%Y") for x in date_list]
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        final_df = None
        for INP_DATE in date_str:
            URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(
                DIST_ID, INP_DATE)
            response = requests.get(URL, headers=header)
            if (response.ok) and ('centers' in json.loads(response.text)):
                resp_json = json.loads(response.text)['centers']
                if resp_json is not None:
                    df = pd.DataFrame(resp_json)
                    if len(df):
                        df = df.explode("sessions")
                        df['min_age_limit'] = df.sessions.apply(lambda x: x['min_age_limit'])
                        df['vaccine'] = df.sessions.apply(lambda x: x['vaccine'])
                        df['available_capacity'] = df.sessions.apply(lambda x: x['available_capacity'])
                        df['date'] = df.sessions.apply(lambda x: x['date'])
                        df = df[
                            ["date", "available_capacity", "vaccine", "min_age_limit", "pincode", "name", "state_name",
                             "district_name", "block_name", "fee_type"]]
                        if final_df is not None:
                            final_df = pd.concat([final_df, df])
                        else:
                            final_df = deepcopy(df)
                else:
                    print("No rows in the data Extracted from the API")

        vaccine = list(final_df.loc[:, "vaccine"].unique())
        pincode = list(final_df.loc[:, "pincode"].unique())
        min_age_limit = list(final_df.loc[:, "min_age_limit"].unique())
        min_age_limit.sort()
        unique_districts = list(df1["district name"].unique())
        unique_districts.sort()
        valid_payments = list(final_df.loc[:, "fee_type"].unique())
        valid_capacity = ["Available"]
        global val
        def val():
            return final_df

        context = {
            'select_districts': unique_districts,
            'vaccine': vaccine,
            'pay': valid_payments,
            'min_age_limit': min_age_limit,
            'pincode': pincode,
            'valid_capacity': valid_capacity,
            'final': final_df
        }
        return render(request, 'cowinmo.html', context)
    url = 'https://raw.githubusercontent.com/bhattbhavesh91/cowin-vaccination-slot-availability/main/district_mapping.csv'
    df = pd.read_csv(url, index_col=0)
    unique_districts = list(df["district name"].unique())
    unique_districts.sort()
    # print(unique_districts)
    context = {
        'select_districts': unique_districts,
    }
    return render(request,'cowinmo.html',context)


def cowintable(request):
    rename_mapping = {
        'date': 'Date',
        'min_age_limit': 'Age Limit',
        'available_capacity': 'Doses Left',
        'vaccine': 'Vaccine',
        'pincode': 'Pincode',
        'name': 'Hospital Name',
        'state_name': 'State',
        'district_name': 'District',
        'block_name': 'Block Name',
        'fee_type': 'Fees'
    }
    if request.POST.get('action') == 'post':
        try:
            ok = val()
            ok.rename(columns=rename_mapping, inplace=True)
            abc = 0
            pincode = request.POST.get('pincode')
            minage = request.POST.get('minage')
            pay = request.POST.get('pay')
            available = request.POST.get('available')
            if pincode == 'Show All' or pincode == 'empty':
                abc = ok
            else:
                pincode = int(pincode)
                abc = deepcopy(ok.loc[ok['Pincode'] == pincode])
            if minage == 'Show All' or minage == 'empty':
                abc = abc
            else:
                minage = int(minage)
                abc = deepcopy(abc.loc[abc['Age Limit'] == minage])
            if pay == 'Show All' or pay == 'empty':
                abc = abc
            else:
                abc = deepcopy(abc.loc[abc['Fees'] == pay])
            if available == 'Show All' or available == 'empty':
                abc = abc
            else:
                abc = deepcopy(abc.loc[abc['Doses Left'] > 0])
            df = re.sub(' mystyle', '" id="example', abc.to_html(classes='mystyle'))
            response = {
                'table1': df
            }
            return JsonResponse(response)

        except:
            messages.warning(request, "Sorry we are having some problem to fetch data try after some time!!")


def covidanalysis(request):
    return render(request,'covidquestionare.html')