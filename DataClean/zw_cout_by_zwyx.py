# -*- encoding=utf-8 -*- 
# 薪水的职位量分布
from models import *
from sqlalchemy import extract,func
# 读取zp_item数据
session=DBSession()
zp_data=session.query(extract('year',ZpItemModel.fbrq),extract('month',ZpItemModel.fbrq),ZpItemModel.zwlb_big, func.count('*'),ZpItemModel.min_zwyx,ZpItemModel.max_zwyx,ZpItemModel.zwyx).group_by(extract('year',ZpItemModel.fbrq),extract('month',ZpItemModel.fbrq),ZpItemModel.zwlb_big,ZpItemModel.zwyx).all()
for item in zp_data:
    zw_data=session.query(ZwCountByZwyx).filter_by(year=item[0],month=item[1],zwlb=item[2],zwyx=item[6]).all()
    if len(zw_data)!=0:
        obj=zw_data[0]
    else:
        obj=ZwCountByZwyx()
    obj.year=item[0]
    obj.month=item[1]
    obj.zwlb=item[2]
    obj.count=item[3]
    obj.min_zwyx=item[4]
    obj.max_zwyx=item[5]
    obj.zwyx=item[6]
    session.add(obj)
    session.commit()