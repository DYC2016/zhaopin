import pymysql
from pymysql import cursors
from datetime import datetime
import jieba.analyse as anls
from collections import Counter
import jieba
def get_category():
    cursor=conn.cursor()
    cursor.execute('select category,words from zp_category')
    zwlb_dict={item[0]:item[1].split(',') for item in cursor.fetchall()}
    return zwlb_dict
def get_zp_data(zwlb_dict):
    cursor=conn.cursor()
    cursor.execute('truncate table zp_zw_by_area')
    cursor.execute('truncate table zp_zw_by_gshy')
    cursor.execute('truncate table zp_zw_by_gsxz')
    cursor.execute('truncate table zp_zw_by_xl')
    cursor.execute('truncate table zp_zw_by_gsgm')
    cursor.execute('truncate table zp_zw_by_zwyx')
    cursor.execute('truncate table zp_zw_by_type')
    for item in zwlb_dict:
        update_sql='update zp_item set category="{}" where {} and (category is null or category="")'.format(item,' or '.join(['zwmc like "%%{}%%"'.format(text) for text in zwlb_dict[item]]))
        print(update_sql)
        cursor.execute(update_sql)
        conn.commit()
        for i in range(1,month+1):
            # 职位薪资、职位量与地点关系
            sql='insert into zp_zw_by_area select NULL,min(min_zwyx),max(max_zwyx),province,pointx,pointy,count(*),"{0}",year(fbrq),month(fbrq),sum(zprs) from zp_item where category="{0}" and year(fbrq)=%s and month(fbrq)=%s and province is not null and pointx>0 and pointx<200 group by province'.format(item)
            cursor.execute(sql,(year,i))

            # 职位薪资、职位量与公司行业关系
            sql = 'insert into zp_zw_by_gshy select NULL,min(min_zwyx),max(max_zwyx),gshy,count(*),"{0}",year(fbrq),month(fbrq),sum(zprs) from zp_item where category="{0}" and year(fbrq)=%s and month(fbrq)=%s and min_zwyx!=0 and min_zwyx!=0 group by gshy'.format(item)
            cursor.execute(sql, (year, i))

            # 职位薪资、职位量与公司性质关系
            sql = 'insert into zp_zw_by_gsxz select NULL,min(min_zwyx),max(max_zwyx),gsxz,count(*),"{0}",year(fbrq),month(fbrq),sum(zprs) from zp_item where category="{0}" and year(fbrq)=%s and month(fbrq)=%s and min_zwyx!=0 group by gsxz'.format(item)
            cursor.execute(sql, (year, i))

            # 职位薪资、职位量与学历关系
            sql = 'insert into zp_zw_by_xl select NULL,min(min_zwyx),max(max_zwyx),xl,count(*),"{0}",year(fbrq),month(fbrq),sum(zprs) from zp_item where category="{0}" and year(fbrq)=%s and month(fbrq)=%s and min_zwyx!=0 group by xl'.format(item)
            cursor.execute(sql, (year, i))

            # 职位薪资、职位量与公司规模关系
            sql = 'insert into zp_zw_by_gsgm select NULL,min(min_zwyx),max(max_zwyx),gsgm,count(*),"{0}",year(fbrq),month(fbrq),sum(zprs) from zp_item where category="{0}" and year(fbrq)=%s and month(fbrq)=%s and min_zwyx!=0 group by gsgm '.format(item)
            cursor.execute(sql, (year, i))

            # 职位量与薪资关系
            sql = 'insert into zp_zw_by_zwyx select NULL,zwyx,min(min_zwyx),max(max_zwyx),count(*),"{0}",year(fbrq),month(fbrq),sum(zprs) from zp_item where category="{0}" and year(fbrq)=%s and month(fbrq)=%s and min_zwyx!=0 group by zwyx'.format(item)
            cursor.execute(sql, (year, i))

            # 职位类型与薪资关系
            sql = 'insert into zp_zw_by_type select NULL,min(min_zwyx),max(max_zwyx),type,count(*),"{0}",year(fbrq),month(fbrq),sum(zprs) from zp_item where category="{0}" and year(fbrq)=%s and month(fbrq)=%s and min_zwyx!=0 group by type '.format(item)
            cursor.execute(sql, (year, i))
            conn.commit()

def import_jb_library():
    """
    导入 mysql 标签库
    :return:
    """
    cursor=conn.cursor()
    cursor.execute('select word from zp_jieba_word_dict')
    result=cursor.fetchall()
    [jieba.add_word(item[0]) for item in result]
# 岗位需求分析
def gwxz_anls():
    cursor2=conn.cursor(cursors.SSCursor)
    cursor2.execute("select rzyq,year(fbrq),month(fbrq),category from zp_item where rzyq!='' and category is not NULL and category!=''")
    import_jb_library()
    result_list=[[*anls.textrank(result[0],topK=10),str(result[-3]),str(result[-2]),str(result[-1])] for result in cursor2]
    result_dict={}
    for i in result_list:
        if len(i)>3:
            key='_'.join(i[-3:])
            result_dict[key]=result_dict.get(key,[])
            result_dict[key].extend(i[:-3])
    cursor2.close()
    cursor=conn.cursor()
    cursor.execute('truncate table zp_word_by_zwlb')
    # 数据插入
    sql='insert into zp_word_by_zwlb value (NULL,%s,%s,%s,%s,%s)'
    for k,v in result_dict.items():
        words=Counter(result_dict[k]).most_common()
        key=k.split('_')
        year=key[0]
        month=key[1]
        category=key[2]
        parm_list=[(num,category,year,month,word)for (word,num) in words]
        cursor.executemany(sql,parm_list)
        conn.commit()
    cursor.close()
    conn.close()
if __name__ == '__main__':
    conn = pymysql.connect(host='47.104.82.16', user='root', passwd='FanTan879', db='zw_spider', charset='utf8')
    date_time = datetime.now()
    year = date_time.year
    month = date_time.month
    date = datetime.now()
    # 生成各项报表
    #get_zp_data(get_category())
    # 生成岗位职责分词
    gwxz_anls()