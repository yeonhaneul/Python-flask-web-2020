from flask import Blueprint, render_template, request, session
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import timedelta
import os, folium, json
import pandas as pd
from my_util.weather import get_weather
import my_util.draw_korea as dk

carto_bp = Blueprint('carto_bp', __name__)

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

@carto_bp.route('/coffee', methods=['GET', 'POST'])
def coffee():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':1, 'cr':0, 'st':0, 'wc':0}
    if request.method == 'GET':
        return render_template('/cartogram/coffee.html', menu=menu, weather=get_weather_main())
    else:
        item = request.form['item']
        f = request.files['csv']
        #filename = os.path.join(current_app.root_path, 'static/upload/') + secure_filename(f.filename)
        filename = os.path.join(current_app.root_path, 'static/upload/') + f.filename
        # 보통 f.filename이아니라 secure.filename을 사용하는데, 이는 from werkzeug.utils import secure_filename을 한 뒤에 사용한다.
        # 파일네임이 보안문제를 야기시킬 수 있어, 그대로 파일네임이아닌 보안이 걸린 이름으로 받아오는것이 좋다.
        f.save(filename)
        current_app.logger.info(f'{filename} is saved')
        
        coffee_index = pd.read_csv(filename, dtype={'이디야 매장수':int, '스타벅스 매장수':int, '커피빈 매장수':int, '빽다방 매장수':int})
        color_dict = {'커피지수':'Reds', '이디야 매장수':'Blues', '스타벅스 매장수':"Greens", '커피빈 매장수':"Oranges", '빽다방 매장수':"Purples"}
        
        img_file = os.path.join(current_app.root_path, 'static/img/coffee.png')
        dk.drawKorea(item, coffee_index, color_dict[item], img_file)
        mtime = int(os.stat(img_file).st_mtime)

        df = coffee_index.sort_values(by=item, ascending=False)[['ID', item]].reset_index()
        top10 = {}
        for i in range(10):
            top10[df['ID'][i]] = round(df[item][i], 2)
        print(top10)

        return render_template('cartogram/coffee_res.html', menu=menu, weather=get_weather_main(),
                                mtime=mtime, item=item, top10=top10)

@carto_bp.route('/population/<option>')
def population(option):
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':1, 'cr':0, 'st':0, 'wc':0}
    pop = pd.read_csv('./static/data/population.csv')
    
    option_dict = {'area':'소멸위기지역', 'ratio':'소멸비율', 'girl_ratio':'여성비', 'y_girl_ratio':'2030여성비'}
    color_dict = {'area':'Reds', 'ratio':"Oranges", 'girl_ratio':"RdBu", 'y_girl_ratio':"RdBu"}
    img_file = os.path.join(current_app.root_path, 'static/img/population.png')
    dk.drawKorea(option_dict[option], pop, color_dict[option], img_file)
    mtime = int(os.stat(img_file).st_mtime)
    return render_template('cartogram/population.html', menu=menu, weather=get_weather_main(), mtime=mtime,
                            option=option, option_dict=option_dict, color_dict=color_dict)

@carto_bp.route('/burger', methods=['GET', 'POST'])
def burger():
    menu = {'ho':0, 'da':1, 'ml':0, 'se':0, 'co':0, 'cg':1, 'cr':0, 'st':0, 'wc':0}
    if request.method == 'GET':
        return render_template('cartogram/burger.html', menu=menu, weather=get_weather_main())
    else:
        item = request.form['item']
        f = request.files['csv']
        #filename = os.path.join(current_app.root_path, 'static/upload/') + secure_filename(f.filename)
        filename = os.path.join(current_app.root_path, 'static/upload/') + f.filename
        # 보통 f.filename이아니라 secure.filename을 사용하는데, 이는 from werkzeug.utils import secure_filename을 한 뒤에 사용한다.
        # 파일네임이 보안문제를 야기시킬 수 있어, 그대로 파일네임이아닌 보안이 걸린 이름으로 받아오는것이 좋다.
        f.save(filename)
        current_app.logger.info(f'{filename} is saved')
        
        burger_index = pd.read_csv(filename, dtype={'맥도날드 매장수':int, '버거킹 매장수':int, 'KFC 매장수':int, '롯데리아 매장수':int, '맘스터치 매장수':int})
        color_dict = {'버거지수':'Reds', '맥도날드 매장수':'Blues', '버거킹 매장수':"Greens", 'KFC 매장수':"Oranges", '롯데리아 매장수':"Purples", '맘스터치 매장수':"PuBu"}
        
        img_file = os.path.join(current_app.root_path, 'static/img/burger.png')
        dk.drawKorea(item, burger_index, color_dict[item], img_file)
        mtime = int(os.stat(img_file).st_mtime)

        df = burger_index.sort_values(by=item, ascending=False)[['ID', item]].reset_index()
        top10 = {}
        for i in range(10):
            top10[df['ID'][i]] = round(df[item][i], 2)
        print(top10)

        return render_template('cartogram/burger_res.html', menu=menu, weather=get_weather_main(),
                                mtime=mtime, item=item, top10=top10)