from flask import g, session, current_app, jsonify, request

from acg_forum.models import Article, db, User, ArticleImageUrl, Comment
from . import api
from acg_forum.utils.commons import login_required
from acg_forum.utils.response_code import RET
from acg_forum.image_storage import storage
from acg_forum import redis_store
from acg_forum import constants
from acg_forum.utils import image_storage

from datetime import datetime, timedelta

import json


@api.route('/articles/texts', methods=['POST'])
@login_required
def public_article():
    """
    发布文章
    :return:
    """
    article_data = request.get_json()
    if not article_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数错误')
    title = article_data.get('title')
    main_text = article_data.get('text')
    type_id = article_data.get('type_id')

    # 获取用户id
    user_id = g.user_id
    # 查询用户信息
    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.NO_DATA, errmsg='未知错误')

    article = Article(title=title, main_text=main_text)
    article.user_id = user_id
    article.type_id = type_id
    try:
        db.session.add(article)
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db.session.rollback()
        return jsonify(errno=RET.DB_ERR, errmsg='保存文章数据失败')
    # 前端得到文章id就可以进行后续操作
    return jsonify(errno=RET.OK, errmsg='OK', data={'article_id': article.id})


@api.route('/articles/images', methods=['POST'])
@login_required
def upload_article_images():
    """
    上传文章图片
    :return:
    """
    user_id = g.user_id

    article_data = request.get_json()
    if not article_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='文章参数错误')

    article_id = article_data.get('article_id')

    image_files = request.files.getlist()
    if not image_files:
        return jsonify(errno=RET.PARAM_ERR, errmsg='没有上传图片')

    # 前端可以使用eval函数转换字符串为数组，然后遍历数组
    images_url_list = []
    for image_file in image_files:
        image_data = image_file.read()
        try:
            image_name = image_storage.storage(image_data)
        except Exception as err:
            current_app.logger.error(err)
            return jsonify(errno=RET.THIRD_ERR, errmsg='上传图片失败')
        else:
            image_url = constants.QINIU_DOMIN_PREFIX + image_name
            try:
                article_image_url = ArticleImageUrl()
                article_image_url.article_id = article_id
                article_image_url.image_url = image_url
                db.session.add(article_image_url)
                db.session.commit()
            except Exception as err:
                current_app.logger.error(err)
                return jsonify(errno=RET.DB_ERR, errmsg='存储文章图片失败')

            images_url_list.append(image_url)

    return jsonify(errno=RET.OK, errmsg='OK', data={'images_url': images_url_list})


@api.route('/index/page/<int:page>', methods=['GET'])
def get_article_info(page):
    """
    获取首页文章缩略信息(article_id, page)
    :return:
    """
    try:
        resp_json = redis_store.get('index_' + page)
    except Exception as err:
        current_app.logger.error(err)
        resp_json = None

    if resp_json:
        return resp_json

    try:
        # 查询所有没有被删除的文章
        articles = Article.query.filter(Article.is_delete is False).all()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询文章失败')
    if not articles:
        return jsonify(errno=RET.NO_DATA, errmsg='未知错误')

    try:
        # 分页的参数,page页数/每页数据条目数/False分页如果发生异常不会报错
        articles_page = articles.paginate(page, constants.INDEX_ARTICLE_PAGES, False)
        # 保存分页后的房屋数据和总页数
        articles_list = articles.items
        total_page = articles.pages

        current_articles_abs_dict_list = []
        for article in articles_list:
            article_id = article.id
            # 拿到对应文章的所有图片中的第一个作为缩略图
            abs_image_url = ArticleImageUrl.query.filter(ArticleImageUrl.article_id == article_id).first().image_url
            # 保存缩略图信息
            article.abs_image_url = abs_image_url
            current_articles_abs_dict_list.append(article.abs_to_dict())
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询文章缩略信息异常')

    resp_json = json.dumps({'errno': RET.OK, 'errmsg': 'OK', 'data': {'articles': current_articles_abs_dict_list, 'total_page': total_page, 'current_page': page}})

    redis_store.setex('page_' + page, constants.INDEX_ARTICLE_LIST_EXPIRES, resp_json)
    return resp_json


@api.route('/articles/index_banners', methods=['GET'])
def get_index_banner():
    """
    获取首页文章轮播图
    :return:
    """
    # 尝试从缓存中获取index_banner信息
    try:
        temp_banner = redis_store.get('index_banner')  # 这是article_banner_dict_list
    except Exception as err:
        current_app.logger.error(err)
        temp_banner = None
    if temp_banner:
        current_app.logger.info('hit index_banner info redis')
        return '{"errno": 0, "errmsg": "OK", "articles_list": %s}' % temp_banner

    # 缓存为空
    # 查询最近一个星期的最多五篇文章，按照收藏数进行排序，且图片不能为空
    try:
        articles = Article.query.filter(Article.create_time >= (datetime.now()-timedelta(days=7)), Article.image_urls is not None, Article.is_delete is False).order_by(Article.collection_count.desc()).limit(5)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询文章失败')

    # 不实用的方法
    # articles_list = []
    # i = 0
    # for article in articles:
    #     if i < 5:
    #         if (datetime.now() - article.create_time).days <= 7:
    #             articles_list.append(article)
    #             i += 1
    #  查询每篇文章对应的图片信息，并且取出其中一张作为首页展示图，动态添加属性banner_image
    index_banner_dict_list = []
    try:
        for article in articles:
            article_id = article.id
            banner_image_url = ArticleImageUrl.query.filter_by(article_id=article_id).order_by(ArticleImageUrl.id.asc()).first().image_url
            article.banner_image_url = banner_image_url
            index_banner_dict_list.append(article.banner_to_dict())
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='文章列表查询异常')

    # 前端接收后，拿出data，遍历articles_list，取得文章信息
    resp_json = json.dumps({"errno": RET.OK, "errmsg": "OK", "index_banner_dict_list": index_banner_dict_list})

    # 将首页轮播图文章列表存入redis缓存中
    redis_store.setex('index_banner', constants.INDEX_ARTICLE_BANNER_EXPIRES, index_banner_dict_list)

    return resp_json


@api.route('/article/<int:article_id>/comments', methods=['GET'])
def get_comments(article_id):
    """
    查看文章评论(用户缩略信息，评论主体)
    :return:
    """
    page = request.args.get('page')

    if not article_id and page:
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数错误')

    # 先尝试从缓存中获取评论信息
    try:
        comments_json = redis_store.hget('comments_%s' % article_id, page)
    except Exception as err:
        current_app.logger.error(err)
        comments_json = None

    if comments_json:
        return comments_json

    try:
        comments = Comment.query.filter(Comment.article_id == article_id).all()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询评论信息异常')

    comments_page = comments.paginate(page, constants.COMMENTS_PAGES, False)
    comments_list = comments_page.items
    total_page = comments_page.pages

    comments_dict_list = []
    for comment in comments_list:
        comments_dict_list.append(comment.to_dict())

    # 包含用户id，文章id，评论文本，点赞数
    resp_json = json.dumps({"errno": RET.OK, "errmsg": "OK", "data": {"comments": comments_dict_list, "total_page": total_page, "current_page": page}})

    if page <= total_page:
        redis_key = 'comments_%s' % article_id
        pip = redis_store.pipeline()
        try:
            # 开启事务
            pip.multi()
            pip.hset(redis_key, page, resp_json)
            pip.expire(redis_key, constants.COMMENTS_EXPIRES)
            # 执行事务
            pip.execute()
        except Exception as err:
            current_app.logger.error(err)
    return resp_json


@api.route('/article/<int:article_id>/comment', methods=['POST'])
@login_required
def add_comments(article_id):
    """
    用户添加评论
    :return:
    """
    comment_data = request.get_json()

    if not comment_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数缺失')

    user_id = comment_data.get('user_id')
    comment = comment_data.get('comment')
    praise_count = comment_data.get('praise_count')

    try:
        comment = Comment()
        comment.user_id = user_id
        comment.article_id = article_id
        comment.praise_count = praise_count

        db.session.add(comment)
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='保存评论信息失败')

    return jsonify(errno=RET.OK, errmsg='OK', data=comment.to_dict())


@api.route('/comments/praise', methods=['PUT'])
@login_required
def comments_praise():
    """
    为评论点赞
    :return:
    """
    comment_data = request.get_json()
    if not comment_data:
        return jsonify(errno=RET.PARAM_ERR, errmsg='参数错误')

    comment_id = comment_data.get('comment_id')
    user_id = g.user_id
    try:
        comment = Comment.query.filter_by(id=comment_id)
        praise_count = comment.first().praise_count + 1
        comment.update({'praise_count': praise_count})
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db.session.rollback()
        return jsonify(errno=RET.DB_ERR, errmsg='更新点赞信息失败')

    return jsonify(errno=RET.OK, errmsg='OK', data={'praise_count': praise_count})


@api.route('/article/<int:article_id>/praise', methods=['PUT'])
@login_required
def article_priase(article_id):
    """
    为文章点赞
    :param article_id:
    :return:
    """
    # todo


@api.route('/article/<article_id>/collect', methods=['POST'])
@login_required
def add_collect(article_id):
    """
    用户收藏文章
    :return:
    """
    pass  # todo 用户收藏文章


@api.route('/articles/<user_id>', methods=['GET'])
def get_user_articles(user_id):
    """
    获取用户所有的文章信息
    :return:
    """
    try:
        user = User.query.get(user_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息失败')
    try:
        articles = user.articles
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询文章信息失败')

    articles_list = []
    if articles:
        for article in articles_list:
            articles_list.append(article)

    return jsonify(errno=RET.OK, errmsg='OK', data={'articles': articles_list})


@api.route('/article/<article_id>/details', methods=['GET'])
def get_article_details(article_id):
    """
    查看文章的详细信息
    :param article_id:
    :return:
    """
    try:
        article = Article.query.get(article_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询文章信息失败')

    if not article:
        return jsonify(errno=RET.NO_DATA, errmsg='没有该文章信息')

    # 要显示用户的缩略信息(头像、用户名、性别)
    try:
        user_id = article.user_id
        user = User.query.get(user_id)
        username = user.username
        sex = user.sex

    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno=RET.DB_ERR, errmsg='查询用户信息失败')

    return jsonify(errno=RET.OK, errmsg='OK', data=article.detail_to_dict())
