from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import os

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
def about_us(request):
    context = {}
    return render(request, 'djangoapp/about-us.html', context)


# Create a `contact` view to return a static contact page
# def contact(request):
def contact_us(request):
    context = {}
    return render(request, 'djangoapp/contact-us.html', context)


# Create a `login_request` view to handle sign in request
# def login_request(request):
def login_request(request):
    context = {}

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # try to authenticate user
        user = authenticate(username=username, password=password)

        # if user exists login if not show same page with a error message
        if (user) is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = 'Incorrect username or password.'
            context['login'] = True
            return render(request, 'djangoapp/login.html', context)

    else:
        context['login'] = True
        return render(request, 'djangoapp/login.html', context)


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
# def registration_request(request):
def registration_request(request):
    context = {}

    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)

    elif request.method == 'POST':
        # get user input
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        password = request.POST['password']

        try:
            # check if user is already registered
            isUser = User.objects.get(username=username)

            if isUser is not None:
                context['message'] = 'User already exist.'
                return render(request, 'djangoapp/registration.html', context)
        except:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect('djangoapp:index')


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    url = "https://au-syd.functions.appdomain.cloud/api/v1/web/54dce734-f891-4f6a-902f-730861fecd05/capstoneproject-package/get_dealership.json"

    context["dealerships"] = get_dealers_from_cf(url)

    return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        reviewUrl = 'https://au-syd.functions.appdomain.cloud/api/v1/web/54dce734-f891-4f6a-902f-730861fecd05/capstoneproject-package/get_review.json'
        dealerUrl = "https://au-syd.functions.appdomain.cloud/api/v1/web/54dce734-f891-4f6a-902f-730861fecd05/capstoneproject-package/get_dealership.json"
        reviews = get_dealer_reviews_from_cf(reviewUrl, dealer_id=dealer_id)
        dealer = get_dealer_by_id(dealerUrl, dealer_id=dealer_id)
        context = {
            "reviews":  reviews,
            "dealer": dealer,
            "dealer_id": dealer_id
        }

        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == 'GET':
            # show user the add review form
            url = f'https://au-syd.functions.appdomain.cloud/api/v1/web/54dce734-f891-4f6a-902f-730861fecd05/capstoneproject-package/get_dealership.json?dealerId={dealer_id}'
            list_car_models = CarModel.objects.all()
            context = {
                "cars": list_car_models,
                "dealer": get_dealer_by_id(url, dealer_id=dealer_id)
            }

            return render(request, 'djangoapp/add_review.html', context)
        if request.method == 'POST':
            # add review to the database
            review = dict()
            review["name"] = request.user.first_name
            review["dealership"] = dealer_id
            review["review"] = request.POST["content"]
            review["purchase"] = request.POST.get("purchasecheck")

            # if purchased is True
            if review["purchase"]:
                review["purchase_date"] = request.POST.get("purchasedate")
            else:
                review['purchase_date'] = None

            car = CarModel.objects.get(pk=request.POST['car'])

            review['car_make'] = car.car_make.name
            review['car_model'] = car.name
            review['car_year'] = car.year

            url = 'https://au-syd.functions.appdomain.cloud/api/v1/web/54dce734-f891-4f6a-902f-730861fecd05/capstoneproject-package/post_review.json'
            payload = {"review": review}

            auth = ''

            try:
                if os.environ['CLOUDANT_API']:
                    auth = os.environ['CLOUDANT_API']
            except KeyError:
                print('Environment variables could not be loaded')

            # make the POST request
            result = post_request(
                url, payload, auth=auth,  dealer_id=dealer_id)

            # if post were successful
            if int(result.status_code) == 200:
                print('Review was added successfully')

            return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
    else:
        return redirect('djangoapp:login')
