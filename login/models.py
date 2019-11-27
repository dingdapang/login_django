from django.db import models

# Create your models here.
# python manage.py makemigrations   python manage.py migrate


class User(models.Model):

    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    # name: 必填，最长不超过128个字符，并且唯一，也就是不能有相同姓名；
    name = models.CharField(max_length=128, unique=True)
    # password: 必填，最长不超过256个字符（实际可能不需要这么长）
    password = models.CharField(max_length=256)
    # email: 使用Django内置的邮箱类型，并且唯一；
    email = models.EmailField(unique=True)
    # sex: 性别，使用了一个choice，只能选择男或者女，默认为男；
    sex = models.CharField(max_length=32, choices=gender, default='男')
    c_time = models.DateTimeField(auto_now_add=True)
    # 判断账号是否进行了邮件注册
    has_confirmed = models.BooleanField(default=False)

    # 使用__str__方法帮助人性化显示对象信息；
    def __str__(self):
        return self.name

    # 元数据里定义用户按创建时间的反序排列，也就是最近的最先显示
    class Meta:
        ordering = ["-c_time"] # 按创建时间的反序排列
        verbose_name = "用户" # 给你的模型类起一个更可读的名字
        verbose_name_plural = "用户" # 指定，模型的复数形式是什么


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE) # 用户与注册码一一对应，user关联的一对一的用户
    c_time = models.DateTimeField(auto_now_add=True) # 注册时间

    def __str__(self):
        return self.user.name + ": " + self.code

    class Meta:
        ordering = ["-c_time"]  # 按创建时间的反序排列
        verbose_name = "确认码"  # 给你的模型类起一个更可读的名字
        verbose_name_plural = "确认码"  # 指定，模型的复数形式是什么
