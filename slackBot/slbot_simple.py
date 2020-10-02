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
import MySQLdb as MySQLdb
import jpholiday

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

        #日付・詳細な日付・時間・曜日を取得
        dt = datetime.date.today()
        dt_now = datetime.datetime.now()
        dt_hour = dt_now.hour
        #weekday()メソッドで、月曜日が0で日曜日が6の整数値が得られる。土日=5,6
        dt_weekday = dt_now.weekday()
        #休業日判定用(改良しないとバグってる)
        closes = [datetime.date(2020,9,25)]

        #質問かどうか判定
        if accsesslog == "質問":
            #休業日判定（バグってる）
            for close in closes:
                if dt == close:
                    requests.post(WEB_HOOK_URL, data=json.dumps({
                        "thread_ts" : event["ts"],
                        "text": "<@" + event["user"] + ">" + "\n本日スクールはお休みです。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"
                        }))
            #平日の場合
            if dt_weekday >= 0 and dt_weekday <= 4:
                #時間外の時
                if not dt_hour > 10 or not dt_hour < 22:
                    if event["text"].startswith(accsesslog):
                        requests.post(WEB_HOOK_URL, data=json.dumps({
                        "thread_ts" : event["ts"],
                        "text": "<@" + event["user"] + ">" + "\n（平日用）営業時間外です。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"
                        }))
                #時間内の時
                else:
                    if event["text"].startswith(accsesslog):
                        requests.post(WEB_HOOK_URL, data=json.dumps({
                        "thread_ts" : event["ts"],
                        "text": "<@" + event["user"] + ">"+ "\n（平日用）先生を探しています。\n【ZOOM URL:】"
                        }))
            else:#休祝日の場合(土日)
                #時間外の時
                if not dt_hour > 10 or not dt_hour < 19:
                    if event["text"].startswith(accsesslog):
                        requests.post(WEB_HOOK_URL, data=json.dumps({
                        "thread_ts" : event["ts"],
                        "text": "<@" + event["user"] + ">" + "\n（休祝日用）営業時間外です。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"
                        }))
                #時間内の時
                else:
                    if event["text"].startswith(accsesslog):
                        requests.post(WEB_HOOK_URL, data=json.dumps({
                        "thread_ts" : event["ts"],
                        "text": "<@" + event["user"] + ">"+ "\n（休祝日用）先生を探しています。\n【ZOOM URL:】"
                        }))
        #「質問」以外の場合
        else:        
            if event["text"].startswith(accsesslog):
                requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts" : event["ts"],
                "text": "<@" + event["user"] + ">" + str(testdb[0])
                }))


    return Response("nothing", mimetype='text/plane')



if __name__ == '__main__':
    app.debug = True
    app.run(host='153.127.9.96', port=8000, debug=True)

