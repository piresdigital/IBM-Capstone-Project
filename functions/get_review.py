from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException


def main(dic):
    try:
        authenticator = IAMAuthenticator(dic['IAM_API_KEY'])
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(dic['COUCH_URL'])

        dealerReviews = service.post_find(
            db='reviews',
            selector={'dealership': {'$eq': int(dic['dealerId'])}}).get_result()

        return dealerReviews

    except ApiException as ae:
        if (ae.code == 404):
            return {'error': 'Dealer does not exist'}
        else:
            return {'error': 'Something went wrong on the server'}
