import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from flask import current_app
import pandas as pd
import re

def diningcode(place):
    url_base = 'https://www.diningcode.com/list.php?query='
    keyword = quote(place)
    url = url_base+keyword
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    atags = soup.select_one('.lc-list.high-rank').find('ul').find_all('li')

    rest_list = []
    for i in range(1, 12):
        text = atags[i].get_text().split('\n')
        try:
            rank = text[3].split('. ')[0]
            store = text[3].split('. ')[-1]
            menu = text[4]
            tag = text[5]
            addr = text[6]
            rest_list.append({'rank':rank, 'store':store, 'menu':menu, 'tag':tag, 'addr':addr})
        except:
            pass
    return rest_list

def genie():
    url = 'https://www.genie.co.kr/chart/top200'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
    req = requests.get(url, headers = header)
    soup = BeautifulSoup(req.text, 'html.parser')
    trs = soup.select_one('.list-wrap').find('tbody').select('tr.list')

    music_list = []
    for tr in trs:
        num = tr.select_one('.number').get_text()
        rank = f'<strong>{num.split()[0]}</strong>'
        last = num.split()[1]
        if last == '유지':
            rank += '<br><small>-</small>'
        elif last.find('상승') > 0:
            rank += f'<br><small><span style="color: red;">▲{last[:-2]}</span></small>'
        else:
            rank += f'<br><small><span style="color: blue;">▼{last[:-2]}</span></small>'
        title = tr.select_one('a.title').string.strip()
        artist = tr.select_one('a.artist').string
        album = tr.select_one('a.albumtitle').string
        img = 'https:' + tr.select_one('a.cover').find('img').attrs['src']
        music_list.append({'rank':rank, 'title':title, 'artist':artist,
                            'album':album, 'img':img})
    return music_list

def kyobo():
    url = 'http://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?orderClick=d79'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    lis = soup.select_one('.list_type01').select('li')

    book_list = []
    for li in lis:
        try:
            rank = li.select_one('.cover').find('a').get_text().strip()
            img = li.select_one('.cover').find('img').attrs['src']

            title = li.select_one('.detail').select_one('.title').get_text().strip()
            apd = li.select_one('.detail').select_one('.author').get_text().strip().replace('\r', '').replace('\t', '').replace('\n', '').split('| ')
            author = apd[0] if apd[0].find('저자 더보기') == -1 else apd[0].replace('저자 더보기', '')
            publisher = apd[1]
            date = apd[2]

            star = li.select_one('.review').find('img').attrs['src']

            find_bracket_s = li.select_one('.price').get_text().strip().find('[')
            find_bracket_e = (li.select_one('.price').get_text().strip().find(']'))+1
            r_price = li.select_one('.price').get_text().strip()
            r_price = r_price.replace(r_price[find_bracket_s:find_bracket_e], '')
            r_price = re.sub('\s', '', r_price).replace('|', '\n')

            book_list.append({'rank':rank, 'img':img, 'title':title, 'author':author, 'publisher':publisher,
                                'date':date, 'star':star, 'r_price':r_price})
        except:
            pass

    return book_list