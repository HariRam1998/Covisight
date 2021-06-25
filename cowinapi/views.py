from users.models import profiledetails
from home.models import Notification1
import os
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
import folium
from datetime import date
from datetime import timedelta
import plotly.graph_objects as go

val = None
val1 = None


# Create your views here.
def cowin(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')

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
            # response = requests.get(URL, headers=header)
            response = requests.get(URL)
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
            'final': final_df,
            'proimage': url12,
        }
        return render(request, 'cowinmo.html', context)
    url = 'https://raw.githubusercontent.com/bhattbhavesh91/cowin-vaccination-slot-availability/main/district_mapping.csv'
    df = pd.read_csv(url, index_col=0)
    unique_districts = list(df["district name"].unique())
    unique_districts.sort()

    context = {
        'select_districts': unique_districts,
        'notification': Notification1.objects.filter(receiver=request.user.username),
        'proimage': url12,
    }
    return render(request, 'cowinmo.html', context)


def cowintable(request):
    if request.POST.get('action') != 'post':
        return
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
    try:
        return _extracted_from_cowintable_16(rename_mapping, request)
    except:
        messages.warning(request, "Sorry we are having some problem to fetch data try after some time!!")


def _extracted_from_cowintable_16(rename_mapping, request):
    ok = val()
    ok.rename(columns=rename_mapping, inplace=True)
    abc = 0
    pincode = request.POST.get('pincode')
    minage = request.POST.get('minage')
    pay = request.POST.get('pay')
    available = request.POST.get('available')
    if pincode in ['Show All', 'empty']:
        abc = ok
    else:
        pincode = int(pincode)
        abc = deepcopy(ok.loc[ok['Pincode'] == pincode])
    if minage in ['Show All', 'empty']:
        abc = abc
    else:
        minage = int(minage)
        abc = deepcopy(abc.loc[abc['Age Limit'] == minage])
    if pay in ['Show All', 'empty']:
        abc = abc
    else:
        abc = deepcopy(abc.loc[abc['Fees'] == pay])
    if available in ['Show All', 'empty']:
        abc = abc
    else:
        abc = deepcopy(abc.loc[abc['Doses Left'] > 0])
    df = re.sub(' mystyle', '" id="example', abc.to_html(classes='mystyle'))
    response = {
        'table1': df
    }
    return JsonResponse(response)


def covidanalysis(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')
    context = {
        'proimage': url12,
    }
    return render(request, 'covidquestionare.html', context)


def vaccinechart(request):
    url12 = None
    try:
        p = profiledetails.objects.filter(usermail=request.user.email).first()
        url12 = p.proimage
    except:
        print('Not Logged in')

    today = date.today()
    # a = today.strftime("%d_%m_%Y") + '.csv'
    # b = os.path.exists('media/' + a)
    # if not b:
    #     req = requests.get('http://api.covid19india.org/csv/latest/cowin_vaccine_data_statewise.csv')
    #     url_content = req.content
    #     csv_file = open('media/' + a, 'wb')
    #     csv_file.write(url_content)
    #     csv_file.close()
    # vaccinestate = pd.read_csv('media/' + a)
    vaccinestate = pd.read_csv('http://api.covid19india.org/csv/latest/cowin_vaccine_data_statewise.csv')
    vaccinestate.columns = [col.replace("Updated On", "Date") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Total Doses Administered", "Doses") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("First Dose Administered", "fDoses") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Second Dose Administered", "sDoses") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Total Covaxin Administered", "Covaxin") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Total CoviShield Administered", "CoviShield") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Total Sputnik V Administered", "Sputnik") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Male(Individuals Vaccinated)", "Male") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Female(Individuals Vaccinated)", "Female") for col in vaccinestate.columns]
    vaccinestate.columns = [col.replace("Transgender(Individuals Vaccinated)", "Transgender") for col in
                            vaccinestate.columns]
    vaccinestate.columns = [col.replace("Total Individuals Vaccinated", "Totalindiviual") for col in
                            vaccinestate.columns]
    vaccinestate.dropna(subset=["Doses"], inplace=True)
    vaccinestate.dropna(subset=["fDoses"], inplace=True)
    vaccinestate.dropna(subset=["sDoses"], inplace=True)
    vaccinestate.dropna(subset=["Covaxin"], inplace=True)
    vaccinestate.dropna(subset=["CoviShield"], inplace=True)

    df = vaccinestate.copy()
    df1 = vaccinestate.copy()
    df2 = vaccinestate.copy()
    df3 = vaccinestate.copy()
    coordinates = pd.read_csv("media/state.csv")

    # today = date.today()
    # yesterday = today - timedelta(days=2)
    # a = yesterday.strftime("%d/%m/%Y")
    last_element = vaccinestate.iloc[-1]
    abc = vaccinestate.loc[vaccinestate['Date'] == last_element.Date]
    # abc = vaccinestate.loc[vaccinestate["Date"] == a]
    covid = abc.join(coordinates.set_index('State'), on='State')
    covid.dropna(subset=["Longitude"], inplace=True)
    covid.dropna(subset=["Latitude"], inplace=True)
    # zoom_control = False,scrollWheelZoom = False,dragging = False
    m1 = folium.Map(location=[22.5937, 78.9629], zoom_start=5, width='100', height='100', scrollWheelZoom=False)
    state = list(covid['State'])
    latitude = list(covid['Latitude'])
    longitude = list(covid['Longitude'])
    total = list(covid['Totalindiviual'])

    for s, lat, long, t in zip(state, latitude, longitude, total):
        folium.Circle(
            location=[lat, long],
            radius=float(t * .01),
            tooltip='State  : ' + s + ' \n\n Total Vaccination : ' + str(t) + '',
            color='green',
            fill=True,
            fill_color='green'
        ).add_to(m1)
    folium.raster_layers.TileLayer('Open Street Map').add_to(m1)
    folium.raster_layers.TileLayer('Stamen Terrain').add_to(m1)
    folium.raster_layers.TileLayer('Stamen Toner').add_to(m1)
    folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m1)
    folium.raster_layers.TileLayer('CartoDB Positron').add_to(m1)
    folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m1)
    folium.LayerControl().add_to(m1)
    m1 = m1._repr_html_()

    df = df.loc[df['State'] == 'India']
    df['Date'] = pd.to_datetime(df["Date"], format='%d/%m/%Y')
    df.dropna(subset=["Doses"], inplace=True)
    # df.head()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=list(df.Date), y=list(df.Doses), name='Total Doses'))
    fig.add_trace(
        go.Scatter(x=list(df.Date), y=list(df.fDoses), name='First Doses'))
    fig.add_trace(
        go.Scatter(x=list(df.Date), y=list(df.sDoses), name='Second Doses'))
    # Set title
    fig.update_layout(
        title_text="Vaccination Time series"
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    m2 = fig.to_html(full_html=False)

    """ vaccine administered comparison """
    df1 = df1.loc[df1['State'] == 'India']
    last_element = df1.iloc[-1]

    df1 = df1.loc[df1['Date'] == last_element.Date]
    z = [list(df1.fDoses), list(df1.sDoses)]
    z = z[0] + z[1]

    y = [list(df1.Covaxin), list(df1.CoviShield), list(df1.Sputnik)]
    a = y[0] + y[1] + y[2]


    labels = ['Covaxin', 'CoviShield', 'Sputnik']
    values = a
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(
        title_text="Vaccination Time series")
    m3 = fig.to_html(full_html=False)

    """ vaccination male-female """
    df2 = df2.loc[df2['State'] == 'India']
    df2['Date'] = pd.to_datetime(df2["Date"], format='%d/%m/%Y')
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(x=list(df2.Date), y=list(df2.Male), name='Male'))
    fig1.add_trace(
        go.Scatter(x=list(df2.Date), y=list(df2.Female), name='Female'))
    fig1.add_trace(
        go.Scatter(x=list(df2.Date), y=list(df2.Transgender), name='Transgender'))
    # Set title
    fig1.update_layout(
        title_text="Vaccination Time series"
    )

    # Add range slider
    fig1.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    m4 = fig1.to_html(full_html=False)

    """vaccination top 20 state"""
    df3 = df3.loc[df3['State'] != 'India']
    last_element = df3.iloc[-1]
    df3 = df3.loc[df3['Date'] == last_element.Date]
    global val1

    def val1():
        return df3.copy()

    Top5 = df3.nlargest(20, 'Doses').reset_index(drop=True)
    State = list(Top5["State"])

    First = list(Top5["fDoses"])

    Second = list(Top5["sDoses"])
    fig2 = go.Figure(data=[

        go.Bar(name='First Dose', x=State, y=First),
        go.Bar(name='Both Doses', x=State, y=Second)
    ])
    # Change the bar mode
    fig2.update_layout(barmode='group')
    fig2.update_layout(
        title_text="Vaccination Chart of 20 States"
    )
    m5 = fig2.to_html(full_html=False)

    """ Total Vaccinated  """
    z1 = int(z[0])
    z2 = int(z[1])
    pop = 1392790451
    first = (z1 / pop) * 100
    second = (z2 / pop) * 100
    first = round(first, 2)
    per = first
    second = round(second, 2)

    unique_state = pd.read_csv("media/state.csv")
    unique_state = list(unique_state["State"].unique())
    unique_state.sort()

    context = {
        'm1': m1,
        'm2': m2,
        'm3': m3,
        'm4': m4,
        'm5': m5,
        'per': per,
        'first': first,
        'second': second,
        'select_state': unique_state,
        'notification': Notification1.objects.filter(receiver=request.user.username),
        'proimage': url12,
    }
    return render(request, 'vaccinechart.html', context)


def mapupdate(request):
    if request.POST.get('action') == 'post':
        dist_inp = request.POST.get('mySelect')
        today = date.today()
        # a = today.strftime("%d_%m_%Y") + 'district.csv'
        # b = os.path.exists('media/' + a)
        # if not b:
        #     req = requests.get('http://api.covid19india.org/csv/latest/cowin_vaccine_data_districtwise.csv')
        #     url_content = req.content
        #     csv_file = open('media/' + a, 'wb')
        #     csv_file.write(url_content)
        #     csv_file.close()
        df = pd.read_csv('http://api.covid19india.org/csv/latest/cowin_vaccine_data_districtwise.csv', sep=',', error_bad_lines=False, index_col=False, dtype='unicode')

        today = date.today()
        today1 = today
        a = today1.strftime("%d/%m/%Y")
        i = 0
        c = 0
        v = []
        while True:
            i += 1
            for col in df.columns:
                if a == col:
                    biz = a
                    v = ["State", "District", a]
                    for i in range(1, 10):
                        j = a + '.' + str(i)
                        v.append(j)

                    c = 1
            if c == 1:
                break
            b = today - timedelta(days=i)
            a = b.strftime("%d/%m/%Y")

        drop_list = v
        df = df.drop(df.columns.difference(drop_list), axis=1)
        df = df.loc[df['State'] == dist_inp]
        coordinates = pd.read_csv("media/coviddistrict.csv")
        covid = df.merge(coordinates, on='District', how='left')
        covid['Latitude'] = covid['Latitude'].fillna(0)
        covid['Longitude'] = covid['Longitude'].fillna(0)
        covid = covid.drop(['State'], axis=1)
        covid = covid.iloc[1:]
        covid = covid.dropna()
        District = list(covid['District'])
        latitude = list(covid['Latitude'])
        longitude = list(covid['Longitude'])
        total = list(covid[biz])
        firstdose = list(covid[biz + '.3'])
        seconddose = list(covid[biz + '.4'])
        districtloc = pd.read_csv("media/state.csv")
        districtloc = districtloc.loc[districtloc['State'] == dist_inp]
        a = districtloc.mean().Latitude
        b = districtloc.mean().Longitude
        population = districtloc['Population']
        # c = a + b
        f = folium.Figure(width=730, height=600)
        m1 = folium.Map(location=[a, b], zoom_start=6.2, scrollWheelZoom=False).add_to(f)
        for s, lat, long, t in zip(District, latitude, longitude, total):
            folium.Circle(
                location=[lat, long],
                radius=float(int(t) * .03),
                tooltip='District  : ' + s + ' \n\n Total Vaccination : ' + str(t) + '',
                color='green',
                fill=True,
                fill_color='green'
            ).add_to(m1)
        folium.raster_layers.TileLayer('Open Street Map').add_to(m1)
        folium.raster_layers.TileLayer('Stamen Terrain').add_to(m1)
        folium.raster_layers.TileLayer('Stamen Toner').add_to(m1)
        folium.raster_layers.TileLayer('Stamen Watercolor').add_to(m1)
        folium.raster_layers.TileLayer('CartoDB Positron').add_to(m1)
        folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(m1)
        folium.LayerControl().add_to(m1)
        m1 = m1._repr_html_()

        today = date.today()
        a = today.strftime("%d_%m_%Y") + '.csv'

        population = int(population)
        ok = val1()
        ok = ok.loc[ok['State'] == dist_inp]

        z1 = int(ok['fDoses'])
        z2 = int(ok['sDoses'])

        first = (z1 / population) * 100
        second = (z2 / population) * 100
        first = round(first, 2)
        second = round(second, 2)


        """ vaccine administered comparison """
        y = [list(ok.Covaxin), list(ok.CoviShield), list(ok.Sputnik)]
        a = y[0] + y[1] + y[2]


        labels = ['Covaxin', 'CoviShield', 'Sputnik']
        values = a
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(
            title_text="Vaccination Time series")
        m3 = fig.to_html(full_html=False)

        """vaccination District"""

        State = District
        First = firstdose
        Second = seconddose
        for i in range(0, len(First)):
            First[i] = int(First[i])
            Second[i] = int(Second[i])

        fig2 = go.Figure(data=[

            go.Bar(name='First Dose', x=State, y=First),
            go.Bar(name='Both Doses', x=State, y=Second)
        ])
        # Change the bar mode
        fig2.update_layout(barmode='group')
        fig2.update_layout(
            title_text="Vaccination Chart of District"
        )
        m5 = fig2.to_html(full_html=False)

        

        context = {
            'h1': m1,
            'h2': m3,
            'h3': m5,
            'disfirst': first,
            'dissecond': second,
        }
    return JsonResponse(context)
