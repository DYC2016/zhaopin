# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from zp.items import ZpItem
from zp.settings import *
from scrapy.exceptions import DropItem
import re
class J51jobsSpider(scrapy.Spider):
    name = '51jobs'
    allowed_domains = ['51job.com']
    start_urls = ['https://www.51job.com/']

    def parse(self, response):
        #print(response.url)
        categroy_a=response.xpath('//div[@class="cn hlist"]/div[@class="e"]/a')
        for item in categroy_a:
            href=item.xpath('@href').extract_first().replace('020000','000000')# 替换城市为全国
            text=item.xpath('span/text()').extract_first()

            yield scrapy.Request(href,callback=self.parse_list,meta={'zwlb':text})

    # 职位列表
    def parse_list(self,response):
        # print(response.url)
        # 提取职位详细页面链接
        info_href=response.xpath('//p[@class="t1 "]/span/a/@href').extract()
        headers=DEFAULT_REQUEST_HEADERS
        # 请求每一个详细链接
        for href in info_href:
            if 'jobs.51job' not in href:
                raise DropItem('Url has problem')
            headers['Rederer']=response.url
            headers['Host']='jobs.51job.com'
            yield scrapy.Request(href,callback=self.parse_info,meta={'zwlb':response.meta['zwlb']},headers=headers)
        next_href=response.xpath('//li[@class="bk"]/a/@href').extract()
        if next_href:
            headers['Rederer']=response.url
            headers['Host']='search.51job.com'
            yield scrapy.Request(next_href[-1],callback=self.parse_list,meta={'zwlb':response.meta['zwlb']},dont_filter=True,headers=headers)

    # 职位详细页面
    def parse_info(self,response):
        items=ZpItem()
        # 职位名称
        items['zwmc']=response.xpath('//div[@class="cn"]/h1/text()').extract_first().strip()
        # 公司名词
        items['gsmc']=response.xpath('//p[@class="cname"]/a/text()').extract_first().strip()
        # 地点、工作经验、学历、招聘人数、发布时日期
        msg=response.xpath('string(//p[@class="msg ltype"])').extract_first().strip()
        msg_list=msg.split('|')
        if len(msg_list)<5:
            zwdd=msg_list[0].strip()
            gzjy=msg_list[1].strip().strip('工作经验')
            zprs=msg_list[2].strip().strip('招人')
            fbrq_text=msg_list[3].strip().strip('发布')
            if int(fbrq_text.split('-')[0])>datetime.now().month:
                fbrq=str(datetime.now().year-1)+'-'+fbrq_text
            else:
                fbrq=str(datetime.now().year)+'-'+fbrq_text
            zdxl='无'
        else:
            zwdd = msg_list[0].strip()
            gzjy = msg_list[1].strip().strip('工作经验')
            zdxl=msg_list[2].strip()
            zprs = msg_list[3].strip().strip('招人')
            fbrq_text = msg_list[4].strip().strip('发布')
            re_com = re.compile('\d{2}-\d{2}')
            if not re_com.search(fbrq_text):
                zdxl=''
                zprs = msg_list[2].strip().strip('招人')
                fbrq_text = msg_list[3].strip().strip('发布')
            if int(fbrq_text.split('-')[0]) > datetime.now().month:
                fbrq = str(datetime.now().year - 1) + '-' + fbrq_text
            else:
                fbrq = str(datetime.now().year) + '-' + fbrq_text
        items['dd']=zwdd.split('-')[0]
        items['gzjy']=gzjy
        items['xl']=zdxl
        items['zprs']=zprs
        items['fbrq']=fbrq
        # 福利信息
        items['flxx']=response.xpath('//div[@class="jtag"]/div/span/text()').extract()
        # 任职要求
        items['rzyq']='\n'.join([p_item.xpath('string()').extract_first().strip() for p_item in response.xpath('//div[@class="bmsg job_msg inbox"]/p')])
        # 职位类别
        zwlb=response.xpath('//a[@class="el tdn"]/text()').extract_first().strip()
        if not zwlb:
            zwlb=response.meta['zwlb']
        items['zwlb']=zwlb
        # 公司性质
        items['gsxz']=response.xpath('//div[@class="com_tag"]/p[1]/@title').extract_first().strip().strip('公司')
        # 公司规模
        items['gsgm']=response.xpath('//div[@class="com_tag"]/p[2]/@title').extract_first().strip()
        # 公司行业
        gshy=response.xpath('//div[@class="com_tag"]/p[3]/@title').extract_first().strip()
        items['zwlb_big'] = items['gshy']=gshy
        # 来源
        items['source']='51job'
        # 详细页链接
        items['href']=response.url
        # 薪资
        xz=response.xpath('//div[@class="cn"]/strong/text()').extract_first()
        if xz:
            xz=xz.strip()
            weight=1
            if '千/月' in xz or 'K' in xz or '千以下/月' in xz:
                weight=1000
            elif '万/月' in xz:
                weight=10000
            elif '万/年' in xz or '万以下/年' in xz or '万以上/年' in xz:
                weight = 10000/12
            xz_list=xz.strip('K万千/年月以上下面议').split('-')
            zwyx=xz
            if len(xz_list)>1:
                zwyx_max=float(xz_list[1])*weight
                zwyx_min=float(xz_list[0])*weight
            elif '元/天' in xz:
                zwyx_max=zwyx_min=float(xz.strip('元/天'))*30
            elif '千以下/月' in xz:
                zwyx_max=zwyx_min=float(xz.strip('千以下/月'))*weight
            elif '万以下/年' in xz or '万以上/年' in xz:
                zwyx_max = zwyx_min = float(xz.strip('万以下上/年'))* weight
            else:
                zwyx_max=zwyx_min=float(xz_list[0])*weight if xz_list[0] else 0
        else:
            zwyx=zwyx_max=zwyx_min=0
        items['zwyx']=zwyx
        items['min_zwyx'] = zwyx_min
        items['max_zwyx'] = zwyx_max
        items['type']='全职'
        return items
