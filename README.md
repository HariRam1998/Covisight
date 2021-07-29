# Covisight

### Overview

* The project titled Covisight deals with the Covid related information.Covisight has a Dashboard which tracks the live COVID data and gives detailed information to the users.

* It also has a Community module where the users can share their thoughts and ideas. 💭

* An ML module that will analyze the chest X-Ray of the patients and predict whether the patient is COVID Positive or Negative. 

* The News module will feed the user with the latest COVID related news across all the countries. 🗞️

* The mask detection model predicts whether the person is wearing the mask or not at live time using the live feed. 😷

* Payment module enables the user to donate to the needy people. 💸

* Hospital module has the details of the hospitals and the availabity of beds all over the India. 🏥

***
### Data Resources

* Indian Covid data - [Coronacluster](https://coronaclusters.in/)

* International Covid data - [Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19)

* Chest X- Ray data set - [Kaggle](https://www.kaggle.com/prashant268/chest-xray-covid19-pneumonia)

* Vaccination details - [Covid19.org](https://api.covid19india.org/) , [COWIN](https://apisetu.gov.in/public/marketplace/api/cowin)

* Newsfeed - [NewsAPI](https://newsapi.org/)

***

### Technologies used

* Django
* Postgres
* Google Data Studio
* Deep Learning
* Teachable Machine
* Rest API
* Payment Gateway

***

### Modules

#### 1. Home 🏠

* Home module contains the common Myth Busters about the COVID-19.

* It also has the popular Podcasts 🎙️ and Youtube videos regarding the COVID-19 prevention, awareness and readiness.

* There will be a dashboard of Indian COVID-19 distribution.

***

#### 2. Newsfeed 📰

* The newsfeed module comprises of the news 📰 regarding the COVID-19.

* The news are fetched from the NEWSAPI.

* Top 20 news are displayed in a crisp manner and the user can also navigate to the original data resource.

***

#### 3. Dashboards 📊

* It holds the Dashboards of the Indian and International covid distribution, as well the vaccination.

* The Dashboards are completely live and interactive.

* The dashboards are created using Google Data Studio and Plotly and the data are taken from the reliable data resources.

***

#### 4. Mask Detection 😷

* This module detects if the person wearing the mask or not.

* It's developed using Teachable Machine. :

* It get the live data from the webcam and predict. It can also be embedded in CCTV live feed.

***

#### 5. Hospitals info 🏥 

* It holds the hospital information across the India.

* It will automatically detect the location and shows the hospitals around the user.

* Once the user clicked on the hospital it shows the details such as availability of Beds and all.

***

#### 6. Community Forum 🧑‍🤝‍🧑

* The users can share their thougts and put their queries here. ❓

* Every user can see the posts and can like , dislike and comment on the post. 👍

* The community forum strictly blocks the abuse talks. The posts are monitored by the admins.

* If any post violates the terms it will be removed from the posts and the user will be barred from future posts. 

***

#### 7. Covid prediction 

* Here the users can upload their Chest X-Ray and the model will predict whether the person has COVID-19 or Pneumonia or a healthy person.

* The model is built using CNN and the dataset is taken from the kaggle. 



* Once the user uploaded the image it will be uploaded to the [API](https://covidlungsdetection.herokuapp.com/) and the model will predict the output.

***

#### 8. Vaccine information

* It fetches the data from COWIN API and feeds the data in a compiled manner using the Dashboards.

* Also it contains the state details and district details.

* The user can further drill down and filter the data to know the more insights.

***

#### 9. Payment 💰

* Here the user can donate to the needy people. 

* Also there will be some categories so that the user can donate to a specific cateogry.

* We integrated the PayTM payment gateway so it's secure and encrypted. 

* This module is still in testing phase. Once we get the approval from the PayTM the user can actually make the payment.

***

#### 10. FAQs and Screening test

* Commonly asked FAQs are given here.

* The screening test asks some questions and it allots the weightage to each answers and give us the exposure to the COVID-19 in percentages.

***

#### 11. Profile

* The user can create a new account or log in to his account.

* Also the user can update his profile picture and change the password.

* User can add the bio.

* The owner of the post can edit and delete the post. 

***

#### 12. Survey

* We conduct a small survey about the COVID-19, Vaccines and Work life balance.

* This data is confidential and only for educational purpose.

* The survey is created using the Typeform. 

####

Feel free to contribute to our project. Have a nice day 😃














