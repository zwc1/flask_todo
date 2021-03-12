
from flask import  request, jsonify

# 导入实体类
from entity.entity import *

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