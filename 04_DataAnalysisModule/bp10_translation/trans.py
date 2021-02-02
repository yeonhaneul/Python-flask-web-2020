from flask import Blueprint, render_template, request, session
from flask import current_app
from fbprophet import Prophet
from datetime import datetime, timedelta
import os
import json
import requests
import pandas as pd
from urllib.parse import quote
import pandas_datareader as pdr
from my_util.weather import get_weather
from my_util.trans_util import naver_trans, kakao_trans
import matplotlib.pyplot as plt 

trans_bp = Blueprint('trans_bp', __name__)

def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        current_app.logger.info("get new weather info")
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=60)
    return weather

@trans_bp.route('/trans', methods=['GET', 'POST'])
def trans():
    menu = {'ho':0, 'da':0, 'ml':1, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0, 'cf':0, 'ac':0, 're':0, 'cu':0, 'tr':1}
    if request.method == 'GET':
        return render_template('translation/trans.html', menu=menu, weather=get_weather())
    else:
        text = request.form['text']
        feature = request.form['feature']
        naver_target = {'en':'en', 'jp':'ja', 'cn':'zh-CN', 'fr':'fr', 'es':'es'}
        kakao_target = {'en':'en', 'jp':'jp', 'cn':'cn', 'fr':'fr', 'es':'es'}
        
        with open('static/keys/papago_key.json') as nkey:
            json_str = nkey.read(100)
        
        with open('static/keys/kakaoaikey.txt') as kfile:
            kai_key = kfile.read(100)
        
        naver = naver_trans(text, 'ko', naver_target[feature], json_str)
        kakao = kakao_trans(text, 'kr', kakao_target[feature], kai_key)

        result = {'text':text, 'naver':naver, 'kakao':kakao}
        return render_template('translation/trans_res.html', menu=menu, weather=get_weather(), res=result, feature=feature)

@trans_bp.route('/tts', methods=['GET', 'POST'])
def tts():
    menu = {'ho':0, 'da':0, 'ml':1, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0, 'cf':0, 'ac':0, 're':0, 'cu':0, 'tr':1}
    if request.method == 'GET':
        return render_template('translation/tts.html', menu=menu, weather=get_weather_main())
    else:
        text = request.form['text']
        speaker = request.form['speaker']
        pitch = request.form['pitch']
        speed = request.form['speed']
        volume = request.form['volume']
        emotion = request.form['emotion']

        with open('static/keys/clova_key.json') as nkey:
            json_str = nkey.read(100)
        json_obj = json.loads(json_str)
        client_id = list(json_obj.keys())[0]
        client_secret = json_obj[client_id]

        url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        val = {
            "speaker": speaker, "speed": speed, "text": text,
            "pitch": pitch, "volume": volume, "emotion": emotion
        }
        response = requests.post(url, data=val, headers=headers)
        rescode = response.status_code
        audio_file = os.path.join(current_app.root_path, 'static/img/cpv.mp3')
        if(rescode == 200):
            with open(audio_file, 'wb') as f:
                f.write(response.content)
        mtime = int(os.stat(audio_file).st_mtime)

        return render_template('translation/tts_res.html', menu=menu, weather=get_weather_main(),
                                res=val, mtime=mtime)
