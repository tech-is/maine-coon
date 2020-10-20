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
import MySQLdb
import jpholiday
from janome.tokenizer import Tokenizer

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

    #日付・詳細な日付・時間・曜日を取得
    dt = datetime.date.today()
    dt_now = datetime.datetime.now()
    dt_hour = dt_now.hour
    #weekday()メソッドで、月曜日が0で日曜日が6の整数値が得られる。土日=5,6
    dt_weekday = dt_now.weekday()
    #休業日判定用
    strdt = dt.strftime('%Y-%m-%d')

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
        sql = "SELECT `keyword`,`tech_info` FROM `tech_information` WHERE keyword REGEXP %s LIMIT 1"
        cursor = connection.cursor()
        cursor.execute(sql,(accsesslog,))
        tests = cursor.fetchall()
        #holidaysから休日を取得
        sql = "SELECT `holiday`,`message` FROM `holidays` WHERE holiday LIKE %s"
        cursor = connection.cursor()
        cursor.execute(sql,(strdt,))
        holidays = cursor.fetchall()

        cursor.close()
        connection.close()

        for testdb in tests:
            print(testdb)

        for holidaydb in holidays:
            print(holidaydb)

    # #DBここまで


        #受け取ったメッセージを形態素分析
        tokenizer = Tokenizer()
        sentences = []

        for token in tokenizer.tokenize(accsesslog):
            sentences.append(token.base_form)


        #返信するメッセージを格納
        botmessages=[]

        #質問かどうか判定
        try:
            if "質問" in sentences:        
                #平日の返し(am=時間内/pm=時間外)
                weekday_am = "\n（平日用）先生を探しています。\n【ZOOM URL:】"
                weekday_pm = "\n（平日用）営業時間外です。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"
                #土日の返し
                ssday_am = "\n（土日用）先生を探しています。\n【ZOOM URL:】"
                ssday_pm = "\n（土日用）営業時間外です。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"
                #祝日の返し
                holiday_am = "\n（祝日用）先生を探しています。\n【ZOOM URL:】"
                holiday_pm = "\n（祝日用）営業時間外です。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"

                #休業日判定
                try:
                    if dt == holidaydb[0]:
                        requests.post(WEB_HOOK_URL, data=json.dumps({
                            "thread_ts" : event["ts"],
                            "text": "<@" + event["user"] + ">" + str(holidaydb[1])
                            }))
                except:
                    #祝日の場合
                    if dt == jpholiday.is_holiday(datetime.date.today()):
                        #祝日の時間外の時
                        if not dt_hour > 9 or not dt_hour < 19:
                            if event["text"].startswith(accsesslog):
                                botmessages.append(holiday_pm)
                        #祝日の時間内の時
                        else:
                            if event["text"].startswith(accsesslog):
                                botmessages.append(holiday_am)
            
                    #平日の場合
                    elif dt_weekday >= 0 and dt_weekday <= 4:
                        #平日の時間外の時
                        if not dt_hour > 9 or not dt_hour < 22:
                            if event["text"].startswith(accsesslog):
                                botmessages.append(weekday_pm)
                        #平日の時間内の時
                        else:
                            if event["text"].startswith(accsesslog):
                                botmessages.append(weekday_am)
                    else:#土日の場合
                        #土日の時間外の時
                        if not dt_hour > 9 or not dt_hour < 19:
                            if event["text"].startswith(accsesslog):
                                botmessages.append(ssday_pm)
                        #土日の時間内の時
                        else:
                            if event["text"].startswith(accsesslog):
                                botmessages.append(ssday_am)

            #「質問」以外の場合
            elif sentences != []:
                #DBに単語が登録されているとき
                try:
                    for sentence in sentences:
                        botmessages.append(str(testdb[1]))
                        print(sentence)
                #DBに単語が登録されていないとき
                except NameError:
                    botmessages.append("その言葉はむずかしいな。\n質問がある時は、「質問」って書き込んでね。")

            #返信するメッセージを取り出す
            for botmessage in botmessages:
                print(botmessage)

            if botmessages == []:
                requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts" : event["ts"],
                "text": "<@" + event["user"] + ">" + "値がからっぽだよ！" 
                }))

            else:
                requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts" : event["ts"],
                "text": "<@" + event["user"] + ">" + botmessage
                }))
        #途中でNameErrorを起こしたとき、止まらないようにする処理
        except NameError:
            requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts" : event["ts"],
                "text": "<@" + event["user"] + ">" + "内部エラーを起こしてるよ！（NameError）"
                }))
        #途中で何かエラーを起こしたとき、止まらないようにする処理
        finally:
            requests.post(WEB_HOOK_URL, data=json.dumps({

                }))


    return Response("nothing", mimetype='text/plane')



if __name__ == '__main__':
    app.debug = True
    app.run(host='153.127.9.96', port=8000, debug=True)

