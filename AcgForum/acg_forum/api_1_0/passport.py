from flask import request, jsonify, current_app, session, g

from . import api
from acg_forum.utils.response_code import RET
from acg_forum.models import User, db
from acg_forum.utils.commons import login_required
from acg_forum.image_storage import storage
from acg_forum import constants
from acg_forum import redis_store

import re
import json


@api.route('/sessions', methods=['POST'])
def login():
    """登录接口"""
    user_data = request.get_json()
    if not user_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='用户数据错误')

    mobile = user_data.get('mobile')
    password = user_data.get('password')
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数不完整')

    if not re.match(r'^1[345678]\d{9}$', mobile):
        return jsonify(errno=RET.PARAM_ERR, errmsg='手机号格式错误')

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息异常')
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATA_ERR, errmsg='用户名或密码错误')

    session['user_id'] = user.id
    session['username'] = user.username
    session['mobile'] = mobile

    return jsonify(errno=RET.OK, errmsg='OK', data={'user_id': user.id})


@api.route('/user', methods=['GET'])
@login_required
def get_user_info():
    """
    获取用户信息
    :return:
    """
    user_id = g.user_id
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息失败')
    if not user:
        return jsonify(errno=RET.NO_DATA, errmsg='无效操作')

    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())


@api.route('/user/avatar', methods=['POST'])
@login_required
def alter_avatar():
    """
    修改上传用户头像
    :return:
    """
    user_id = g.user_id
    avatar = request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAM_ERR, errmsg='图片数据错误')
    avatar_data = avatar.read()

    try:
        image_name = storage(avatar_data)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.THIRD_ERR, errmsg='图片上传失败')

    try:
        User.query.filter_by(id=user_id).update({'avatar_url': image_name})
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db.session.rollback()
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息失败')
    image_url = constants.QINIU_DOMIN_PREFIX + image_name
    return jsonify(errno=RET.OK, errmsg='OK', data={'avatar_url': avatar_data})


@api.route('/user/base_info', methods=['PUT'])
@login_required
def alter_user_info():
    """
    修改用户信息(用户名、个人简介、性别)
    :return:
    """
    # 获取用户id
    user_id = g.user_id
    #  获取put请求的参数信息
    user_info = request.get_json()
    if not user_info:
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数错误')

    username = user_info.get('username')
    description = user_info.get('description')
    sex = user_info.get('sex')

    if not (username or description or sex):
        return jsonify(errno=RET.PARAM_ERR, errmsg='您没有修改任何数据')

    try:
        User.query.filter_by(id=user_id).update({'username': username, 'description': description, 'sex': sex})
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db.session.rollback()
        return jsonify(errno=RET.DB_ERR, errmsg='用户信息保存错误')

    session['username'] = username
    session['sex'] = sex
    session['description'] = description

    return jsonify(errno=RET.OK, errmsg='OK', data={'username': username, 'sex': sex, 'description': description})


@api.route('/user/session', methods=['DELETE'])
@login_required
def logout():
    """
    退出登录
    :return:
    """
    session.clear()
    return jsonify(errno=RET.OK, errmsg='OK')


@api.route('/session', methods=['GET'])
def check_login():
    """
    检查用户登录状态
    :return:
    """
    username = session.get('username')
    if username:
        return jsonify(errno=RET.OK, errmsg='True', data={'username': username})
    else:
        return jsonify(errno=RET.SESSION_ERR, errmsg='False')


@api.route('/users/abstract', methods=['GET'])
def get_abs_user_info():
    """
    获取用户缩略信息(文章附带的用户信息展示)
    :return:
    """
    user_data = request.get_json()
    if not user_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数错误')
    user_id = user_data.get('user_id')

    try:
        temp_resp_json = redis_store.get('user_abs_%s' % user_id)
    except Exception as err:
        current_app.logger.error(err)
        temp_resp_json = None

    if temp_resp_json:
        return temp_resp_json

    try:
        user = User.query.get(user_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息异常')

    resp_json = json.dumps({"errno": RET.OK, "errmsg": "OK", "data": user.abs_to_dict()})
    try:
        redis_store.setex('user_abs_' + str(user_id), constants.USER_ABSTRACT_INFO_EXPIRES, resp_json)
    except Exception as err:
        current_app.logger.error(err)

    return resp_json
