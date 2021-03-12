from flask import request
# 导入实体类
from entity.entity import *
import requests
import json


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
