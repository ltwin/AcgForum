import redis


class Config:
    """基本配置参数"""
    SECRET_KEY = 'Ft4a8h4t8ah4t8a9h4t8a9h4t8a9ht8a9h4t8a964ht8a9h4t8a9h4t8a9h48'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost:3306/AcgForum'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"  # 保存session数据的地方
    SESSION_USE_SIGNER = True  # 为session id进行签名
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 保存session数据的redis配置
    PERMANENT_SESSION_LIFETIME = 86400  # session数据有效时间

    # flask_msearch配置参数
    MSEARCH_INDEX_NAME = 'whoosh_index'
    MSEARCH_BACKEND = 'whoosh'
    MSEARCH_ENABLE = True

    # 配置celery参数
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'


class DevelopmentConfig(Config):
    """开发者模式"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置参数"""
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
