# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import quote

import scrapy
from zp.items import ZpItem
import os


class ZhaopinSpider(scrapy.Spider):
    name = 'zhaopin'  #爬虫名
    allowed_domains = ['zhaopin.com', 'fe-api.zhaopin.com', 'jobs.zhaopin.com']  # 允许访问的域名
    start_urls = ['https://www.zhaopin.com/']  # 进口链接
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cookie': 'CNZZDATA1256793290=331662787-1554180895-%7C1554341753; sts_deviceid=16a01f14c8f193-0cd879ac3cd7ab-2464751f-2073600-16a01f14c9017e; sou_experiment=unexperiment; x-zp-client-id=bcd4b932-948e-4aa4-9e28-dc017f0d4143; acw_tc=2760827d15639616398503296e43465f6d2f4049cfe10126e0441fd9c632b5; jobRiskWarning=true; CANCELALL=1; sts_sg=1; sts_chnlsid=Unknown; zp_src_url=http%3A%2F%2Fsou.zhaopin.com%2F; x-zp-device-id=901901dde8b1c6b98b3805eee174102c; dywez=95841923.1564991777.8.3.dywecsr=sou.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/; __utma=269921210.728871691.1554810862.1564366937.1564991778.8; __utmc=269921210; __utmz=269921210.1564991778.8.3.utmcsr=sou.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/; privacyUpdateVersion=1; urlfrom=121126445; urlfrom2=121126445; adfcid=none; adfcid2=none; adfbid=0; adfbid2=0; dywea=95841923.3285671991617382000.1554810862.1564366937.1564991777.8; dywec=95841923; at=068f6b763b224a7989639db13848384c; rt=241083582eb74f1badf217b1056646b7; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22651224639%22%2C%22%24device_id%22%3A%2216a01f15d2b9d-0c6dce2ee0ea14-2464751f-2073600-16a01f15d2c230%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216a01f15d2b9d-0c6dce2ee0ea14-2464751f-2073600-16a01f15d2c230%22%7D; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1564120229,1564366937,1564991773; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1565140348; ZL_REPORT_GLOBAL={%22sou%22:{%22actionid%22:%22457b6629-6e5b-400d-a1d6-505b42634c15-sou%22%2C%22funczone%22:%22smart_matching%22}}; ZP_OLD_FLAG=false; sts_evtseq=5; sts_sid=16c69a247af851-0ebc7634dfbfa5-2464751f-2073600-16c69a247b099d; LastCity=%E5%85%A8%E5%9B%BD; LastCity%5Fid=489',
        'Host': 'fe-api.zhaopin.com',
        'Origin':'https://sou.zhaopin.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36 Qiyu/2.1.1.1'
    }
    job_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Host': 'jobs.zhaopin.com',
        'cookie': 'CNZZDATA1256793290=331662787-1554180895-%7C1554341753; sts_deviceid=16a01f14c8f193-0cd879ac3cd7ab-2464751f-2073600-16a01f14c9017e; sou_experiment=unexperiment; x-zp-client-id=bcd4b932-948e-4aa4-9e28-dc017f0d4143; acw_tc=2760827d15639616398503296e43465f6d2f4049cfe10126e0441fd9c632b5; jobRiskWarning=true; CANCELALL=1; sts_sg=1; sts_chnlsid=Unknown; zp_src_url=http%3A%2F%2Fsou.zhaopin.com%2F; x-zp-device-id=901901dde8b1c6b98b3805eee174102c; dywez=95841923.1564991777.8.3.dywecsr=sou.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/; __utma=269921210.728871691.1554810862.1564366937.1564991778.8; __utmc=269921210; __utmz=269921210.1564991778.8.3.utmcsr=sou.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/; privacyUpdateVersion=1; urlfrom=121126445; urlfrom2=121126445; adfcid=none; adfcid2=none; adfbid=0; adfbid2=0; dywea=95841923.3285671991617382000.1554810862.1564366937.1564991777.8; dywec=95841923; at=068f6b763b224a7989639db13848384c; rt=241083582eb74f1badf217b1056646b7; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22651224639%22%2C%22%24device_id%22%3A%2216a01f15d2b9d-0c6dce2ee0ea14-2464751f-2073600-16a01f15d2c230%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216a01f15d2b9d-0c6dce2ee0ea14-2464751f-2073600-16a01f15d2c230%22%7D; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1564120229,1564366937,1564991773; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1565140348; ZL_REPORT_GLOBAL={%22sou%22:{%22actionid%22:%22457b6629-6e5b-400d-a1d6-505b42634c15-sou%22%2C%22funczone%22:%22smart_matching%22}}; ZP_OLD_FLAG=false; sts_evtseq=5; sts_sid=16c69a247af851-0ebc7634dfbfa5-2464751f-2073600-16c69a247b099d; LastCity=%E5%85%A8%E5%9B%BD; LastCity%5Fid=489',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36 Qiyu/2.1.1.1'
    }

    def start_requests(self):  # 用start_requests()方法,代替start_urls
        """第一次请求一下登录页面，设置开启cookie使其得到cookie，设置回调函数"""
        return [scrapy.Request(url, meta={'cookiejar': True}, callback=self.parse)for url in self.start_urls]
    def parse(self, response):
        sel=scrapy.Selector(response)
        div_list = sel.xpath('//div[@class="zp-jobNavigater__pop--container"]')
        for div_item in div_list:
            zwlb_big = div_item.xpath('div[@class="zp-jobNavigater__pop--title"]/text()').extract_first()
            for zwlb in div_item.xpath('div[@class="zp-jobNavigater__pop--list"]/a/text()').extract():
                url = 'https://fe-api.zhaopin.com/c/i/sou?start=0&pageSize=60&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={}&kt=3'.format(
                    quote(zwlb))
                self.headers['Referer']='https://sou.zhaopin.com/?jl=%E4%B8%8A%E6%B5%B7&sf=0&st=0&kw={}&kt=3'.format(quote(zwlb))
                yield scrapy.Request(url=url, callback=self.parse_list, meta={'zwlb_big': zwlb_big, 'zwlb': zwlb, 'p': 1, 'size': 60, 'start': 60,'cookiejar':response.meta['cookiejar']},headers=self.headers,cookies=self.cookies)

    #通过列表页面获取详细页面链接，并完成分页处理
    def parse_list(self,response):
        text=response.body_as_unicode()
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'json.text'), 'a+') as f:
            f.write(text + '\n')
        js = json.loads(text)
        res_zwlb=response.meta['zwlb']
        self.job_headers['referer'] = 'https://sou.zhaopin.com/?jl=489&kw={}&kt=3'.format(quote(res_zwlb))
        data=js.get('data','')
        if data:
            for index,i in enumerate(js['data'].get('results',[])):
                zwmc = i['jobName']  # zwmc
                try:
                    zwlb_big = i['jobType']['items'][0].get('name',i['jobType'].get('display',res_zwlb))  # zwlb_big
                    zwlb = i['jobType']['items'][-1].get('name',res_zwlb)  # zwlb
                    gsmc = i['company']['name']  # gsmc
                    gsgm = i['company']['size']['name']  # gsgm
                    gsxz = i['company']['type']['name']  # gsxz
                    gzjy = i['workingExp']['name']  # gzjy
                    type = i['emplType']  # type
                    zwyx = i['salary']
                    zdxl = i['eduLevel']['name']# zdxl
                    gzdd = i['city']['items'][0]['name']
                    fbrq = i['updateDate']
                    flxx = i['welfare']
                except Exception as e:
                    with open('/vdb/python/zwhx/zp/zhaopin/'+response.meta['zwlb']+'_'+str(index)+'.log','w') as f:
                        f.write(str(e)+'\n')
                        f.write(json.dumps(i))
                    continue
                pattern = re.compile('(\d+.?\d?)K-(\d+.?\d?)K').findall(zwyx)
                if pattern:
                    min_zwyx = str(int(float(pattern[0][0]) * 10)) + '00'
                    max_zwyx = str(int(float(pattern[0][1]) * 10)) + '00'
                else:
                    min_zwyx = max_zwyx = 0

                item_one = ZpItem()
                item_one['zwmc']=zwmc
                item_one['gsmc'] = gsmc
                item_one['flxx'] = flxx
                item_one['zwyx']=zwyx
                item_one['min_zwyx'] = min_zwyx
                item_one['max_zwyx'] = max_zwyx
                item_one['dd'] = gzdd
                item_one['fbrq'] = fbrq
                item_one['gsxz'] = gsxz
                item_one['gzjy'] = gzjy
                item_one['xl'] = zdxl
                item_one['zwlb'] = zwlb
                item_one['gsgm'] = gsgm
                item_one['zwlb_big'] = zwlb_big
                item_one['type'] = type
                url = i['positionURL']
                item_one['href']=url
                if url:
                    yield scrapy.Request(url=url, callback=self.parse_info, dont_filter=True, meta={'item': item_one,'cookiejar':response.meta['cookiejar']},
                                         headers=self.job_headers)
            num = js['data']['numFound']
            if num > response.meta['start']:
                p = response.meta['p'] + 1
                url2 = 'https://fe-api.zhaopin.com/c/i/sou?start={0}&pageSize={1}&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={2}&kt=3'.format(
                    response.meta['start'], response.meta['size'], response.meta['zwlb'])
                start = response.meta['start'] + 60
                yield scrapy.Request(url=url2, callback=self.parse_list, dont_filter=True,
                                     meta={'zwlb_big': response.meta['zwlb_big'], 'zwlb': response.meta['zwlb'], 'p': p,
                                           'size': response.meta['size'], 'start': start,'cookiejar':response.meta['cookiejar']},
                                     headers=self.headers)

    # 职位详细信息
    def parse_info(self, response):
        item = response.meta['item']
        item['gshy'] = response.xpath('//button[@class="company__industry"]/text()').extract_first()
        item['rzyq'] = response.xpath('string(//div[@class="describtion__detail-content"])').extract_first()
        item['source'] = '智联招聘'
        item['zprs'] = response.xpath('//ul[@class="summary-plane__info"]/li[last()]/text()').extract_first().strip(
            '招人')
        return item
    def parse(self, response):
        sel=scrapy.Selector(response)
        div_list = sel.xpath('//div[@class="zp-jobNavigater-popContainer"]')
        for div_item in div_list:
            zwlb_big = div_item.xpath('div[@class="zp-jobNavigater-pop-title"]/text()').extract_first()
            for zwlb in div_item.xpath('div[@class="zp-jobNavigater-pop-list"]/a/text()').extract():
                url = 'https://fe-api.zhaopin.com/c/i/sou?start=0&pageSize=60&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={}&kt=3'.format(
                    quote(zwlb))
                yield scrapy.Request(url=url, callback=self.parse_list, dont_filter=True,
                                     meta={'zwlb_big': zwlb_big, 'zwlb': zwlb, 'p': 1, 'size': 60, 'start': 60},
                                     headers=self.headers)

    #通过列表页面获取详细页面链接，并完成分页处理
    def parse_list(self,response):
        js = json.loads(response.body_as_unicode())
        self.job_headers['referer'] = 'https://sou.zhaopin.com/?jl=489&kw={}&kt=3'.format(quote(response.meta['zwlb']))
        for i in js['data']['results']:
            job = {}
            zwmc = i['jobName']  # zwmc
            zwlb_big = i['jobType']['items'][0]['name']  # zwlb_big
            zwlb = i['jobType']['items'][1]['name']  # zwlb
            gsmc = i['company']['name']  # gsmc
            gsgm = i['company']['size']['name']  # gsgm
            gsxz = i['company']['type']['name']  # gsxz
            gzjy = i['workingExp']['name']  # gzjy
            zdxl = i['eduLevel']['name']  # zdxl
            zwyx = i['salary']
            job['emplType'] = i['emplType']
            gzdd = i['city']['items'][0]['name']
            fbrq = i['updateDate']
            flxx = i['welfare']

            pattern = re.compile('(\d+)K-(\d+)K').findall(zwyx)
            if pattern:
                min_zwyx = pattern[0][0] + '000'
                max_zwyx = pattern[0][1] + '000'
            else:
                min_zwyx = max_zwyx = 0

            item_one = ZpItem()
            item_one['zwmc']=zwmc
            item_one['gsmc'] = gsmc
            item_one['flxx'] = flxx
            item_one['min_zwyx'] = min_zwyx
            item_one['max_zwyx'] = max_zwyx
            item_one['gzdd'] = gzdd
            item_one['fbrq'] = fbrq
            item_one['gsxz'] = gsxz
            item_one['gzjy'] = gzjy
            item_one['zdxl'] = zdxl
            item_one['zwlb'] = zwlb
            item_one['gsgm'] = gsgm
            item_one['zwlb_big'] = zwlb_big
            url = i['positionURL']
            if url:
                yield scrapy.Request(url=url, callback=self.parse_info, dont_filter=True, meta={'item': item_one},
                                     headers=self.job_headers)

        num = js['data']['numFound']
        if num > response.meta['start']:
            p = response.meta['p'] + 1
            url2 = 'https://fe-api.zhaopin.com/c/i/sou?start={0}&pageSize={1}&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={2}&kt=3'.format(
                response.meta['start'], response.meta['size'], response.meta['zwlb'])
            start = response.meta['start'] + 60
            yield scrapy.Request(url=url2, callback=self.parse_list, dont_filter=True,
                                 meta={'zwlb_big': response.meta['zwlb_big'], 'zwlb': response.meta['zwlb'], 'p': p,
                                       'size': response.meta['size'], 'start': start},
                                 headers=self.headers)

    # 职位详细信息
    def parse_info(self, response):
        item = response.meta['item']
        ul_li = response.css('ul.terminal-ul li')
        info_dict = {}
        for li_item in ul_li:
            # decode 解码为unicode
            span_one = li_item.xpath('span/text()').extract_first().strip("：")
            # string 表示获取strong下的所有文本，不管下面的节点包含关系
            # 会有缺点，他会保留所有的空格
            strong_one = li_item.xpath('string(strong)').extract_first()
            # 对strong_one的文本中的空格进行处理
            strong_list = [one.strip() for one in strong_one.split()]
            strong_one = ''.join(strong_list)
            info_dict[span_one] = strong_one
        item['gshy'] = info_dict.get('公司行业', '')
        item['href'] = response.url
        item['rzyq'] = response.xpath('string(//div[@class="pos-ul"]|//div[@class="tab-inner-cont"])').extract_first()
        return item
