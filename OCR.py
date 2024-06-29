# 파파고 API 문서번역

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import uuid

def translate_document(api_url, api_key_id, api_key, file_path, source_lang='en', target_lang='ko'):
    # Use a with statement to safely open and close the file
    with open(file_path, 'rb') as file:
        data = {
            'source': source_lang,
            'target': target_lang,
            'file': (file_path, file, 'application/octet-stream', {'Content-Transfer-Encoding': 'binary'})
        }
        m = MultipartEncoder(data, boundary=uuid.uuid4())

        headers = {
            "Content-Type": m.content_type,
            "X-NCP-APIGW-API-KEY-ID": api_key_id,
            "X-NCP-APIGW-API-KEY": api_key
        }

        response = requests.post(api_url, headers=headers, data=m.to_string())

        # Error handling
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

# Configuration values
api_url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/translate"
api_key_id = "h9r6m27w0d"
api_key = "7PbdD8RtQR0AyEwsp11tvqjazukN33AfAePbhuAa"
file_path = '/Users/yoon/Downloads/backend/visa_document.pdf' # Check Your Path

# Example usage
try:
    translated_text = translate_document(api_url, api_key_id, api_key, file_path)
    print(translated_text)
except Exception as e:
    print(e)

