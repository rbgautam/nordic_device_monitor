import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from google.oauth2 import service_account
import os
import json
import requests
import datetime
import python_jwt as jwt
from requests.models import HTTPError
from Crypto.PublicKey import RSA
import uuid
from firebase_admin import auth
from oauth2client.service_account import ServiceAccountCredentials
import google.auth

cert_dict = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])


scopes = [
                'https://www.googleapis.com/auth/firebase.database',
                'https://www.googleapis.com/auth/userinfo.email',
                "https://www.googleapis.com/auth/cloud-platform"
            ]



def create_token_uid():
    cred = credentials.Certificate(cert_dict)
    default_app = firebase_admin.initialize_app(cred,{
    'projectId': 'jupiter-flutter'})
    print(default_app)
    # requests = requests.Session()
    
    # [START create_token_uid]
    uid =  uuid.uuid4().urn
    custom_token = auth.create_custom_token(uid)
    # [END create_token_uid]
    # firebase_admin.delete_app(default_app)
    return custom_token

def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        # raise detailed error message
        # TODO: Check if we get a { "error" : "Permission denied." } and handle automatically
        raise HTTPError(e, request_object.text)

def connect_to_firebase():
    uid =  uuid.uuid4().urn
    json_acct_info = cert_dict
    credentials = service_account.Credentials.from_service_account_info(
    json_acct_info)

    scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])

    # credentials, project = google.auth.default()
    firestore_db = firestore.Client(project='jupiter-flutter', credentials=credentials)

    #read data
    snapshots = list(firestore_db.collection(u'api_keys').get())
    for snapshot in snapshots:
        print(snapshot.to_dict())   

    #write data
    data = {
    u'key': u'nRFCloud',
    u'userId': u'RifjRnC6FXdKLCizm6DUyeXcMMm2',
    u'userName': u'conexiotech@gmail.com',
    u'value': u'6e7895fd68747e0bc51df10d2256f615485068db',
    }

    # Add a new doc in collection 'cities' with ID 'LA'
    # firestore_db.collection(u'api_keys').document(uid).set(data)
    firestore_db.collection(u'api_keys').add(document_data=data,document_id=uid)
   
def read_from_firebase(project,collection):
    uid =  uuid.uuid4().urn
    json_acct_info = cert_dict
    try:
        credentials = service_account.Credentials.from_service_account_info(
        json_acct_info)

        scoped_credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform'])

        # credentials, project = google.auth.default()
        firestore_db = firestore.Client(project=project, credentials=credentials)

        #read data
        snapshots = list(firestore_db.collection(collection).get())
        # for snapshot in snapshots:
        #     print(snapshot.to_dict())
        return snapshots
    except Exception as ex:
        print(ex)

def write_to_firebase(project,collection,data,doc_id):
    uid =  uuid.uuid4().urn
    json_acct_info = cert_dict
    try:
        credentials = service_account.Credentials.from_service_account_info(
        json_acct_info)

        scoped_credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform'])

        # credentials, project = google.auth.default()
        firestore_db = firestore.Client(project=project, credentials=credentials)

        #write data
        # data = {
        # u'user_id': u'RifjRnC6FXdKLCizm6DUyeXcMMm2',
        # u'user_name': u'conexiotech@gmail.com',
        # u'api_key': u'6e7895fd68747e0bc51df10d2256f615485068db',
        # }

        # Add a new doc in collection 'cities' with ID 'LA'
        firestore_db.collection(collection).document(doc_id).set(data, {merge: true})
        # Add new document with doc_id in collection
        # firestore_db.collection(collection).add(document_data=data,document_id=doc_id)
    except Exception as ex:
        print(ex)

def upsert_to_firebase(project,collection,data,doc_id):
    uid =  uuid.uuid4().urn
    json_acct_info = cert_dict
    try:
        credentials = service_account.Credentials.from_service_account_info(
        json_acct_info)

        scoped_credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform'])

        
        firestore_db = firestore.Client(project=project, credentials=credentials)
        doc_ref = firestore_db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
             doc_ref.update(data)
        else:
        # Add a new doc in collection 'cities' with ID 'LA'
            firestore_db.collection(collection).document(doc_id).set(data)
        # Add new document with doc_id in collection
        # firestore_db.collection(collection).add(document_data=data,document_id=doc_id)
    except Exception as ex:
        print(ex)


def implicit():
    from google.cloud import storage
    json_acct_info = cert_dict
    credentials = service_account.Credentials.from_service_account_info(
    json_acct_info)
    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client(project='jupiter-flutter', credentials=credentials)

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)

# connect_to_firebase()
# implicit()