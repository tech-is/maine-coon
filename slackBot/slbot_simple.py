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
import random

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

        #受け取ったメッセージ（accsesslog）を形態素分析（「質問」用）
        tokenizer = Tokenizer()
        sentences = []
        for token in tokenizer.tokenize(accsesslog):
            sentences.append(token.base_form)


        #DB接続用
        connection = getConnection()
        #accesslogsにログを登録
        cursor = connection.cursor()
        sql = "INSERT INTO `access_logs`(`user_id`, `log`) VALUES (%s,%s)"
        cursor.execute(sql,(username,accsesslog,))
        connection.commit()
        #study_timeにログを登録
        if "始め" in accsesslog or "はじめ" in accsesslog or "初め" in accsesslog:
            cursor = connection.cursor()
            sql = "INSERT INTO `study_time`(`user_name`, `keyword`,`start_time`) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE `keyword`=%s,`start_time`=%s"
            cursor.execute(sql,(username,accsesslog,dt_now,accsesslog,dt_now,))
            connection.commit()
        #study_timeにログを登録
        if "終わり" in accsesslog or "終り" in accsesslog or "おわり" in accsesslog:
            cursor = connection.cursor()
            sql = "UPDATE `study_time` SET `end_time`=%s,`keyword`=%s WHERE user_name=%s ORDER BY id DESC limit 1"
            cursor.execute(sql,(dt_now,accsesslog,username,))
            connection.commit()
        #study_timeから勉強時間を抽出（まだできていない！！！！！）
        # if "終わり" in accsesslog or "終り" in accsesslog or "おわり" in accsesslog:
        #     cursor = connection.cursor()
        #     sql = "SELECT `start_time`,`end_time`, timestampdiff(MINUTE,start_time,end_time) FROM `study_time` WHERE user_name=%s ORDER BY id DESC limit 1"
        #     cursor.execute(sql,(username,))
        #     st_times = cursor.fetchall()
        
        #tech-informationから回答を取得(ここでは形態素分析は行わない)
        sql = "SELECT `tech_info` FROM `tech_information` WHERE keyword REGEXP %s"
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

        # for testdb in tests:
        #     print(testdb)

        for holidaydb in holidays:
            print(holidaydb)


    # #DBここまで

        #返信するメッセージを格納
        botmessages=[]

        #質問かどうか判定
        try:
            if "質問" in sentences:        
                #平日の返し(am=時間内/pm=時間外)
                weekday_am = "\n（平日用）先生を探しています。\n5分以上経っても反応がない時は、もう一度「質問があります」って話しかけてね。"
                weekday_pm = "\n（平日用）営業時間外です。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"
                #土日の返し
                ssday_am = "\n（土日用）先生を探しています。\n5分以上経っても反応がない時は、もう一度「質問があります」って話しかけてね。"
                ssday_pm = "\n（土日用）営業時間外です。\n営業時間は以下の通りとなります。\n【平日】10時～22時\n【休祝日】10時～19時"
                #祝日の返し
                holiday_am = "\n（祝日用）先生を探しています。\n5分以上経っても反応がない時は、もう一度「質問があります」って話しかけてね。"
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
                    if True == jpholiday.is_holiday(datetime.date.today()):
                        #祝日の時間外の時
                        if not dt_hour > 9 or not dt_hour < 19:
                            botmessages.append(holiday_pm)
                        #祝日の時間内の時
                        else:
                            botmessages.append(holiday_am)
            
                    #平日の場合
                    elif dt_weekday >= 0 and dt_weekday <= 4:
                        #平日の時間外の時
                        if not dt_hour > 9 or not dt_hour < 22:
                            botmessages.append(weekday_pm)
                        #平日の時間内の時
                        else:
                            botmessages.append(weekday_am)
                    else:#土日の場合
                        #土日の時間外の時
                        if not dt_hour > 9 or not dt_hour < 19:
                            botmessages.append(ssday_pm)
                        #土日の時間内の時
                        else:
                            botmessages.append(ssday_am)

            #「質問」以外の場合
            elif sentences != []:
                #DBに単語が登録されているとき
                try:
                    if event["text"].startswith(accsesslog):
                        i=len(tests)
                        j=i-1
                        k=random.randint(0,j)
                        botmessages.append(str(tests[k]).replace("('",'').replace("',)",''))

                #DBに単語が登録されていないとき
                except NameError:
                    botmessages.append(":relaxed:")#おばけの絵文字
                except ValueError:#基本こちらで返される
                    botmessages.append(":thinking_face:")#考える絵文字

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
                "text": "<@" + event["user"] + ">" + str(botmessage)
                }))
        #途中でNameErrorを起こしたとき、止まらないようにする処理
        except NameError:
            requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts" : event["ts"],
                "text": "<@" + event["user"] + ">" + "内部エラーを起こしてるよ！（NameError）"
                }))
        #途中で何かエラーを起こしたとき、止まらないようにする処理
        finally:
            #sentences.clear()
            requests.post(WEB_HOOK_URL, data=json.dumps({

                }))


    return Response("nothing", mimetype='text/plane')



if __name__ == '__main__':
    app.debug = True
    app.run(host='153.127.9.96', port=8000, debug=True)

