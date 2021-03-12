# 导入实体类
from entity.entity import *
# 导入api
from todo_api.beiwanglu_api import *
from todo_api.bianjian_api import *
from todo_api.danci_api import *
from todo_api.group_api import *
from todo_api.user_api import *
from todo_api.wenjian_api import *


'''
首页
'''
@app.route('/')
def index():
    return 'hello world'
    # return render_template("index.html")


if __name__ == '__main__':

    app.run(debug=True)
