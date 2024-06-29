# 파파고 API 번역 진행 상태 확인

import requests

def check_translation_status(api_url, api_key_id, api_key, request_id):
    status_url = f"{api_url}/status?requestId={request_id}"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": api_key_id,
        "X-NCP-APIGW-API-KEY": api_key
    }
    response = requests.get(status_url, headers=headers)
    
    # Error handling
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

# Example usage
api_url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1"
api_key_id = "h9r6m27w0d"
api_key = "7PbdD8RtQR0AyEwsp11tvqjazukN33AfAePbhuAa"
request_id = '20240620_1718890845654_074'

try:
    status = check_translation_status(api_url, api_key_id, api_key, request_id)
    print(status)
except Exception as e:
    print(e)
