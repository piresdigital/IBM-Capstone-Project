import requests
import json
import os
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},  auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, auth=False, **kwargs):
    if auth:
        try:
            response = requests.get(
                url, headers={'Content-Type': 'application/json'}, params=kwargs, auth=HTTPBasicAuth('apikey', auth))
            return json.loads(response.text)
        except:
            print('Network exception occurred.')
            return {'error': response.status_code}
    else:
        try:
            response = requests.get(
                url, headers={'Content-Type': 'application/json'}, params=kwargs)
            return json.loads(response.text)
        except:
            print('Network exception occurred.')
            return {'error': response.status_code}


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(f"POST to {url}")
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("An error occurred while making POST request. ")
    status_code = response.status_code
    print(f"With status {status_code}")

    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    # Retrieve the dealer data from the response
    dealers = json_result['rows']
    # For each dealer in the response
    for dealer in dealers:
        # Get its data in `doc` object
        dealer_doc = dealer['doc']
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer_doc['address'], city=dealer_doc['city'], full_name=dealer_doc['full_name'], id=dealer_doc['id'], lat=dealer_doc['lat'],
                               long=dealer_doc['long'], short_name=dealer_doc['short_name'], st=dealer_doc['st'], state=dealer_doc['state'], zip=dealer_doc['zip'])
        results.append(dealer_obj)

    return results


# Gets a single dealer from the Cloudant DB with the Cloud Function get-dealerships
def get_dealer_by_id(url, dealer_id):
    # Call get_request with the dealer_id param
    json_result = get_request(url, dealerId=dealer_id)

    # Create a CarDealer object from response
    dealer = json_result["docs"][0]
    dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                           id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                           short_name=dealer["short_name"],
                           st=dealer["st"], state=dealer["state"], zip=dealer["zip"])

    return dealer_obj


# Gets a single dealer from the Cloudant DB with the Cloud Function get-dealerships
def get_dealers_by_state(url, state):
    results = []
    # Call get_request with the dealer_id param
    json_result = get_request(url, state=state)

    # Create a CarDealer object from response
    dealers = json_result["docs"]

    for dealer in dealers:
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                               id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"], state=dealer["state"], zip=dealer["zip"])
        results.append(dealer_obj)

    return results


# Gets all dealer reviews for a specified dealer from the Cloudant DB
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Perform a GET request with the specified dealer id
    json_result = get_request(url, dealerId=dealer_id)

    if json_result:
        # Get all review data from the response
        reviews = json_result["docs"]
        # For every review in the response
        for review in reviews:
            # Create a DealerReview object from the data
            if review['purchase']:
                review_obj = DealerReview(
                    dealership=review["dealership"], id=review["_id"], name=review["name"], purchase=review["purchase"], review=review["review"], car_make=review['car_make'], car_model=review['car_model'], car_year=review['car_year'], purchase_date=review['purchase_date'])
            else:
                review_obj = DealerReview(
                    dealership=review["dealership"], id=review["_id"], name=review["name"], purchase=review["purchase"], review=review["review"])

            # Analysing the sentiment of the review object's review text and saving it to the object attribute "sentiment"
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)

            # Saving the review object to the list of results
            results.append(review_obj)

    return results


# Calls the Watson NLU API and analyses the sentiment of a review
def analyze_review_sentiments(review):
    # Watson NLU configuration
    try:
        if os.environ['WATSON_NLU_URL']:
            url = os.environ['WATSON_NLU_URL']
            api_key = os.environ["WATSON_NLU_API_KEY"]
    except KeyError:
        print('Enviroment variables could not be loaded')

    version = '2022-04-07'
    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version=version, authenticator=authenticator)
    nlu.set_service_url(url)

    # get sentiment of the review
    try:
        response = nlu.analyze(text=review, features=Features(
            sentiment=SentimentOptions())).get_result()
        sentiment_label = response["sentiment"]["document"]["label"]
    except:
        print("Review is too short for sentiment analysis. Assigning default sentiment value 'neutral' instead")
        sentiment_label = "neutral"

    return sentiment_label
