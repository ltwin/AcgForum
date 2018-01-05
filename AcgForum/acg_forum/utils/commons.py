import functools
from flask import g, session, jsonify
from werkzeug.routing import BaseConverter

from acg_forum.utils.response_code import RET


class RegexConverter(BaseConverter):
    """在路由中使用正则表达式进行提取参数的转换工具"""
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_required(f):
    """要求用户登录的装饰器"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(errno=RET.SESSION_ERR, errmsg='用户未登录')
        else:
            g.user_id = user_id
            return f(*args, **kwargs)
    return wrapper
