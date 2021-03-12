from flask import request, jsonify, send_file

# 导入实体类
from entity.entity import *

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