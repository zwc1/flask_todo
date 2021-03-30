from flask import  request, jsonify, send_file
# 导入实体类
from entity.entity import *
import os

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
返回该用户文件
'''
@app.route('/returnfile', methods=['GET', 'POST'])
def return_file():

    name = request.values.get('username')
    file = File.query.filter(File.username == name).all()

    payload = []

    if file!=None:

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
    if file!=None:


            db.session.delete(file)
            db.session.commit()
            # 之后还要删除该文件
            filepath = 'D:\python_pro\\flask_todo\static\\file\\'+path
            # filepath = '/home/flask_todo/static/file/' + path
            os.remove(filepath)
            return 'success'
    else:
        return 'fail'
