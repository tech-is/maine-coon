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
#設定ファイルの読み込み(iniファイルはフルパスにしないと動かない)
import configparser
config = configparser.ConfigParser()
config.read('/var/www/html/slackbot_config.ini', encoding='utf-8')

WEB_HOOK_URL = config.get('WEBHOOK','URL1')

app = flask.Flask(__name__)

#DB接続用
def getConnection():
    return MySQLdb.connect(
        host=config.get('DB','host'),
        db=config.get('DB','db'),
        user=config.get('DB','user'),
        password=config.get('DB','password'),
        charset=config.get('DB','charset')
    )
#DBここまで

# 質問用
def getQuestion(word):
            connection = getConnection()
            sql = "SELECT `tech_info` FROM `tech_information` WHERE keyword REGEXP %s"
            cursor = connection.cursor()
            cursor.execute(sql,(word,))
            print(word)
            schooltimes = cursor.fetchall()
            cursor.close()
            connection.close()
            a = []
            for schooltime in schooltimes:
                a.append(str(schooltime[0]))
            return a

#質問以外
def getDB(word):
    connection = getConnection()
    #tech-informationから回答を取得
    sql = "SELECT `tech_info` FROM `tech_information` WHERE keyword REGEXP %s"
    cursor = connection.cursor()
    cursor.execute(sql,(word,))
    ohenji = cursor.fetchall()
    cursor.close()
    connection.close()
    i=len(ohenji)
    j=i-1
    k=random.randint(0,j)
    a=[]
    a.append(str(ohenji[k]).replace("('",'').replace("',)",''))
    return a


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

    if 'event' not in data:
        return Response("nothing", mimetype="text/plane")
    
    event = data['event']

    if 'user' not in event:
        return Response("nothing", mimetype='text/plane')
    
    username = event['user']

    if 'text' not in event:
        return Response("nothing", mimetype='text/plane')

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
        if "質問" in sentences or "もん" in sentences:        
            #休業日判定
            try:
                if dt == holidaydb[0]:
                    botmessages.append(str(holidaydb[1]))
            except:
                #祝日の場合
                if True == jpholiday.is_holiday(datetime.date.today()):
                    #祝日の時間外の時
                    if not dt_hour > 9 or not dt_hour < 19:
                        botmessages = getQuestion("営業時間・祝日・時間外")
                    #祝日の時間内の時
                    else:
                        botmessages = getQuestion("営業時間・祝日・時間内")
        
                #平日の場合
                elif dt_weekday >= 0 and dt_weekday <= 4:
                    #平日の時間外の時
                    if not dt_hour > 9 or not dt_hour < 22:
                        botmessages = getQuestion("営業時間・平日・時間外")
                    #平日の時間内の時
                    else:
                        botmessages = getQuestion("営業時間・平日・時間内")
                else:#土日の場合
                    #土日の時間外の時
                    if not dt_hour > 9 or not dt_hour < 19:
                        botmessages = getQuestion("営業時間・土日・時間外")
                    #土日の時間内の時
                    else:
                        botmessages = getQuestion("営業時間・土日・時間内")

        #「質問」以外の場合
        elif sentences != []:
            #DBに単語が登録されているとき
            try:
                if "おわる" in sentences or "終わる" in sentences or "終る" in sentences or "終" in sentences or "終了" in sentences:
                    botmessages = getDB("おわる")

                elif "中断" in sentences or "ゅうだんします" in sentences or "ゅうだん" in sentences or "休憩" in sentences or "きゅう" in sentences or "抜ける" in sentences or "ぬける" in sentences:
                    botmessages = getDB("中断")

                elif "再開" in sentences or "さい" in sentences or "もどる" in sentences or "戻る" in sentences:
                    botmessages = getDB("再開")

                elif "はじめ" in sentences or "初め" in sentences or "始める" in sentences or "開始" in sentences:
                    botmessages = getDB("はじめ")

                elif event["text"].startswith(accsesslog):
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
    #app.run(host='153.127.9.96', port=8000, debug=True)
    app.run(host=config.get('app_run','host'),port=config.get('app_run','port'),debug=config.get('app_run','debug'))

