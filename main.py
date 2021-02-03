from flask import Flask, render_template, request, jsonify
from flask_apscheduler import APScheduler
# 导入实体类
from entity.entity import *
import requests
import json
import time
from flask import current_app
# 全局变量用于存token及上一次获取的时间,有效期(s)
global token
expires_in=0
old_time=0

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
          "page": "index",
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
if __name__ == '__main__':

    app.run(debug=True)
