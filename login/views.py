from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from . import models, forms
import hashlib
import datetime
# Create your views here.


def hash_code(s, site='mysite'):
    h = hashlib.sha3_256()
    s += site
    h.update(s.encode())
    return h.hexdigest()


def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'login/index.html')


def make_confirm_string(user):
    '''
    通过时间和密码生成独一无二的hash值
    :param user:
    :return:
    '''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user,)
    return code


def send_mail(email, code):
    print(code)
    subject = '来自---的注册确认邮件'
    text_content = '''
        感谢注册本网站，如果你收到了这条消息，说明你的邮箱不提供html链接功能，请联系管理员qq:2608619307
    '''
    html_content = '''
        <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>dlb.top</a>,</p>
        <p>请点击链接完成邮箱确认！</p>
        <p>此链接有效期{}天</p>    
        '''.format('127.0.0.1:9000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def user_confirm(request):
    code = request.GET.get('code', None)  # 获取确认码
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求！'
        return render(request, 'login/confirm.html', locals())
    c_time = confirm.c_time
    now = timezone.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()  # 邮件过期，注册码也会删除掉
        message = '您的邮件已经过期！请重新注册！'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True  # 注册成功
        confirm.user.save()
        message = '感谢确认，请使用账号登录！'
        return render(request, 'login/confirm.html', locals())


def login(request):
    '''
    对于非POST方法发送数据时，比如GET方法请求页面，返回空的表单，让用户可以填入数据；
    对于POST方法，接收表单数据，并验证；
    使用表单类自带的is_valid()方法一步完成数据验证工作；
    验证成功后可以从表单对象的cleaned_data数据字典中获取表单的具体值；
    如果验证不通过，则返回一个包含先前数据的表单给前端页面，方便用户修改。也就是说，它会帮你保留先前填写的数据内容，而不是返回一个空表！
    locals()函数，它返回当前所有的本地变量字典
    :param request:
    :return:
    '''
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message = '请检查填写的内容！'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            # 验证账号密码
            try:
                user = models.User.objects.get(name=username)
            except:
                message = '用户不存在！'
                return render(request, 'login/login.html', locals())

            if not user.has_confirmed:
                message = '该用户还未经邮件确认！,点击这里验证邮箱'
                return render(request, 'login/login.html', locals())

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/blog/index')
            else:
                message = '密码不正确！'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())
    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == "POST":
        register_form = forms.ResiterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password = register_form.cleaned_data.get('password')
            password_d = register_form.cleaned_data.get('password_d')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')
            if password != password_d:
                message = '两次填写的密码不同！'
                return render(request, 'login/login.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已存在!'
                    return render(request, 'login/login.html', locals())
                same_name_email = models.User.objects.filter(email=email)
                if same_name_email:
                    message = '该邮箱已被注册！'
                    return render(request, 'login/login.html', locals())
                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)  # 生成hash码
                send_mail(email, code)   # 发送码邮件进行确认

                message = '请前往邮箱进行确认！'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.ResiterForm(request.POST)
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    request.session.flush()  # flush()方法是比较安全的一种做法，而且一次性将session中的所有内容全部清空
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect('/login/')


def check_email(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == "POST":
        check_form = forms.CheckForm(request.POST)
        message = "请检查填写的内容！"
        if check_form.is_valid():
            email = check_form.cleaned_data.get('email')
            try:
                user = models.User.objects.filter(email=email).first()
                if user:
                    if int(user.has_confirmed) == 1:
                        message = '该邮箱已被验证，如果是您的邮箱，请联系管理员！'
                        return render(request, 'login/checkemail.html', locals())
                    else:
                        cod = str(models.ConfirmString.objects.get(user=user))
                        code = cod.split(' ')[-1]
                        send_mail(email, code)  # 发送码邮件进行确认
                        message = '请前往邮箱进行确认！,确认完毕点击这里可以进行登录'
                        return render(request, 'login/checkemail.html', locals())
                else:
                    message = '未知邮箱，请检查邮箱信息，如想更换邮箱，请点击下方更换邮箱'
                    return render(request, 'login/checkemail.html', locals())
            except ObjectDoesNotExist:
                message2 = '邮箱与初始邮箱不符合，请输入正确的邮箱，或者点击下方更改绑定邮箱！'
                return render(request, 'login/checkemail.html', locals())
    check_form = forms.CheckForm(request.POST)
    return render(request, 'login/checkemail.html', locals())