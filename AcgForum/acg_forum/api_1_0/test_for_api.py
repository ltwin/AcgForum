from . import api

from flask import Flask, jsonify, request, current_app, session

from acg_forum.utils.response_code import RET
from acg_forum.models import User
from acg_forum.utils.commons import g, login_required
from acg_forum.models import User, db

# app = Flask(__name__)


@api.route('/')
def hello_world():
    return 'Hello World!'

#
# @api.route('/test', methods=['GET'])
# def get_api():
#     username = request.cookies.get('username')
#     password = request.cookies.get('password')
#     mobile = request.cookies.get('mobile')
#


@api.route('/test', methods=['POST'])
def test_api():
    user_data = request.get_json()
    if not user_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='用户数据错误')

    username = user_data.get('username')
    password = user_data.get('password')
    mobile = user_data.get('mobile')
    print(username, password, mobile)

    try:
        user = User.query.filter_by(username=username).first()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询数据库错误')

    # if user:
    #     return jsonify(errno=RET.DATA_EXISTS, errmsg='用户名已存在')

    user = User(username=username, mobile=mobile)
    user.password = password
    print(user.password_hash)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db.session.rollback()
        return jsonify(errno=RET.DB_ERR, errmsg='用户信息保存错误')

    session['user_id'] = user.id
    session['username'] = username
    session['mobile'] = mobile

    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict()) # todo ?


@api.route('/index', methods=['GET'])
@login_required
def index():
    user_id = g.user_id
    print(user_id)
    print('test_for_index')
    # try:
    #     user_id = g.user_id
    # except Exception as err:
    #     return jsonify(errno=RET.SESSION_ERR, errmsg='用户未登录')

    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='数据库查询错误')

    print(user.username)
    # username = user.username
    # password = user.password
    # mobile = user.mobile
    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())


# if __name__ == '__main__':
#     api.run()
