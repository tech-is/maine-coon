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
#設定ファイルの読み込み(iniファイルはフルパスにしないと動かない)
import configparser
config = configparser.ConfigParser()
config.read('/var/www/html/slackbot_config.ini', encoding='utf-8')

WEB_HOOK_URL = config.get('WEBHOOK','URL2')

app = flask.Flask(__name__)
app.secret_key = 'hogehoge'

def is_int(s, ts, user):

    try:
        s = str(s)

        if len(s) != 1:
            raise ValueError

        s = str(int(s))
        return s

    except ValueError:
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
            host=config.get('DB','host'),
            db=config.get('DB','db'),
            user=config.get('DB','user'),
            password=config.get('DB','password'),
            charset=config.get('DB','charset')
                )
        cur = conn.cursor()
        
        if event['text'] == '森':
            requests.post(WEB_HOOK_URL, data=json.dumps({
                "thread_ts": event["ts"],
                "text": "<@" + event["user"] + ">さん\n" + "森さんって最高だよね！"
            }))
            return Response("nothing", mimetype='text/plane')
        if event['text'] == '4':
            requests.post(WEB_HOOK_URL, data=json.dumps({
            "thread_ts" : event["ts"],
            "text": "<@" + event["user"] + ">さん\n質問かな？\nわからない言葉をひと言送ってね！\n調べるね！！"
            }))
            quNumDB = '4'
            sqlUp = "UPDATE Qu SET quNum=%s WHERE ts=%s"
            cur.execute(sqlUp, (quNumDB, event["thread_ts"],) )
            conn.commit()
            cur.close()
            conn.close()
            return Response("nothing", mimetype='text/plane')

        try:
            sqlSe = "SELECT * FROM %s WHERE ts=%s"
            cur.execute(sqlSe, (Qu, event["thread_ts"],))
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
                requests.post(WEB_HOOK_URL, data=json.dumps({
                    "thread_ts" : ts,
                    "text": "<@" + user + ">さん\n半角数字を1つ送ってください。"
                }))
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

            sqlUp = "UPDATE Qu SET quNum=%s WHERE ts=%s"
            cur.execute(sqlUp,(quNumDB ,event["thread_ts"],))
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e:' + str(e))

        try:
            conn = MySQLdb.connect(
                host=config.get('DB','host'),
                db=config.get('DB','db'),
                user=config.get('DB','user'),
                password=config.get('DB','password'),
                charset=config.get('DB','charset')
                    )
            cur = conn.cursor()
            sqlSe = "SELECT * FROM An WHERE anNum='" + quNumDB + "'"
            cur.execute(sqlSe)
            row = cur.fetchone()
            a1DB = row[3]
            conn.commit()
            cur.close()
            conn.close()

            #print(a1DB)

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
            host=config.get('DB','host'),
            db=config.get('DB','db'),
            user=config.get('DB','user'),
            password=config.get('DB','password'),
            charset=config.get('DB','charset')
                )
        cur = conn.cursor()
        sqlIn = "INSERT INTO Qu (id, user, ts, quNum) VALUES (NULL, %s, %s,'000')"
        cur.execute(sqlIn,(event['user'], event['ts']))
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
    app.run(host=config.get('app_run','host'),port=config.get('app_run','port2'),debug=config.get('app_run','debug'))