from flask import Flask, render_template, request, session
from my_util.weather import get_weather
from datetime import timedelta
app = Flask(__name__)
app.secret_key = "hoseo"

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

@app.route("/")
def index():
    menu = {'ho':1, 'da':0, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'st':0, 'wc':0} #해당 메뉴가 선택되면, active가 되도록
    return render_template('09.m_page.html', menu=menu, weather=get_weather_main())

if __name__ == '__main__':
    app.run(debug=True)