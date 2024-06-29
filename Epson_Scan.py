import sys
from urllib import request, parse, error
from http import HTTPStatus
import base64
import json

HOST = 'api.epsonconnect.com'
ACCEPT = 'application/json;charset=utf-8'

CLIENT_ID = 'bbea82536e774efa93eb2ce1fb769f4a'
SECRET = 'Q74Edy4fCUcU7xSUoFKyT4flZCq2Tgosxr7q2OJI6wkuSwk0ALtzsfaTXFZQSmMm'
DEVICE = 'masterofapi@print.epsonconnect.com'

def authenticate():
    AUTH_URI = f'https://{HOST}/api/1/printing/oauth2/auth/token?subject=printer'
    auth = base64.b64encode(f"{CLIENT_ID}:{SECRET}".encode()).decode()
    query_param = {
        'grant_type': 'password',
        'username': DEVICE,
        'password': ''
    }
    query_string = parse.urlencode(query_param)
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
    }

    try:
        req = request.Request(AUTH_URI, data=query_string.encode('utf-8'), headers=headers, method='POST')
        with request.urlopen(req) as res:
            body = res.read()
            if res.status == HTTPStatus.OK:
                return json.loads(body)
            else:
                print(f"Failed to authenticate: {res.status} - {res.reason}")
                return None
    except error.HTTPError as err:
        print(f"HTTP Error: {err.code} - {err.reason}")
        return None
    except error.URLError as err:
        print(f"URL Error: {err.reason}")
        return None

def register_scan_destination(access_token, subject_id):
    add_uri = f'https://{HOST}/api/1/scanning/scanners/{subject_id}/destinations'
    data_param = {
        'alias_name': 'google_email',
        'type': 'mail',
        'destination': 'musicstar9588@gmail.com'
    }
    data = json.dumps(data_param)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8'
    }

    try:
        req = request.Request(add_uri, data=data.encode('utf-8'), headers=headers, method='POST')
        with request.urlopen(req) as res:
            body = res.read()
            if res.status == HTTPStatus.OK:
                return json.loads(body)
            else:
                print(f"Failed to register scan destination: {res.status} - {res.reason}")
                return None
    except error.HTTPError as err:
        print(f"HTTP Error: {err.code} - {err.reason}")
        return None
    except error.URLError as err:
        print(f"URL Error: {err.reason}")
        return None

def main():
    auth_response = authenticate()
    if not auth_response:
        print("Authentication failed")
        sys.exit(1)

    subject_id = auth_response.get('subject_id')
    access_token = auth_response.get('access_token')

    scan_response = register_scan_destination(access_token, subject_id)
    if not scan_response:
        print("Failed to register scan destination")
        sys.exit(1)

if __name__ == "__main__":
    main()
