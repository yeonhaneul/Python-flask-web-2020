def get_weather():
    import requests
    from urllib.parse import urlparse, quote
    import pandas as pd

    # 강서구 검색하기
    key_fd = open('kakaomapkey.txt', mode='r')
    kmap_key = key_fd.read(100)
    key_fd.close()

    keyword = '강서구'
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query=' + quote(keyword)
    result = requests.get(url,headers={'Authorization': "KakaoAK "+kmap_key}).json()
    
    lat = float(result['documents'][0]['y'])
    lng = float(result['documents'][0]['x'])

    # openweather 받기
    key_fd = open('oepnweatherkey.txt', mode='r')
    oweather_key = key_fd.read(100)
    key_fd.close()

    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={oweather_key}&units=metric&lang=kr'
    result = requests.get(urlparse(url).geturl()).json()
    main = result['weather'][0]['main']
    desc = result['weather'][0]['description']
    icon = result['weather'][0]['icon']
    temp = result['main']['temp']
    temp_min = result['main']['temp_min']
    temp_max = result['main']['temp_max']
    temp = round(float(temp)+0.01, 1)
    
    html = f'<img src= "http://openweathermap.org/img/w/{icon}.png" height="32"> <strong>{desc}</strong>, 온도: <strong>{temp}&#8451</strong>, {temp_min}/{temp_max}&#8451'

    return html