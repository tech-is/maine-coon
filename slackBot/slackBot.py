# test
#!/usr/bin/python3
# coding: UTF-8
import flask
from flask import request, Response, session
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
# import mysql.connector as MySQLdb
from janome.tokenizer import Tokenizer
import pya3rt

WEB_HOOK_URL = "URL"
WEB_HOOK_URL += "KEY"

app = flask.Flask(__name__)
app.secret_key = 'KEY'

@app.route('/', methods=["POST"])
def index():

    # decodeでバイト列を文字列に変換
    # data = request.data.decode('utf-8')
    data = request.get_data().decode('utf-8')

    # json 文字列を辞書型に変換
    data = json.loads(data)

    # challengeをslackにレスポンスの必要がある。
    if 'challenge' in data:
        token = str(data['challenge'])
        return Response(token, status=200, mimetype='text/plane')

    if 'event' not in data:
        return Response("nothing", mimetype="text/plane")

    event = data['event']
    print(event)

    # talk apiを使用
    apikey = "api key"
    client = pya3rt.TalkClient(apikey)
    reply_message = client.talk(event["text"])
    reply = reply_message['results'][0]['reply']

    requests.post(WEB_HOOK_URL, data=json.dumps({
        "thread_ts" : event["ts"],
        "text": "<@" + event["user"] + ">さん\n" + reply
        }))

    # print(point)
    # if point == 1:
    #     print('session')
    #     # print(urllib.parse.quote(event["text"]))
    #     os.system("python /var/www/html/get2.py " + urllib.parse.quote(event["text"]) + " &")
    #     session.pop('point', None)
    #     requests.post(WEB_HOOK_URL, data=json.dumps({
        # "thread_ts" : event["ts"],
    #     "text": "<@" + event["user"] + ">さん\n" + event["text"] + "だね\n今から調べるね！"
    #     }))
    #     return Response("nothing", mimetype="text/plane")


    #     # 接続する
    #     conn= MySQLdb.connect(
    #             user='USER',
    #             passwd='PASS',
    #             host='HOST',
    #             db='DB')

    #     # カーソルを取得する
    #     cur = conn.cursor()
    #     # SQL（データベースを操作するコマンド）を実行する
    #     # flask_sqlテーブルから、log列を取り出す
    #     #sql = "select log,user_id from log"
    #     sql2 = "SELECT * FROM log WHERE user_id LIKE '%A%'"
    #     cur.execute(sql2)
    #     # 実行結果を取得する
    #     rows = cur.fetchall()
    #     # 一行ずつ表示する
    #     for row in rows:
    #         print(row)
    #     #print(sql2)
    #     cur.close
    #     # 接続を閉じる
    #     conn.close

        # botなら
        # if 'bot_id' in event:
            # file = codecs.open('get.txt', 'a', 'utf-8')
            # file.write("[bot = " + event["text"] + "]\n")
            # file.close()

    # userなら
    if 'user' not in event:
        return Response("nothing", mimetype='text/plane')

    if "text" not in event:
        return Response("nothing", mimetype='text/plane')

    tokenizer = Tokenizer()

    sentence = event['text']
    japanese = []
    for token in tokenizer.tokenize(sentence):
        japanese.append(token.base_form)

    if "質問" not in japanese and "ある" not in japanese:
        return Response("nothing", mimetype='text/plane')

    # file = codecs.open('get.txt', 'a', 'utf-8')
    # file.write("[user = " + event["user"] + ":text = " + event["text"] + "]\n")
    # file.close()

    # 挨拶
    # if event["text"].startswith('こんにちは'):
    #     requests.post(WEB_HOOK_URL, data=json.dumps({
    #     "text": "<@" + event["user"] + ">さん\nこんにちは"
    #     }))

    # else:
    requests.post(WEB_HOOK_URL, data=json.dumps({
    "thread_ts" : event["ts"],
    "text": "<@" + event["user"] + ">さん\n質問かな？\nわからない言葉をひと言送ってね！\n調べるね！！"
    }))

    # ここで、スレッドの情報と、次回の入力内容を質問として認識できるように

        # ここで&を記述することで、非同期で、裏で動いてくれる記述をしている
        # print(urllib.parse.quote(event["text"]))

    # ここで、因数を追加してtsを送ったり
    os.system('python slackBOt2.py "'+ urllib.parse.quote(event["text"]) + '" &')

    return Response("nothing", mimetype='text/plane')

if __name__ == '__main__':
    app.debug = True
    app.run(host='HOST', port=PORT, debug=True)

