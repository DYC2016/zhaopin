# -*- coding:utf-8 -*-
# Created by ibf at 2018/11/12 0012
from sqlalchemy import create_engine, Column, Integer,Float, String,Text,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

Base = declarative_base()
url = 'mysql+pymysql://root:FanTan879@127.0.0.1/zw_spider?charset=utf8'
#url='hive://127.0.0.1:10000/zp'
engine = create_engine(url, echo=False,pool_pre_ping=True, pool_recycle=3600)


class DB_Util(object):
    @staticmethod
    def get_session(url=None):
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    @staticmethod
    def init_db():
        Base.metadata.create_all(engine)

class Zp(Base):
    __tablename__ = 'zp_item'
    id = Column(Integer, primary_key=True)
    zwmc = Column(String(300), nullable=True)
    gsmc = Column(String(300), nullable=True)
    min_zwyx = Column(Integer, nullable=True)
    max_zwyx = Column(Integer,nullable=True)
    dd = Column(String(100),nullable=True)
    fbrq = Column(String(100), nullable=True)
    gsxz = Column(String(100), nullable=True)
    gzjy = Column(String(100), nullable=True)
    xl = Column(String(100), nullable=True)
    zwlb = Column(String(100), nullable=True)
    gsgm = Column(String(100), nullable=True)
    gshy = Column(String(100), nullable=False)
    rzyq = Column(Text, nullable=True)
    href = Column(String(100), nullable=False)
    zwlb_big=Column(String(100), nullable=True)
    zprs = Column(Integer, nullable=True)
    province=Column(String(100), nullable=True)
    pointy=Column(String(100), nullable=True)
    pointx=Column(String(100), nullable=True)
    source=Column(String(100), nullable=True)
    zwyx=Column(String(100), nullable=True)
    type=Column(String(100), nullable=True)
    category=Column(String(100),nullable=True)
    flxx=Column(String(255),nullable=True)
    
class ZpProxy(Base):
    __tablename__ = 'zp_proxy'
    id = Column(Integer, primary_key=True)
    proxy = Column(String(100), nullable=True)

if __name__ == '__main__':
    Base.metadata.create_all(engine)