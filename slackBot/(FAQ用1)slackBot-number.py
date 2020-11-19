#!/usr/bin/python3
# coding: UTF-8
import flask
from flask import request, Response, session
import json
import requests
import sys
import os
import traceback
import urllib
#import mysql.connector as MySQLdb
import MySQLdb
from janome.tokenizer import Tokenizer
import re

WEB_HOOK_URL = "https://hooks.slack.com/services/"
WEB_HOOK_URL += "T017D1H6Y7L/B01DP911DA9/RI84U8jgiHl97fn2vjzHQwTm"

# DM
# WEB_HOOK_URL = "https://hooks.slack.com/services/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"

app = flask.Flask(__name__)
app.secret_key = 'hogehoge'

def is_int(s, ts, user):

    try:
        s = str(s)

        if len(s) != 1:
            raise ValueError

        int(s)

        p = re.compile('[0-9]')

        if p.fullmatch(s) == None:
            trans_table = str.maketrans({"０": "0", "１": "1", "２": "2", "３": "3", "４": "4", "５": "5", "６": "6", "７": "7", "８": "8", "９": "9"})
            s = s.translate(trans_table)

        return s

    except ValueError:
        requests.post(WEB_HOOK_URL, data=json.dumps({
            "thread_ts" : ts,
            "text": "<@" + user + ">さん\n半角数字を1つ送ってください。"
            }))
        return 'False'

@app.route('/', methods=["POST"])

def index():

    data = request.get_data().decode('utf-8')
    data = json.loads(data)

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
        conn = MySQLdb.connect(
            host="localhost",#dbサーバ
            db="maine-coon",#db名
            user="root",
            password="q2eiVk1V",
            charset="utf8",
            #cursorclass=MySQLdb.cursors.DictCursor
                )
        cur = conn.cursor()

        if event['text'] == '4':
            requests.post(WEB_HOOK_URL, data=json.dumps({
            "thread_ts" : event["ts"],
            "text": "<@" + event["user"] + ">さん\n質問かな？\nわからない言葉をひと言送ってね！\n調べるね！！"
            }))
            quNumDB = '4'
            sqlUp = "UPDATE Qu SET quNum='" + quNumDB + "' WHERE ts='" + event["thread_ts"] + "'"
            cur.execute(sqlUp)
            conn.commit()
            cur.close()
            conn.close()
            return Response("nothing", mimetype='text/plane')

        try:
            sqlSe = "SELECT * FROM Qu WHERE ts='" + event["thread_ts"] + "'"
            cur.execute(sqlSe)
            row = cur.fetchone()
            print(row)
            userDB = row[1]
            tsDB = row[2]
            quNumDB = row[3]

            if quNumDB == '4':
                os.system('python3 /var/www/html/slackBot2.py '+ userDB +' '+ tsDB + ' "' +urllib.parse.quote(event["text"]) + '" &')
                requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts": tsDB,
                "text": "<@" + userDB + ">さん\n" + event["text"] + "だね\n今から調べるね！"
                }))
                cur.close()
                conn.close()
                return Response("nothing", mimetype='text/plane')

            event["text"] = is_int(event["text"], event["thread_ts"], event["user"])
            if event["text"] == 'False':
                return Response("nothing", mimetype='text/plane')

            if quNumDB != '000':
                # 4回目
                if '0' not in quNumDB:
                    requests.post(WEB_HOOK_URL, data=json.dumps({
                        "thread_ts" : event["ts"],
                        "text": "<@" + event["user"] + ">さん\nもう質問は、できないよ！"
                        }))
                    return Response("nothing", mimetype='text/plane')

                # 3回目
                elif '00' not in quNumDB:
                    quNumDB = quNumDB[1] + quNumDB[2] + event["text"]

                # 2回目
                else:
                    quNumDB = '0' + quNumDB[2] + event["text"]

            # 1回目
            else:
                quNumDB = '00' + event["text"]

            sqlUp = "UPDATE Qu SET quNum='" + quNumDB + "' WHERE ts='" + event["thread_ts"] + "'"
            cur.execute(sqlUp)
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e:' + str(e))

        try:
            conn = MySQLdb.connect(
                    user='root',
                    passwd='q2eiVk1V',
                    host='localhost',
                    db='maine-coon'
                    )
            cur = conn.cursor()
            sqlSe = "SELECT * FROM An WHERE anNum='" + quNumDB + "'"
            cur.execute(sqlSe)
            row = cur.fetchone()
            a1DB = row[2]
            conn.commit()
            cur.close()
            conn.close()

            requests.post(WEB_HOOK_URL, data=json.dumps({
            "thread_ts" : event["ts"],
            "text": "<@" + event["user"] + ">さん\n" + a1DB
            }))

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


    requests.post(WEB_HOOK_URL, data=json.dumps({
    "thread_ts" : event["ts"],
    "text": "<@" + event["user"] + ">さん,学習お疲れ様です！質問ですね\n質問を選択形式で送りますので、このスレッドに選択した番号をしてください\n1.質問のやり方\n2.営業時間について\n3.Tech-Isの学費について\n4.その他\n4を選択された場合は、キーワードを入力すると、google検索を実行します。"
    }))

    try:
        conn = MySQLdb.connect(
                user='root',
                passwd='q2eiVk1V',
                host='localhost',
                db='maine-coon'
                )
        cur = conn.cursor()
        sqlIn = "INSERT INTO Qu (id, user, ts, quNum) VALUES (NULL, '" + event['user'] + "' ,'" + event['ts'] + "','000')"
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
    app.run(host='153.127.9.96', port=5000, debug=True)