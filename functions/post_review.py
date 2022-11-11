from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException


def main(dic):
    try:
        authenticator = IAMAuthenticator(dic['IAM_API_KEY'])
        service = CloudantV1(authenticator=authenticator)
        service.set_service_url(dic['COUCH_URL'])

        document_response = service.post_document(
            db='reviews',
            document=dic['review']
        ).get_result()

        return {'document': document_response}

    except ApiException as ae:
        return {"error": 'Something went wrong on the server.'}
