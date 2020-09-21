# coding:utf-8
# 引入app配置
import json
import os
import traceback  # 异常处理模块
from datetime import datetime, date, timedelta

import pymysql
import utils_en as utils  # 生成验证码模块
from application import app, cache  # 引入app
from flask import render_template, request  # 读取页面
from flask import send_from_directory, session, redirect, url_for, make_response, jsonify
from gevent import monkey
from gevent.pywsgi import WSGIServer
# 在玩websockets，可以无视之哈，有空贴下flask websockets实现哈
from geventwebsocket.handler import WebSocketHandler
from pymysql import cursors
from scipy.misc import imread, imsave
from wordcloud import WordCloud

# gevent的猴子魔法
monkey.patch_all()


# 自定义缓存名
def make_cache_key():
    """Dynamic creation the request url."""

    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return path + args


# 数据库链接
def connect_mysql():
    # 建立操作游标
    # mysql_free_result();
    # cursor = connection_pool.cursor()
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='FanTan879', db='zp', charset='utf8')
    cursor = conn.cursor(cursors.SSCursor)
    return conn, cursor


# 图标
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 500
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# 首页
@app.route('/')
def index():
    return render_template('index.html')


# 地点薪资图页面(地图)
# 图表形式参考链接：http://echarts.baidu.com/demo.html#map-china-dataRange
@app.route('/zwyx/dd_index')
def zwyx_dd_view():
    return render_template('zwyx_dd.html')


# 地点和薪资
@app.route('/zwyx/dd')
@cache.cached(timeout=60*60*24*7)
def show_zwyx_dd():
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 初始化返回的字典
    returnDate = {}
    returnDate['status'] = 0
    # 查询地点和薪资的关系，职位总数，平均薪资
    sql = "select avg((zp_list.max_zwyx+zp_list.min_zwyx)/2) as avg_zwyx,zp_dd.province,zp_dd.id from zp_list inner join zp_dd on zp_dd.Id=zp_list.dd_id where province is not NULL and zp_list.min_zwyx!=0 group by province"
    # 执行sql语句
    cursor.execute(sql)
    # 取出所有结果集
    #dd_zwyx_list = cursor.fetchall()
    # 平均薪资
    avg_zwyx = {}
    # 总职位数
    count_zw = {}
    if cursor:
        # 循环遍历重新构建数据
        for value in cursor:
            # 取得地点名
            dd_name = value[1]
            # 判断平均薪资数据录入
            count_zw[dd_name] = {'name': dd_name, 'value': float(round(value[0], 2))}
        # 重新构建数据
        return_avg_zwyx = list(count_zw.values())
        # 数据汇总
        returnDate['avg_zwyx'] = return_avg_zwyx
        returnDate['status'] = 1
    # 关闭游标链接
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# 学历薪资图页面（柱状图）
# 参考链接:http://echarts.baidu.com/demo.html#bar-stack
@app.route('/zwyx/xl_index')
def zwyx_xl_view():
    return render_template('zwyx_xl.html')


# 学历和薪资
@app.route('/zwyx/xl')
@cache.cached(timeout=60*60*24*7)
def show_zwyx_xl():
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    returnDate['status'] = 0
    returnDate['data'] = {}
    # 查询地点和薪资的关系，职位总数，平均薪资
    sql = 'select count(zp_list.Id) as count_zw,avg((zp_list.max_zwyx+zp_list.min_zwyx)/2) as avg_zwyx,zp_xl.xl_name,max(max_zwyx),min(max_zwyx) from zp_list inner join zp_xl on zp_xl.Id=zp_list.xl_id where min_zwyx!=0 group by xl_id order by count_zw desc'
    # 执行sql语句
    cursor.execute(sql)
    # 取出所有结果集
    #xl_zwyx_list = cursor.fetchall()
    if cursor:
        returnDate['status'] = 1
        # 总职位数
        count_zw = []
        # 平均薪资
        avg_zw = []
        # 学历名
        xl_list = []
        # 最大薪资
        max_xz = []
        # 最小薪资
        min_xz = []
        # 循环遍历存入数据
        for item in cursor:
            count_zw.append(item[0])
            avg_zw.append(float(round(item[1], 2)))  # 精度保留2位小数
            xl_list.append(item[2])
            max_xz.append(int(item[3]))
            min_xz.append(int(item[4]))
        # 数据json化
        returnDate['count_zw'] = count_zw
        returnDate['avg_zw'] = avg_zw
        returnDate['xl_list'] = xl_list
        returnDate['max_xz'] = max_xz
        returnDate['min_xz'] = min_xz
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# 公司规模薪资图页面（饼图）
# 参考链接：http://echarts.baidu.com/demo.html#pie-roseType
@app.route('/zwyx/gsgm_index')
def zwyx_gsgm_view():
    return render_template('zwyx_gsgm.html')


# 公司规模和薪资（饼图）
@app.route('/zwyx/gsgm')
@cache.cached(timeout=60*60*24*7)
def show_zwyx_gsgm():
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    returnDate['status'] = 0
    # 查询地点和薪资的关系，职位总数，平均薪资
    sql = 'select count(zp_list.Id) as count_zw,avg((zp_list.max_zwyx+zp_list.min_zwyx)/2) as avg_zwyx,zp_gsgm.gsgm_name from zp_list inner join zp_gsgm on zp_gsgm.Id=zp_list.gsgm_id where min_zwyx!=0 group by gsgm_id order by count_zw desc'
    # 执行sql语句
    cursor.execute(sql)
    # 取出所有结果集
    #gsgm_zwyx_list = cursor.fetchall()
    if cursor:
        returnDate['status'] = 1
        # 总职位数
        count_zw = []
        # 平均薪资
        avg_zw = []
        # 公司规模名
        gsgm_list = []
        # 循环遍历存入数据
        for item in cursor:
            count_zw.append({'name': item[2], 'value': item[0]})
            avg_zw.append({'name': item[2], 'value': float(round(item[1], 2))})
            gsgm_list.append(item[2])
        returnDate['count_zw'] = count_zw
        returnDate['avg_zw'] = avg_zw
        returnDate['gsgm_list'] = gsgm_list
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# 公司性质薪资图页面（折线图）
# 参考链接：http://echarts.baidu.com/demo.html#line-marker
@app.route('/zwyx/gsxz_index')
def zwyx_gsxz_view():
    return render_template('zwyx_gsxz.html')


# 公司性质和薪资
@app.route('/zwyx/gsxz')
@cache.cached(timeout=60*60*24*7)
def show_zwyx_gsxz():
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    # 查询地点和薪资的关系，职位总数，平均薪资
    sql = 'select count(zp_list.Id) as count_zw,avg((zp_list.max_zwyx+zp_list.min_zwyx)/2) as avg_zwyx,zp_gsxz.gsxz_name,max(max_zwyx),min(min_zwyx) from zp_list inner join zp_gsxz on zp_gsxz.Id=zp_list.gsxz_id where min_zwyx!=0 group by gsxz_id order by count_zw desc'
    # 执行sql语句
    cursor.execute(sql)
    # 取出所有结果集
    #gsxz_zwyx_list = cursor.fetchall()
    if cursor:
        returnDate['status'] = 1
        # 总职位数
        count_zw = []
        # 平均薪资
        avg_zw = []
        # 公司规模名
        gsxz_list = []
        # 最大薪资
        max_xz = []
        # 最小薪资
        min_xz = []
        # 循环遍历存入数据
        for item in cursor:
            count_zw.append({'name': item[2], 'value': item[0]})
            avg_zw.append({'name': item[2], 'value': float(round(item[1], 2))})
            gsxz_list.append(item[2])
            max_xz.append(int(item[3]))
            min_xz.append(int(item[4]))
        # 数据json化
        returnDate['count_zw'] = count_zw
        returnDate['avg_zw'] = avg_zw
        returnDate['gsxz_list'] = gsxz_list
        returnDate['max_xz'] = max_xz
        returnDate['min_xz'] = min_xz
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# 经验薪资图页面（雷达图）
# 参考链接：http://echarts.baidu.com/demo.html#radar-custom
@app.route('/zwyx/jy_index')
def zwyx_jy_view():
    return render_template('zwyx_jy.html')


# 经验和薪资
@app.route('/zwyx/jy')
@cache.cached(timeout=60*60*24*7)
def show_zwyx_jy():
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    returnDate['status'] = 0
    sql = 'select count(zp_list.Id) as count_zw,avg((zp_list.max_zwyx+zp_list.min_zwyx)/2) as avg_zwyx,zp_jy.jy_name,max(max_zwyx),min(min_zwyx) from zp_list inner join zp_jy on zp_jy.Id=zp_list.jy_id where min_zwyx!=0 group by jy_id order by count_zw desc'
    # 执行sql语句
    cursor.execute(sql)
    # 取出所有结果集
    #jy_zwyx_list = cursor.fetchall()
    if cursor:
        # 总职位数
        count_zw = []
        # 平均薪资
        avg_zw = []
        # 经验分类名
        jy_list = []
        # 最大薪资
        max_xz = []
        # 最小薪资
        min_xz = []
        # 循环遍历存入数据
        returnDate['status'] = 1
        for item in cursor:
            count_zw.append(item[0])
            avg_zw.append(float(round(item[1], 2)))
            jy_list.append({'text': item[2]})
            max_xz.append(int(item[3]))
            min_xz.append(int(item[4]))
        # 数据json化
        returnDate['count_zw'] = count_zw
        returnDate['avg_zw'] = avg_zw
        returnDate['jy_list'] = jy_list
        returnDate['max_xz'] = max_xz
        returnDate['min_xz'] = min_xz
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# 职位名称薪资图页面（象形柱图）
# 参考链接：http://echarts.baidu.com/demo.html#pictorialBar-dotted
@app.route('/zwyx/zwmc_index')
def zwyx_zwmc_view():
    return render_template('zwyx_zwmc.html')


# 职位名称和薪资
@app.route('/zwyx/zwmc')
@cache.cached(timeout=60*60*24*7)
def show_zwyx_zwmc():
    returnDate={}
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    returnDate['status'] = 0
    sql = 'select count(zp_list.Id) as count_zw,avg((zp_list.max_zwyx+zp_list.min_zwyx)/2) as avg_zwyx,zp_zwlb.zwlb_name,max(max_zwyx),min(min_zwyx) from zp_list inner join zp_zwlb on zp_zwlb.Id=zp_list.zwlb_id where min_zwyx!=0 and max_zwyx!=0 and zwlb_name!="其他" group by zp_list.zwlb_id order by count(zwlb_id) desc limit 10'
    # 执行sql语句
    cursor.execute(sql)
    # 总职位数
    #count_zw = {}
    # 平均薪资
    #avg_zw = {}
    # 职位名
    zwmc_list = []
    # 最大薪资
    #max_xz = {}
    # 最小薪资
    #min_xz = {}
    #count_zw['其他'] = []
    #avg_zw['其他'] = []
    #max_xz['其他'] = 0
    #min_xz['其他'] = 0
    #zwmc_zwyx_list = cursor.fetchall()
    # 打开职位分类文本
    return_data = {}
    return_avg_zw = []
    if cursor:
        # 提取数据
        for row in cursor:
            item = row[2]
            return_data.setdefault(item, {}).setdefault('count_zw', []).append(row[0])
            return_data[item].setdefault('avg_zw', []).append(row[1])
            return_data[item].setdefault('count_zw', []).append(row[0])
            return_data[item]['max_xz'] = float(max(return_data[item].get('max_xz', 0), row[3]))
            return_data[item]['min_xz'] = float(max(return_data[item].get('min_xz', 0), row[4]))
        return_count_zw = []
        return_max_xz=[]
        return_min_xz = []
        for value in return_data:
            return_count_zw.append(sum(return_data[value]['count_zw']))
            avg_num_list = return_data[value]['avg_zw']
            return_avg_zw.append(float(round(sum(avg_num_list) / len(avg_num_list), 2)))
            zwmc_list.append(value)
            return_max_xz.append(return_data[value]['max_xz'])
            return_min_xz.append(return_data[value]['min_xz'])


        # 重新构建数据
        #return_max_xz = list(max_xz.values())
        #return_min_xz = list(min_xz.values())
        # json数据
        returnDate['status'] = 1
        returnDate['count_zw'] = return_count_zw
        returnDate['avg_zw'] = return_avg_zw
        returnDate['zwmc_list'] = list(zwmc_list)
        returnDate['max_xz'] = return_max_xz
        returnDate['min_xz'] = return_min_xz
    else:
        returnDate['status'] = 0
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# Top10最稀缺职位页面（象形柱图）
# 参考链接：http://echarts.baidu.com/demo.html#pictorialBar-dotted
@app.route('/zwyx/zwmc_last_index')
def zwyx_zwmc_last_view():
    return render_template('zwyx_zwmc_last.html')


# 职位名称和薪资
@app.route('/zwyx/zwmc_last')
@cache.cached(timeout=60 * 60 * 24 * 7)
def show_zwyx_zwmc_last():
    returnDate = {}
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    returnDate['status'] = 0
    sql = 'select count(zp_list.Id) as count_zw,avg((zp_list.max_zwyx+zp_list.min_zwyx)/2) as avg_zwyx,zp_zwlb.zwlb_name,max(max_zwyx),min(min_zwyx) from zp_list inner join zp_zwlb on zp_zwlb.Id=zp_list.zwlb_id where min_zwyx!=0 and max_zwyx!=0 group by zp_list.zwlb_id order by count(zwlb_id) asc limit 10'
    # 执行sql语句
    cursor.execute(sql)
    # 总职位数
    # count_zw = {}
    # 平均薪资
    # avg_zw = {}
    # 职位名
    zwmc_list = []
    # 最大薪资
    # max_xz = {}
    # 最小薪资
    # min_xz = {}
    # count_zw['其他'] = []
    # avg_zw['其他'] = []
    # max_xz['其他'] = 0
    # min_xz['其他'] = 0
    # zwmc_zwyx_list = cursor.fetchall()
    # 打开职位分类文本
    return_data = {}
    return_avg_zw = []
    if cursor:
        # 提取数据
        for row in cursor:
            item = row[2]
            return_data.setdefault(item, {}).setdefault('count_zw', []).append(row[0])
            return_data[item].setdefault('avg_zw', []).append(row[1])
            return_data[item].setdefault('count_zw', []).append(row[0])
            return_data[item]['max_xz'] = float(max(return_data[item].get('max_xz', 0), row[3]))
            return_data[item]['min_xz'] = float(max(return_data[item].get('min_xz', 0), row[4]))
        return_count_zw = []
        return_max_xz = []
        return_min_xz = []
        for value in return_data:
            return_count_zw.append(sum(return_data[value]['count_zw']))
            avg_num_list = return_data[value]['avg_zw']
            return_avg_zw.append(float(round(sum(avg_num_list) / len(avg_num_list), 2)))
            zwmc_list.append(value)
            return_max_xz.append(return_data[value]['max_xz'])
            return_min_xz.append(return_data[value]['min_xz'])

        # 重新构建数据
        # return_max_xz = list(max_xz.values())
        # return_min_xz = list(min_xz.values())
        # json数据
        returnDate['status'] = 1
        returnDate['count_zw'] = return_count_zw
        returnDate['avg_zw'] = return_avg_zw
        returnDate['zwmc_list'] = list(zwmc_list)
        returnDate['max_xz'] = return_max_xz
        returnDate['min_xz'] = return_min_xz
    else:
        returnDate['status'] = 0
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv

# 公司数和地点关系（散点图）
# 参考链接：http://echarts.baidu.com/demo.html#scatter-map-brush
@app.route('/dd/gsmc_index')
def dd_gsmc_view():
    return render_template('dd_gsmc.html')


# 公司数和地点
@app.route('/dd/gsmc')
@cache.cached(timeout=60*60*24*7)
def show_dd_gsmc():
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    returnDate['status'] = 0
    sql = 'select count(distinct zp_list.gsmc_id) as count_gs,zp_dd.dd_name from zp_list inner join zp_dd on zp_dd.Id=zp_list.dd_id group by zp_list.dd_id'
    # 执行sql语句
    cursor.execute(sql)
    # 公司数
    count_gs = []
    # 城市经纬度
    geoCoordMap={}
    if cursor:
        returnDate['status'] = 1
        for item in cursor:
            count_gs.append({'name': item[1], 'value': item[0]})
        returnDate['count_gs'] = count_gs
        sql_dd='select dd_name,format(pointx,2),format(pointy,2) from zp_dd where pointx>100 and pointx<999;'
        cursor.execute(sql_dd)
        for item1 in cursor:
            geoCoordMap[item1[0]]=[item1[1],item1[2]]
        returnDate['geoCoordMap'] = geoCoordMap
    else:
        returnDate['status'] = 0
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# 职位数和地点页面（热力图）
# 参考链接：http://echarts.baidu.com/demo.html#heatmap-map
@app.route('/dd/zwmc_index')
def dd_zwmc_view():
    return render_template('dd_zwmc.html')


# 职位名称和地点
@app.route('/dd/zwmc')
@cache.cached(timeout=60*60*24*7)
def show_dd_zwmc():
    # 建立链接游标
    conn, cursor = connect_mysql()
    returnDate = {}
    returnDate['status'] = 0
    sql = 'select count(distinct zp_list.zwmc_id) as count_zw,zp_dd.dd_name from zp_list inner join zp_dd on zp_dd.Id=zp_list.dd_id group by zp_list.dd_id'
    # 执行sql语句
    cursor.execute(sql)
    # 职位数
    count_zw = []
    # 城市经纬度
    geoCoordMap={}
    if cursor:
        returnDate['status'] = 1
        for item in cursor:
            count_zw.append({'name': item[1], 'value': item[0]})
        returnDate['count_zw'] = count_zw
        sql_dd='select dd_name,format(pointx,2),format(pointy,2) from zp_dd where pointx>100 and pointx<999;'
        cursor.execute(sql_dd)
        for item1 in cursor:
            geoCoordMap[item1[0]]=[item1[1],item1[2]]
        returnDate['geoCoordMap'] = geoCoordMap
    else:
        returnDate['status'] = 0
    cursor.close()
    conn.close()
    rv = json.dumps(returnDate)
    return rv


# 职位类型相关关系（综合图）
# 参考链接：http://echarts.baidu.com/demo.html#watermark
@app.route('/dd/type_index')
def dd_type_view():
    return render_template('dd_type.html')


@app.route('/zwmc/search')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def zwmc_search():
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 省份
    provinceList = []
    province_sql = 'select province from zp_dd where province!="" and pointx<200 group by province'
    cursor.execute(province_sql)
    for item in cursor:
        provinceList.append(item[0])
    # 城市
    cityList = []
    city_sql = 'select id,dd_name from zp_dd'
    cursor.execute(city_sql)
    for item in cursor:
        cityList.append({'id': item[0], 'dd_name': item[1]})
    # 公司性质
    gsxzList = []
    gsxz_sql = 'select * from zp_gsxz'
    cursor.execute(gsxz_sql)
    for item in cursor:
        gsxzList.append({'id': item[0], 'gsxz_name': item[1]})
    # 公司规模
    gsgmList = []
    gsgm_sql = 'select * from zp_gsgm'
    cursor.execute(gsgm_sql)
    for item in cursor:
        gsgmList.append({'id': item[0], 'gsgm_name': item[1]})
    # 学历
    xlList = []
    xl_sql = 'select * from zp_xl'
    cursor.execute(xl_sql)
    for item in cursor:
        xlList.append({'id': item[0], 'xl_name': item[1]})
    # 工作经验
    gzjyList = []
    gzjy_sql = 'select * from zp_gzjy'
    cursor.execute(gzjy_sql)
    for item in cursor:
        gzjyList.append({'id': item[0], 'gzjy_name': item[1]})
    # 公司行业
    gshyList = []
    gshy_sql = 'select * from zp_gshy'
    cursor.execute(gshy_sql)
    for item in cursor:
        gshyList.append({'id': item[0], 'gshy_name': item[1]})
    # 大分类
    zwlbBigList = []
    zwlb_big_sql = 'select * from zp_zwlb_big'
    cursor.execute(zwlb_big_sql)
    for item in cursor:
        zwlbBigList.append({'id': item[0], 'zwlb_big_name': item[1]})
    # 小分类
    zwlbList = []
    zwlb_sql = 'select * from zp_zwlb'
    cursor.execute(zwlb_sql)
    for item in cursor:
        zwlbList.append({'id': item[0], 'zwlb_name': item[1]})
    cursor.close()
    conn.close()
    return render_template('zw_search.html', provinces=provinceList, cities=cityList, gsxz=gsxzList, gsgm=gsgmList,
                           xl=xlList, gzjy=gzjyList, gshy=gshyList, zwlb_big=zwlbBigList, zwlb=zwlbList)


# 获取省份对应城市信息
@app.route('/get/city/list')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def city_list():
    # 省份
    # 建立链接游标
    conn, cursor = connect_mysql()
    cityList = []
    province_sql = 'select id,dd_name from zp_dd where province=%s'
    cursor.execute(province_sql, (request.args.get('province', '')))
    for item in cursor:
        cityList.append({'id': item[0], 'dd_name': item[1]})
    cursor.close()
    conn.close()
    return json.dumps(cityList)


@app.route('/get/zwlb/list')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def zwlb_list():
    # 职位分类
    # 建立链接游标
    conn, cursor = connect_mysql()
    zwlbList = []
    zwlb_sql = 'select id,zwlb_name from zp_zwlb where zwlb_big_id=%s'
    cursor.execute(zwlb_sql, (request.args.get('zwlb', '')))
    for item in cursor:
        zwlbList.append({'id': item[0], 'zwlb_name': item[1]})
    cursor.close()
    conn.close()
    return json.dumps(zwlbList)


@app.route('/zw/list')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def zw_list():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    province = request.args.get('province', '')
    dd_id = int(request.args.get('city', '0'))
    gsxz_id = int(request.args.get('gsxz', '0'))
    gsgm_id = int(request.args.get('gsgm', '0'))
    xl_id = int(request.args.get('xl', '0'))
    gzjy_id = int(request.args.get('gzjy', '0'))
    gshy_id = int(request.args.get('gshy', '0'))
    zwlb_big_id = int(request.args.get('zwlb_big', '0'))
    zwlb_id = int(request.args.get('zwlb', '0'))
    zw_list_sql = 'select zp_list.id,dd_name,gsxz_name,gsgm_name,xl_name,gzjy_name,gshy_name,zwlb_name,min_zwyx,max_zwyx,zwmc_name,gsmc_name from zp_list inner join zp_dd on zp_dd.id=zp_list.dd_id inner join zp_gsgm on zp_gsgm.id=zp_list.gsgm_id inner join zp_gsxz on zp_gsxz.id=zp_list.gsxz_id inner join zp_xl on zp_xl.id=zp_list.xl_id inner join zp_gzjy on zp_gzjy.id=zp_list.gzjy_id inner join zp_gshy on zp_gshy.id=zp_list.gshy_id inner join zp_zwlb on zp_zwlb.id=zp_list.zwlb_id inner join zp_zwmc on zp_zwmc.id=zp_list.zwmc_id inner join zp_gsmc on zp_gsmc.id=zp_list.gsmc_id '
    zw_list_count_sql = 'select count(*) from zp_list inner join zp_dd on zp_dd.id=zp_list.dd_id inner join zp_gsgm on zp_gsgm.id=zp_list.gsgm_id inner join zp_gsxz on zp_gsxz.id=zp_list.gsxz_id inner join zp_xl on zp_xl.id=zp_list.xl_id inner join zp_gzjy on zp_gzjy.id=zp_list.gzjy_id inner join zp_gshy on zp_gshy.id=zp_list.gshy_id inner join zp_zwlb on zp_zwlb.id=zp_list.zwlb_id inner join zp_zwmc on zp_zwmc.id=zp_list.zwmc_id inner join zp_gsmc on zp_gsmc.id=zp_list.gsmc_id '
    sql_list = []
    if dd_id != 0:
        sql_list.append('dd_id=' + str(dd_id))
    elif dd_id == 0 and province != '':
        sql_list.append('province="' + province + '"')
    if gsxz_id != 0:
        sql_list.append('gsxz_id=' + str(gsxz_id))
    if gsgm_id != 0:
        sql_list.append('gsgm_id=' + str(gsgm_id))
    if xl_id != 0:
        sql_list.append('xl_id=' + str(xl_id))
    if gzjy_id != 0:
        sql_list.append('gzjy_id=' + str(gzjy_id))
    if gshy_id != 0:
        sql_list.append('gshy_id=' + str(gshy_id))
    if zwlb_id != 0:
        sql_list.append('zwlb_id=' + str(zwlb_id))
    elif zwlb_id == 0 and zwlb_big_id != 0:
        sql_list.append('zp_list.zwlb_big_id=' + str(zwlb_big_id))
    if len(sql_list) > 0:
        zw_list_sql += 'where ' + ' and '.join(sql_list)
        zw_list_count_sql += 'where ' + ' and '.join(sql_list)
    zw_list_sql += ' order by id desc limit ' + str((int(page) - 1) * int(limit)) + ',' + limit
    zwList = []
    cursor.execute(zw_list_sql)
    zwCount = 0
    for item in cursor:
        # select zp_list.id,dd_name,gsxz_name,gsgm_name,xl_name,gzjy_name,gshy_name,zwlb_name,min_zwyx,max_zwyx,count(*) from zp_list
        zwItem = {'id': item[0], 'dd_name': item[1], 'gsxz_name': item[2], 'gsgm_name': item[3], 'xl_name': item[4],
                  'gzjy_name': item[5], 'gshy_name': item[6], 'zwlb_name': item[7], 'min_zwyx': item[8],
                  'max_zwyx': item[9], 'zwmc_name': item[10], 'gsmc_name': item[11]}
        zwList.append(zwItem)
    cursor.execute(zw_list_count_sql)
    for item in cursor:
        zwCount = item[0]
    cursor.close()
    conn.close()
    return json.dumps({'code': 0, 'msg': '', 'count': zwCount, 'data': zwList})


@app.route('/zp/wordcloud')
@cache.cached(timeout=60 * 60 * 24 * 7)
def zp_wordcloud():
    return render_template('zp_wordcloud.html')


@app.route('/zp/get/wordcloud')
def zp_get_wordcloud():
    conn, cursor = connect_mysql()
    try:
        cursor.execute('select flxx_name from zp_flxx')
        text = ' '.join([item[0] for item in cursor.fetchall()])
        pic_path = './static/image/b5.jpg'
        mask_image = imread(pic_path, flatten=False)
        word_pic = WordCloud(
            font_path='c:/windows/fonts/simhei.ttf',
            background_color='white',
            mask=mask_image
        ).generate(text)
        imsave('./static/image/wordcloud_result_b5.jpg', word_pic)
        return '1'
    except Exception as e:
        with open('app_info.log', 'a+') as f:
            f.write(traceback.format_exc())
        return '-1'


# 假如没有进行后台登录，则进行拦截
@app.before_request
def before_request():
    if 'admin' in request.url and 'userid' not in session and 'admin/login' not in request.url and 'admin/captcha' not in request.url:
        return redirect(url_for('admin_login'))


@app.route('/admin/captcha')
def captcha():
    # 把strs发给前端,或者在后台使用session保存
    # code_img, code_text = utils.generate_verification_code()
    code_img, code_text = utils.generate_verification_code()
    session['vercode'] = code_text
    response = make_response(code_img)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        vercode = request.form.get('vercode')
        returnData = {
            'status': 0,
            'info': '未知错误'
        }
        if vercode != session['vercode']:
            returnData['info'] = '验证码错误'
        else:
            if username == 'root' and password == 'root':
                returnData['status'] = 1
                returnData['redirect'] = url_for('admin_index')
                session['userid'] = 1
            else:
                returnData['info'] = '用户名或者密码错误 '
        return jsonify(returnData)
    return render_template('admin/login.html', title='后台登录')


@app.route('/admin/index')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_index():
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 获取职位数据总量
    cursor.execute('select count(1) from zp_list')
    total_zw_num = [item[0] for item in cursor][0]
    # 获取三天内新增的数量
    today = datetime.strptime(str(date.today()), '%Y-%m-%d')
    three_day = today + timedelta(days=-1)
    cursor.execute('select count(1) from zp_list where fbrq>%s', (three_day,))
    total_zw_num_three_day = [item[0] for item in cursor][0]
    # 获取一周内新增的数据
    seven_day = today + timedelta(days=-7)
    cursor.execute('select count(1) from zp_list where fbrq>%s', (seven_day,))
    total_zw_num_by_week = [item[0] for item in cursor][0]
    # 获取当月的新增的数量
    thirdty_day = today + timedelta(days=-30)
    cursor.execute('select count(1) from zp_list where fbrq>%s', (thirdty_day,))
    total_zw_num_by_month = [item[0] for item in cursor][0]
    return render_template('admin/index.html', title='后台首页', total_zw_num=total_zw_num,
                           total_zw_num_three_day=total_zw_num_three_day, total_zw_num_by_week=total_zw_num_by_week,
                           total_zw_num_by_month=total_zw_num_by_month)


# 根据日期获取每天的职位数据量
@app.route('/admin/get/zw/count/by/date')
@cache.cached(timeout=60 * 60 * 24 * 3)
def admin_get_zw_count_by_date():
    # 建立链接游标
    conn, cursor = connect_mysql()
    cursor.execute('select fbrq,count(1) from zp_list where fbrq!="1970-01-01"  group by fbrq')
    total_zw_num_by_month = [(item[0].strftime('%Y-%m-%d'), item[1]) for item in cursor]
    today = datetime.strptime(str(date.today()), '%Y-%m-%d')
    startValue = today + timedelta(days=-30)
    return jsonify({'zw_list': total_zw_num_by_month, 'startValue': startValue.strftime('%Y-%m-%d')})


@app.route('/admin/dd')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_dd():
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 查询省份数据
    province_sql = 'select province from zp_dd group by province'
    cursor.execute(province_sql)
    province_data = []
    for item in cursor:
        province_data.append(item[0])
    cursor.close()
    conn.close()
    return render_template('admin/dd_list.html', title='城市列表', province_list=province_data)


# 获取城市信息
@app.route('/admin/get/dd')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_dd():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    city = request.args.get('city', '')
    province = request.args.get('province', '')
    sql_list = []
    if province != '':
        sql_list.append('province="' + province + '"')
    elif city != '':
        sql_list.append('dd_name="' + city + '"')
    dd_list_sql = 'select * from zp_dd'
    if len(sql_list) > 0:
        dd_list_sql += ' where ' + ' and '.join(sql_list)
    dd_list_sql += ' limit ' + str((page - 1) * limit) + ',' + str(limit)
    cursor.execute(dd_list_sql)
    dd_data = []
    for item in cursor:
        dd_data.append({'id': item[0], 'city': item[1], 'province': item[2], 'pointx': item[3], 'pointy': item[4]})
    dd_count_sql = 'select count(1) from zp_dd'
    cursor.execute(dd_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = dd_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除城市
@app.route('/admin/del/dd')
def admin_del_dd():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_dd where id=%s', (one,))
            cursor.execute('delete from zp_list where dd_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_dd where id=%s', (id,))
            cursor.execute('delete from zp_list where dd_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改城市信息
@app.route('/admin/edit/dd/<int:dd_id>', methods=['GET', 'POST'])
def admin_edit_dd(dd_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    if request.method == 'POST':
        province = request.form.get('province', '')
        dd_name = request.form.get('dd_name', '')
        pointx = request.form.get('pointx', '')
        pointy = request.form.get('pointy', '')
        returnData = {'status': 0, 'info': ''}
        try:
            update_dd_sql = 'update zp_dd set province=%s,dd_name=%s,pointx=%s,pointy=%s where id=%s'
            update_dd_parm = (province, dd_name, pointx, pointy, dd_id)
            cursor.execute(update_dd_sql, update_dd_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
    # 查询省份数据
    province_sql = 'select province from zp_dd group by province'
    cursor.execute(province_sql)
    province_data = []
    for item in cursor:
        province_data.append(item[0])
    dd_sql = 'select * from zp_dd where id=%s'
    parm = (dd_id,)
    cursor.execute(dd_sql, parm)
    dd_info = {}
    for item in cursor:
        dd_info = {'id': item[0], 'city': item[1], 'province': item[2], 'pointx': item[3], 'pointy': item[4]}
    cursor.close()
    conn.close()
    return render_template('admin/edit_dd.html', province_list=province_data, dd_info=dd_info)


# 公司规模
@app.route('/admin/gsgm')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_gsgm():
    return render_template('admin/gsgm_list.html', title='公司规模列表')


# 获取公司规模
@app.route('/admin/get/gsgm')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_gsgm():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    gsgm_list_sql = 'select * from zp_gsgm limit ' + str((page - 1) * limit) + ',' + str(limit)
    cursor.execute(gsgm_list_sql)
    gsgm_data = []
    for item in cursor:
        gsgm_data.append({'id': item[0], 'gsgm_name': item[1]})
    gsgm_count_sql = 'select count(1) from zp_gsgm'
    cursor.execute(gsgm_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = gsgm_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除城市
@app.route('/admin/del/gsgm')
def admin_del_gsgm():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_gsgm where id=%s', (one,))
            cursor.execute('delete from zp_list where gsgm_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_gsgm where id=%s', (id,))
            cursor.execute('delete from zp_list where gsgm_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改城市信息
@app.route('/admin/edit/gsgm/<int:gsgm_id>', methods=['GET', 'POST'])
def admin_edit_gsgm(gsgm_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    if request.method == 'POST':
        gsgm_name = request.form.get('gsgm_name', '')
        returnData = {'status': 0, 'info': ''}
        try:
            update_gsgm_sql = 'update zp_gsgm set gsgm_name=%s where id=%s'
            update_gsgm_parm = (gsgm_name, gsgm_id)
            cursor.execute(update_gsgm_sql, update_gsgm_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
    # 查询省份数据
    gsgm_sql = 'select id,gsgm_name from zp_gsgm where id=%s'
    cursor.execute(gsgm_sql, (gsgm_id,))
    gsgm_info = {}
    for item in cursor:
        gsgm_info = {'id': item[0], 'gsgm_name': item[1]}
    cursor.close()
    conn.close()
    return render_template('admin/edit_gsgm.html', gsgm_info=gsgm_info)


# 公司性质
@app.route('/admin/gsxz')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_gsxz():
    return render_template('admin/gsxz_list.html', title='公司性质列表')

    # 获取公司规模


@app.route('/admin/get/gsxz')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_gsxz():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    gsxz_list_sql = 'select * from zp_gsxz limit ' + str((page - 1) * limit) + ',' + str(limit)
    cursor.execute(gsxz_list_sql)
    gsxz_data = []
    for item in cursor:
        gsxz_data.append({'id': item[0], 'gsxz_name': item[1]})
    gsxz_count_sql = 'select count(1) from zp_gsxz'
    cursor.execute(gsxz_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = gsxz_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除城市
@app.route('/admin/del/gsxz')
def admin_del_gsxz():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_gsxz where id=%s', (one,))
            cursor.execute('delete from zp_list where gsxz_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_gsxz where id=%s', (id,))
            cursor.execute('delete from zp_list where gsxz_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改城市信息
@app.route('/admin/edit/gsxz/<int:gsxz_id>', methods=['GET', 'POST'])
def admin_edit_gsxz(gsxz_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    if request.method == 'POST':
        gsxz_name = request.form.get('gsxz_name', '')
        returnData = {'status': 0, 'info': ''}
        try:
            update_gsxz_sql = 'update zp_gsxz set gsxz_name=%s where id=%s'
            update_gsxz_parm = (gsxz_name, gsxz_id)
            cursor.execute(update_gsxz_sql, update_gsxz_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
    # 查询省份数据
    gsxz_sql = 'select id,gsxz_name from zp_gsxz where id=%s'
    cursor.execute(gsxz_sql, (gsxz_id,))
    gsxz_info = {}
    for item in cursor:
        gsxz_info = {'id': item[0], 'gsxz_name': item[1]}
    cursor.close()
    conn.close()
    return render_template('admin/edit_gsxz.html', gsxz_info=gsxz_info)


# 学历
@app.route('/admin/xl')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_xl():
    return render_template('admin/xl_list.html', title='学历列表')


# 获取学历
@app.route('/admin/get/xl')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_xl():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    xl_list_sql = 'select * from zp_xl limit ' + str((page - 1) * limit) + ',' + str(limit)
    cursor.execute(xl_list_sql)
    xl_data = []
    for item in cursor:
        xl_data.append({'id': item[0], 'xl_name': item[1]})
    xl_count_sql = 'select count(1) from zp_xl'
    cursor.execute(xl_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = xl_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除学历
@app.route('/admin/del/xl')
def admin_del_xl():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_xl where id=%s', (one,))
            cursor.execute('delete from zp_list where xl_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_xl where id=%s', (id,))
            cursor.execute('delete from zp_list where xl_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改学历信息
@app.route('/admin/edit/xl/<int:xl_id>', methods=['GET', 'POST'])
def admin_edit_xl(xl_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    if request.method == 'POST':
        xl_name = request.form.get('xl_name', '')
        returnData = {'status': 0, 'info': ''}
        try:
            update_xl_sql = 'update zp_xl set xl_name=%s where id=%s'
            update_xl_parm = (xl_name, xl_id)
            cursor.execute(update_xl_sql, update_xl_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
        # 查询省份数据
    xl_sql = 'select id,xl_name from zp_xl where id=%s'
    cursor.execute(xl_sql, (xl_id,))
    xl_info = {}
    for item in cursor:
        xl_info = {'id': item[0], 'xl_name': item[1]}
    cursor.close()
    conn.close()
    return render_template('admin/edit_xl.html', xl_info=xl_info)


# 公司行业
@app.route('/admin/gshy')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_gshy():
    return render_template('admin/gshy_list.html', title='公司行业列表')


# 获取公司行业
@app.route('/admin/get/gshy')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_gshy():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    gshy_list_sql = 'select * from zp_gshy limit ' + str((page - 1) * limit) + ',' + str(limit)
    cursor.execute(gshy_list_sql)
    gshy_data = []
    for item in cursor:
        gshy_data.append({'id': item[0], 'gshy_name': item[1]})
    gshy_count_sql = 'select count(1) from zp_gshy'
    cursor.execute(gshy_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = gshy_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除公司行业
@app.route('/admin/del/gshy')
def admin_del_gshy():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_gshy where id=%s', (one,))
            cursor.execute('delete from zp_list where gshy_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_gshy where id=%s', (id,))
            cursor.execute('delete from zp_list where gshy_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改公司行业信息
@app.route('/admin/edit/gshy/<int:gshy_id>', methods=['GET', 'POST'])
def admin_edit_gshy(gshy_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    if request.method == 'POST':
        gshy_name = request.form.get('gshy_name', '')
        returnData = {'status': 0, 'info': ''}
        try:
            update_gshy_sql = 'update zp_gshy set gshy_name=%s where id=%s'
            update_gshy_parm = (gshy_name, gshy_id)
            cursor.execute(update_gshy_sql, update_gshy_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
    # 查询行业数据
    gshy_sql = 'select id,gshy_name from zp_gshy where id=%s'
    cursor.execute(gshy_sql, (gshy_id,))
    gshy_info = {}
    for item in cursor:
        gshy_info = {'id': item[0], 'gshy_name': item[1]}
    cursor.close()
    conn.close()
    return render_template('admin/edit_gshy.html', gshy_info=gshy_info)


# 职位分类
@app.route('/admin/zwlb')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_zwlb():
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 查询大分类列表
    cursor.execute('select * from zp_zwlb_big')
    zwlb_big_list = [{'id': item[0], 'zwlb_big_name': item[1]} for item in cursor]
    cursor.close()
    conn.close()
    return render_template('admin/zwlb_list.html', title='职位类别列表', zwlb_big_list=zwlb_big_list)


# 获取职位类别
@app.route('/admin/get/zwlb')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_zwlb():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    zwlb_big_id = int(request.args.get('zwlb_big_id', '0'))
    where = ''
    if zwlb_big_id != 0:
        where = 'where zwlb_big_id=' + str(zwlb_big_id)
    zwlb_list_sql = 'select zp_zwlb.id,zp_zwlb.zwlb_name,zp_zwlb_big.zwlb_big_name from zp_zwlb inner join zp_zwlb_big on zp_zwlb_big.id=zp_zwlb.zwlb_big_id ' + where + ' limit ' + str(
        (page - 1) * limit) + ',' + str(limit)
    cursor.execute(zwlb_list_sql)
    zwlb_data = []
    for item in cursor:
        zwlb_data.append({'id': item[0], 'zwlb_name': item[1], 'zwlb_big_name': item[2]})
    zwlb_count_sql = 'select count(1) from zp_zwlb ' + where
    cursor.execute(zwlb_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = zwlb_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除职位类别
@app.route('/admin/del/zwlb')
def admin_del_zwlb():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_zwlb where id=%s', (one,))
            cursor.execute('delete from zp_list where zwlb_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_zwlb where id=%s', (id,))
            cursor.execute('delete from zp_list where zwlb_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改职位类别
@app.route('/admin/edit/zwlb/<int:zwlb_id>', methods=['GET', 'POST'])
def admin_edit_zwlb(zwlb_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 查询原始数据
    zwlb_sql = 'select * from zp_zwlb where id=%s'
    cursor.execute(zwlb_sql, (zwlb_id,))
    zwlb_info = {}
    for item in cursor:
        zwlb_info = {'id': item[0], 'zwlb_name': item[1], 'zwlb_big_id': item[2]}
    if request.method == 'POST':
        zwlb_name = request.form.get('zwlb_name', zwlb_info['zwlb_name']) if request.form.get('zwlb_name', zwlb_info[
            'zwlb_name']) else zwlb_info['zwlb_name']
        zwlb_big_id = request.form.get('zwlb_big_id', zwlb_info['zwlb_big_id']) if request.form.get('zwlb_big_id',
                                                                                                    zwlb_info[
                                                                                                        'zwlb_big_id']) else \
            zwlb_info['zwlb_big_id']
        returnData = {'status': 0, 'info': ''}
        try:
            update_zwlb_sql = 'update zp_zwlb set zwlb_name=%s,zwlb_big_id=%s where id=%s'
            update_zwlb_parm = (zwlb_name, zwlb_big_id, zwlb_id)
            cursor.execute(update_zwlb_sql, update_zwlb_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
    # 查询大分类列表
    cursor.execute('select * from zp_zwlb_big')
    zwlb_big_list = [{'id': item[0], 'zwlb_big_name': item[1]} for item in cursor]
    cursor.close()
    conn.close()
    return render_template('admin/edit_zwlb.html', zwlb_info=zwlb_info, zwlb_big_list=zwlb_big_list)


# 职位大分类
@app.route('/admin/zwlb/big')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_zwlb_big():
    return render_template('admin/zwlb_big_list.html', title='职位大类别列表')


# 获取职位大类别
@app.route('/admin/get/zwlb/big')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_zwlb_big():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    zwlb_big_list_sql = 'select * from zp_zwlb_big limit ' + str((page - 1) * limit) + ',' + str(limit)
    cursor.execute(zwlb_big_list_sql)
    zwlb_big_data = []
    for item in cursor:
        zwlb_big_data.append({'id': item[0], 'zwlb_big_name': item[1]})
    zwlb_big_count_sql = 'select count(1) from zp_zwlb_big'
    cursor.execute(zwlb_big_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = zwlb_big_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除职位名称
@app.route('/admin/del/zwlb_big')
def admin_del_zwlb_big():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_zwlb_big where id=%s', (one,))
            cursor.execute('delete from zp_list where zwlb_big_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_zwlb_big where id=%s', (id,))
            cursor.execute('delete from zp_list where zwlb_big_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改职位类别
@app.route('/admin/edit/zwlb_big/<int:zwlb_big_id>', methods=['GET', 'POST'])
def admin_edit_zwlb_big(zwlb_big_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 查询原始数据
    zwlb_big_sql = 'select * from zp_zwlb_big where id=%s'
    cursor.execute(zwlb_big_sql, (zwlb_big_id,))
    zwlb_big_info = {}
    for item in cursor:
        zwlb_big_info = {'id': item[0], 'zwlb_big_name': item[1]}
    if request.method == 'POST':
        zwlb_big_name = request.form.get('zwlb_big_name', zwlb_big_info['zwlb_big_name']) if request.form.get(
            'zwlb_big_name', zwlb_big_info['zwlb_big_name']) else zwlb_big_info['zwlb_big_name']
        returnData = {'status': 0, 'info': ''}
        try:
            update_zwlb_big_sql = 'update zp_zwlb_big set zwlb_big_name=%s where id=%s'
            update_zwlb_big_parm = (zwlb_big_name, zwlb_big_id)
            cursor.execute(update_zwlb_big_sql, update_zwlb_big_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
            cursor.close()
            conn.close()
        return jsonify(returnData)
    cursor.close()
    conn.close()
    return render_template('admin/edit_zwlb_big.html', zwlb_big_info=zwlb_big_info)


# 职位名称
@app.route('/admin/zwmc')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_zwmc():
    return render_template('admin/zwmc_list.html', title='职位名称列表')


# 获取职位名称
@app.route('/admin/get/zwmc')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_zwmc():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    cursor.execute('select * from zp_zwmc limit %s,%s', ((page - 1) * limit, limit))
    zwmc_data = []
    for item in cursor:
        zwmc_data.append({'id': item[0], 'zwmc_name': item[1]})
    zwmc_count_sql = 'select count(1) from zp_zwmc'
    cursor.execute(zwmc_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = zwmc_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除职位名称
@app.route('/admin/del/zwmc')
def admin_del_zwmc():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_zwmc where id=%s', (one,))
            cursor.execute('delete from zp_list where zwmc_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_zwmc where id=%s', (id,))
            cursor.execute('delete from zp_list where zwmc_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改职位名称
@app.route('/admin/edit/zwmc/<int:zwmc_id>', methods=['GET', 'POST'])
def admin_edit_zwmc(zwmc_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 查询原始数据
    zwmc_sql = 'select * from zp_zwmc where id=%s'
    cursor.execute(zwmc_sql, (zwmc_id,))
    zwmc_info = {}
    for item in cursor:
        zwmc_info = {'id': item[0], 'zwmc_name': item[1]}
    if request.method == 'POST':
        zwmc_name = request.form.get('zwmc_name', zwmc_info['zwmc_name']) if request.form.get('zwmc_name', zwmc_info[
            'zwmc_name']) else zwmc_info['zwmc_name']
        returnData = {'status': 0, 'info': ''}
        try:
            update_zwmc_sql = 'update zp_zwmc set zwmc_name=%s where id=%s'
            update_zwmc_parm = (zwmc_name, zwmc_id)
            cursor.execute(update_zwmc_sql, update_zwmc_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
        cursor.close()
        conn.close()
        return jsonify(returnData)
    cursor.close()
    conn.close()
    return render_template('admin/edit_zwmc.html', zwmc_info=zwmc_info)


# 公司名称
@app.route('/admin/gsmc')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_gsmc():
    return render_template('admin/gsmc_list.html', title='公司名称列表')


# 获取公司名称
@app.route('/admin/get/gsmc')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_gsmc():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    cursor.execute('select * from zp_gsmc limit %s,%s', ((page - 1) * limit, limit))
    gsmc_data = []
    for item in cursor:
        gsmc_data.append({'id': item[0], 'gsmc_name': item[1]})
    gsmc_count_sql = 'select count(1) from zp_gsmc'
    cursor.execute(gsmc_count_sql)
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = gsmc_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除公司名称
@app.route('/admin/del/gsmc')
def admin_del_gsmc():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_gsmc where id=%s', (one,))
            cursor.execute('delete from zp_list where gsmc_id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_gsmc where id=%s', (id,))
            cursor.execute('delete from zp_list where gsmc_id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改公司名称
@app.route('/admin/edit/gsmc/<int:gsmc_id>', methods=['GET', 'POST'])
def admin_edit_gsmc(gsmc_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 查询原始数据
    gsmc_sql = 'select * from zp_gsmc where id=%s'
    cursor.execute(gsmc_sql, (gsmc_id,))
    gsmc_info = {}
    for item in cursor:
        gsmc_info = {'id': item[0], 'gsmc_name': item[1]}
    if request.method == 'POST':
        gsmc_name = request.form.get('gsmc_name', gsmc_info['gsmc_name']) if request.form.get('gsmc_name', gsmc_info[
            'gsmc_name']) else gsmc_info['gsmc_name']
        returnData = {'status': 0, 'info': ''}
        try:
            update_gsmc_sql = 'update zp_gsmc set gsmc_name=%s where id=%s'
            update_gsmc_parm = (gsmc_name, gsmc_id)
            cursor.execute(update_gsmc_sql, update_gsmc_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
    cursor.close()
    conn.close()
    return render_template('admin/edit_gsmc.html', gsmc_info=gsmc_info)


# 职位列表
@app.route('/admin/list')
@cache.cached(timeout=60 * 60 * 24 * 7)
def admin_list():
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 省份
    provinceList = []
    province_sql = 'select province from zp_dd where province!="" and pointx<200 group by province'
    cursor.execute(province_sql)
    for item in cursor:
        provinceList.append(item[0])
    # 城市
    cityList = []
    city_sql = 'select id,dd_name from zp_dd'
    cursor.execute(city_sql)
    for item in cursor:
        cityList.append({'id': item[0], 'dd_name': item[1]})
    # 公司性质
    gsxzList = []
    gsxz_sql = 'select * from zp_gsxz'
    cursor.execute(gsxz_sql)
    for item in cursor:
        gsxzList.append({'id': item[0], 'gsxz_name': item[1]})
    # 公司规模
    gsgmList = []
    gsgm_sql = 'select * from zp_gsgm'
    cursor.execute(gsgm_sql)
    for item in cursor:
        gsgmList.append({'id': item[0], 'gsgm_name': item[1]})
    # 学历
    xlList = []
    xl_sql = 'select * from zp_xl'
    cursor.execute(xl_sql)
    for item in cursor:
        xlList.append({'id': item[0], 'xl_name': item[1]})
    # 工作经验
    gzjyList = []
    gzjy_sql = 'select * from zp_gzjy'
    cursor.execute(gzjy_sql)
    for item in cursor:
        gzjyList.append({'id': item[0], 'gzjy_name': item[1]})
    # 公司行业
    gshyList = []
    gshy_sql = 'select * from zp_gshy'
    cursor.execute(gshy_sql)
    for item in cursor:
        gshyList.append({'id': item[0], 'gshy_name': item[1]})
    # 大分类
    zwlbBigList = []
    zwlb_big_sql = 'select * from zp_zwlb_big'
    cursor.execute(zwlb_big_sql)
    for item in cursor:
        zwlbBigList.append({'id': item[0], 'zwlb_big_name': item[1]})
    # 小分类
    zwlbList = []
    zwlb_sql = 'select * from zp_zwlb'
    cursor.execute(zwlb_sql)
    for item in cursor:
        zwlbList.append({'id': item[0], 'zwlb_name': item[1]})
    cursor.close()
    conn.close()
    return render_template('admin/zp_list.html', title='职位列表', provinces=provinceList, cities=cityList, gsxz=gsxzList,
                           gsgm=gsgmList,
                           xl=xlList, gzjy=gzjyList, gshy=gshyList, zwlb_big=zwlbBigList, zwlb=zwlbList)


# 获取职位数据
@app.route('/admin/get/list')
@cache.cached(timeout=60 * 60 * 24 * 7, key_prefix=make_cache_key)
def admin_get_list():
    # 建立链接游标
    conn, cursor = connect_mysql()
    page = int(request.args.get('page', '1'))
    limit = int(request.args.get('limit', '10'))
    province = request.args.get('province', '')
    dd_id = int(request.args.get('city', '0'))
    gsxz_id = int(request.args.get('gsxz', '0'))
    gsgm_id = int(request.args.get('gsgm', '0'))
    xl_id = int(request.args.get('xl', '0'))
    gzjy_id = int(request.args.get('gzjy', '0'))
    gshy_id = int(request.args.get('gshy', '0'))
    zwlb_big_id = int(request.args.get('zwlb_big', '0'))
    zwlb_id = int(request.args.get('zwlb', '0'))
    sql_list = []
    if dd_id != 0:
        sql_list.append('dd_id=' + str(dd_id))
    elif dd_id == 0 and province != '' and province != '0':
        sql_list.append('province="' + province + '"')
    if gsxz_id != 0:
        sql_list.append('gsxz_id=' + str(gsxz_id))
    if gsgm_id != 0:
        sql_list.append('gsgm_id=' + str(gsgm_id))
    if xl_id != 0:
        sql_list.append('xl_id=' + str(xl_id))
    if gzjy_id != 0:
        sql_list.append('gzjy_id=' + str(gzjy_id))
    if gshy_id != 0:
        sql_list.append('gshy_id=' + str(gshy_id))
    if zwlb_id != 0:
        sql_list.append('zwlb_id=' + str(zwlb_id))
    elif zwlb_id == 0 and zwlb_big_id != 0:
        sql_list.append('zp_list.zwlb_big_id=' + str(zwlb_big_id))
    zp_list_sql = 'select {} from zp_list inner join zp_dd on zp_dd.id=zp_list.dd_id inner join zp_gsgm on zp_gsgm.id=zp_list.gsgm_id inner join zp_gsxz on zp_gsxz.id=zp_list.gsxz_id inner join zp_xl on zp_xl.id=zp_list.xl_id inner join zp_gzjy on zp_gzjy.id=zp_list.gzjy_id inner join zp_gshy on zp_gshy.id=zp_list.gshy_id inner join zp_zwlb on zp_zwlb.id=zp_list.zwlb_id inner join zp_zwmc on zp_zwmc.id=zp_list.zwmc_id inner join zp_zwlb_big on zp_zwlb_big.id=zp_list.zwlb_big_id inner join zp_gsmc on zp_gsmc.id=zp_list.gsmc_id'
    if len(sql_list) > 0:
        zp_list_sql += ' where ' + ' and '.join(sql_list)
    cursor.execute(zp_list_sql.format(
        'zp_list.id,dd_name,gsxz_name,gsgm_name,xl_name,gzjy_name,gshy_name,zwlb_name,zwlb_big_name,min_zwyx,max_zwyx,zwmc_name,gsmc_name') + ' limit %s,%s',
                   ((page - 1) * limit, limit))
    list_data = []
    for item in cursor:
        list_data.append(
            {'id': item[0], 'dd_name': item[1], 'gsxz_name': item[2], 'gsgm_name': item[3], 'xl_name': item[4],
             'gzjy_name': item[5], 'gshy_name': item[6], 'zwlb_name': item[7], 'zwlb_big_name': item[8],
             'min_zwyx': item[9], 'max_zwyx': item[10], 'zwmc_name': item[11], 'gsmc_name': item[12]})
    cursor.execute(zp_list_sql.format('count(*)'))
    list_count = 0
    for item in cursor:
        list_count = item[0]
    returnData = {}
    returnData['code'] = 0
    returnData['count'] = list_count
    returnData['data'] = list_data
    returnData['msg'] = ''
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 删除公司名称
@app.route('/admin/del/list')
def admin_del_list():
    # 建立链接游标
    conn, cursor = connect_mysql()
    ids = request.args.get('ids', [])
    id = int(request.args.get('id', '0'))
    returnData = {'status': 0, 'info': ''}
    try:
        for one in ids:
            cursor.execute('delete from zp_list where id=%s', (one,))
        if id != 0:
            cursor.execute('delete from zp_list where id=%s', (id,))
        conn.commit()
        returnData['status'] = 1
    except Exception as e:
        returnData['info'] = '数据异常'
    cursor.close()
    conn.close()
    return jsonify(returnData)


# 修改公司名称
@app.route('/admin/edit/list/<int:list_id>', methods=['GET', 'POST'])
def admin_edit_list(list_id):
    # 建立链接游标
    conn, cursor = connect_mysql()
    # 查询原始数据
    list_sql = 'select zp_list.id,zp_zwmc.zwmc_name,zp_gsmc.gsmc_name,min_zwyx,max_zwyx,dd_id,fbrq,gsxz_id,gzjy_id,xl_id,zprs,zwlb_id,zwlb_big_id,gsgm_id,gshy_id,href from zp_list inner join zp_zwmc on zp_zwmc.id=zp_list.zwmc_id inner join zp_gsmc on zp_gsmc.id=zp_list.gsmc_id where zp_list.id=%s'
    cursor.execute(list_sql, (list_id,))
    list_info = {}
    for item in cursor:
        list_info = {'id': item[0], 'zwmc_name': item[1], 'gsmc_name': item[2], 'min_zwyx': item[3],
                     'max_zwyx': item[4], 'dd_id': item[5], 'fbrq': item[6], 'gsxz_id': item[7], 'gzjy_id': item[8],
                     'xl_id': item[9], 'zprs': item[10], 'zwlb_id': item[11], 'zwlb_big_id': item[12],
                     'gsgm_id': item[13], 'gshy_id': item[14], 'href': item[15]}
    if request.method == 'POST':
        min_zwyx = float(request.form.get('min_zwyx', '0.0'))
        min_zwyx = min_zwyx if min_zwyx != 0.0 else list_info['min_zwyx']
        max_zwyx = float(request.form.get('max_zwyx', '0.0'))
        max_zwyx = max_zwyx if max_zwyx else list_info['max_zwyx']
        dd_id = int(request.form.get('dd_id', '0'))
        dd_id = dd_id if dd_id else list_info['dd_id']
        fbrq = request.form.get('fbrq', '')
        fbrq = fbrq if fbrq else list_info['fbrq']
        gsxz_id = int(request.form.get('gsxz', '0'))
        gsxz_id = gsxz_id if gsxz_id else list_info['gsxz_id']
        gzjy_id = int(request.form.get('gzjy_id', '0'))
        gzjy_id = gzjy_id if gzjy_id else list_info['gzjy_id']
        xl_id = int(request.form.get('xl_id', '0'))
        xl_id = xl_id if xl_id else list_info['xl_id']
        zprs = int(request.form.get('zprs', '0'))
        zprs = zprs if zprs else list_info['zprs']
        zwlb_id = int(request.form.get('zwlb_id', '0'))
        zwlb_id = zwlb_id if zwlb_id else list_info['zwlb_id']
        zwlb_big_id = int(request.form.get('zwlb_big_id', '0'))
        zwlb_big_id = zwlb_big_id if zwlb_big_id else list_info['zwlb_big_id']
        gsgm_id = int(request.form.get('gsgm_id', '0'))
        gsgm_id = gsgm_id if gsgm_id else list_info['gsgm_id']
        gshy_id = int(request.form.get('gshy_id', '0'))
        gshy_id = gshy_id if gshy_id else list_info['gshy_id']
        returnData = {'status': 0, 'info': ''}
        try:
            update_list_sql = 'update zp_list set min_zwyx=%s,max_zwyx=%s,dd_id=%s,fbrq=%s,gsxz_id=%s,gzjy_id=%s,xl_id=%s,zprs=%s,zwlb_id=%s,zwlb_big_id=%s,gsgm_id=%s,gshy_id=%s where id=%s'
            update_list_parm = (
                min_zwyx, max_zwyx, dd_id, fbrq, gsxz_id, gzjy_id, xl_id, zprs, zwlb_id, zwlb_big_id, gsgm_id, gshy_id)
            cursor.execute(update_list_sql, update_list_parm)
            conn.commit()
            returnData['status'] = 1
        except Exception as e:
            print(e)
            returnData['info'] = '异常数据'
        cursor.close()
        conn.close()
        return jsonify(returnData)
    # 城市
    cityList = []
    city_sql = 'select id,dd_name from zp_dd'
    cursor.execute(city_sql)
    for item in cursor:
        cityList.append({'id': item[0], 'dd_name': item[1]})
    # 公司性质
    gsxzList = []
    gsxz_sql = 'select * from zp_gsxz'
    cursor.execute(gsxz_sql)
    for item in cursor:
        gsxzList.append({'id': item[0], 'gsxz_name': item[1]})
    # 公司规模
    gsgmList = []
    gsgm_sql = 'select * from zp_gsgm'
    cursor.execute(gsgm_sql)
    for item in cursor:
        gsgmList.append({'id': item[0], 'gsgm_name': item[1]})
    # 学历
    xlList = []
    xl_sql = 'select * from zp_xl'
    cursor.execute(xl_sql)
    for item in cursor:
        xlList.append({'id': item[0], 'xl_name': item[1]})
    # 工作经验
    gzjyList = []
    gzjy_sql = 'select * from zp_gzjy'
    cursor.execute(gzjy_sql)
    for item in cursor:
        gzjyList.append({'id': item[0], 'gzjy_name': item[1]})
    # 公司行业
    gshyList = []
    gshy_sql = 'select * from zp_gshy'
    cursor.execute(gshy_sql)
    for item in cursor:
        gshyList.append({'id': item[0], 'gshy_name': item[1]})
    # 大分类
    zwlbBigList = []
    zwlb_big_sql = 'select * from zp_zwlb_big'
    cursor.execute(zwlb_big_sql)
    for item in cursor:
        zwlbBigList.append({'id': item[0], 'zwlb_big_name': item[1]})
    # 小分类
    zwlbList = []
    zwlb_sql = 'select * from zp_zwlb'
    cursor.execute(zwlb_sql)
    for item in cursor:
        zwlbList.append({'id': item[0], 'zwlb_name': item[1]})
    cursor.close()
    conn.close()
    return render_template('admin/edit_list.html', list_info=list_info, cities=cityList, gsxz=gsxzList, gsgm=gsgmList,
                           xl=xlList, gzjy=gzjyList, gshy=gshyList, zwlb_big=zwlbBigList, zwlb=zwlbList)

# 入口
if __name__ == '__main__':
    # 调试模式
    #app.debug = True
    # 外部可访问的服务器
    WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler).serve_forever()
