
from flask import  request, jsonify

# 导入实体类
from entity.entity import *

'''
创建团队
'''
@app.route('/creategroup', methods=['GET', 'POST'])
def add_group():

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


    try:
        db.session.commit()
        db.session.add(groupmember)
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


    if group!=None:

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

    if group!=None:

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



'''
返回该团队所有成员
'''
@app.route('/returnmaters', methods=['GET', 'POST'])
def return_maters():

    groupid = request.values.get('groupid')
    # , Group.groupid==GroupMember.groupid
    maters = db.session.query(Users.username, Users.url).join(GroupMember, Users.username==GroupMember.username).filter(GroupMember.groupid==groupid).all()

    payload = []

    if maters!=None:

        for re in maters:


            content = { 'userName': re.username,
                      'userUrl': re.url
                      }
            # print(content)
            payload.append(content)

        return jsonify(payload)
    else:
        return 'null'


'''
返回某团队信息
'''
@app.route('/groupdetail', methods=['GET', 'POST'])
def group_detail():

    groupid = request.values.get('groupid')
    # , Group.groupid==GroupMember.groupid
    group = Group.query.filter(Group.groupid==groupid).first()



    if group!=None:


        re = group

        content = { 'groupName': re.groupname,
                      'groupDetail': re.groupdetail,
                      'groupUrl': re.groupurl,
                      'groupId':  re.groupid,
                      'userName': re.username,
                      'groupPw': re.grouppw,
                      'number': re.number}
        # print(content)

        return jsonify(content)
    else:
        return 'null'


'''
验证群密码是否正确
'''
@app.route('/groupsecret', methods=['GET','POST'])
def check_group():

    groupid = request.values.get('groupid')
    password = request.values.get('password')





    group = Group.query.filter(Group.groupid==groupid).first()

    if group.grouppw==password:
        return 'success'
    else:
        return 'fail'



'''
将成员加入该群中
'''
@app.route('/addgm', methods=['GET', 'POST'])
def add_group_member():

    username = request.values.get('userName')
    groupid = request.values.get('groupId')

    # print(username, groupid)
    # 实例化一个实体，插入表中
    # group = Group(username, groupid, groupname, groupdetail, groupurl, 1, grouppw)
    groupmember = GroupMember(username, groupid)
    db.session.add(groupmember)

    # 再修改群信息
    group = Group.query.filter(Group.groupid == groupid).first()
    group.number = group.number + 1

    try:

        db.session.commit()
        return 'success'

    except Exception as e:
        print(e)
        return 'fail'


'''
解散团队
'''
@app.route('/deletegroup', methods=['GET','POST'])
def delete_group():

    groupid = request.values.get('groupId')

    group = Group.query.filter(Group.groupid==groupid).first()

    try:
        db.session.delete(group)
        db.session.commit()

        return 'success'

    except Exception as e:

         print(e)

         return 'fail'

'''
修改团队信息
'''
@app.route('/updategroup', methods = ['GET', 'POST'])
def update_group():

    groupid = request.values.get('groupId')
    groupname = request.values.get('groupName')
    groupdetail = request.values.get('groupDetail')
    grouppw = request.values.get('groupPw')

    group = Group.query.filter(Group.groupid == groupid).first()

    group.groupname = groupname
    group.groupdetail = groupdetail
    group.grouppw = grouppw

    try:
        db.session.commit()
        return 'success'

    except Exception as e:

        print(e)
        return 'fail'

