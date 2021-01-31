from flask import Flask, render_template, request, jsonify
# 导入实体类
from entity.entity import *
import requests
import json
import time
# from entity.entity import Users, Beiwanglu
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:15263080731@127.0.0.1:3306/todo'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# # 兼容py3，要导入pymysql
# pymysql.install_as_MySQLdb()
# db = SQLAlchemy(app)

# 全局变量用于存token及上一次获取的时间,有效期(s)
global token, expires_in
old_time=0

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
    url = request.values.get('url')
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
    user = Users(name, phonenum, password, nickname, url, openid)
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


    try:
        db.session.commit()
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

            beiwanglu.content = request.values.get('content')
            beiwanglu.tip = bool(int(request.values.get('tip')))

            beiwanglu.date = request.values.get('date')
            beiwanglu.time = request.values.get('time')
            db.session.commit()
        # 删除
        else:
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


if __name__ == '__main__':


    app.run(debug=True)
