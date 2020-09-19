#!/usr/bin/python3
# coding: UTF-8
import flask
from flask import request, Response
import json
import requests
import codecs
import time
import sys
import os
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import traceback
import urllib
# import unicode
# import mysql.connector as MySQLdb


WEB_HOOK_URL = "URL"
WEB_HOOK_URL += "KEY"

# f = sys.argv[1].encode('utf-8')
# get = urllib.parse.quote(f)

get = sys.argv[1]
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("chromedriver", chrome_options=chrome_options)

try:

    # これを用いれば、複数の単語を検索可能に
    # google = "https://www.google.co.jp"
    # driver.get(google)
    # search_bar = driver.find_element_by_name("q")
    # search_bar.send_keys(get)
    # search_bar.submit()
    # themes = driver.find_elements_by_xpath("//div[@class=\'r\']/a/h3")
    # urls = driver.find_elements_by_xpath("//div[@class=\'r\']/a")

    google =  "https://www.google.com/search?q={}&safe=off".format(get)
    driver.get(google)
    themes = driver.find_elements_by_xpath("//div[@class=\'r\']/a/h3")
    urls = driver.find_elements_by_xpath("//div[@class=\'r\']/a")

    # listを制作するため
    li = []

    #５件のみ取得
    num = 0

    for theme, url in zip(themes, urls):
        if num > 4:
            break
        th = theme.text
        ur = url.get_attribute('href')
        li.append([th, ur])
        num += 1
        word = '以下が参考資料です！\n'
        for response in li:
            word += response[0] + '\n' + response[1] + '\n'
    requests.post(WEB_HOOK_URL, data=json.dumps({
        "text" : "<@" + get + ">\n" + word
    }))
    driver.quit()
except:
    requests.post(WEB_HOOK_URL, data=json.dumps({
        "text" : "エラーしました"
    }))
traceback.print_exc()