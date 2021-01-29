from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pymysql
# 导入实体类
from entity.entity import Users, Beiwanglu

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:15263080731@127.0.0.1:3306/todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 兼容py3，要导入pymysql
pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)


'''
首页
'''
@app.route('/')
def index():
    # return 'hello world'
    return render_template("index.html")

'''
插入用户信息（注册）
'''
@app.route('/adduser', methods=['GET','POST'])
def add_user():

    name = request.values.get('username')
    phonenum = request.values.get('phonenum')
    password = request.values.get('password')

    # 实例化一个实体，插入表中
    user = Users(name, phonenum, password)
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


if __name__ == '__main__':

    app.run(debug=True)