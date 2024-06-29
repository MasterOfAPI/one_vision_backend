# 파파고 API 문서 다운로드

import requests

def download_translated_document(api_url, api_key_id, api_key, request_id, output_file_path):
    download_url = f"{api_url}/download?requestId={request_id}"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": api_key_id,
        "X-NCP-APIGW-API-KEY": api_key
    }
    response = requests.get(download_url, headers=headers)
    
    # Error handling
    if response.status_code == 200:
        with open(output_file_path, 'wb') as f:
            f.write(response.content)
        print(f"Translated document downloaded to {output_file_path}")
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

# Example usage
api_url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1"
api_key_id = "h9r6m27w0d"
api_key = "7PbdD8RtQR0AyEwsp11tvqjazukN33AfAePbhuAa"
request_id = '20240620_1718890845654_074'
output_file_path = '/Users/yoon/Downloads/OneVision/backend/translated_document.pdf'

try:
    download_translated_document(api_url, api_key_id, api_key, request_id, output_file_path)
except Exception as e:
    print(e)
