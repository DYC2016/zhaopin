# -*- encoding=utf-8 -*- 
# 任职要求生成职位分类
from models import *
from sqlalchemy import extract,func,or_,and_
import requests
import time
from lxml import etree
import random
# 读取zp_item数据
session=DBSession()
headers={
    'Cookie':'user_trace_token=20181107135533-276d29e1-baa0-46ee-831e-847f535a7963; LGUID=20181107135534-be68254d-e251-11e8-8fa1-525400f775ce; UM_distinctid=166ecbd7ea3ab9-058c9e594de2d5-2464751f-1fa400-166ecbd7ea4907; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22166ecc13302177-0776c8bfc92093-2464751f-2073600-166ecc13303309%22%2C%22%24device_id%22%3A%22166ecc13302177-0776c8bfc92093-2464751f-2073600-166ecc13303309%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; LG_LOGIN_USER_ID=96924a2de151b148ff9ba44f7f1f894e607cd303dd705023ac7054d389c7c7c9; index_location_city=%E4%B8%8A%E6%B5%B7; utm_source=m_cf_seo_ald_wap; JSESSIONID=ABAAABAAAGGABCB59317CA0CCE1D9566E57626B8BEDC167; PRE_UTM=m_cf_seo_ald_zhw; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2F5307913.html%3Futm_source%3Dm_cf_seo_ald_zhw; _putrc=BAD00814459D1306123F89F2B170EADC; login=true; unick=%E8%8C%83%E5%BF%97%E4%BF%8A; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; gate_login_token=cae8d9f36ecead63238d777d8e017cdf60958ac99ce60b35ab025997e5090c03; _gid=GA1.2.1219494535.1547435113; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1546600833,1547435112,1547442707,1547519161; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1547519163; _ga=GA1.2.402531303.1541570133; LGSID=20190115102601-e69c2d2f-186c-11e9-b66c-5254005c3644; LGRID=20190115102603-e802e473-186c-11e9-b0fe-525400f775ce; CNZZDATA1256793290=173743419-1541569289-%7C1547515639',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}
num=0
while True:
    print(num)
    zp_data=session.query(ZpItemModel).filter(ZpItemModel.source=='拉勾网',ZpItemModel.flxx==None).limit(10).offset(num).all()
    if zp_data:
        for item in zp_data:
            time.sleep(random.randint(0,10))
            url=item.href
            print(url)
            headers['Referer']=url
            headers['Host']='www.lagou.com'
            res = requests.get(url, headers=headers)
            res_html = res.content.decode('utf-8')
            sel = etree.HTML(res_html)
            flxx = sel.xpath('//dd[@class="job-advantage"]/p/text()')
            if flxx:
                flxx_info = flxx[0].replace('\n', ',')
                item.flxx=flxx
                session.add(item)
            else:
                print('信息不存在')
                print(res.url)
                if res.url == url:
                    pass
                    num += 1
                continue
            session.commit()
        time.sleep(10)
    else:
        break
while True:
    zp_data=session.query(ZpItemModel).filter(or_(ZpItemModel.min_zwyx==None,and_(ZpItemModel.min_zwyx==0,ZpItemModel.zwyx!='面议')).limit(1000)).all()
    if zp_data:
        for item in zp_data:
            zwyx=item.zwyx
            print(zwyx)
            min_zwyx=max_zwyx=0
            if '元' in zwyx:
                zwyx_list=zwyx[:-1].split('-')
                if len(zwyx_list)>2:
                    min_zwyx=zwyx_list[0]
                    max_zwyx=zwyx_list[1]
                else:
                    min_zwyx=max_zwyx=zwyx_list[0]
            elif 'K' in zwyx:
                zwyx_list=zwyx[:-1].replace('K','').split('-')
                if len(zwyx_list)>2:
                    min_zwyx=str(zwyx_list[0])+'000'
                    max_zwyx=str(zwyx_list[1])+'000'
                else:
                    min_zwyx=max_zwyx=zwyx_list[0]
            item.min_zwyx=min_zwyx
            item.max_zwyx=max_zwyx
            session.add(item)
            session.commit()
    else:
        break