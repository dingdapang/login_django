###Django通用登录模块

###使用方法：

创建虚拟环境

使用pip安装第三方依赖

修改settings.example.py文件为settings.py，填写自己的数据库，邮箱

运行migrate命令，创建数据库和数据表

运行python manage.py runserver启动服务器



###urls.py路由设置

    from django.contrib import admin
    from django.urls import path, include
    from login import views
    
    
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('index/', views.index),
        path('login/', views.login),
        path('register/', views.register),
        path('logout/', views.logout),
        path('confirm/', views.user_confirm),
        path('captcha/', include('captcha.urls')),
        path('check/', views.check_email),
    ]
   
###2019-12-19新增


即使注册的时候没有验证邮箱，也可以通过登录的时候重新输入注册的邮箱，完成邮箱验证
    
