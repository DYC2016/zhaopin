import pymysql
conn = pymysql.connect(host='47.104.82.16', user='root', passwd='FanTan879', db='zw_spider', charset='utf8')
cursor=conn.cursor()
with open('userdict_01.txt',encoding='utf-8') as f:
    words = f.readlines()
    cursor.executemany('insert into zp_jieba_word_dict value (NULL,%s)',words)
    conn.commit()
cursor.close()
conn.close()