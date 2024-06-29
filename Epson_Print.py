import sys
import os
from urllib import request, parse, error
from http import HTTPStatus
import base64
import json
import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Epson Connect API Configuration
HOST = 'api.epsonconnect.com'
ACCEPT = 'application/json;charset=utf-8'

# Credentials (Directly included for simplicity)
CLIENT_ID = 'bbea82536e774efa93eb2ce1fb769f4a'
SECRET = 'Q74Edy4fCUcU7xSUoFKyT4flZCq2Tgosxr7q2OJI6wkuSwk0ALtzsfaTXFZQSmMm'
DEVICE = 'masterofapi@print.epsonconnect.com'

def authenticate():
    AUTH_URI = f'https://{HOST}/api/1/printing/oauth2/auth/token?subject=printer'
    auth = base64.b64encode(f"{CLIENT_ID}:{SECRET}".encode()).decode()
    query_param = {
        'grant_type': 'password',
        'username': DEVICE,
        'password': ''  # Set the device password
    }
    query_string = parse.urlencode(query_param)
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }
    req = request.Request(AUTH_URI, data=query_string.encode('utf-8'), headers=headers, method='POST')
    try:
        with request.urlopen(req) as res:
            body = res.read()
            if res.status == HTTPStatus.OK:
                return json.loads(body)
            else:
                logger.error(f"Failed to authenticate: {res.status} - {res.reason}")
                return None
    except error.HTTPError as err:
        logger.error(f"HTTP Error: {err.code} - {err.reason}")
        return None
    except error.URLError as err:
        logger.error(f"URL Error: {err.reason}")
        return None

def create_print_job(access_token, subject_id):
    job_uri = f'https://{HOST}/api/1/printing/printers/{subject_id}/jobs'
    data_param = {
        'job_name': 'SampleJob1',
        'print_mode': 'document'
    }
    data = json.dumps(data_param)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8'
    }
    req = request.Request(job_uri, data=data.encode('utf-8'), headers=headers, method='POST')
    try:
        with request.urlopen(req) as res:
            body = res.read()
            if res.status == HTTPStatus.CREATED:
                return json.loads(body)
            else:
                logger.error(f"Failed to create print job: {res.status} - {res.reason}")
                return None
    except error.HTTPError as err:
        logger.error(f"HTTP Error: {err.code} - {err.reason}")
        return None
    except error.URLError as err:
        logger.error(f"URL Error: {err.reason}")
        return None

def upload_print_file(upload_uri, local_file_path):
    _, ext = os.path.splitext(local_file_path)
    file_name = '1' + ext
    upload_uri = f"{upload_uri}&File={file_name}"
    headers = {
        'Content-Length': str(os.path.getsize(local_file_path)),
        'Content-Type': 'application/octet-stream'
    }
    try:
        with open(local_file_path, 'rb') as f:
            req = request.Request(upload_uri, data=f, headers=headers, method='POST')
            with request.urlopen(req) as res:
                if res.status == HTTPStatus.OK:
                    return True
                else:
                    logger.error(f"Failed to upload file: {res.status} - {res.reason}")
                    return False
    except error.HTTPError as err:
        logger.error(f"HTTP Error: {err.code} - {err.reason}")
        return False
    except error.URLError as err:
        logger.error(f"URL Error: {err.reason}")
        return False

def execute_print(access_token, subject_id, job_id):
    print_uri = f'https://{HOST}/api/1/printing/printers/{subject_id}/jobs/{job_id}/print'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    req = request.Request(print_uri, data=''.encode('utf-8'), headers=headers, method='POST')
    try:
        with request.urlopen(req) as res:
            if res.status == HTTPStatus.OK:
                return True
            else:
                logger.error(f"Failed to execute print: {res.status} - {res.reason}")
                return False
    except error.HTTPError as err:
        logger.error(f"HTTP Error: {err.code} - {err.reason}")
        return False
    except error.URLError as err:
        logger.error(f"URL Error: {err.reason}")
        return False

def main():
    auth_response = authenticate()
    if not auth_response:
        logger.error("Authentication failed")
        sys.exit(1)

    subject_id = auth_response.get('subject_id')
    access_token = auth_response.get('access_token')

    job_response = create_print_job(access_token, subject_id)
    if not job_response:
        logger.error("Failed to create print job")
        sys.exit(1)

    job_id = job_response.get('id')
    upload_uri = job_response.get('upload_uri')

    local_file_path = r'C:\OneVision\backend\translated_document.pdf'
    if not upload_print_file(upload_uri, local_file_path):
        logger.error("Failed to upload print file")
        sys.exit(1)

    if not execute_print(access_token, subject_id, job_id):
        logger.error("Failed to execute print")
        sys.exit(1)

if __name__ == "__main__":
    main()
