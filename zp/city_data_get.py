import json

import pymysql
import requests

# 1.查询数据库，获取城市名称
conn=pymysql.connect(host='127.0.0.1',user='root',password='FanTan879',db='zp',charset='utf8')
cursor=conn.cursor()
cursor.execute('select dd_name from zp_dd group by dd_name')
result=cursor.fetchall()
for city in result:
    # 2.拼接查询链接
    if city[0]:
        url='http://apis.map.qq.com/jsapi?qt=poi&wd={}&pn=0&rn=10&rich_source=qipao&rich=web&nj=0&c=1&key=FBOBZ-VODWU-C7SVF-B2BDI-UK3JE-YBFUS&output=jsonp&pf=jsapi&ref=jsapi&cb=qq.maps._svcb3.search_service_0'.format(city)
        # 执行URL查询
        response=requests.get(url).text
        json_text=response.strip('qq.maps._svcb3.search_service_0 && qq.maps._svcb3.search_service_0()')
        #print(json_text)
        json_dict=json.loads(json_text)
        pointx=json_dict['detail']['city'].get('pointx','')
        pointy=json_dict['detail']['city'].get('pointy','')
        cname=json_dict['detail'].get('parent',{}).get('cname','')
        if cname=='中国':
            cname=city[0]
        elif cname=='':
            url = 'https://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=s&da_src=searchBox.button&wd=' + \
                  city[
                      0] + '县' + '&c=2784&src=0&wd2=&pn=0&sug=0&l=11&b=(12358860.848516092,3428616.78898689;12562720.727419548,3528317.0110131116)&from=webmap&biz_forward={%22scaler%22:1,%22styles%22:%22pl%22}&sug_forward=&tn=B_NORMAL_MAP&nn=0&u_loc=13518834,3633392&ie=utf-8&t=1528119982145'
            response = requests.get(url).text
            json_dict = json.loads(response)
            geo_list = json_dict['current_city']['geo'].split('|')
            pointx = float(geo_list[-1].split(',')[0]) / 100000
            pointy = float(geo_list[-1].split(',')[1]) / 100000
            cname=json_dict['current_city']['up_province_name']

        cname=cname.strip('壮族回族维吾尔市省自治区')
        if cname=='上海':
            cname=city[0]
        # 更新数据库记录
        update_sql='update zp_dd set pointx=%s,pointy=%s,province=%s where dd_name=%s'
        update_parm=(pointx,pointy,cname,city[0])
        print(update_parm)
        cursor.execute(update_sql,update_parm)
        conn.commit()