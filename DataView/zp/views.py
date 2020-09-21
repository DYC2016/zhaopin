from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
from django.views import View
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
import pandas as pd
from zp.models import *
import json
# Create your views here.
import logging
logger = logging.getLogger('django')
from DataView.settings import *
from django.views.decorators.cache import cache_page
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url



def readFile(filename, chunk_size=512):
    """
    缓冲流下载文件方法
    :param filename:
    :param chunk_size:
    :return:
    """
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
@cache_page(60 * 60*24)
def page_not_found(request,exception):
    return render(request, '404.html',context={'title':'404'})
@cache_page(60 * 60*24)
def sever_error(request):
    return render(request, '500.html',context={'title':'500'})

def get_echarts_all_by_zwyx_value(x,key):
    return pd.Series({key: x[key].tolist()[0], 'max_zwyx': x['max_zwyx'].max(), 'min_zwyx': x['min_zwyx'].min(), 'count': x['count'].sum()})

@cache_page(60 * 60*24)
def home(request):
    category_list=CategoryModel.objects.all()
    return render(request, 'index.html',context={'title':'首页','category_list':category_list})

@cache_page(60 * 60*24)
def no_found(request):
    zwlb=request.GET.get('zwlb','')
    return render(request,'no_found.html',context={'title':'未找到','zwlb':zwlb})

def go_redict(zwlb,path):
    try:
        if not os.path.exists(os.path.join(BASE_DIR, 'templates/{}'.format(path))):
            return redirect('/no_found/?zwlb={}'.format(zwlb))
        else:
            return HttpResponse(readFile(os.path.join(BASE_DIR, 'templates/{}'.format(path))))
    except Exception as e:
        logger.error(str(e))

# 地点薪资关系图(地图+柱状)
@cache_page(60 * 60*24)
def zwyx_dd(request):
    try:
        zwlb = request.GET.get('zwlb', '')
        if zwlb:
            path=f'zwyx_dd/{zwlb}.html'
        else:
            path = 'zwyx_dd.html'
        return go_redict(zwlb,path)
    except Exception as e:
        logger.error(str(e))

# 学历 薪资+职位量关系图
@cache_page(60 * 60*24)
def zwyx_xl(request):
    zwlb = request.GET.get('zwlb', '')
    if zwlb:

        path=f'zwyx_xl/{zwlb}.html'
    else:
        path = 'zwyx_xl.html'
    return go_redict(zwlb,path)

# 公司规模 薪资+职位量关系图
@cache_page(60 * 60*24)
def zwyx_gsgm(request):
    zwlb = request.GET.get('zwlb', '')
    if zwlb:
        path = f'zwyx_gsgm/{zwlb}.html'
    else:
        path = 'zwyx_gsgm.html'
    return go_redict(zwlb, path)

# 公司性质 薪资+职位量关系图
@cache_page(60 * 60*24)
def zwyx_gsxz(request):
    zwlb = request.GET.get('zwlb', '')
    if zwlb:
        path = f'zwyx_gsxz/{zwlb}.html'
    else:
        path = 'zwyx_gsxz.html'
    return go_redict(zwlb, path)

# 各就业方向职位月薪和招聘人数
@cache_page(60 * 60*24)
def zwyx_zw_count(request):
    zwlb = request.GET.get('zwlb', '')
    if zwlb:
        path = f'zwyx_zw_count/{zwlb}.html'
    else:
        path = 'zwyx_zw_count.html'
    return go_redict(zwlb, path)


# 公司行业
@cache_page(60 * 60*24)
def zwyx_gshy(request):
    zwlb = request.GET.get('zwlb', '')
    if zwlb:
        path = f'zwyx_gshy/{zwlb}.html'
    else:
        path = 'zwyx_gshy.html'
    return go_redict(zwlb, path)

# 职位类型
@cache_page(60 * 60*24)
def zwyx_type(request):
    zwlb = request.GET.get('zwlb', '')
    if zwlb:
        path = f'zwyx_type/{zwlb}.html'
    else:
        path = 'zwyx_type.html'
    return go_redict(zwlb, path)

# 词云
@cache_page(60*60*24)
def zp_word(request):
    zwlb = request.GET.get('zwlb', '')
    if zwlb:
        path = f'zp_word/{zwlb}.html'
    else:
        path = 'zp_word.html'
    return go_redict(zwlb, path)

# 后台首页
def zp_admin_index(request):
    return render(request, 'admin/index.html', context={'title': '首页'})
    # if request.user.is_authenticated():
    #     return render(request, 'admin/index.html',context={'title':'首页'})
    # else:
    #     return HttpResponseRedirect('/admin/login/')

# 登陆
def zp_admin_login(request):
    if request.session.get('is_login', None):
        return redirect('/admin/index')
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        captchaStr=request.POST['captcha']
        captchaHashkey=request.POST['hashkey']
        redirect_url=request.POST['redirect']
        returnData={'status':0}
        if jarge_captcha(captchaStr, captchaHashkey):
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    returnData['status']=1
                    returnData['redirect']=redirect_url if 'admin/login' not in redirect_url and 'admin/logout' not in redirect_url and redirect_url else '/admin/index'
                else:
                    # 返回一个无效帐户的错误
                    returnData['info']='无效帐户'
            else:
                # 返回登录失败页面。
                returnData['info']='用户名或密码不正确'
        else:
            # 验证码不正确
            returnData['info'] = '验证码不正确'
        return HttpResponse(json.dumps(returnData), content_type='application/json')
    else:
        redirect_url=request.META.get('HTTP_REFERER')
        return render(request, 'admin/login.html',{'title':'后台登录','captcha':captcha(),'redirect':redirect_url})
# 登出
def zp_admin_logout(request):
    logout(request)

# 注册用户的方法
def createUser(request):
    if request.method == 'GET':
        return render(request, 'admin/user_add.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        upassword = request.POST.get('password')
        # 创建新的用户
        user = User.objects.create_user(
            username=username,
            password=upassword
        )
        user.is_staff = True
        user.save()
        # 这个返回可以优化，让它直接转到登录页面
        return HttpResponse('创建成功')

# 创建验证码
def captcha():
    # 验证码，第一次请求
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    captcha = {'hashkey': hashkey, 'image_url': image_url}
    return captcha

# 验证验证码
def jarge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        try:
            # 获取根据hashkey获取数据库中的response值
            get_captcha = CaptchaStore.objects.get(hashkey=captchaHashkey)
            # 如果验证码匹配
            if get_captcha.response == captchaStr.lower():
                return True
        except:
            return False
    else:
        return False

# 刷新验证码
def refresh_captcha(request):
    return HttpResponse(json.dumps(captcha()), content_type='application/json')

# 地点管理
def admin_dd(request):
    pass

# 公司规模
def admin_gsgm(request):
    pass

# 公司性质
def admin_gsxz(request):
    pass

# 公司行业
def admin_gshy(request):
    pass

#学历
def admin_xl(request):
    pass

# 职位类别
def admin_zwlb(request):
    pass

# 职位列表
def admin_list(request):
    pass
