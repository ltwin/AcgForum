# 常量模块

# 图片验证码有效时间，单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码redis有效期，单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 七牛空间域名
QINIU_DOMIN_PREFIX = "http://p1rjz3nv1.bkt.clouddn.com/"

# 城区信息redis缓存时间，单位：秒
AREA_INFO_REDIS_EXPIRES = 7200

# 首页展示最多的房屋数量
HOME_PAGE_MAX_HOUSES = 5

# 首页房屋数据的Redis缓存时间，单位：秒
HOME_PAGE_DATA_REDIS_EXPIRES = 7200

# 房屋详情页展示的评论最大数
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30

# 房屋详情页面数据Redis缓存时间，单位：秒
HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200

# 房屋列表页面每页显示条目数
HOUSE_LIST_PAGE_CAPACITY = 2

# 房屋列表页面Redis缓存时间，单位：秒
HOUSE_LIST_REDIS_EXPIRES = 7200

# 首页文章轮播图过期时间
INDEX_ARTICLE_BANNER_EXPIRES = 24 * 60 * 60

# 首页显示的文章条目数
INDEX_ARTICLE_PAGES = 10

# 首页文章缩略信息的缓存时间
INDEX_ARTICLE_LIST_EXPIRES = 7200

# 评论缓存时间
COMMENTS_EXPIRES = 7200

# 文章评论每页显示条目数
COMMENTS_PAGES = 8

# 用户缩略信息缓存时间
USER_ABSTRACT_INFO_EXPIRES = 7200
