# -*- coding: utf-8 -*-
from scrapy.spiders import XMLFeedSpider
from scrapy import Request,Selector
from zp.items import ZpItem

class LgspiderSpider(XMLFeedSpider):
    name = 'lgspider'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/upload/third_data_interface/newBaidu/2c90efa427153f9e0127153f9eaa0006/dataIndex.xml']
    iterator = 'xml' # you can change this; see the docs
    itertag = 'sitemapindex' # change it accordingly

    def parse_node(self, response, selector):
        urls = selector.xpath('sitemap/loc/text()').extract()
        return [Request(url=url, callback=self.parse_list, dont_filter=True) for url in urls]

    def parse_list(self,response):
        selector = Selector(response, type='xml')
        data_list = selector.xpath('/urlset/url/data/display')
        for node_dict in data_list:
            zp_obj = ZpItem()
            zwmc = node_dict.xpath('title/text()').extract_first()
            zp_obj['zwmc'] = zwmc[:zwmc.find('(')]  # 职位名称
            zp_obj['zwlb'] = node_dict.xpath('jobsecondclass/text()|jobfirstclass/text()').extract_first()  # 职位类别
            zp_obj['rzyq'] = node_dict.xpath('description/text()').extract_first()  # 岗位职责#
            zp_obj['xl'] = node_dict.xpath('education/text()').extract_first()  # 学历
            zp_obj['gzjy'] = node_dict.xpath('experience/text()').extract_first()  # 工作经验#
            zp_obj['fbrq'] = node_dict.xpath('startdate/text()').extract_first()  # 发布日期#
            zwyx = node_dict.xpath('salary/text()').extract_first()  # 薪资#
            zp_obj['zwyx'] = zwyx
            if zwyx[-1] == '元':
                zwyx_list = zwyx[:-1].split('-')
                min_zwyx = zwyx_list[0]
                max_zwyx = zwyx_list[1]
            elif 'K' in zwyx :
                zwyx_list = zwyx.replace('K', '').split('-')
                if len(zwyx_list) > 2:
                    min_zwyx = str(zwyx_list[0]) + '000'
                    max_zwyx = str(zwyx_list[1]) + '000'
                else:
                    min_zwyx = max_zwyx = zwyx_list[0]
            else:
                min_zwyx = max_zwyx = 0
            zp_obj['min_zwyx'] = min_zwyx  # 最低薪资#
            zp_obj['max_zwyx'] = max_zwyx  # 最高薪资#
            zp_obj['dd']= node_dict.xpath('city/text()').extract_first()# 城市#
            zp_obj['gsmc'] = node_dict.xpath('officialname/text()').extract_first()  # 公司名称#
            zp_obj['gsxz'] = node_dict.xpath('employertype/text()').extract_first()  # 公司性质#
            zp_obj['gsgm'] = node_dict.xpath('size/text()').extract_first()  # 公司规模
            gshy=node_dict.xpath('industry/text()').extract_first().split()
            if gshy:
                zp_obj['gshy'] = gshy[0]# 公司行业
            else:
                zp_obj['gshy'] = gshy
            zp_obj['zwlb_big'] = node_dict.xpath('industry/text()').extract_first()  # 公司行业
            zp_obj['source'] = node_dict.xpath('source/text()').extract_first()  # 来源
            zp_obj['href'] = node_dict.xpath('joblink/text()').extract_first()  # 链接
            zp_obj['type'] = node_dict.xpath('type/text()').extract_first()  # 职位类型
            zp_obj['zprs'] = 0  # 招聘人数
            zp_obj['flxx'] =node_dict.xpath('welfare/text()').extract_first().split(',')  # 福利信息
            yield zp_obj