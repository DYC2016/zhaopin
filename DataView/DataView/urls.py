"""TestDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
#from django.contrib import admin
from django.urls import path
from django.conf.urls import url,re_path,include
from zp import views as zp_views
from DataView import settings

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static
urlpatterns = [
    #path('admin/', admin.site.urls,name='admin'),
    re_path(r'^$',zp_views.home,name='home'),
    path('zwyx/dd_index/',zp_views.zwyx_dd,name='zwyx_dd'),
    path('zwyx/xl_index/',zp_views.zwyx_xl,name='zwyx_xl'),
    path('zwyx/gsgm_index/',zp_views.zwyx_gsgm,name='zwyx_gsgm'),
    path('zwyx/gsxz_index/',zp_views.zwyx_gsxz,name='zwyx_gsxz'),
    path('zwyx/gshy_index/',zp_views.zwyx_gshy,name='zwyx_gshy'),
    path('no_found/', zp_views.no_found,name='no_found'),
    path('zwyx/type_index/',zp_views.zwyx_type,name='type_index'),
    path('zwyx/zwyx_zw_count/',zp_views.zwyx_zw_count,name='zwyx_zw_count'),
    path('zp/wordcloud/',zp_views.zp_word,name='zp_word'),
    # 后台
    path('admin/index/',zp_views.zp_admin_index,name='admin_index'),
    path('admin/login/',zp_views.zp_admin_login,name='admin_login'),
    path('admin/logout/',zp_views.zp_admin_logout,name='admin_logout'),
    path('admin/refresh_captcha/',zp_views.refresh_captcha,name='refresh_captcha'),
    path('admin/admin_dd/', zp_views.admin_dd, name='admin_dd'),
    path('admin/admin_gsgm/', zp_views.admin_dd, name='admin_gsgm'),
    path('admin/admin_gsxz/', zp_views.admin_dd, name='admin_gsxz'),
    path('admin/admin_gshy/', zp_views.admin_dd, name='admin_gshy'),
    path('admin/admin_xl/', zp_views.admin_dd, name='admin_xl'),
    path('admin/admin_zwlb/', zp_views.admin_dd, name='admin_zwlb'),
    path('admin/admin_list/', zp_views.admin_dd, name='admin_list'),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
if not settings.DEBUG:
    handler404 = "zp.views.page_not_found"
    handler500 = "zp.views.sever_error"
captcha = [url(r'^captcha/', include('captcha.urls'),name='captcha')]
urlpatterns += captcha