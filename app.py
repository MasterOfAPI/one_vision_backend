import os
import time
import requests
import uuid
import base64
from urllib import parse
from Epson_Print import authenticate, create_print_job, execute_print, upload_print_file
from check_status import check_translation_status
from down_transfile import download_translated_document
from flask import Flask, json, request, jsonify, render_template_string
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pdf2image import convert_from_path

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
SCAN_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'scans')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(SCAN_UPLOAD_FOLDER):
    os.makedirs(SCAN_UPLOAD_FOLDER)

# Epson Connect API configuration
HOST = 'api.epsonconnect.com'
CLIENT_ID = 'bbea82536e774efa93eb2ce1fb769f4a'
SECRET = 'Q74Edy4fCUcU7xSUoFKyT4flZCq2Tgosxr7q2OJI6wkuSwk0ALtzsfaTXFZQSmMm'
DEVICE = 'masterofapi@print.epsonconnect.com'

# Papago API configuration
PAPAGO_API_URL = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1"
API_KEY_ID = "z4rq4ov19l"
API_KEY = "FRhyAL1AvbHmlwiym6iQbcWIWv8usIv1odPwryAN"
TARGET_LANG = 'en'  # Target language for translation

# Route to handle file uploads, scanning, translation, and printing
@app.route('/process_scan_translate_print', methods=['POST'])
def process_scan_translate_print():
    try:
        # Step 1: Scan document and upload to local server
        scan_file = request.files['file']
        if scan_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        scan_file_path = os.path.join(SCAN_UPLOAD_FOLDER, scan_file.filename)
        scan_file.save(scan_file_path)

        # Step 2: Call Papago API for document translation
        translated_pdf_path = translate_document(scan_file_path)

        time.sleep(20)

        # Step 3: Print translated PDF using Epson Print API
        print_job_status = print_document(translated_pdf_path)

        return jsonify({
            'message': 'Scan, translate, and print process completed successfully',
            'print_job_status': print_job_status
        }), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

# Function to call Papago API for document translation
def translate_document(file_path):
    with open(file_path, 'rb') as file:
        
        data = {
            'source': 'ko',  # Source language (English)
            'target': TARGET_LANG,
            'file': (file_path, file, 'application/octet-stream', {'Content-Transfer-Encoding': 'binary'})
        }
        
        m = MultipartEncoder(data, boundary=uuid.uuid4())
        
        headers = {
            "Content-Type": m.content_type,
            "X-NCP-APIGW-API-KEY-ID": API_KEY_ID,
            "X-NCP-APIGW-API-KEY": API_KEY
        }

        response = requests.post("https://naveropenapi.apigw.ntruss.com/doc-trans/v1/translate", headers=headers, data=m.to_string())

        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Papago API request failed with status code {response.status_code}: {response.text}")

# Function to print document using Epson Print API
def print_document(pdf_path):
    subject_id, access_token = authenticate_and_get_token()

    print_uri = f'https://{HOST}/api/1/printing/printer/' + subject_id + '/print'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8'
    }
    data_param = {
        'file_type': 'pdf',
        'file': base64.b64encode(open(pdf_path, 'rb').read()).decode('utf-8')
    }
    data = json.dumps(data_param)
    response = requests.post(print_uri, headers=headers, data=data)

    if response.status_code == 200:
        return 'Print job submitted successfully'
    else:
        raise Exception(f"Epson Print API request failed with status code {response.status_code}: {response.text}")

# Function to authenticate and get token from Epson API
def authenticate_and_get_token():
    auth_uri = f'https://{HOST}/api/1/printing/oauth2/auth/token?subject=printer'
    auth = base64.b64encode(f'{CLIENT_ID}:{SECRET}'.encode()).decode()
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

    response = requests.post(auth_uri, headers=headers, data=query_string)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('subject_id'), response_data.get('access_token')
    else:
        raise Exception(f"Epson API authentication failed with status code {response.status_code}: {response.text}")

#@Author KBS
#@DESC 공장장의 매운맛을 보여주마
@app.route('/trans/document', methods=['POST'])
def postTranslateDocument():
    
    try:
        # Step 1: Scan document and upload to local server
        scan_file = request.files['file']
        if scan_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        scan_file_path = os.path.join(SCAN_UPLOAD_FOLDER, scan_file.filename)
        scan_file.save(scan_file_path)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    
    try :
        # Step 2: Call Papago API for document translation
        requestJson = translate_document(scan_file_path)
        data = json.loads(requestJson)
        requestID = data["data"]["requestId"]

        if (requestID == "" or requestID == None) :
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({"id" : requestID}), 200

#@Author KBS
#@DESC 공장장의 매운맛을 보여주마 2
@app.route('/trans/document', methods=['GET'])
def getTranslateResult() : 

    args = request.args
    requestId = args.get("request", default="", type=str)

    if (requestId == "") :
        return jsonify({"status" : "fail"}), 404
    
    result = check_translation_status("https://naveropenapi.apigw.ntruss.com/doc-trans/v1", API_KEY_ID, API_KEY, requestId)
    
    status = result["data"]["status"]
    percent = result["data"]["progressPercent"]

    if (status == "COMPLETE") :
        
        download_translated_document("https://naveropenapi.apigw.ntruss.com/doc-trans/v1", API_KEY_ID, API_KEY, requestId, '/Users/yoon/Desktop/one_vision_backend/translated_document.pdf')

        # 프린터 인증 시작
        auth_response = authenticate()
        if not auth_response:
            return jsonify({"status" : "fail"}), 417

        subject_id = auth_response.get('subject_id')
        access_token = auth_response.get('access_token')
        job_response = create_print_job(access_token, subject_id)
        
        if not job_response:
            return jsonify({"status" : "fail"}), 417

        job_id = job_response.get('id')
        upload_uri = job_response.get('upload_uri')
        upload_print_file(upload_uri, '/Users/yoon/Desktop/one_vision_backend/translated_document.pdf')
        execute_print(access_token, subject_id, job_id)

        return jsonify({"status" : "success"}), 200

    elif (status == "WAITING" or status == "PROGRESS"):
        return jsonify({"status" : "PROGRESS", "percent" : percent}), 200
    else :
        return jsonify({"status" : "fail"}), 417
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

