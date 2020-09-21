from sqlalchemy import Column, String, create_engine,Integer,Date,Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()
engine=create_engine('mysql+pymysql://root:FanTan879@127.0.0.1/zw_spider?charset=utf8')
    # 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
class ZpItemModel(Base):
    __tablename__='zp_item'

    id = Column(Integer, primary_key=True)
    zwmc=Column(String(255))
    gsmc = Column(String(255))
    zwyx = Column(String(255))
    min_zwyx = Column(Integer)
    max_zwyx = Column(Integer)
    dd = Column(String(255))
    fbrq = Column(String(255))
    gsxz=Column(String(255))
    gzjy = Column(String(255))
    xl = Column(String(255))
    zwlb= Column(String(255))
    gsgm= Column(String(255))
    gshy= Column(String(255))
    rzyq= Column(Text)
    href= Column(String(255))
    zwlb_big= Column(String(255))
    zprs= Column(Integer)
    province= Column(String(255))
    pointx= Column(String(255))
    pointy= Column(String(255))
    source= Column(String(255))
    category=Column(String(255))# 分类
    flxx=Column(String(255))# 分类

# 分地域职位量分布
class ZwCountByArea(Base):
    __tablename__ = 'zp_zw_count_by_area'

    id = Column(Integer, primary_key=True)
    province = Column(String(255))
    pointx = Column(String(255))
    pointy = Column(String(255))
    count=Column(Integer)
    year = Column(Integer)
    month = Column(Integer)
    zwlb=Column(String(255))

# 分地域职位薪资分布
class ZwyxByArea(Base):
    __tablename__ = 'zp_zwyx_by_area'

    id = Column(Integer, primary_key=True)
    province = Column(String(255))
    pointx = Column(String(255))
    pointy = Column(String(255))
    min_zwyx = Column(Integer)
    max_zwyx=Column(Integer)
    year = Column(Integer)
    month = Column(Integer)
    zwlb=Column(String(255))

# 职位量薪水分布
class ZwCountByZwyx(Base):
    __tablename__ = 'zp_zw_count_by_zwyx'

    id = Column(Integer, primary_key=True)
    count=Column(Integer)
    zwyx = Column(String(255))
    min_zwyx = Column(Integer)
    max_zwyx = Column(Integer)
    year = Column(Integer)
    month = Column(Integer)
    zwlb=Column(String(255))

# 分行业职位量分布
class ZwCountByGshy(Base):
    __tablename__ = 'zp_zw_count_by_gshy'

    id = Column(Integer, primary_key=True)
    count=Column(Integer)
    gshy = Column(String(255))
    year = Column(Integer)
    month = Column(Integer)
    zwlb=Column(String(255))

# 分行业职位薪水分布
class ZwyxByGshy(Base):
    __tablename__ = 'zp_zwyx_by_gshy'

    id = Column(Integer, primary_key=True)
    gshy = Column(Integer)
    min_zwyx = Column(Integer)
    max_zwyx = Column(Integer)
    year = Column(Integer)
    month = Column(Integer)
    zwlb = Column(String(255))

if __name__=='__main__':
    Base.metadata.create_all(engine)