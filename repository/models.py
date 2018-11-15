from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import User, PermissionsMixin
# Create your models here.


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=64, verbose_name="姓名")
    role = models.ManyToManyField(to="Role", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'        # 使用email作为用户名
    REQUIRED_FIELDS = ['name']      # 必须要有的字段
    
    class Meta:
        permissions = (
            ("sale_stu_enrollment", "是否能够给学员报名"),
            ("sale_enrollment_links", "是否能够获取报名链接"),
            ("sale_file_upload", "是否能够上传身份证附件"),
            ("sale_contract_approve", "是否能够同意报名"),
            ("sale_enrollment_success", "是否能够去到报名成功页面"),
            ("student_my_course", "是否能够去我的上课记录展示页面"),
            ("student_my_class", "是否能够去到课程展示页面"),
            ("student_homework", "是否能够去到我的作业"),
            ("student_submit_homework", "是否能够提交作业"),
            ("student_course_record", "是否能够查看我的上课记录"),
            ("teacher_manage_class", "能否管理班级"),
            ("teacher_student_list", "能否显示学生列表"),
            ("teacher_course_record", "能够展示课程记录"),
            ("teacher_check_homework", "能够检查作业"),
            ("teacher_check_homework_detail", "能否去到作业详情检查"),
            ("teacher_download_file", "能否下载作业"),
        )

    def __str__(self):
        return self.name


class Role(models.Model):
    """ 角色表 """
    name = models.CharField(max_length=64, unique=True)     # 添加唯一索引
    menus = models.ManyToManyField(to="Menu", blank=True)

    def __str__(self):
        return self.name


class CustomerInfo(models.Model):
    """ 客户信息表 """
    name = models.CharField(max_length=64, default=None, verbose_name="姓名")
    contact_type_choice = ((0, 'QQ'), (1, "WeChat"), (2, "Mobile"))
    contact_type = models.SmallIntegerField(choices=contact_type_choice, default=0, verbose_name="联系方式")

    contact = models.CharField(max_length=64, unique=True, verbose_name="联系人")
    source_choice = ((0, "QQ群"), (1, "51CTO"), (2, "百度推广"), (3, "知乎"), (4, "转介绍"), (5, "其他"))
    source = models.SmallIntegerField(choices=source_choice, verbose_name="客户来源")
    referral_from = models.ForeignKey(to="self", blank=True, null=True, on_delete=models.CASCADE, verbose_name="转介绍人")

    consult_courses = models.ManyToManyField(to="Course", verbose_name="咨询课程")
    consult_content = models.TextField(verbose_name="咨询内容")
    consultant = models.ForeignKey(to="UserProfile", verbose_name="课程顾问", null=True, blank=True,
                                   on_delete=models.CASCADE)
    status_choices = ((0, '未报名'), (1, "已报名"), (2, "已退学"))
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态")
    date = models.DateField(auto_now_add=True)

    id_num = models.CharField(max_length=128, blank=True, null=True, verbose_name="身份证号")
    emergency_contact = models.PositiveIntegerField(blank=True, null=True, verbose_name="紧急联系人")
    gender_choices = (
        (0, '男'),
        (1, '女'),
    )
    gender = models.SmallIntegerField(choices=gender_choices, blank=True, null=True, verbose_name="性别")
    email = models.EmailField(verbose_name="邮箱")

    def __str__(self):
        return "%s" % self.name


class Student(models.Model):
    """ 学员表 """
    user = models.OneToOneField(to=UserProfile, on_delete=models.CASCADE)
    customer = models.OneToOneField(to=CustomerInfo, on_delete=models.CASCADE)
    class_grade = models.ManyToManyField(to="ClassList")

    def __str__(self):
        return "%s" % self.user


class CustomerFollowUp(models.Model):
    """ 客户跟踪记录 """
    customer = models.ForeignKey(to=CustomerInfo, on_delete=models.CASCADE, verbose_name="客户")
    content = models.TextField(verbose_name="跟踪内容")
    user = models.ForeignKey(to=UserProfile, verbose_name="跟进人", on_delete=models.CASCADE, null=True, blank=True)
    status_choices = ((0, "近期无报名计划"), (1, "一个月内报名"), (2, "2周内报名"), (3, "已报名"))
    status = models.SmallIntegerField(choices=status_choices)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content


class Course(models.Model):
    """ 课程表 """
    name = models.CharField(max_length=64, verbose_name="课程名称", unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="课程周期", default=5)
    outline = models.TextField(verbose_name="课程大纲")

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """ 班级列表 """
    branch = models.ForeignKey(to="Branch", on_delete=models.CASCADE)
    course = models.ForeignKey(to="Course", on_delete=models.CASCADE)
    # 合同模板
    constract_template = models.OneToOneField(to="ContractTemplate", on_delete=models.CASCADE)
    class_type_choices = (
        (0, "脱产"),
        (1, "周末"),
        (2, "网络班"),
    )
    class_type = models.SmallIntegerField(choices=class_type_choices, default=0)

    semester = models.SmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField(to="UserProfile", verbose_name="讲师", blank=True)
    start_date = models.DateField(verbose_name="开班日期")
    graduate_date = models.DateField(verbose_name="毕业日期", blank=True, null=True)

    def __str__(self):
        return "{0}{1}期".format(self.course, self.semester)

    class Meta:
        unique_together = (("branch", "class_type", "course", "semester"), )
        verbose_name_plural = "班级表"


class CourseRecord(models.Model):
    """ 上课记录 """
    class_grade = models.ForeignKey(to=ClassList, verbose_name="上课班级", on_delete=models.CASCADE)
    day_num = models.PositiveSmallIntegerField(verbose_name="课程节次")
    teacher = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=64, verbose_name="本节主题")
    content = models.TextField(verbose_name="本节内容")
    has_homework = models.BooleanField(verbose_name="本节有无作业", default=True)
    homework = models.TextField(verbose_name="作业需求", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{0}第{1}节".format(self.class_grade, self.day_num)

    class Meta:
        unique_together = (('class_grade', 'day_num'), )


class StudyRecord(models.Model):
    """ 学习记录表 """
    course_record = models.ForeignKey(to=CourseRecord, on_delete=models.CASCADE)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)
    score_choices = (
        (100, "A+"),
        (90, "A"),
        (85, "B+"),
        (80, "B"),
        (75, "B-"),
        (70, "C+"),
        (60, "C"),
        (40, "C-"),
        (-50, "D"),
        (-100, "COPY"),
        (0, "N/A"),   # not avaliable
    )
    score = models.SmallIntegerField(choices=score_choices, null=True, blank=True)

    show_status_choices = (
        (0, "缺勤"),
        (1, "已签到"),
        (2, "迟到"),
        (3, "早退"),
    )
    show_status = models.SmallIntegerField(choices=show_status_choices, default=1)
    note = models.TextField(blank=True, null=True, verbose_name="成绩备注")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{0}-{1}-{2}".format(self.course_record, self.student, self.score)


class Branch(models.Model):
    """ 校区 """
    name = models.CharField(max_length=64, unique=True)
    addr = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    """ 动态菜单 """
    name = models.CharField(max_length=64)
    url_type_choices = ((0, "absolute url"), (1, "dynamic url"))
    url_type = models.SmallIntegerField(choices=url_type_choices, default=0)
    url_name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "url_name")


class ContractTemplate(models.Model):
    """
    储存合同模板
    """
    name = models.CharField(max_length=64, verbose_name="模板名称")
    content = models.TextField(verbose_name="内容")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.name


class StudentEnrollment(models.Model):
    """
    学员报名表
    """
    customer = models.OneToOneField(to=CustomerInfo, on_delete=models.CASCADE, verbose_name="关联客户")
    class_grade = models.ForeignKey(to=ClassList, on_delete=models.CASCADE, verbose_name="报名班级")
    consultant = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, verbose_name="联系人", null=True, blank=True)
    contract_agree = models.BooleanField(default=False, verbose_name="是否同意报名")
    contract_signed_date = models.DateTimeField(blank=True, null=True, verbose_name="同意时间")
    contract_approved = models.BooleanField(default=False, verbose_name="是否通过审核")
    contract_approved_date = models.DateTimeField(verbose_name="合同审核时间", blank=True, null=True)

    class Meta:
        unique_together = ('customer', 'class_grade')

    def __str__(self):
        return "%s" % self.customer


class PaymentRecord(models.Model):
    """
    储存学员缴费记录
    """
    enrollment = models.ForeignKey(to=StudentEnrollment, on_delete=models.CASCADE)
    payment_type_choices = (
        (0, "报名费"),
        (1, "学费"),
        (2, "退费"),
    )
    payment_type = models.SmallIntegerField(choices=payment_type_choices, default=0)
    amount = models.IntegerField(verbose_name="费用", default=500)
    consulant = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.enrollment


