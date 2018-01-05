from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, SQLAlchemy


class BaseModel:
    """模型基类"""
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    is_delete = db.Column(db.Boolean, default=False)


class User(BaseModel, db.Model):
    """用户模型类"""
    __tablename__ = 'af_user_profile'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    mobile = db.Column(db.String(11), nullable=False)
    avatar_url = db.Column(db.String(64), default='avatar_default')
    sex = db.Column(db.SmallInteger, default=0)  # 0为未知，1为男，2为女
    description = db.Column(db.String(256), default='该用户很懒')
    rank = db.Column(db.SmallInteger, default=0)  # 级别

    followers = db.relationship('Followers', backref='user')
    articles = db.relationship('Article', backref='user')

    # 将password提升为属性
    @property
    def password(self):
        """获取password属性时调用"""
        raise AttributeError('不可读')

    @password.setter
    def password(self, pwd):
        """password被设置时调用"""
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        """检查密码的正确性"""
        return check_password_hash(self.password_hash, pwd)

    def to_dict(self):
        """将对象转化为字典数据"""
        user_dict = {
            'user_id': self.id,
            'username': self.username,
            # 'password': self.password,
            'mobile': self.mobile,
            'sex': self.sex,
            'description': self.description,
            'rank': self.rank,
            'avatar_url': self.avatar_url,
        }
        return user_dict

    def abs_to_dict(self):
        """缩略信息"""
        user_abs_dict = {
            'user_id': self.id,
            'username': self.username,
            'avatar_url': self.avatar_url,
        }

    # def __repr__(self):
    #     return 'user(username="%s")' % self.username


class Followers(BaseModel, db.Model):
    """粉丝列表"""
    __tablename__ = 'af_followers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('af_user_profile.id'))
    follower_id = db.Column(db.Integer, db.ForeignKey('af_user_profile.id'))


class ArticleType(BaseModel, db.Model):
    """分区列表"""
    __tablename__ = 'af_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, default='未分类', index=True)
    type_image_url = db.Column(db.String(64), default='type_default')

    articles = db.relationship('Article', backref='type')

    def __repr__(self):
        return 'type(type_name="%s")' % self.name


class Article(BaseModel, db.Model):
    """文章列表"""
    __tablename__ = 'af_article'

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('af_type.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('af_user_profile.id'))
    title = db.Column(db.String(32), default='无标题', index=True)
    abstract = db.Column(db.String(100))  # 文章摘要
    view_count = db.Column(db.Integer, default=0)  # 浏览数
    comment_count = db.Column(db.Integer, default=0)  # 评论数
    collection_count = db.Column(db.Integer, default=0)  # 收藏数
    praise_count = db.Column(db.Integer, default=0)  # 点赞数
    main_text = db.Column(db.Text, nullable=False)
    # image_url = db.Column(db.String(64), default=None)
    # main_image_urls = db.Column(db.String(64), default=None)
    abs_image_url = db.Column(db.String(64), default=None)  # 文章缩略图
    banner_image_url = db.Column(db.String(64))  # 首页轮播图

    images_url = db.relationship('ArticleImageUrl', backref='article')

    def abs_to_dict(self):
        article_dict = {
            'title': self.title,
            'abs_image_url': self.abs_image_url,
            'abstract': self.abstract,
            'user_id': self.user_id,  # 返回给前端user_id，然后前端可以通过它寻找用户缩略信息
            # 'comment_count': self.comment_count,
            # 'collection_count': self.collection_count,
            # 'main_text': self.main_text,
            # 'main_image_url': self.main_image_url,
            # 'praise_count': self.praise_count,
        }
        return article_dict

    def detail_to_dict(self):
        detail_dict = {
            'title': self.title,
            # 'abs_image_url': self.abs_image_url,
            'comment_count': self.comment_count,
            'collection_count': self.collection_count,
            'praise_count': self.praise_count,
            'main_text': self.main_text,
            'main_image_url': self.main_image_url,
            'user_id': self.user_id,
            'type_id': self.type_id,
        }
        return detail_dict

    def banner_to_dict(self):
        banner_dict = {
            'title': self.title,
            'banner_image_url': self.banner_image_url,
            'abstract': self.abstract,
        }
        return banner_dict

    def __repr__(self):
        return 'article(title="%s")' % self.title


class IndexBanner(BaseModel, db.Model):
    """首页推荐轮播图"""
    # todo 暂时作废
    __tablename__ = 'af_index_banner'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('af_article.id'))
    banner_image_url = db.Column(db.String(64), default='banner_default')


class ArticleImageUrl(BaseModel,db.Model):
    """文章图片列表"""
    __tablename__ = 'af_article_image_url'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('af_article.id'))
    image_url = db.Column(db.String(64), default=None)


class Comment(BaseModel, db.Model):
    """评论模型类"""
    __tablename__ = 'af_comment'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('af_article.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('af_user_profile.id'))
    comment = db.Column(db.Text)
    praise_count = db.Column(db.Integer, default=0)  # 点赞数

    def to_dict(self):
        """将评论信息转换为字典"""
        comment_dict = {
            'comment_id': self.id,
            'article_id': self.article_id,
            'user_id' : self.user_id,
            'comment': self.comment,
            'praise_count': self.praise_count,
        }

        return comment_dict


class ArticlePraise(BaseModel, db.Model):
    """文章点赞模型类(可以存储为每篇文章点赞的用户)"""
    __tablename__ = 'af_article_praise'

    id = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('af_user_profile.id'))
    praise_user_id = db.Column(db.Integer, db.ForeignKey('af_user_profile.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('af_article.id'))
