from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:15263080731@127.0.0.1:3306/todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 兼容py3，要导入pymysql
pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)

# 创建用户实体类
class Users(db.Model):
    # 表名
    __tablename__='user'
    # 表属性
    username = db.Column(db.String(255), primary_key = True)
    phonenum = db.Column(db.String(255))
    password = db.Column(db.String(255))
    nickname = db.Column(db.String(255))
    url = db.Column(db.String(255))
    openid = db.Column(db.String(255))
    def __init__(self, name, phone, password, nickname, url, openid):
        self.username = name
        self.phonenum = phone
        self.password = password
        self.nickname = nickname
        self.url = url
        self.openid = openid

# 创建备忘录实体类
class Beiwanglu(db.Model):
    # 表名
    __tablename__='beiwanglu'
    # 表属性
    id = db.Column(db.String(255), primary_key = True)
    username = db.Column(db.String(255), primary_key = True)
    tip = db.Column(db. Boolean(1))
    date = db.Column(db.Date())
    time = db.Column(db.Time())
    content = db.Column(db.Text(255))
    complete = db.Column(db. Boolean(1))


    def __init__(self, id, name, tip, date, time, content, complete):

        self.id = id
        self.tip = tip
        self.date = date
        self.time = time
        self.username = name
        self.content = content
        self.complete = complete
