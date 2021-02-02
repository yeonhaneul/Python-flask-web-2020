import json
import requests
from urllib.parse import quote

def naver_trans(text, src, target, json_str):
    json_obj = json.loads(json_str) # 오브젝트(딕셔너리) 출력
    client_id = list(json_obj.keys())[0] # 딕셔너리의 key(ID)출력
    client_secret = json_obj[client_id]

    naver_url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"

    val = {
    "source": src,
    "target": target,
    "text": text
    }

    headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret
    }

    response = requests.post(naver_url, data=val, headers=headers)
    result = response.json()
    trans_text = result['message']['result']['translatedText']

    return trans_text

def kakao_trans(text, src, target, kai_key):
    def generate_url(text, src, target):
        return f'https://dapi.kakao.com/v2/translation/translate?query={quote(text)}&src_lang={src}&target_lang={target}'
    result = requests.get(generate_url(text, src, target), headers={"Authorization": "KakaoAK "+kai_key}).json()
    trans_text = result['translated_text']
    for nested_element in trans_text:
        return nested_element[0]