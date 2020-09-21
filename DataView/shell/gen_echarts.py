import sys
import os,django
sys.path.append(os.path.dirname(os.path.abspath('.')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataView.settings")# project_name 项目名称
django.setup()
from django_pandas.io import read_frame
import pandas as pd
import random
from DataView.settings import *
from zp.models import *
from pyecharts import Page,Line,Bar,Pie,Map,Grid,Overlap,Timeline,WordCloud
import math
zwlb_list = CategoryModel.objects.all()
zwlb_list=[item.category for item in zwlb_list]+['']
def get_echarts_all_by_zwyx_value(x,key):
    return pd.Series({key: x[key].tolist()[0], 'max_zwyx': x['max_zwyx'].max(), 'min_zwyx': x['min_zwyx'].min(), 'count': x['count'].sum(),'zprs':x['zprs'].sum()})

def get_echarts_all_by_value(x,key):
    return pd.Series({key:x[key].tolist()[0],'count':x['count'].sum()})

# 地点(地图+柱状)
def gen_zwyx_dd(zwlb):
    qs = ZpZwByAreaModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path=f'zwyx_dd/{zwlb}.html'
    else:
        path = 'zwyx_dd.html'
    page=Page()
    df = read_frame(qs.all())
    if len(df)>0:
        df_group=df.groupby(['year','month'])
        time_line_chart1= Timeline(width=1500, height=450,is_auto_play=False,timeline_bottom=0)
        time_line_chart2= Timeline(width=1500, height=450,is_auto_play=False,timeline_bottom=0)
        for name,group in df_group:
            # 地图 平均薪资
            month=group['month'].tolist()[0]
            year=group['year'].tolist()[0]
            df_new=group.groupby('province').apply(get_echarts_all_by_zwyx_value,'province')
            data = [(a, (b + c) / 2) for a, b, c in
                     zip(df_new['province'].tolist(), df_new['max_zwyx'].tolist(), df_new['min_zwyx'].tolist())]
            chart = Map(f'{zwlb}平均职位月薪与地点',width=1500, height=450)
            attr, value = chart.cast(data)
            chart.add(f'平均薪资', attr, value, wmaptype='china', is_label_show=True, is_visualmap=True,
                       visual_range=[int(min(value)), int(max(value))],visual_pos='right',visual_top='top')
            time_line_chart1.add(chart,f'{year}年{month}月')

            # 本月职位量Top20
            chart3=Pie(f'{zwlb}职位量及招聘人数',width=1500)
            chart3.add('职位量', df_new['province'].tolist(), df_new['count'].tolist(),center=[25,50],is_label_show=True)
            chart3.add('招聘人数', df_new['province'].tolist(), df_new['zprs'].tolist(),center=[75,50],is_label_show=True)
            time_line_chart2.add(chart3,f'{year}年{month}月')
        page.add(time_line_chart1)
        page.add(time_line_chart2)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))

# 学历（柱状图+饼图）
def gen_zwyx_xl(zwlb):
    qs = ZpZwyxByXlModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path = f'zwyx_xl/{zwlb}.html'
    else:
        path = 'zwyx_xl.html'
    df = read_frame(qs.all())
    if len(df) > 0:
        page = Page()
        df_group = df.groupby(['year', 'month'])
        time_line_chart1 = Timeline(width=1500, height=450, is_auto_play=False, timeline_bottom=0)
        time_line_chart2 = Timeline(width=1500, height=450, is_auto_play=False, timeline_bottom=0)
        for name, group in df_group:
            # 地图 平均薪资
            month = group['month'].tolist()[0]
            year = group['year'].tolist()[0]
            df_new=group.groupby('xl').apply(get_echarts_all_by_zwyx_value, 'xl')
            Overlap_chart = Overlap(width=1500, height=450)
            bar_chart = Bar(f'{zwlb}职位月薪与学历')
            bar_chart.add('最低薪资', df_new['xl'].tolist(), df_new['min_zwyx'].tolist(), is_label_show=True,
                          is_stack=True,is_more_utils=True)
            bar_chart.add('最高薪资', df_new['xl'].tolist(), df_new['max_zwyx'].tolist(),is_more_utils=True)
            line_chart = Line()
            line_chart.add("平均薪资", df_new['xl'].tolist(),
                           [(a + b) / 2 for a, b in zip(df_new['min_zwyx'].tolist(), df_new['max_zwyx'].tolist())])
            Overlap_chart.add(bar_chart)
            Overlap_chart.add(line_chart)
            time_line_chart1.add(Overlap_chart,f'{year}年{month}月')

            chart3 = Pie(f'{zwlb}职位量及招聘人数', width=1500)
            chart3.add('职位量', df_new['xl'].tolist(), df_new['count'].tolist(), is_label_show=True, is_stack=True,
                       center=[25, 50])
            chart3.add('招聘人数', df_new['xl'].tolist(), df_new['zprs'].tolist(), is_label_show=True, is_stack=True,
                       center=[75, 50])
            time_line_chart2.add(chart3,f'{year}年{month}月')
        page.add(time_line_chart1)
        page.add(time_line_chart2)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))

# 公司规模（折线图+柱状图）
def gen_zwyx_gsgm(zwlb):
    qs = ZpZwyxByGsgmModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path = f'zwyx_gsgm/{zwlb}.html'
    else:
        path = 'zwyx_gsgm.html'
    # 当月职位月薪与公司规模
    df = read_frame(qs.all())
    if len(df) > 0:
        page = Page()
        Grid_chart1 = Timeline(width=1500, height=450,timeline_bottom=0)
        Grid_chart2 = Timeline(width=1500, height=450,timeline_bottom=0)
        df_group=df.groupby(['year','month'])
        for name,group in df_group:
            month=group['month'].tolist()[0]
            year=group['year'].tolist()[0]
            df_new=group.groupby('gsgm').apply(get_echarts_all_by_zwyx_value, 'gsgm')
            # 薪资
            Overlap_chart = Overlap(width=800, height=450)
            bar_chart = Bar(f'{zwlb}职位月薪与公司规模')
            bar_chart.add('最低薪资', df_new['gsgm'].tolist(), df_new['min_zwyx'].tolist(), is_label_show=True,is_more_utils=True)
            bar_chart.add('最高薪资', df_new['gsgm'].tolist(), df_new['max_zwyx'].tolist(),is_label_show=True,is_more_utils=True)
            line_chart = Line()
            line_chart.add("平均薪资", df_new['gsgm'].tolist(),
                           [(a + b) / 2 for a, b in zip(df_new['min_zwyx'].tolist(), df_new['max_zwyx'].tolist())],is_label_show=True)
            Overlap_chart.add(bar_chart)
            Overlap_chart.add(line_chart)
            Grid_chart1.add(Overlap_chart,f'{year}年{month}月')
            # 职位量
            chart3 = Bar(f'{zwlb}职位量及招聘人数', width=1500)
            chart3.add('职位量', df_new['gsgm'].tolist(), df_new['count'].tolist(), is_label_show=True,is_toolbox_show=True)
            chart3.add('招聘人数', df_new['gsgm'].tolist(), df_new['zprs'].tolist(), is_label_show=True)
            Grid_chart2.add(chart3,f'{year}年{month}月')
        page.add(Grid_chart1)
        page.add(Grid_chart2)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))

# 公司性质（柱状+饼图）
def gen_zwyx_gsxz(zwlb):
    qs = ZpZwyxByGsxzModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path = f'zwyx_gsxz/{zwlb}.html'
    else:
        path = 'zwyx_gsxz.html'
    # 公司性质
    df = read_frame(qs.all())
    if len(df) > 0:
        page = Page()
        Grid_chart1 = Timeline(width=1500, height=450, timeline_bottom=0)
        Grid_chart2 = Timeline(width=1500, height=450, timeline_bottom=0)
        df_group = df.groupby(['year', 'month'])
        for name, group in df_group:
            month = group['month'].tolist()[0]
            year = group['year'].tolist()[0]
            df_new = group.groupby('gsxz').apply(get_echarts_all_by_zwyx_value, 'gsxz')
            # 薪资
            Overlap_chart = Overlap(width=800, height=450)
            bar_chart = Bar(f'{zwlb}职位月薪与公司性质')
            bar_chart.add('最低薪资', df_new['gsxz'].tolist(), df_new['min_zwyx'].tolist(),
                          is_label_show=True,is_more_utils=True)
            bar_chart.add('最高薪资', df_new['gsxz'].tolist(), df_new['max_zwyx'].tolist(),
                          is_label_show=True,is_more_utils=True)
            line_chart = Line()
            line_chart.add("平均薪资", df_new['gsxz'].tolist(),
                           [(a + b) / 2 for a, b in zip(df_new['min_zwyx'].tolist(), df_new['max_zwyx'].tolist())],
                           is_label_show=True,is_more_utils=True)
            Overlap_chart.add(bar_chart)
            Overlap_chart.add(line_chart)
            Grid_chart1.add(Overlap_chart, f'{year}年{month}月')
            # 职位量
            chart3 = Pie(f'{zwlb}职位量及招聘人数', width=1500)
            chart3.add('职位量'.format(zwlb), df_new['gsxz'].tolist(), df_new['count'].tolist(), is_label_show=True,is_stack=True,center=[25, 50])
            chart3.add('招聘人数'.format(zwlb), df_new['gsxz'].tolist(), df_new['zprs'].tolist(), is_label_show=True,is_stack=True,center=[75, 50])
            Grid_chart2.add(chart3, f'{year}年{month}月')
        page.add(Grid_chart1)
        page.add(Grid_chart2)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))

# 公司行业 （复合图+折线图）
def gen_zwyx_gshy(zwlb):
    qs = ZpZwyxByGshyModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path = f'zwyx_gshy/{zwlb}.html'
    else:
        path = 'zwyx_gshy.html'
    df = read_frame(qs.all())
    if len(df) > 0:
        page = Page()
        Grid_chart1 = Timeline(width=1500, height=450, timeline_bottom=0)
        Grid_chart2 = Timeline(width=1500, height=450, timeline_bottom=0)
        df_group = df.groupby(['year', 'month'])
        for name, group in df_group:
            month = group['month'].tolist()[0]
            year = group['year'].tolist()[0]
            df_new = group.groupby('gshy').apply(get_echarts_all_by_zwyx_value, 'gshy')
            # 薪资
            Overlap_chart = Overlap(width=800, height=450)
            bar_chart = Bar(f'{zwlb}职位月薪与公司行业')
            data_len=math.ceil(0.1*len(df_new))
            bar_chart.add('最低薪资', df_new['gshy'].tolist(), df_new['min_zwyx'].tolist(), is_label_show=True,datazoom_type="both",datazoom_range=[0,data_len], is_datazoom_show=True,is_more_utils=True)
            bar_chart.add('最高薪资', df_new['gshy'].tolist(), df_new['max_zwyx'].tolist(), is_label_show=True,datazoom_type="both",datazoom_range=[0,data_len], is_datazoom_show=True,is_more_utils=True)
            line_chart = Line()
            line_chart.add("平均薪资", df_new['gshy'].tolist(),
                           [(a + b) / 2 for a, b in zip(df_new['min_zwyx'].tolist(), df_new['max_zwyx'].tolist())],
                           is_label_show=True,datazoom_type="both",datazoom_range=[0,10], is_datazoom_show=True)
            Overlap_chart.add(bar_chart)
            Overlap_chart.add(line_chart)
            Grid_chart1.add(Overlap_chart, f'{year}年{month}月')
            # 职位量
            chart3 = Bar(f'{zwlb}职位量及招聘人数', width=1500)
            chart3.add('职位量', df_new['gshy'].tolist(), df_new['count'].tolist(), is_label_show=True,
                       is_toolbox_show=True,datazoom_type="both",datazoom_range=[0,data_len], is_datazoom_show=True)
            chart3.add('招聘人数', df_new['gshy'].tolist(), df_new['zprs'].tolist(), is_label_show=True,datazoom_type="both",datazoom_range=[0,data_len], is_datazoom_show=True)
            Grid_chart2.add(chart3, f'{year}年{month}月')
        page.add(Grid_chart1)
        page.add(Grid_chart2)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))

# 职位类型（饼图+柱状）
def gen_zwyx_type(zwlb):
    qs = ZpZwyxByTypeModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path = f'zwyx_type/{zwlb}.html'
    else:
        path = 'zwyx_type.html'
    # 当月职位月薪与公司性质
    df = read_frame(qs.all())
    if len(df) > 0:
        page = Page()
        Grid_chart1 = Timeline(width=1500, height=450, timeline_bottom=0)
        Grid_chart2 = Timeline(width=1500, height=450, timeline_bottom=0)
        df_group = df.groupby(['year', 'month'])
        for name, group in df_group:
            month = group['month'].tolist()[0]
            year = group['year'].tolist()[0]
            df_new = group.groupby('type').apply(get_echarts_all_by_zwyx_value, 'type')
            # 薪资
            Overlap_chart = Overlap(width=800, height=450)
            bar_chart = Bar(f'{zwlb}职位月薪与公司性质')
            bar_chart.add('最低薪资', df_new['type'].tolist(), df_new['min_zwyx'].tolist(),
                          is_label_show=True,is_more_utils=True)
            bar_chart.add('最高薪资', df_new['type'].tolist(), df_new['max_zwyx'].tolist(),
                          is_label_show=True,is_more_utils=True)
            line_chart = Line()
            line_chart.add("平均薪资", df_new['type'].tolist(),
                           [(a + b) / 2 for a, b in zip(df_new['min_zwyx'].tolist(), df_new['max_zwyx'].tolist())],
                           is_label_show=True)
            Overlap_chart.add(bar_chart)
            Overlap_chart.add(line_chart)
            Grid_chart1.add(Overlap_chart, f'{year}年{month}月')
            # 职位量
            chart3 = Pie(f'{zwlb}职位量及招聘人数', width=1500)
            chart3.add('职位量'.format(zwlb), df_new['type'].tolist(), df_new['count'].tolist(), is_label_show=True,
                       is_stack=True, center=[25, 50])
            chart3.add('招聘人数'.format(zwlb), df_new['type'].tolist(), df_new['zprs'].tolist(), is_label_show=True,
                       is_stack=True, center=[75, 50])
            Grid_chart2.add(chart3, f'{year}年{month}月')
        page.add(Grid_chart1)
        page.add(Grid_chart2)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))

# 各就业方向分析（折线+饼图）
def gen_zwyx_zw_count(zwlb):
    # 不同薪资的职位量和招聘人数分布
    qs = ZpZwCountByZwyxModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path = f'zwyx_zw_count/{zwlb}.html'
    else:
        path = 'zwyx_zw_count.html'
    df = read_frame(qs.all())
    if len(df) > 0:
        page = Page()
        Grid_chart1 = Timeline(width=1500, height=800, timeline_bottom=0)
        df_group = df.groupby(['year', 'month'])
        for name, group in df_group:
            month = group['month'].tolist()[0]
            year = group['year'].tolist()[0]
            df_new = group.groupby('zwyx').apply(get_echarts_all_by_zwyx_value, 'zwyx')
            # 薪资
            bar_chart = Bar(f'{zwlb}招聘人数与职位量', width=1500)
            bar_chart.add('职位量', df_new['zwyx'].tolist(), df_new['count'].tolist(),is_label_show=True,datazoom_type="both",datazoom_range=[0,5], is_datazoom_show=True)
            bar_chart.add('招聘人数'.format(zwlb), df_new['zwyx'].tolist(), df_new['zprs'].tolist(), is_label_show=True,datazoom_type="both",datazoom_range=[0, 5], is_datazoom_show=True)
            Grid_chart1.add(bar_chart, f'{year}年{month}月')
        page.add(Grid_chart1)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))

# 职位技能词云
def gen_gwzz_word(zwlb):
    qs = ZpWordByZwlbModel.objects
    if zwlb:
        qs = qs.filter(zwlb=zwlb)
        path = f'zp_word/{zwlb}.html'
    else:
        path = 'zp_word.html'
    df = read_frame(qs.all())
    if len(df) > 0:
        page = Page()
        Grid_chart1 = Timeline(width=1500, height=800, timeline_bottom=0)
        df_group = df.groupby(['year', 'month'])
        for name, group in df_group:
            month = group['month'].tolist()[0]
            year = group['year'].tolist()[0]
            df_new = group.groupby('word').apply(get_echarts_all_by_value, 'word')
            chart = WordCloud(f'{zwlb}岗位需求词云', width=1500)
            shape_list=[None,'circle', 'cardioid', 'diamond', 'triangle-forward', 'triangle', 'pentagon', 'star']
            chart.add("", df_new['word'].tolist(), df_new['count'].tolist(), word_size_range=[30, 100], rotate_step=66,shape=shape_list[random.randint(0,len(shape_list)-1)])
            Grid_chart1.add(chart, f'{year}年{month}月')
        page.add(Grid_chart1)
        page.render(os.path.join(BASE_DIR, 'templates/{}'.format(path)))
for zwlb in zwlb_list:
    print(zwlb)
    gen_zwyx_zw_count(zwlb)
    # gen_zwyx_dd(zwlb)
    # gen_zwyx_xl(zwlb)
    # gen_zwyx_gsgm(zwlb)
    # gen_zwyx_gsxz(zwlb)
    # gen_zwyx_gshy(zwlb)
    # gen_zwyx_type(zwlb)
    # gen_gwzz_word(zwlb)