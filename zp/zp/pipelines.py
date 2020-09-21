# -*- coding: utf-8 -*-
<<<<<<< HEAD
from scrapy.exceptions import DropItem
import jieba.analyse as jb_an
from zp.zw_model import DB_Util,Zp
import json
import requests
import time
import redis
import re
from scrapy.exceptions import DropItem
from zp.base_model import DB_Util, DD, Zwmc, Gsmc, Zwlb, ZwlbBig, Gshy, Gsxz, Gzjy, Xl, Gsgm, List, ListOld, Flxx, \
    engine
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#数据清洗
class DataCleanPipeline(object):
    def process_item(self,item,spider):
        #去除职位名称和公司名称的数据的两端空格
        item['zwmc']=item['zwmc'].strip()
        item['gsmc'] = item['gsmc'].strip()
        if item['zwmc']=='' or item['xl']=='' or item['dd']=='' or item['gsmc']=='':
            #如果数据为空，那么返回DropItem,传递的文本信息任意
            raise DropItem('The position has failed')
        if item['gsxz']=='':
            item['gsxz']='其它'
        if item['min_zwyx']=='' or item['max_zwyx']=='':
            item['min_zwyx']=item['max_zwyx']=0
        if item['gzjy']=='':
            item['gzjy']='不限' 
        if item['gsgm']=='':
            item['gsgm']='其他'
        if item['gshy']=='' or item['gshy']==None:
            item['gshy']='其他'
        if item.get('zprs','')=='' or item['zprs']=='若干':
            item['zprs']=0
        re_com=re.compile('\(.*?\)')
        item['gshy'] = re_com.sub('',item['gshy'].split(',')[0].split('|')[0].split()[0].split('、')[0].split('/')[0])
        item['flxx']='|'.join(item['flxx'])
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
        pool = redis.ConnectionPool(host='47.104.82.16',password='FanTan879425', port=6379)
        self.conn = redis.Redis(connection_pool=pool)
    def process_item(self,item,spider):
        if item['zwmc']=='' or item['gsmc']=='' or item['gsmc']==None or item['zwlb']=='' or self.conn.sismember('zwmc_gsmc_zwlb',item['zwmc']+'_'+item['gsmc']+'_'+item['zwlb']):
            #如果存在这样的数据组合，那么表示职位数据已经存在
            #返回异常
            raise DropItem('Duplicate item found %s'%item)
        else:
            #数据组合添加到集合内
            self.conn.sadd('zwmc_gsmc_zwlb',item['zwmc']+'_'+item['gsmc']+'_'+item['zwlb'])
            return item
# 数据存储
class ZpMysqlPipeline(object):
    def open_spider(self, spider):
        DB_Util.init_db()  # 表不存在时候,初始化表结构

    def process_item(self, item, spider):
        session = DB_Util.get_session()
        zp = Zp(**item)
        session.add(zp)
        session.commit()
        return item
# 地点信息添加
class DdAddPipeline(object):
    def process_item(self,items,spider):
        dd_url = 'https://apis.map.qq.com/jsapi?qt=poi&wd={}&pn=0&rn=10&rich_source=qipao&rich=web&nj=0&c=1&key=FBOBZ-VODWU-C7SVF-B2BDI-UK3JE-YBFUS&pf=jsapi&ref=jsapi&cb=qq.maps._svcb3.search_service_0'.format(items['dd'])
        headers1={
            'Cookie':'_ga=GA1.2.285526489.1550120561; pgv_pvi=1174981632; UM_distinctid=169386a0f8f64f-0b685090d66d1e-2464751f-1fa400-169386a0f90648; pgv_pvid=2994191362; ptui_loginuin=1009137312; RK=UFIZvll4dP; ptcz=d40c3343b27988f0af911b7d8418e1a96688f313d3db901c44ccb2eee980fd44',
            'Host':'apis.map.qq.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/5.0 Chrome/47.0.2526.73 Safari/537.36'
        }
        json_text = json.loads(requests.get(dd_url,headers=headers1).text)
        try:
            # 经纬度
            items['pointx'] = json_text['detail']['city']['pointx']
            items['pointy'] = json_text['detail']['city']['pointy']
        except Exception as e:
            raise DropItem('dd url:{}'.format(dd_url))
            
        path = json_text['detail']['city']['path']
        if len(path) > 1:
            items['province'] = path[-2]['cname'].strip('省市')
        else:
            url = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd={}&c=2581&src=0&wd2=&pn=0&sug=0&l=9&b=(13282586.275849119,3475009.146650934;13507068.5169812,3831430.4533490525)&from=webma&sug_forward=&auth=5TQcN9D6b89yWFBfUCaMNQc4O42v8aaGuxHENLEBTTztBnlQADZZzy1uVt1GgvPUDZYOYIZuVt1cv3uVtGccZcuVtPWv3Guzt7xjhN%40ThwzBDGJ4P6VWvcEWe1GD8zv7u%40ZPuVteuztghxehwzJGP4GDVz4vtx77IXHhBaIWKvADJzEjjg2J&device_ratio=1&tn=B_NORMAL_MAP&nn=0&u_loc=13529785,3640331&ie=utf-8&t=1547643990801'.format(items['dd'])
            headers2={
                'Cookie':'BAIDUID=14D48E4640AE58978871452B00E74EE5:FG=1; BIDUPSID=14D48E4640AE58978871452B00E74EE5; PSTM=1540891879; __cfduid=deb1ee0b916274d09c1462c2f703b53f31544064787; routeiconclicked=1; BDUSS=VFveXlCdUN3WHpwM1A0dW5EVm8tVzl5OVJQcWlsVVBqOHhLMVN-d2RGR01ibWRjQVFBQUFBJCQAAAAAAAAAAAEAAAC7htcGZmFuZnpqAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIzhP1yM4T9cS; UM_distinctid=168599c75ee9a3-04caff6c2a690e-2464751f-1fa400-168599c75f1a5a; BDRCVFR[T6vU1RAZ_Ds]=mk3SLVN4HKm; delPer=0; PSINO=3; H_PS_PSSID=1449_21122_28328_28131_28267_22075; M_LG_UID=114788027; M_LG_SALT=4f5bc1b91633d1ea6152f9e58bbc838e; MCITY=-%3A; CNZZDATA1256793290=1995238011-1541045435-%7C1547691556',
                'Host':'map.baidu.com',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/5.0 Chrome/47.0.2526.73 Safari/537.36'
            }
            json_text2 = json.loads(requests.get(url,headers=headers2).text)
            point = json_text2['content']['ext']['detail_info']['point']
            items['pointx'] = str(point['x'])[:-5] + '.' + str(point['x'])[-5:]
            items['pointy'] = str(point['y'])[:-5] + '.' + str(point['y'])[-5:]
            items['province'] = json_text2['content']['ext']['detail_info']['poi_address'].split('省')[0]
        return items
