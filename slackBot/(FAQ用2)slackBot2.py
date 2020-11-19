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


WEB_HOOK_URL = "https://hooks.slack.com/services/"
WEB_HOOK_URL += "T017D1H6Y7L/B01DP911DA9/RI84U8jgiHl97fn2vjzHQwTm"

# f = sys.argv[1].encode('utf-8')
# get = urllib.parse.quote(f)

user = sys.argv[1]
ts = sys.argv[2]
get = sys.argv[3]
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("/var/www/html/chromedriver", chrome_options=chrome_options)

try:

    # google = "https://www.google.co.jp"
    # driver.get(google)
    # search_bar = driver.find_element_by_name("q")
    # search_bar.send_keys(get)
    # search_bar.submit()
    # themes = driver.find_elements_by_xpath("//div[@class=\'r\']/a/h3")
    # urls = driver.find_elements_by_xpath("//div[@class=\'r\']/a")

    google =  "https://www.google.com/search?q={}&safe=off".format(get)
    driver.get(google)
    themes = driver.find_elements_by_xpath("//*[@id=\"rso\"]/div/div/div[1]/a/h3")
    urls = driver.find_elements_by_xpath("//*[@id=\"rso\"]/div/div/div[1]/a")

    li = []

    num = 0

    for theme, url in zip(themes, urls):
        if num > 4:
            break
        th = theme.text
        ur = url.get_attribute('href')
        li.append([th, ur])
        num += 1
        word = '以下が参考資料です！\n'

    a = int(1)

    for response in li:
        word += str(a) + '<' + response[1] + '|' + response[0] + '> \n'
        a += 1

    requests.post(WEB_HOOK_URL, data=json.dumps({
        "thread_ts": ts,
        "blocks": [
            {
                "type": "section",
                "block_id": "section1",
                "text": {
                    "type": "mrkdwn",
                    "text": word
                }
            }
        ]
    }))
    driver.quit()

except Exception as e:
    print('type:' + str(type(e)))
    print('args:' + str(e.args))
    print('e:' + str(e))