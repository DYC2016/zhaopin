# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ZpItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    zwmc = scrapy.Field() # 职位名称
    gsmc = scrapy.Field() # 公司名称
    min_zwyx = scrapy.Field()  # 最低薪资
    max_zwyx = scrapy.Field()  # 最高薪资
    zwyx = scrapy.Field()  # 职位月薪
    dd = scrapy.Field() # 工作地点
    fbrq = scrapy.Field() # 发表日期
    gsxz = scrapy.Field() # 公司性质
    gzjy = scrapy.Field()  # 工作经验
    rzyq = scrapy.Field()  # 任职要求
    href = scrapy.Field()  # 详细页面链接,不能为空值
    zwlb = scrapy.Field()  # 职位小类别
    zwlb_big = scrapy.Field()  # 职位大类别
    zprs = scrapy.Field()  # 招聘人数
    xl = scrapy.Field() # 学历
    gsgm = scrapy.Field()  # 公司规模
    source = scrapy.Field()  # 来源
    gshy = scrapy.Field()  # 公司行业
    type = scrapy.Field()  # 职位类型（全职/兼职）
    province = scrapy.Field()  # 省份
    pointx = scrapy.Field()  # 经度
    pointy = scrapy.Field()  # 纬度
    flxx=scrapy.Field() # 福利信息
