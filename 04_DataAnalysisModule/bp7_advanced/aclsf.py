from flask import Blueprint, render_template, request, session, g
from flask import current_app
from fbprophet import Prophet
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from sklearn.datasets import load_digits
import os, joblib
import pandas as pd
import re
from konlpy.tag import Okt
import matplotlib.pyplot as plt
from my_util.weather import get_weather

aclsf_bp = Blueprint('aclsf_bp', __name__)

def get_weather_main():
    ''' weather = None
    try:
        weather = session['weather']
    except:
        current_app.logger.info("get new weather info")
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(minutes=60) '''
    weather = get_weather()
    return weather

@aclsf_bp.route('/digits', methods=['GET', 'POST'])
def digits():
    menu = {'ho':0, 'da':0, 'ml':1, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':1, 're':0, 'cu':0}
    if request.method == 'GET':
        return render_template('a_classification/digits.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'] or '0')
        index_list = list(range(index, index+5))
        digits = load_digits()
        df = pd.read_csv('static/data/digits_test.csv')
        img_index_list = df['index'].values
        target_index_list = df['target'].values
        index_list = img_index_list[index:index+5]

        scaler = MinMaxScaler()
        scaled_test = scaler.fit_transform(df.drop(columns=['index','target'], axis=1))
        test_data = scaled_test[index:index+5, :]
        label_list = target_index_list[index:index+5]
        lrc = joblib.load('static/model/digits_lr.pkl')
        svc = joblib.load('static/model/digits_sv.pkl')
        rfc = joblib.load('static/model/digits_rf.pkl')
        pred_lr = lrc.predict(test_data)
        pred_sv = svc.predict(test_data)
        pred_rf = rfc.predict(test_data)

        img_file_wo_ext = os.path.join(current_app.root_path, 'static/img/digit')
        for k, i in enumerate(index_list):
            plt.figure(figsize=(2,2))
            plt.xticks([]); plt.yticks([])
            img_file = img_file_wo_ext + str(k+1) + '.png'
            plt.imshow(digits.images[i], cmap=plt.cm.binary, interpolation='nearest')
            plt.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        result_dict = {'index':index_list, 'label':label_list,
                       'pred_lr':pred_lr, 'pred_sv':pred_sv, 'pred_rf':pred_rf}
        
        return render_template('a_classification/digits_res.html', menu=menu, mtime=mtime,
                                result=result_dict, weather=get_weather())

@aclsf_bp.before_app_first_request
def before_app_first_request():
    global news20_countlr, news20_tfidflr, news20_tfidfsvc, imdb_countlr, imdb_tfidflr, naver_countlr, naver_countnb, naver_tfidflr, naver_tfidfnb
    naver_countlr = joblib.load('static/model/naver_countlr.pkl')
    naver_countnb = joblib.load('static/model/naver_countnb.pkl')
    naver_tfidflr = joblib.load('static/model/naver_tfidflr.pkl')
    naver_tfidfnb = joblib.load('static/model/naver_tfidfnb.pkl')
    news20_countlr = joblib.load('static/model/news20_countlr.pkl')
    news20_tfidflr = joblib.load('static/model/news20_tfidflr.pkl')
    news20_tfidfsvc = joblib.load('static/model/news20_tfidfsvc.pkl')
    imdb_countlr = joblib.load('static/model/IMDB_countlr.pkl')
    imdb_tfidflr = joblib.load('static/model/IMDB_tfidflr.pkl')

@aclsf_bp.route('/news20', methods=['GET', 'POST'])
def news20():
    target_names = ['alt.atheism', 'comp.graphics', 'comp.os.ms-windows.misc',
                    'comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware', 'comp.windows.x',
                    'misc.forsale', 'rec.autos', 'rec.motorcycles', 'rec.sport.baseball',
                    'rec.sport.hockey', 'sci.crypt', 'sci.electronics', 'sci.med', 'sci.space',
                    'soc.religion.christian', 'talk.politics.guns', 'talk.politics.mideast',
                    'talk.politics.misc', 'talk.religion.misc']
    menu = {'ho':0, 'da':0, 'ml':1, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':1, 're':0, 'cu':0}
    if request.method == 'GET':
        return render_template('a_classification/news20.html', menu=menu, weather=get_weather())
    else:
        index = int(request.form['index'] or '0')
        df = pd.read_csv('static/data/new20_test.csv')
        label = f'{df.target[index]} ({target_names[df.target[index]]})'
        test_data = []
        test_data.append(df.data[index])

        pred_cl = news20_countlr.predict(test_data)
        pred_tl = news20_tfidflr.predict(test_data)
        pred_ts = news20_tfidfsvc.predict(test_data)

        result = {'index':index, 'label':label,
                  'pred_cl':f'{pred_cl[0]} ({target_names[pred_cl[0]]})',
                  'pred_tl':f'{pred_tl[0]} ({target_names[pred_tl[0]]})',
                  'pred_ts':f'{pred_ts[0]} ({target_names[pred_ts[0]]})'}
        org = dict(zip(df.columns[:-1], df.iloc[index, :-1]))
        return render_template('a_classification/news20_res.html', menu=menu, 
                                res=result, org=org, news=df.data[index], weather=get_weather())

@aclsf_bp.route('/imdb', methods=['GET', 'POST'])
def imdb():
    menu = {'ho':0, 'da':0, 'ml':1, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':1, 're':0, 'cu':0}
    if request.method == 'GET':
        return render_template('a_classification/imdb.html', menu=menu, weather=get_weather())
    else:
        review_list = []
        if request.form['option'] == 'index':
            index = int(request.form['index'] or '0') # default 0
            df = pd.read_csv('static/data/IMDB/testData.tsv', header=0, sep='\t', quoting=3)
            text_data = df.iloc[index, -1]
            review_list.append(text_data)

            pred_cl = imdb_countlr.predict(review_list)
            pred_tl = imdb_tfidflr.predict(review_list)

            result = {'index':index, 'pred_cl':pred_cl, 'pred_tl':pred_tl}
            
        else:
            review = request.form['review']     
            r_review = review.replace('<br />', ' ')
            n_review = re.sub('[^a-zA-Z]', ' ', r_review)
            review_list.append(n_review)

            pred_cl = imdb_countlr.predict(review_list)
            pred_tl = imdb_tfidflr.predict(review_list)

            result = {'review':review, 'pred_cl':pred_cl, 'pred_tl':pred_tl}
        return render_template('a_classification/imdb_res.html', menu=menu, 
                                res=result, imdb=review_list[0], weather=get_weather())

@aclsf_bp.route('/naver', methods=['GET', 'POST'])
def naver():
    menu = {'ho':0, 'da':0, 'ml':1, 
            'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':1, 're':0, 'cu':0}
    if request.method == 'GET':
        return render_template('a_classification/naver.html', menu=menu, weather=get_weather())
    else:
        if request.form['option'] == 'index':
            index = int(request.form['index'] or '0') # default 0
            df = pd.read_csv('static/data/NaverMovie/test.tsv', sep='\t')
            review_text = df.document[index]
            label = df.label[index]
        else:
            review_text = request.form['review']
            label = '직접확인'  

        review_list = []
        r_review = re.sub('[^ㄱ-ㅎㅏ-ㅣ가-힣 ]', '', review_text)
        okt = Okt()
        stopwords = ['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다', '을']
        morphs = okt.morphs(r_review, stem=True)
        n_review = ' '.join([word for word in morphs if not word in stopwords])
        review_list.append(n_review)

        pred_cl = naver_countlr.predict(review_list)
        pred_cn = naver_countnb.predict(review_list)
        pred_tl = naver_tfidflr.predict(review_list)
        pred_tn = naver_tfidfnb.predict(review_list)

        result = {'label':label,
                'pred_cl':pred_cl[0],
                'pred_tl':pred_tl[0],
                'pred_cn':pred_cn[0],
                'pred_tn':pred_tn[0]}
        return render_template('a_classification/naver_res.html', menu=menu, 
                                res=result, naver=review_text, weather=get_weather())