# -*- coding: utf-8 -*-
import random
import time

import jieba.analyse as jb_an
import pymysql
import redis
from scrapy.exceptions import DropItem


#数据清洗
class DataCleanPipeline(object):
    def process_item(self,item,spider):
        #去除职位名称和公司名称的数据的两端空格
        item['zwmc']=item['zwmc'].strip()
        item['gsmc'] = item['gsmc'].strip()
        if item['zwmc']=='' or item['zdxl']=='' or item['gzdd']=='' or item['gsmc']=='':
            #如果数据为空，那么返回DropItem,传递的文本信息任意
            raise DropItem('The position has failed')
        if item['gsxz']=='':
            item['gsxz']='其它'
        if item['min_zwyx']=='' or item['max_zwyx']=='':
            item['min_zwyx']=item['max_zwyx']=0
        if item['gzjy']=='':
            item['gzjy'] = '不限'
        if item['gsgm']=='':
            item['gsgm']='其他'
        return item

#发布时间转换为正确的时间格式
class DataTimePipeline(object):
    def process_item(self,item,spider):
        # 判断是否为空
        if item['fbrq']=='' or '0002-01-01' in item['fbrq']:
            ##修改日期为今天的日期,使用time完成操作
            now_timetmp=time.time()  #当前的时间戳
            last_day_timetmp=now_timetmp
            last_day_tupel=time.localtime(last_day_timetmp)#将时间戳转换为时间元祖
            item['fbrq'] = time.strftime('%Y-%m-%d', last_day_tupel)  # 时间元祖格式化为规定的时间字符串
        else:
            item['fbrq'] = item['fbrq'].split(' ')[0]
        return item

#数据去重(针对的一次爬虫执行过程中数据重复的处理)
class DuplicatesPipeline(object):
    #scrapy会自动过滤已经走过的链接，但是很多情况，不同链接，可能存在同样的数据
    #判断职位和公司是否已经抓取过
    def __init__(self):
        pool = redis.ConnectionPool(host='127.0.0.1',password='FanTan879425', port=6379)
        self.conn = redis.Redis(connection_pool=pool)
    def process_item(self,item,spider):
        if item['zwmc']=='' or item['gsmc']=='' or item['gsmc']==None or item['zwlb']=='' or self.conn.zrank('zwmc_gsmc_zwlb',item['zwmc']+'_'+item['gsmc']+'_'+item['zwlb']):
            #如果存在这样的数据组合，那么表示职位数据已经存在
            #返回异常
            raise DropItem('Duplicate item found %s'%item)
        else:
            #数据组合添加到集合内
            self.conn.zadd('zwmc_gsmc_zwlb',item['zwmc']+'_'+item['gsmc']+'_'+item['zwlb'],item['href'])
            return item

#数据存储
class MysqlPipeline(object):
    # 建立初始化方法
    def __init__(self, mysql_host, mysql_user, mysql_passwd, mysql_db):
        self.MYSQL_HOST = mysql_host
        self.MYSQL_USER = mysql_user
        self.MYSQL_PASSWD = mysql_passwd
        self.MYSQL_DB = mysql_db

    # 从settings文件中提取mysql的配置信息
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            #crawler.settings.get 代表从爬虫项目的settings文件里查找配置信息
            mysql_host=crawler.settings.get('MYSQL_HOST', 'localhost'),
            mysql_user=crawler.settings.get('MYSQL_USER', 'root'),
            mysql_passwd=crawler.settings.get('MYSQL_PASSWD', 'root'),
            mysql_db=crawler.settings.get('MYSQL_DB','zp')
        )

    # 在爬虫启动的时候链接数据库
    def open_spider(self, spider):
        #要在上面引入pymysql模块
        self.conn = pymysql.connect(host=self.MYSQL_HOST, user=self.MYSQL_USER, passwd=self.MYSQL_PASSWD,
                                    db=self.MYSQL_DB, charset='utf8')

    # 在爬虫关闭的时候，断开数据库链接
    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    # 数据存储
    def process_item(self, item, spider):
        #操作游标
        cusor = self.conn.cursor()
        #1. 查询地点ID
        cusor.execute('select id from zp_dd where dd_name=%s', (item['gzdd'],))
        #1. cusor.execute('select id from zp_dd where dd_name=%s', (item['gzdd'],))
        # cursor.execute(sql,parm)
        # parm 对于前面的sql中%s（字段值）进行填充
        # sql->  select id from zp_dd where dd_name='上海'
        #2.cusor.execute('select id from zp_dd where dd_name="%s"'%(item['gzdd']))
        # sql->  select id from zp_dd where dd_name="上海"
        result_dd = cusor.fetchone()
        if result_dd:
            dd_id = result_dd[0]
        else:  # 如果没有查询到结果,插入数据到数据库
            cusor.execute('insert into zp_dd (dd_name) value (%s)', (item['gzdd'],))
            cusor.execute('select id from zp_dd where dd_name=%s', (item['gzdd'],))
            result_dd = cusor.fetchone()
            dd_id = result_dd[0]
        #2. 查询职位名称id
        cusor.execute('select * from zp_zwmc where zwmc_name=%s', (item['zwmc'],))
        result_zwmc = cusor.fetchone()
        if result_zwmc:
            zwmc_id = result_zwmc[0]
        else:  # 如果没有查询到结果
            cusor.execute('insert into zp_zwmc value (null,%s)', (item['zwmc'],))
            self.conn.commit()
            cusor.execute('select * from zp_zwmc where zwmc_name=%s', (item['zwmc'],))
            result_zwmc = cusor.fetchone()
            zwmc_id = result_zwmc[0]

        #3. 查询公司名称id
        cusor.execute('select * from zp_gsmc where gsmc_name=%s', (item['gsmc'],))
        result_gsmc = cusor.fetchone()
        if result_gsmc:
            gsmc_id = result_gsmc[0]
        else:
            cusor.execute('insert into zp_gsmc value (null,%s)', (item['gsmc'],))
            cusor.execute('select * from zp_gsmc where gsmc_name=%s', (item['gsmc'],))
            result_gsmc = cusor.fetchone()
            gsmc_id = result_gsmc[0]
        # 12 查询大分类的id
        cusor.execute('select * from zp_zwlb_big where zwlb_big_name=%s', (item['zwlb_big'],))
        result_zwlb_big = cusor.fetchone()
        if result_zwlb_big:
            zwlb_big_id = result_zwlb_big[0]
        else:
            cusor.execute('insert into zp_zwlb_big VALUES (NULL ,%s)', (item['zwlb_big'],))
            cusor.execute('select * from zp_zwlb_big where zwlb_big_name=%s', (item['zwlb_big'],))
            result_zwlb_big = cusor.fetchone()
            zwlb_big_id = result_zwlb_big[0]
        #4. 查询职位分类的id
        cusor.execute('select * from zp_zwlb where zwlb_name=%s and zwlb_big_id=%s', (item['zwlb'],zwlb_big_id))
        result_zwlb = cusor.fetchone()
        if result_zwlb:
            zwlb_id = result_zwlb[0]
        else:
            cusor.execute('insert into zp_zwlb VALUES (NULL ,%s,%s)', (item['zwlb'],zwlb_big_id))
            cusor.execute('select * from zp_zwlb where zwlb_name=%s and zwlb_big_id=%s', (item['zwlb'],zwlb_big_id))
            result_zwlb = cusor.fetchone()
            zwlb_id = result_zwlb[0]
        #5. 查询公司行业的id
        cusor.execute('select * from zp_gshy where gshy_name=%s', (item['gshy'],))
        result_gshy = cusor.fetchone()
        if result_gshy:
            gshy_id = result_gshy[0]
        else:
            cusor.execute('insert into zp_gshy VALUES (NULL ,%s)', (item['gshy'],))
            cusor.execute('select * from zp_gshy where gshy_name=%s', (item['gshy'],))
            result_gshy = cusor.fetchone()
            gshy_id = result_gshy[0]
        #6. 查询公司性质的id
        cusor.execute('select * from zp_gsxz where gsxz_name=%s', (item['gsxz'],))
        result_gsxz = cusor.fetchone()
        if result_gsxz:
            gsxz_id = result_gsxz[0]
        else:
            cusor.execute('insert into zp_gsxz VALUES (NULL ,%s)', (item['gsxz'],))
            cusor.execute('select * from zp_gsxz where gsxz_name=%s', (item['gsxz'],))
            result_gsxz = cusor.fetchone()
            gsxz_id = result_gsxz[0]
        #7. 查询工作经验的id
        cusor.execute('select * from zp_gzjy where gzjy_name=%s', (item['gzjy'],))
        result_gzjy = cusor.fetchone()
        if result_gzjy:
            gzjy_id = result_gzjy[0]
        else:
            cusor.execute('insert into zp_gzjy VALUES (NULL ,%s)', (item['gzjy'],))
            cusor.execute('select * from zp_gzjy where gzjy_name=%s', (item['gzjy'],))
            result_gzjy = cusor.fetchone()
            gzjy_id = result_gzjy[0]
        #8. 查询学历的id
        cusor.execute('select * from zp_xl where xl_name=%s', (item['zdxl'],))
        result_xl = cusor.fetchone()
        if result_xl:
            xl_id = result_xl[0]
        else:
            cusor.execute('insert into zp_xl VALUES (NULL ,%s)', (item['zdxl'],))
            cusor.execute('select * from zp_xl where xl_name=%s', (item['zdxl'],))
            result_xl = cusor.fetchone()
            xl_id = result_xl[0]
        # 9. 查询公司规模的id
        cusor.execute('select * from zp_gsgm where gsgm_name=%s', (item['gsgm'],))
        result_gsgm = cusor.fetchone()
        if result_gsgm:
            gsgm_id = result_gsgm[0]
        else:
            cusor.execute('insert into zp_gsgm VALUES (NULL ,%s)', (item['gsgm'],))
            cusor.execute('select * from zp_gsgm where gsgm_name=%s', (item['gsgm'],))
            result_gsgm = cusor.fetchone()
            gsgm_id = result_gsgm[0]
        #10.存储数据到zp_list中
        cusor.execute('select * from zp_list where href=%s',(item['href']))
        result_list = cusor.fetchone()
        #11.分词
        rzyq_fenci_list=jb_an.extract_tags(item['rzyq'],topK=5)
        
        if result_list:
            print('Data is have')
        else:
            sql = 'insert into zp_list value (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            parm = (
                zwmc_id, gsmc_id, dd_id, item['min_zwyx'], item['max_zwyx'], item['fbrq'], item['href'], zwlb_id,
                gsxz_id,
                gzjy_id, xl_id, gshy_id, gsgm_id, zwlb_big_id)
            cusor.execute(sql, parm)
            if item['zprs']=='若干':
                item['zprs']=0
            sql = 'insert into zp_list_old value (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            parm = (
                item['zwmc'], item['gsmc'], item['gzdd'], item['min_zwyx'], item['max_zwyx'], item['fbrq'],
                item['href'],
                item['zwlb'], item['gsxz'], item['gzjy'], item['zdxl'], item['rzyq'], item['gshy'], item['gsgm'],
                item['zwlb_big'])
            cusor.execute(sql, parm)
            cusor.execute('select id from zp_list where href=%s or (zwmc_id=%s and gsmc_id=%s)',
                          (item['href'], zwmc_id, gsmc_id))
            result_list = cusor.fetchone()
            list_id = result_list[0]
            sql = 'insert into zp_rzyq_fenci value (null,%s,%s,%s)'
            parm = []
            for rzyq_item in rzyq_fenci_list:
                parm.append((rzyq_item, list_id,zwlb_id))
            cusor.executemany(sql, parm)
            sql = 'insert into zp_flxx value (null,%s,%s,%s)'
            parm = []
            for flxx_item in item['flxx']:
                parm.append((flxx_item, list_id,zwlb_id))
            cusor.executemany(sql, parm)
        #大于随机数则执行插入
        if random.random()>0.7:
            self.conn.commit()
        return item
