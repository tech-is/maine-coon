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
import mysql.connector as MySQLdb
from janome.tokenizer import Tokenizer

WEB_HOOK_URL = "https://hooks.slack.com/services/"
WEB_HOOK_URL += "API"

app = flask.Flask(__name__)
app.secret_key = 'KEY'

@app.route('/', methods=["POST"])
def index():

    # decodeでバイト列を文字列に変換
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

    if 'user' not in event:
        return Response("nothing", mimetype='text/plane')

    if 'text' not in event:
        return Response("nothing", mimetype='text/plane')

    if 'thread_ts' in event:
        try:
            conn = MySQLdb.connect(
                    user='USER',
                    passwd='PASS',
                    host='HOST',
                    db='DB')
            cur = conn.cursor()
            sqlSe = "SELECT * FROM Question WHERE ts='" + event['thread_ts'] + "'"
            cur.execute(sqlSe)
            row = cur.fetchone()

            userDB = row[1]
            tsDB = row[2]
            nextDB = row[3]
            doneDB = row[4]

            if nextDB == 0 and doneDB == 0:
                os.system('python /var/www/html/slackBot2.py '+ userDB +' '+ tsDB + ' "' +urllib.parse.quote(event["text"]) + '" &')
                requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts": tsDB,
                "text": "<@" + userDB + ">さん\n" + event["text"] + "だね\n今から調べるね！"
                }))

                try:
                    sqlUp = "UPDATE Question SET next=1, done=1 WHERE ts='" + tsDB + "'"
                    cur.execute(sqlUp)

                except Exception as e:
                    print('type:' + str(type(e)))
                    print('args:' + str(e.args))
                    print('e:' + str(e))

            conn.commit()
            cur.close()
            conn.close()
            return Response("nothing", mimetype='text/plane')

        except Exception as e:
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e:' + str(e))
            return Response("nothing", mimetype='text/plane')

    tokenizer = Tokenizer()

    sentence = event['text']
    japanese = []
    for token in tokenizer.tokenize(sentence):
        japanese.append(token.base_form)

    if "質問" not in japanese and "ある" not in japanese:
        return Response("nothing", mimetype='text/plane')

    else:
        requests.post(WEB_HOOK_URL, data=json.dumps({
        "thread_ts" : event["ts"],
        "text": "<@" + event["user"] + ">さん\n質問かな？\nわからない言葉をひと言送ってね！\n調べるね！！"
        }))

        try:
            conn = MySQLdb.connect(
                    user='USER',
                    passwd='PASS',
                    host='HOST',
                    db='DB')
            cur = conn.cursor()
            sqlIn = "INSERT INTO Question (id, name, ts, next, done) VALUES (NULL, '" + event['user'] + "' ,'" + event['ts'] + "' ,0 ,0)"
            cur.execute(sqlIn)
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e:' + str(e))

    return Response("nothing", mimetype='text/plane')

if __name__ == '__main__':
    app.debug = True
    app.run(host='HOST', port=0, debug=True)
