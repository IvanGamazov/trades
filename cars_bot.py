from __future__ import print_function
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
import time
import re
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import telebot
#3from telebot import apihelper


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

TRADES_SPREADSHEET_ID = '1kFqoISnADprv9H71nzTq7vrjF-D5T-7W395C_kCyHOg'

TRADES_SPREADSHEET_ID_OLD = '1bevgPBYdh6-hHqFGKQ6o7cBLsFaY15yHL9PLQPtd3ks'



#CARS_URL = 'https://xn----etbpba5admdlad.xn--p1ai/search?categorie_childs%5B0%5D=2&regions%5B0%5D=50&regions%5B1%5D=77&trades-section=bankrupt&page='

#CARS_EN_URL = 'https://xn----etbpba5admdlad.xn--p1ai/search?categorie_childs%5B0%5D=2&regions%5B0%5D=50&regions%5B1%5D=77&trades-section=bankrupt&page=1'

CARS_URL = 'https://xn----etbpba5admdlad.xn--p1ai/search?categorie_childs%5B0%5D=2&regions%5B0%5D=33&regions%5B1%5D=40&regions%5B2%5D=44&regions%5B3%5D=50&regions%5B4%5D=62&regions%5B5%5D=69&regions%5B6%5D=71&regions%5B7%5D=76&regions%5B8%5D=77&regions%5B9%5D=47&regions%5B10%5D=78&trades-section=bankrupt&page='

CARS_EN_URL = 'https://xn----etbpba5admdlad.xn--p1ai/search?categorie_childs%5B0%5D=2&regions%5B0%5D=33&regions%5B1%5D=40&regions%5B2%5D=44&regions%5B3%5D=50&regions%5B4%5D=62&regions%5B5%5D=69&regions%5B6%5D=71&regions%5B7%5D=76&regions%5B8%5D=77&regions%5B9%5D=47&regions%5B10%5D=78&trades-section=bankrupt&page=1'

AUTODOC = "https://catalogoriginal.autodoc.ru/api/catalogs/original/cars/"

MODS = "/modifications?clientId=375"

vinregex = '[0-9abcdefghjklmnprstuvwxyzABCDEFGHJKLMNPRSTUVWXYZ]{17,20}'


 #-*- coding: utf-8 -*-

#apihelper.proxy = {'https': 'socks5://alexstav_bot:hxhqhyiq@167.71.53.214:1080'}
bot = telebot.TeleBot("1125563549:AAFVJyN1Em2itQr26fGLCAxXGcizvrxcHlk")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

def google_auth():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service

def get_sheet(service, sheet, srange):
    # Call the Sheets API

    resrange = sheet+'!'+srange

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TRADES_SPREADSHEET_ID,
                                range=resrange).execute()
    values = result.get('values', [])
    return values
 #   if not values:
 #       print('No data found.')
 #   else:
 #       print('Name, Major:')
 #       for row in values:
 #           # Print columns A and E, which correspond to indices 0 and 4.
 #           print('%s, %s' % (row[1], row[2]))   774034668,

def clear(sheet, service):
    body = {
    'range' : sheet+'!'+'A2:N',
    }
    result = service.spreadsheets().values().clear(spreadsheetId=TRADES_SPREADSHEET_ID, range=sheet+'!'+'A2:N', body=body)
    result.execute()

def deleteSheets(service):
    request = service.spreadsheets().get(spreadsheetId=TRADES_SPREADSHEET_ID)
    response = request.execute()
    sheetList = response.get('sheets')
    while len(sheetList) >10:
            lastSheetId = sheetList[len(sheetList)-1]['properties']['sheetId']
            deleteSheet(service, lastSheetId)
            sheetList.pop()


def deleteSheet(service, sheetId):
    body = {
            "requests": [
                            {
                                "deleteSheet": {
                                    "sheetId": sheetId
                                            }
                         }
                        ]
        }
    response = service.spreadsheets().batchUpdate(spreadsheetId=TRADES_SPREADSHEET_ID, body=body).execute()
    print(response)



def copy_sheet(service):
    request = service.spreadsheets().get(spreadsheetId=TRADES_SPREADSHEET_ID, ranges='LastDownload!A:N', includeGridData=False)
    response = request.execute()
    sheetId = response['sheets'][0]['properties']['sheetId']
    body = {
        'destinationSpreadsheetId' : TRADES_SPREADSHEET_ID
    }
    request = service.spreadsheets().sheets().copyTo(spreadsheetId=TRADES_SPREADSHEET_ID, sheetId=sheetId, body=body)
    response = request.execute()


def write_sheet(service, sheet, srange, data):
    resrange = sheet+'!'+srange
    values = []
    for car in data:
        value = []
        value.append(car['id'])
        value.append(car['name'])
        value.append(car['act_price'])
        value.append(car['start_price'])
        value.append(car['start'])
        value.append(car['end'])
        value.append(car['link'])
        value.append(car['type'])
        value.append(car['vins'])
        value.append(car['info'])
        value.append(car['brand'])
        value.append(car['model'])
        value.append(car['carprod'])
        value.append(car['cardesc'])
        values.append(value)
    body = {
    'values': values,
    'range' : resrange,
    'majorDimension':'ROWS'
    }
    result = service.spreadsheets().values().update(spreadsheetId=TRADES_SPREADSHEET_ID, range=resrange, valueInputOption='RAW', body=body)
    result.execute()
    resrange1 = sheet + '!N1:P1'
    #resrange1 = resrange1 + 'N1'
    body = {
        'values': [[str(datetime.now())]],
        'range' : resrange1,
        'majorDimension':'ROWS'
    }
    result1 = service.spreadsheets().values().update(spreadsheetId=TRADES_SPREADSHEET_ID, range=resrange1, valueInputOption='USER_ENTERED', body=body)
    result1.execute()

def fetch_torgi_page():
    page = NamedTemporaryFile()
    urlretrieve(CARS_EN_URL, page.name)
    return page

def fetch_one_page(pgnum):
    page = NamedTemporaryFile()
    urlretrieve(CARS_URL+str(pgnum), page.name)
    return page

def fetch_url(addr):
    page = NamedTemporaryFile()
    urlretrieve(addr, page.name)
    return page


def get_car_info_from_div(div):
    block_divs = div.find_all('div')
    car_id = get_car_id(block_divs)
    car_name = get_car_name(block_divs)
    car_info = get_car_info(block_divs)
    car_link = get_car_link(block_divs)
    car = fetch_url(car_link)
    car_divs, car_p = parse_car_page(car)
    car_act_price, car_start_price = get_car_price(car_divs)
    #car_start_price = 0
    #car_act_price = get_car_price(car_divs)
    auction_type = get_car_auction_type(block_divs)
    d_start = get_date_start(car_p)
    d_end = get_date_end(car_p)
    vins = get_vin(car_info, car_name)
    cardesc = get_car_by_vin(vins)
    #d_start =
    #d_end = 
    #trade_place = 
    return {'id': car_id, 'name': car_name, 'act_price': car_act_price, 'start_price': car_start_price, 'start': d_start, 'end':d_end, 'link': car_link, 'type': auction_type, 'vins':vins, 'info': car_info, 'brand':cardesc[0], 'model':cardesc[1], 'carprod': cardesc[2], 'cardesc':cardesc[3]}

def get_vin(car_info, car_name):
    text3 = str(car_info)+' '+str(car_name)
    vins = []
    replacer = ['А', 'A', 'В', 'B', 'Е', 'E', 'К', 'K', 'М', 'M','Н', 'H','О', 'O','Р', 'P','С', 'C','Т', 'T', 'У', 'Y', 'Х', 'X']
    ru = []
    en = []
    text3.upper()
    i = 0
    while i < len(replacer)-1:
        ru.append(replacer[i])
        en.append(replacer[i+1])
        i = i+2
    i = 0
    while i < len(text3):
        if text3[i] in ru:
            text3 = text3[0:i]+str(en[ru.index(text3[i])])+text3[i+1:]
        i=i+1
    res = re.findall(vinregex, text3)
    for vin in res:
        if vin not in vins:
            vins.append(vin)
    return str(vins)

def get_cars_from_torgi(divs):
    car_divs = list(filter(lambda div: 'class' in div.attrs and
                                         'lot-card' in div.get('class'), divs))
    cars = list(map(lambda div: get_car_info_from_div(div), car_divs))
    #print(cars)
    return cars

def get_date_start(p_tags):
            if p_tags[4].text[0:6] == 'Начало':
                return p_tags[4].text[21:31]
            if p_tags[5].text[0:6] == 'Начало':
                return p_tags[5].text[21:31]

def get_date_end(p_tags):
            if p_tags[5].text[0:5] == 'Конец':
                return p_tags[5].text[20:30]
            if p_tags[6].text[0:5] == 'Конец':
                return p_tags[6].text[20:30]



def get_car_id(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'lot-caption' in car_div.get('class'):
            #print(car_div.b.string)
            return car_div.b.string

def get_car_link(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'lot-description' in car_div.get('class'):
            #print(car_div.a.get('href'))
            return car_div.a.get('href')

def get_car_name(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'lot-description' in car_div.get('class'):
            #print(car_div.h3.string)
            return car_div.h3.string

def get_car_info(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'lot-description' in car_div.get('class'):
                try:        
                    return car_div.p.string
                except AttributeError:
                    return ""
                     

def get_car_price(div_tags):
    prices = []
    for price_div in div_tags:
        if 'class' in price_div.attrs and \
                        'lot-cost__inner' in price_div.get('class'):
            #print(price_div.span.string + "  " + price_div.p.string)
            prices.append(price_div.span.string + "  " + price_div.p.string)
            #print(price_div.p.string)
            #prices = list.append(price_div)
            #if len(prices)>3:
            #    price_list[0] = prices[1].text
            #    price_list[1] = prices[3].text
            #else:
            #    price_list[0] = prices[1].text
            #    price_list[1] = prices[1].text
    #print(prices)
    if len(prices)<2:
        prices.append(prices[0])
    return prices[0], prices[1]

def get_car_by_vin(vin):
    vin1 = []
    print(vin)
    if len(vin)>17:
        vin1 = vin[2:19]
    else:
        vin1 = vin
    url = AUTODOC+vin1+MODS
    ssl._create_default_https_context = ssl._create_unverified_context
    carbrand = ""
    carname = ""
    carproddate = ""
    caragg = ""
    print(vin1)
    if len(vin1)>3:
        with requests.get(url) as res:
            print(res.status_code)
            if res.status_code == 200:
                car = res.json()['commonAttributes']
                for elem in car:
                    if elem['key']=="Brand":
                        carbrand = elem['value']
                    if elem['key']=="Name":
                        carname = elem['value']
                    if elem['key']=="Date":
                        carproddate = elem['value']
                    if elem['key']=="aggregates":
                        caragg = elem['value']
    return carbrand, carname, carproddate, caragg

def get_car_auction_type(div_tags):
    for car_div in div_tags:
        if 'class' in car_div.attrs and \
                        'new-component1' in car_div.get('class'):
            try:
                return str(car_div.a.svg.get('class'))
            except AttributeError:
                return ""

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

def parse_car_page(raw_html_file):
    soup = BeautifulSoup(raw_html_file.read(), 'html.parser')
    div_tags = soup.find_all('div')
    p_tags = soup.find_all('p')
    return div_tags, p_tags


#def get_page_count(divs):
#    pages_list = list(filter(lambda li: 'class' in li.attrs and 'page-item' in li.get('class'), divs))
   # pagination = list(filter(lambda div: 'class' in div.attrs and 'pagination' in div.get('class'), divs))
   # pages_count = len(pagination.ul.find_all('li'))
   # return pages_count
    #return len(pages_list)-2


def get_page_count(divs):
    pages_list = list(filter(lambda li: 'class' in li.attrs and 'page-item' in li.get('class'), divs))
    litags = []
    for litag in pages_list:
        litags.append(litag.string)
   # pagination = list(filter(lambda div: 'class' in div.attrs and 'pagination' in div.get('class'), divs))
   # pages_count = len(pagination.ul.find_all('li'))
   # return pages_count
    return int(litags[len(litags)-2])

def get_cars_on_page(page):
    page_name = fetch_one_page(page)
    page_div_tags, page_li_tags = parse_page(page_name)
    cars_on_page = get_cars_from_torgi(page_div_tags)
    return cars_on_page

def read_existing_lots(service):
    rows = get_sheet(service, 'LastDownload', 'A2:A')
    id = []
    for row in rows:
        i = 0
        while i < len(row):
            id.append(row[i])
            i = i+1
    return id

def read_existing_cars(service):
    rows = get_sheet(service, 'LastDownload', 'A2:N')
    return rows

def read_new_cars(service):
    rows = get_sheet(service, 'New', 'A2:N')
    return rows



def new_cars(cars, ids):
    newcars =[]
    for car in cars:
        if str(car['id']) in ids:
            pass
        else:
            newcars.append(car)
    return newcars

@bot.message_handler(commands=['collect'])
def collect_cars(message):
    bot.send_message(message.chat.id, "Все объявления:")
    serv = google_auth()
    deleteSheets(serv)
    copy_sheet(serv)
    ssl._create_default_https_context = ssl._create_unverified_context
    html_page_name = fetch_torgi_page()
    page_div_tags, page_li_tags = parse_page(html_page_name)
    pages_count = get_page_count(page_li_tags)
    bot.send_message(message.chat.id,'Страниц: '+str(pages_count))
    i = 1
    cars=[]
    while i <= pages_count:
        bot.send_message(message.chat.id, 'Обрабатываю страницу : '+str(i))
        cars.extend(get_cars_on_page(i))
        i = i+1
    ids = read_existing_lots(serv)
    mycars = new_cars(cars, ids)
    clear('New', serv)
    write_sheet(serv, 'New', 'A2:N'+str(len(mycars)+1), mycars)
    clear('LastDownload',serv)
    write_sheet(serv, 'LastDownload', 'A2:N'+str(len(cars)+1), cars)
    bot.send_message(message.chat.id,'Всего объявлений: '+str(len(cars)))
    bot.send_message(message.chat.id,'Новых объявлений: '+str(len(mycars)))

@bot.message_handler(commands=['allcars'])
def all_cars(message):
    serv = google_auth()
    ssl._create_default_https_context = ssl._create_unverified_context
    cars = read_existing_cars(serv)
    bot.send_message(message.chat.id, 'Всего объявлений: '+str(len(cars)))
    bot.send_message(message.chat.id, 'https://docs.google.com/spreadsheets/d/1kFqoISnADprv9H71nzTq7vrjF-D5T-7W395C_kCyHOg/edit#gid=2059968966')


@bot.message_handler(commands=['newcars'])
def newcars(message):
    serv = google_auth()
    ssl._create_default_https_context = ssl._create_unverified_context
    cars = read_new_cars(serv)
    bot.send_message(message.chat.id, 'Всего объявлений: '+str(len(cars)))
    for car in cars:
        if len(car)>11:
            try:
                bot.send_message(message.chat.id, 'Объявление: ' + car[0] + '\nНазвание: ' + car[1] + '\nЦена: ' + car[2] + '\nМодель: ' + car[11] + '\nВыпущена: ' + car[12] + '\nСсылка: ' + car[6])
            except:
                bot.send_message(message.chat.id, 'Объявление: ' + car[0] + '\nНазвание: ' + car[1] + '\nЦена: ' + car[2] + '\nМодель: ' + car[11] + '\nСсылка: ' + car[6])
        else:
            bot.send_message(message.chat.id, 'Объявление: ' + car[0] + '\nНазвание: ' + car[1] + '\nЦена: ' + car[2] + '\nСсылка: ' + car[6])
        time.sleep(3.1)
    bot.send_message(message.chat.id,'Это все объявления на данный момент')

@bot.message_handler(commands=['status'])
def status(message):
    serv = google_auth()
    ssl._create_default_https_context = ssl._create_unverified_context
    lastupd = get_sheet(serv, 'LastDownload', 'N1')
    bot.send_message(message.chat.id, 'Последнее обновление: '+str(lastupd[0][0]))




bot.polling()

####
#Если вы хотите дописать или залить новую версию бота, то введите команду:

#sudo systemctl stop bot

#Провидите все необходимые манипуляции. А потом введите следующие команды, чтобы он опять заработал:

#sudo systemctl daemon-reload
#sudo systemctl start bot
#sudo systemctl status bot
###