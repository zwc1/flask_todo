from flask import request, jsonify
# 导入实体类
from entity.entity import *
import requests
import json
import time
import sys
import uuid
import hashlib
from imp import reload


# 有道翻译api的配置
reload(sys)
YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '740ab7019bb0a60e'
APP_SECRET = 'y4C89HIWVDt7H4M09Nv4yF0945FNmEUW'

'''
有道翻译api
'''


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


@app.route('/translate', methods=['GET', 'POST'])
def translate():
    q = name = request.values.get('content')
    data = {}
    data['from'] = 'auto'
    data['to'] = 'auto'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    # data['vocabId'] = "您的用户词表ID"

    response = do_request(data)
    # contentType = response.headers['Content-Type']
    # if contentType == "audio/mp3":
    #     millis = int(round(time.time() * 1000))
    #     filePath = str(millis) + ".mp3"
    #     fo = open(filePath, 'wb')
    #     fo.write(response.content)
    #     fo.close()
    # else:
    #     print(response.content)

    return response.content


'''
添加单词
'''


@app.route('/addword', methods=['GET', 'POST'])
def addword():
    name = request.values.get('username')
    content = request.values.get('content')
    translate = request.values.get('translate')
    # print(translate)
    # 实例化一个实体，插入表中
    word = Word(name, content, translate)
    db.session.add(word)

    try:
        db.session.commit()
        return 'success'

    except Exception as e:
        print(e)
        return 'fail'


'''
返回该用户单词
'''


@app.route('/returnword', methods=['GET', 'POST'])
def return_word():
    name = request.values.get('username')
    word = Word.query.filter(Word.username == name).all()

    payload = []

    if word!=None:

        for re in word:
            translate = re.translate
            content = {'content': re.content, 'translate': json.loads(translate),
                       'active': '0', 'ready': '1'}
            # print(content)
            payload.append(content)

        return jsonify(payload)
    else:
        return 'null'


'''
更新某用户单词
'''


@app.route('/deleteword', methods=['GET', 'POST'])
def delete_word():
    name = request.values.get('username')
    content = request.values.get('content')

    # print(name, id)
    # 先获取再修改提交
    word = Word.query.filter(Word.username == name, Word.content == content).first()

    # print(bianjain)
    if word!=None:

        db.session.delete(word)
        db.session.commit()

        return 'success'
    else:
        return 'fail'

