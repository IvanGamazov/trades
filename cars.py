import requests
import sys
import ssl
import urllib.request as req
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
import openpyxl as excel
import os
from datetime import datetime, date, time

CARS_URL = 'https://xn----etbpba5admdlad.xn--p1ai/bankrot?categorie_childs%5B0%5D=2&regions%5B0%5D=50&regions%5B1%5D=77&section=%D0%91%D0%B0%D0%BD%D0%BA%D1%80%D0%BE%D1%82%D1%81%D1%82%D0%B2%D0%BE&forms%5B0%5D=public&forms%5B1%5D=auction&page='

CARS_EN_URL = 'https://xn----etbpba5admdlad.xn--p1ai/bankrot?categorie_childs%5B0%5D=2&regions%5B0%5D=50&regions%5B1%5D=77&section=%D0%91%D0%B0%D0%BD%D0%BA%D1%80%D0%BE%D1%82%D1%81%D1%82%D0%B2%D0%BE&forms%5B0%5D=public&forms%5B1%5D=auction&page=1'


#PAGE_URL = 'https://www.afisha.ru'

 #-*- coding: utf-8 -*-

def fetch_torgi_page():
    page = NamedTemporaryFile()
    urlretrieve(CARS_EN_URL, page.name)
    return page

def fetch_one_page(pgnum):
    page = NamedTemporaryFile()
    urlretrieve(CARS_URL+str(pgnum), page.name)
    return page


def get_car_info_from_div(div):
    block_divs = div.find_all('div')
    car_id = get_car_id(block_divs)
    car_name = get_car_name(block_divs)
    car_info = get_car_info(block_divs)
    car_price = get_car_price(block_divs)
    car_link = get_car_link(block_divs)
    auction_type = get_car_auction_type(block_divs)
    #name = get_cinema_caption(block_divs)
    return {'id': car_id, 'name': car_name, 'price': car_price, 'link': car_link, 'type': auction_type, 'info': car_info}


def get_cars_from_torgi(divs):
    car_divs = list(filter(lambda div: 'class' in div.attrs and
                                         'lot-card-wrapper' in div.get('class'), divs))
    cars = list(map(lambda div: get_car_info_from_div(div), car_divs))
    return cars


def get_car_id(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'component4__header' in car_div.get('class'):
            return car_div.span.string

def get_car_link(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'component4__body' in car_div.get('class'):
            return car_div.a.get('href')

def get_car_name(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'component4__body' in car_div.get('class'):
            return car_div.h3.string

def get_car_info(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'component4__body' in car_div.get('class'):
                try:        
                    return car_div.p.string
                except AttributeError:
                    return ""
                     

def get_car_price(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'new-component1__price' in car_div.get('class'):
            return car_div.p.string

def get_car_auction_type(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'new-component1' in car_div.get('class'):
            return car_div.a.img.get('data-tooltip')

def parse_cars_list(raw_html_file):
    soup = BeautifulSoup(raw_html_file.read(), 'html.parser')
    div_tags = soup.find_all('div')
    return div_tags

def parse_pages_list(raw_html_file):
    soup = BeautifulSoup(raw_html_file.read(), 'html.parser')
    li_tags = soup.find_all('li')
    return li_tags

def parse_page(raw_html_file):
    soup = BeautifulSoup(raw_html_file.read(), 'html.parser')
    div_tags = soup.find_all('div')
    li_tags = soup.find_all('li')
    return div_tags, li_tags


def get_page_count(divs):
    pages_list = list(filter(lambda li: 'class' in li.attrs and 'page-item' in li.get('class'), divs))
   # pagination = list(filter(lambda div: 'class' in div.attrs and 'pagination' in div.get('class'), divs))
   # pages_count = len(pagination.ul.find_all('li'))
   # return pages_count
    return len(pages_list)-2

def get_cars_on_page(page):
    page_name = fetch_one_page(page)
    page_div_tags, page_li_tags = parse_page(page_name)
    cars_on_page = get_cars_from_torgi(page_div_tags)
    return cars_on_page

def put_to_excel(cars):
    filename = os.path.abspath('Trades.xlsx')
    workbook = excel.load_workbook(filename)
    ws = workbook['LastDownload']
    target = workbook.copy_worksheet(ws)
    target.title = 'Download'+str(datetime.date(datetime.today()))
    for row in ws['A2:F'+str(ws.max_row)]:
        for cell in row:
            cell.value = None
    row = 2 
    for car in cars:
        ws.cell(row=row, column=1, value=car['id'])
        ws.cell(row=row, column=2, value=car['name'])
        ws.cell(row=row, column=3, value=car['price'])
        ws.cell(row=row, column=4, value=car['link'])
        ws.cell(row=row, column=5, value=car['type'])
        ws.cell(row=row, column=6, value=car['info'])
        row = row +1
    workbook.save(filename)
    workbook.close()


def put_new_to_excel(cars):
    filename = os.path.abspath('Trades.xlsx')
    workbook = excel.load_workbook(filename)
    ws = workbook['New']
    for row in ws['A2:F'+str(ws.max_row)]:
        for cell in row:
            cell.value = None
    row = 2 
    for car in cars:
        ws.cell(row=row, column=1, value=car['id'])
        ws.cell(row=row, column=2, value=car['name'])
        ws.cell(row=row, column=3, value=car['price'])
        ws.cell(row=row, column=4, value=car['link'])
        ws.cell(row=row, column=5, value=car['type'])
        ws.cell(row=row, column=6, value=car['info'])
        row = row +1
    workbook.save(filename)
    workbook.close()



def read_existing_lots():
    filename = os.path.abspath('Trades.xlsx')
    workbook = excel.load_workbook(filename)
    id = []
    ws = workbook['LastDownload']
    for row in ws['A2:A'+str(ws.max_row)]:
        for cell in row:
            id.append(cell.value)
    return id

def new_cars(cars, ids):
    newcars =[]
    for car in cars:
        if str(car['id']) in ids:
            pass
        else:
            newcars.append(car)
    return newcars



if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    html_page_name = fetch_torgi_page()
    page_div_tags, page_li_tags = parse_page(html_page_name)
    pages_count = get_page_count(page_li_tags)
    print('Pages:'+str(pages_count))
    i = 1
    cars=[]
    while i <= pages_count:
        print('Page: '+str(i))
        cars.extend(get_cars_on_page(i))
        i = i+1
    ids = read_existing_lots()
    mycars = new_cars(cars, ids)
    put_new_to_excel(mycars)
    put_to_excel(cars)
    print('Finished!')