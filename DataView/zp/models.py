from django.db import models
from datetime import datetime

# 原始数据
class ZpModel(models.Model):
    class Meta:
        db_table = "zp_item"

    def __str__(self):
        return self.zwmc

    # 设置字段，及其数据类型和属性
    zwmc=models.CharField(max_length=100)# 职位名称
    gsmc=models.CharField(max_length=100)# 公司名称
    min_zwyx=models.IntegerField()# 最低薪资
    max_zwyx=models.IntegerField()#最高薪资
    zwyx=models.CharField(max_length=100)#职位月薪
    dd=models.CharField(max_length=100)#工作地点
    fbrq=models.CharField(max_length=100)#发表日期
    gsxz=models.CharField(max_length=100)#公司性质
    gzjy=models.CharField(max_length=100)#工作经验
    rzyq=models.TextField()#任职要求
    href=models.CharField(max_length=100)#详细页面链接,不能为空值
    zwlb=models.CharField(max_length=100)# 职位小类别
    zwlb_big=models.CharField(max_length=100)# 职位大类别
    zprs=models.CharField(max_length=100)# 招聘人数
    xl=models.CharField(max_length=100)# 学历
    gsgm=models.CharField(max_length=100)# 公司规模
    source=models.CharField(max_length=100)# 来源
    gshy=models.CharField(max_length=100,null=True)# 公司行业
    type=models.CharField(max_length=100)# 职位类型（全职/兼职）
    category=models.CharField(max_length=100,null=True)# 数据挖掘提供分类数据
    province=models.CharField(max_length=100)# 省份
    pointx=models.CharField(max_length=100)# 经度
    pointy=models.CharField(max_length=100)# 纬度
    flxx=models.CharField(max_length=255)#福利信息

# 职位量、职位薪资by地点
class ZpZwByAreaModel(models.Model):
    class Meta:
        db_table = "zp_zw_by_area"
    min_zwyx = models.IntegerField()  # 最低薪资
    max_zwyx = models.IntegerField()  # 最高薪资
    province=models.CharField(max_length=100)# 省份
    pointx=models.CharField(max_length=100)# 经度
    pointy=models.CharField(max_length=100)# 纬度
    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    zprs = models.IntegerField(default=0)  # 招聘人数

# 职位量by职位月薪
class ZpZwCountByZwyxModel(models.Model):
    class Meta:
        db_table = "zp_zw_by_zwyx"

    zwyx = models.CharField(max_length=100)  # 职位月薪
    min_zwyx = models.IntegerField()  # 最低薪资
    max_zwyx = models.IntegerField()  # 最高薪资
    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    zprs=models.IntegerField(default=0)# 招聘人数

# 职位量、职位月薪by公司行业
class ZpZwyxByGshyModel(models.Model):
    class Meta:
        db_table = "zp_zw_by_gshy"

    min_zwyx = models.IntegerField()  # 最低薪资
    max_zwyx = models.IntegerField()  # 最高薪资
    gshy = models.CharField(max_length=100)  # 公司行业
    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    zprs=models.IntegerField(default=0)# 招聘人数

# 职位量、职位月薪by公司规模
class ZpZwyxByGsgmModel(models.Model):
    class Meta:
        db_table = "zp_zw_by_gsgm"

    min_zwyx = models.IntegerField()  # 最低薪资
    max_zwyx = models.IntegerField()  # 最高薪资
    gsgm = models.CharField(max_length=100)  # 公司规模
    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    zprs = models.IntegerField(default=0)  # 招聘人数

# 职位量、职位月薪by公司性值性质
class ZpZwyxByGsxzModel(models.Model):
    class Meta:
        db_table = "zp_zw_by_gsxz"

    min_zwyx = models.IntegerField()  # 最低薪资
    max_zwyx = models.IntegerField()  # 最高薪资
    gsxz = models.CharField(max_length=100)  # 公司性质
    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    zprs=models.IntegerField(default=0)# 招聘人数

# 职位量、职位月薪by学历性质
class ZpZwyxByXlModel(models.Model):
    class Meta:
        db_table = "zp_zw_by_xl"

    min_zwyx = models.IntegerField()  # 最低薪资
    max_zwyx = models.IntegerField()  # 最高薪资
    xl = models.CharField(max_length=100)  # 学历
    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    zprs=models.IntegerField(default=0)# 招聘人数

# 日志记录
class ZpLogModel(models.Model):
    class Meta:
        db_table='zp_log'

    datetime=models.DateTimeField()
    state=models.CharField(max_length=100)
    info=models.TextField()
    request_model=models.CharField(max_length=100)
    href=models.CharField(max_length=255)
    referer=models.CharField(max_length=255)
    contents=models.TextField()

# 分类隐射
class CategoryModel(models.Model):
    class Meta:
        db_table='zp_category'

    category=models.CharField(max_length=50)
    words=models.CharField(max_length=255)

# 工作类型
class ZpZwyxByTypeModel(models.Model):
    class Meta:
        db_table = "zp_zw_by_type"

    min_zwyx = models.IntegerField()  # 最低薪资
    max_zwyx = models.IntegerField()  # 最高薪资
    type = models.CharField(max_length=100)  # 职位类型
    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    zprs=models.IntegerField(default=0)# 招聘人数

# 职位技能词云
class ZpWordByZwlbModel(models.Model):
    class Meta:
        db_table = "zp_word_by_zwlb"

    count=models.IntegerField()#统计
    zwlb=models.CharField(max_length=100)#职位类别
    year=models.IntegerField()# 年
    month=models.IntegerField()# 月
    word=models.CharField(max_length=100)#关键词

# 分词表
class jiebaWordDict(models.Model):
    class Meta:
        db_table = "zp_jieba_word_dict"

    word=models.CharField(max_length=100)# 关键词