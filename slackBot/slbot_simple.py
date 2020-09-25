#!/usr/bin/python3
# coding: UTF-8
#test
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
import MySQLdb as MySQLdb

# from operate import operate
# app.register_blueprint(operate)


WEB_HOOK_URL = "https://hooks.slack.com/services/"
WEB_HOOK_URL += "T017D1H6Y7L/B018CH391CG/CCBSFcq7IM0Ey0qWYKTIP8OR"

app = flask.Flask(__name__)

#DB接続用
def getConnection():
    return MySQLdb.connect(
        host="localhost",#dbサーバ
        db="maine-coon",#db名
        user="root",
        password="q2eiVk1V",
        charset="utf8",
        #cursorclass=MySQLdb.cursors.DictCursor
    )
#DBここまで


@app.route('/', methods=["POST"])
def index():

    data = request.get_data().decode('utf-8')

    # json 文字列を辞書型に変換
    data = json.loads(data)

    # challengeをslackにレスポンスの必要がある。
    if 'challenge' in data:

        token = str(data['challenge'])
        return Response(token, status=200, mimetype='text/plane')
        # return token, 200
        # time.sleep(10)
    
    if 'event' in data:
        event = data['event']
        username = event['user']
        accsesslog = event['text']
    #     print(event)

        #DB接続用
        connection = getConnection()
        #accesslogsにログを登録
        cursor = connection.cursor()
        sql = "INSERT INTO `access_logs`(`user_id`, `log`) VALUES (%s,%s)"
        cursor.execute(sql,(username,accsesslog,))
        connection.commit()
        #tech-informationから回答を取得
        sql = "SELECT `tech_info` FROM `tech_information` WHERE keyword REGEXP %s LIMIT 1"
        cursor = connection.cursor()
        cursor.execute(sql,(accsesslog,))
        tests = cursor.fetchall()

        cursor.close()
        connection.close()

        for testdb in tests:
            print(testdb)
    # #DBここまで

        if event["text"].startswith(accsesslog):
            requests.post(WEB_HOOK_URL, data=json.dumps({
            "thread_ts" : event["ts"],
            "text": "<@" + event["user"] + ">" + str(testdb[0])
            }))

    return Response("nothing", mimetype='text/plane')



if __name__ == '__main__':
    app.debug = True
    app.run(host='153.127.9.96', port=8000, debug=True)

