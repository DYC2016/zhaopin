# -*- encoding=utf-8 -*- 
# 任职要求生成职位分类
from models import *
from sqlalchemy import extract,func,or_
import jieba
from jieba.analyse import extract_tags
# 读取zp_item数据
session=DBSession()
zp_data=session.query(ZpItemModel).filter(or_(ZpItemModel.min_zwyx==None,ZpItemModel.min_zwyx==0)).all()
for item in zp_data:
    fc_list=extract_tags(item.rzyq, topK=20, withWeight=True, allowPOS=('n','nt','nz','x'))
    if '大数据' in fc_list or 'hadoop' in fc_list or 'mapreduce' in fc_list or 'zokkeeper' in fc_list or 'flume' in fc_list or 'spark' in fc_list or 'kafka' in fc_list or '大数据' in item.zwmc:
        category='大数据'
    elif '数据分析' in fc_list or 'excel' in fc_list or 'mysql' in fc_list or 'tableau' in fc_list or 'power' in fc_list or 'spss' in fc_list or 'sas' in fc_list or 'python' in fc_list or '数据分析' in item.zwmc or '数据挖掘' in item.zwmc:
        category='数据分析'
    

