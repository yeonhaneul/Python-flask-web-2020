from flask import Flask, render_template, session, request
from fbprophet import Prophet
from datetime import datetime, timedelta
import os
import pandas as pd
import pandas_datareader as pdr
import matplotlib as mpl 
import matplotlib.pyplot as plt 
# 한글폰트 사용
mpl.rc('font', family='Malgun Gothic')
mpl.rc('axes', unicode_minus=False)

from my_util.weather import get_weather
app = Flask(__name__)
app.secret_key = 'qwert12345'

def get_weather_main():
    weather = None
    try:
        weather = session['weather']
    except:
        app.logger.info("get new weather info") # 개발중에는 보통 debug나 trace를 사용하며, 사용이 완료된 후 윗레벨인 info를 사용한다.
        weather = get_weather()
        session['weather'] = weather
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60)
    return weather

@app.before_first_request # 웹 서버가 처음의 리퀘스트를 처리하기 전에 한번만 처리 (메모리를 잡아먹지 않게하기 위하여)
def defore_first_request():
    kospi = pd.read_csv('./static/data/kospi.csv', dtype={'종목코드':str})
    for i in kospi.index:
        kospi_dict[kospi['종목코드'][i]] = kospi['기업명'][i]
    kosdaq = pd.read_csv('./static/data/kosdaq.csv', dtype={'종목코드':str})
    for i in kosdaq.index:
        kosdaq_dict[kosdaq['종목코드'][i]] = kosdaq['기업명'][i]

@app.before_request
def before_request():
    pass # 모든 GET 요청을 처리하기 전에 앞서서 공통적으로 어떠한 일을 처리한다. (타이밍을 맞추기 위하여 / 메모리를 위하여)

@app.route("/")
def index():
    menu = {'ho':1, 'da':0, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0} #해당 메뉴가 선택되면, active가 되도록
    return render_template('09.m_page.html', menu=menu, weather=get_weather_main())

@app.route("/stock", methods=['GET', 'POST'])
def stock():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':1, 'wc':0} #해당 메뉴가 선택되면, active가 되도록
    if request.method == 'GET':
        # 종목 코드의경우, 하루에 한번만 작동되면 되기 때문에 밖으로 빼놓는편이 데이터 로딩을 하기에 더욱 수월하다.
        return render_template('10.stock.html', menu=menu, weather=get_weather_main(), kospi=kospi_dict, kosdaq=kosdaq_dict)
    else:
        learn_period = int(request.form['learn'])
        pred_period = int(request.form['pred'])
        today = datetime.now()
        start_learn = today - timedelta(datys - learn_period*365)
        end_learn = today - timedelta(days=1)
        end_pred = today + timedelta(days=pred_period)

        stock_data = pdr.DataReader(code, data_source='yahoo', start=start_learn, end=end_learn)
        app.logger.debug("get stock data")
        df = pd.DataFrame({'ds':stock_data.index, 'y':stock_data['Close']})
        df.reset_index(inplace=True)
        del df['Date']

        model = Prophet(daily_seasonality=True)
        model.fit(df)
        app.logger.debug(f'학습 완료')
        future = model.make_future_dataframe(periods = pred_period)
        forecast = model.predict(future)
        fig = model.plot(forecast);
        img_file = os.path.join(app.root_path, 'static/img/stock.png')
        fig.savefig(img_file)
        mtime = int(os.stat(img_file).st_mtime)

        return render_template('10.stock_res.html', menu=menu, weather=get_weather_main(), mtime=mtime)

if __name__ == '__main__':
    app.run(debug=True)