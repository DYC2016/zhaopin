import redis
conn=redis.Redis(host='127.0.0.1',db=0)
url_list=conn.smembers('zwmc_gsmc_zwlb')
for url in url_list:
    print(url.decode('utf-8'))
    if 'zhaopin' in url.decode('utf-8'):
        print('rm {}'.format(url.decode('utf-8')))
        conn.srem('zwmc_gsmc_zwlb',url)