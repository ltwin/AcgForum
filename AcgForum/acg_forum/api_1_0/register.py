from flask import current_app, jsonify, make_response, request, session
from celery import Celery

from . import api
from acg_forum.utils.captcha.captcha import captcha
from acg_forum import redis_store, constants, db
from acg_forum.utils.response_code import RET
from acg_forum.models import User, db
from acg_forum.utils import sms

import random
import re


@api.route('/image_code/<image_code_id>', methods=['GET'])
def generate_image_code(image_code_id):
    """
    生成图片验证码
    :param image_code_id:
    :return:
    """
    # 调用captcha扩展包，生成图片验证码
    name, text, image = captcha.generate_captcha()
    # 把图片验证码存入redis
    try:
        redis_store.setex('ImageCode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='图片验证码保存失败')
    else:
        response = make_response(image)
        # 设置响应类型
        response.headers['Content-Type'] = 'image/jpg'
        return response


@api.route('/sms_code/<mobile>', methods=['GET'])
def send_sms_code(mobile):
    """
    发送短信验证码
    :param mobile:
    :return:
    """
    image_code_id = request.args.get('image_code_id')
    image_code = request.args.get('image_code')

    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数不完整')

    if not re.match(r'1[345678]\d{9}$', mobile):
        return jsonify(errno=RET.PARAM_ERR, errmsg='手机号格式错误')

    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询图片验证码失败')

    if not image_code:
        return jsonify(errno=RET.NO_DATA, errmsg='图片验证码已过期')

    # 删除缓存中的该验证码
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as err:
        current_app.logger.error(err)

    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=RET.PARAM_ERR, errmsg='图片验证码错误')

    # 接下来发送短信验证码
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='获取用户信息失败')

    if user:
        return jsonify(errno=RET.DATA_EXISTS, errmsg='手机号已注册')

    sms_code = '%06d' % random.randint(1, 1000000)
    try:
        redis_store.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='短信验证码存储异常')

    try:
        ccp = sms.CCP()
        # 发送短信的方法有返回值，返回0为成功放松
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.THIRD_ERR, errmsg='短信发送异常')

    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRD_ERR, errmsg='发送失败')


@api.route('/users', methods=['POST'])
def register():
    """
    注册
    :return:
    """
    user_data = request.get_json()
    if not user_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='用户数据不存在')

    mobile = user_data.get('mobile')
    sms_code_id = user_data.get('sms_code_id')
    sms_code = user_data.get('sms_code')
    password = user_data.get('password')

    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数不完整')

    if not re.match(r'^1[345678]\d{9}$', mobile):
        return jsonify(errno=RET.PARAM_ERR, errmsg='手机号格式错误')

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息错误')

    if user:
        return jsonify(errno=RET.DATA_EXISTS, errmsg='该手机号已注册')

    try:
        real_sms_code = session.get('SMSCode_' + sms_code_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(RET.DB_ERR, errmsg='获取短信验证码失败')

    if real_sms_code != sms_code:
        return jsonify(RET.PARAM_ERR, errmsg='短信验证码错误')

    user = User(mobile=mobile, username=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db.session.rollback()
        return jsonify(RET.DB_ERR, errmsg='用户信息保存失败')

    session['user_id'] = user.id
    session['username'] = mobile
    session['mobile'] = mobile

    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())
