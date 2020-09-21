# coding:utf-8
from flask import Flask  # 默认
from flask_cache import Cache  # 缓存

# from pymysqlpool import ConnectionPool
# app入口定义
app = Flask(__name__)

cache = Cache()
config = {
  'CACHE_TYPE': 'redis',
  'CACHE_REDIS_HOST': '127.0.0.1',
  'CACHE_REDIS_PORT': 6379,
  'CACHE_REDIS_DB': '1',
    # 'CACHE_REDIS_PASSWORD': 'FanTan879425'
}
app.config.from_object(config)
cache.init_app(app,config)
app.config.update(SECRET_KEY='tanxiangyu')
