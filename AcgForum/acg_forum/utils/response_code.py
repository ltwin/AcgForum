class RET:
    OK = '0'
    DB_ERR = '4001'
    SESSION_ERR = '4101'
    PARAM_ERR = '4103'
    DATA_ERR = '4004'
    DATA_EXISTS = '4003'
    NO_DATA = '4002'
    THIRD_ERR = '4301'
    pass


err_map = {
    RET.OK: '成功',
    RET.DB_ERR: '数据库查询错误',
    RET.SESSION_ERR: '用户未登录',
    RET.PARAM_ERR: '参数错误',
    RET.DATA_ERR: '数据错误',
    RET.DATA_EXISTS: '参数已存在',
    RET.NO_DATA: '数据不存在',
    RET.THIRD_ERR: '第三方系统错误',
}
