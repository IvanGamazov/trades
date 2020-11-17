from __future__ import print_function
import requests
import sys
import ssl
import urllib.request
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


AUTODOC = "https://catalogoriginal.autodoc.ru/api/catalogs/original/cars/"
MODS = "/modifications"


if __name__ == '__main__':
    vin = "WDC1668231A257600"
    url = AUTODOC+vin+MODS
    ssl._create_default_https_context = ssl._create_unverified_context
    with requests.get(url) as res:
        car = res.json()['commonAttributes']
        for elem in car:
            if elem['key']=="Brand":
                print(elem['value'])
            if elem['key']=="Name":
                print(elem['value'])
            if elem['key']=="Date":
                print(elem['value'])
            if elem['key']=="aggregates":
                print(elem['value'])
