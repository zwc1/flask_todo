from flask import Flask, render_template, request, jsonify, send_file
from flask_apscheduler import APScheduler
# 导入实体类
from entity.entity import *
import requests
import json
import time
from flask import current_app
import sys
import uuid
import hashlib
from imp import reload
import os
# 全局变量用于存token及上一次获取的时间,有效期(s)
global token
expires_in=0
old_time=0

# 有道翻译api的配置
reload(sys)
YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '740ab7019bb0a60e'
APP_SECRET = 'y4C89HIWVDt7H4M09Nv4yF0945FNmEUW'

# 调度器及其配置要写在这，不要在__main__里
class Config(object):
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()
app.config.from_object(Config())
scheduler.init_app(app)
scheduler.start()

'''
首页
'''
@app.route('/')
def index():
    return 'hello world'
    # return render_template("index.html")

'''
插入用户信息（注册）
'''
@app.route('/adduser', methods=['GET','POST'])
def add_user():


    name = request.values.get('username')
    phonenum = request.values.get('phonenum')
    password = request.values.get('password')
    nickname = request.values.get('nickname')
    userurl = request.values.get('url')
    code = request.values.get('code')
    # print(code, name)
    # 调用api获取openid
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=wx869f84b17b6897e0&secret=4f85f84bb001b83e6bb3c3e95597307e' \
          '&js_code='+code+'&grant_type=authorization_code'

    response = requests.get(url)
    # 将获取到的json字符串转为字典
    dict_json = json.loads(response.content)

    openid = dict_json['openid']


    # # 实例化一个实体，插入表中
    user = Users(name, phonenum, password, nickname, userurl, openid)
    db.session.add(user)

    try :
        db.session.commit()
        return 'success'
    except:

        return 'fail'
'''
验证用户名是否重名（注册）或密码是否正确（登录）
'''
@app.route('/check', methods=['GET','POST'])
def check_user():

    name = request.values.get('username')

    # 用来标识是否需要验证密码(1/0)
    have_password = request.values.get('have_password')


    # print(have_password)
    # print(name)
    # 只验证用户名是否重名
    if have_password == '0':
        count = Users.query.filter(Users.username==name).count()
        if count == 0:
            return 'success'
        else:
            return 'fail'
    # 验证密码是否正确
    else:
        password = request.values.get('password')
        user = Users.query.filter(Users.username==name).first()

        if user.password==password:
            return 'success'
        else:
            return 'fail'

'''
找回密码
'''
@app.route('/findpassword', methods=['GET', 'POST'])
def find_password():

    name = request.values.get('username')
    phonenum = request.values.get('phonenum')

    user = Users.query.filter(Users.username == name, Users.phonenum == phonenum).first()

    if user:
        return user.password
    else:
        return 'null'


'''
添加备忘录
'''
@app.route('/addbeiwanglu', methods=['GET', 'POST'])
def add_beiwanglu():

    name = request.values.get('username')
    id = request.values.get('id')
    tip = request.values.get('tip')
    date = request.values.get('date')
    time = request.values.get('time')
    content = request.values.get('content')
    complete = request.values.get('complete')


    # 实例化一个实体，插入表中
    beiwang = Beiwanglu(id, name, bool(int(tip)), date, time, content, bool(int(complete)))
    db.session.add(beiwang)

    tip_time = date+' '+time+':00'
    print(tip_time)
    if(len(content)>25):
        tip_content = content[0:25]+'...'
    else:
        tip_content = content

    try:
        db.session.commit()
        # 如果需要提醒
        if (bool(int(tip)) == True):
            # 先获取openid
            user = Users.query.filter(Users.username == name).first()
            openid = user.openid
            # 添加一个定时器
            add_tip(openid, content, tip_time, id)

        return 'success'
    except:

        return 'fail'

'''
返回该用户备忘录
'''
@app.route('/returnbeiwanglu', methods=['GET', 'POST'])
def return_beiwang():

    name = request.values.get('username')
    beiwanglu = Beiwanglu.query.filter(Beiwanglu.username == name).all()

    payload = []

    if beiwanglu:

        for re in beiwanglu:
            content = {'username': re.username, 'tip': re.tip, 'date': re.date,
                       'time': str(re.time), 'content': re.content,
                       'complete': re.complete, 'id': re.id}
            payload.append(content)

        return jsonify(payload)
    else:
        return 'null'

'''
更新某用户备忘录
'''
@app.route('/updatebeiwanglu', methods=['GET', 'POST'])
def update_beiwang():


    update = request.values.get('update')   # 要执行的操作
    name = request.values.get('username')
    id = request.values.get('id')

    print(name, id)
    # 先获取再修改提交
    beiwanglu = Beiwanglu.query.filter(Beiwanglu.username == name, Beiwanglu.id == id).first()

    print(beiwanglu)
    if beiwanglu:
        # 完成
        if update=='complete':
            beiwanglu.complete=True
            db.session.commit()
        # 撤销
        elif update=='back':
            beiwanglu.complete = False
            db.session.commit()
        # 修改
        elif update=='update':

            content = request.values.get('content')
            tip = bool(int(request.values.get('tip')))
            date = request.values.get('date')
            time = request.values.get('time')
            # 删除提醒
            if beiwanglu.tip==True and tip==False:
                try:
                    current_app.apscheduler.remove_job(id)
                except:
                    print('no such job!')
            # 添加提醒
            if beiwanglu.tip==False and tip==True:
                try:
                    # 先获取openid
                    user = Users.query.filter(Users.username == name).first()
                    openid = user.openid

                    tip_time = date + ' ' + time + ':00'
                    print(tip_time)
                    if (len(content) > 25):
                        tip_content = content[0:25] + '...'
                    else:
                        tip_content = content
                    # 添加一个定时器
                    add_tip(openid, tip_content, tip_time, id)

                except:
                    print('no such job!')

            beiwanglu.content = content
            beiwanglu.tip = tip
            beiwanglu.date = date
            beiwanglu.time = time
            db.session.commit()

        # 删除
        else:
            ##### 这里还要删除定时器，判断tip是否为1，根据id删除
            if beiwanglu.tip == True:

                try:
                    current_app.apscheduler.remove_job(id)
                except:
                    print('no such job!')

            db.session.delete(beiwanglu)
            db.session.commit()


        return 'success'
    else:
        return 'fail'

'''
调用微信接口获取access_token，用于调用发送消息的api
token有效期为7200s，使用时，先根据当前时间判断token是否有效，有则用，无则调用该函数获取
'''
def get_data():

    # 修改全局变量时需先声明一下
    global token, old_time, expires_in
    # print('ppp')
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx869f84b17b6897e0&secret=4f85f84bb001b83e6bb3c3e95597307e'
    response =  requests.get(url)
    # 将获取到的json字符串转为字典
    dict_json = json.loads(response.content)
    # 获取到的token
    token = dict_json['access_token']
    # 当前的时间戳(s)
    old_time = time.time()
    # 有效期(s)
    expires_in = dict_json['expires_in']

'''
下发模板消息
'''
def send(openid, content, date):

    # 如果token失效，则重新获取
    if(time.time()-old_time>=expires_in):
        get_data()

    url = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?' \
          'access_token='+token
    # openid = 'oaBdd5M0DHnBt7j7k_75qNSro2CA'
    # content = '32个字符以内'
    # date = '2021-10-02'
    data = {
          "touser": openid,
          "template_id": "oiX_o8XHDzPqmh8AQ0tIv7mlaMd0NhfNiS58enFjRsY",
          "page": "/pages/main/main",
          "miniprogram_state":"developer",
          "lang":"zh_CN",
          "data": {
              "thing4": {
                  "value": content
              },
              "time2": {
                  "value": date
              }

          }
        }
    data = json.dumps(data)
    res = requests.post(url=url, data=data)
    print(res.text)


'''
添加定时器任务
'''
# @app.route('/test', methods=['GET', 'POST'])
def add_tip(openid, content, date, id):

    # openid = 'oaBdd5M0DHnBt7j7k_75qNSro2CA'
    # content = '32个字符以内'
    # date = '2021-10-02'
    # scheduler.add_job(func=send, id=id, trigger='date', run_date=date,
    #                   args=[openid, content, date])
    current_app.apscheduler.add_job(func=send, id=id, trigger='date', run_date=date,
                      args=[openid, content, date])

    return 'success'


'''
上传图片到服务器
'''
@app.route('/uploadimg', methods=['GET', 'POST'])
def getImg():
    # 通过表单中name值获取图片
    imgData = request.files["file"]
    # 设置图片要保存到的路径
    # print(basedir)
    path = "static/image/"

    # 获取图片名称及后缀名
    imgName = imgData.filename
    print(imgName)
    # 图片path和名称组成图片的保存路径
    file_path = path + imgName

    # 保存图片
    imgData.save(file_path)

    # url是图片的路径
    # url = '/static/image/' + imgName

    return imgName


'''
返回图片给前端
'''
@app.route('/sendimg', methods=['GET', 'POST'])
def sendImg():
    name = request.values.get('name')
    # path = 'D:\python_pro\\flask_todo\static\image\\' +name
    path = '/home/flask_todo/static/image/' + name
    return send_file(path)

'''
添加便笺
'''
@app.route('/addbianjian', methods=['GET', 'POST'])
def addbianjian():

    name = request.values.get('username')
    id = request.values.get('id')
    date = request.values.get('date')
    time = request.values.get('time')
    content = request.values.get('content')
    # 实例化一个实体，插入表中
    bianjian = Bianjian(id, name,  date, time, content)
    db.session.add(bianjian)


    try:
        db.session.commit()
        return 'success'

    except Exception as e:
        print(e)
        return 'fail'

'''
更新某用户便笺
'''
@app.route('/updatebianjian', methods=['GET', 'POST'])
def update_bianjian():


    update = request.values.get('update')   # 要执行的操作
    name = request.values.get('username')
    id = request.values.get('id')

    # print(name, id)
    # 先获取再修改提交
    bianjain = Bianjian.query.filter(Bianjian.username == name, Bianjian.id == id).first()

    # print(bianjain)
    if bianjain:

        if update=='update':

            content = request.values.get('content')
            date = request.values.get('date')
            time = request.values.get('time')

            bianjain.content = content
            bianjain.date = date
            bianjain.time = time
            db.session.commit()

        # 删除
        else:

            db.session.delete(bianjain)
            db.session.commit()

        return 'success'
    else:
        return 'fail'


'''
返回该用户便笺
'''
@app.route('/returnbianjian', methods=['GET', 'POST'])
def return_bianjian():

    name = request.values.get('username')
    bianjian = Bianjian.query.filter(Bianjian.username == name).all()

    payload = []

    if bianjian:

        for re in bianjian:
            content = {'date': re.date,'time': str(re.time),
                       'content': re.content, 'id': re.id}
            payload.append(content)

        return jsonify(payload)
    else:
        return 'null'
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

    q =  name = request.values.get('content')
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

    if word:

        for re in word:

            translate = re.translate
            content = {'content': re.content, 'translate': json.loads(translate),
                       'active':'0', 'ready':'1'}
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
    if word:


            db.session.delete(word)
            db.session.commit()

            return 'success'
    else:
        return 'fail'


'''
上传文件到服务器
'''
@app.route('/uploadfile', methods=['GET', 'POST'])
def getFile():
    # 通过表单中name值获取图片
    imgData = request.files["file"]
    # 设置图片要保存到的路径
    # print(basedir)
    path = "static/file/"

    # 获取图片名称及后缀名
    imgName = imgData.filename
    print(imgName)
    # 图片path和名称组成图片的保存路径
    file_path = path + imgName

    # 保存图片
    imgData.save(file_path)

    # url是图片的路径
    # url = '/static/image/' + imgName

    return imgName

'''
返回文件给前端
'''
@app.route('/sendfile', methods=['GET', 'POST'])
def sendFile():
    name = request.values.get('name')
    path = 'D:\python_pro\\flask_todo\static\\file\\' +name
    # path = '/home/flask_todo/static/image/' + name
    return send_file(path)

'''
添加文件
'''
@app.route('/addfile', methods=['GET', 'POST'])
def addfile():

    username = request.values.get('username')
    type = request.values.get('type')
    path = request.values.get('path')
    size = request.values.get('size')
    filename = request.values.get('name')

    # print(translate)
    # 实例化一个实体，插入表中
    file = File(username, path, type, filename, size)
    db.session.add(file)

    try:
        db.session.commit()
        return 'success'

    except Exception as e:
        print(e)
        return 'fail'



'''
返回该用户单词
'''
@app.route('/returnfile', methods=['GET', 'POST'])
def return_file():

    name = request.values.get('username')
    file = File.query.filter(File.username == name).all()

    payload = []

    if file:

        for re in file:


            content = {'type': re.type, 'path': re.path,
                       'size': re.size, 'name': re.filename}
            # print(content)
            payload.append(content)

        return jsonify(payload)
    else:
        return 'null'

'''
删除文件
'''
@app.route('/deletefile', methods=['GET', 'POST'])
def delete_file():


    name = request.values.get('username')
    path = request.values.get('path')

    # print(name, id)
    # 先获取再修改提交
    file = File.query.filter(File.username == name, File.path == path).first()

    # print(bianjain)
    if file:


            db.session.delete(file)
            db.session.commit()
            # 之后还要删除该文件
            filepath = 'D:\python_pro\\flask_todo\static\\file\\'+path
            # filepath = '/home/flask_todo/static/file/' + path
            os.remove(filepath)
            return 'success'
    else:
        return 'fail'


'''
创建团队
'''
@app.route('/creategroup', methods=['GET', 'POST'])
def addgroup():

    username = request.values.get('userName')
    groupname = request.values.get('groupName')
    groupdetail = request.values.get('groupDetail')
    groupurl = request.values.get('groupUrl')
    groupid = request.values.get('groupId')
    grouppw = request.values.get('groupPw')
    # print(translate)
    # 实例化一个实体，插入表中
    group = Group(username, groupid, groupname, groupdetail, groupurl, 1, grouppw)
    groupmember = GroupMember(username, groupid)
    db.session.add(group)
    db.session.add(groupmember)

    try:
        db.session.commit()
        return 'success'

    except Exception as e:
        print(e)
        return 'fail'



'''
返回某个团队的人数
'''
@app.route('/groupnumber', methods=['GET', 'POST'])
def return_groupnum():

    groupid = request.values.get('groupId')
    group = Group.query.filter(Group.groupid == groupid).first()


    if group:

        return str(group.number)
    else:
        return 'null'


'''
返回该用户所在的所有团队
'''
@app.route('/returngroups', methods=['GET', 'POST'])
def return_groups():

    name = request.values.get('username')
    # , Group.groupid==GroupMember.groupid
    group = db.session.query(Group).join(GroupMember, Group.groupid==GroupMember.groupid).filter(GroupMember.username==name).all()

    payload = []

    if group:

        for re in group:


            content = { 'groupName': re.groupname,
                      'groupDetail': re.groupdetail,
                      'groupUrl': re.groupurl,
                      'groupId':  re.groupid,
                      'userName': re.username,
                      'groupPw': re.grouppw,
                      'number': re.number}
            # print(content)
            payload.append(content)

        return jsonify(payload)
    else:
        return 'null'

if __name__ == '__main__':

    app.run(debug=True)
