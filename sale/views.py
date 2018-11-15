from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from django.views import View
from repository import models
from . import model_form_cls
from django.utils import timezone
from django import conf
from django.core.mail import EmailMultiAlternatives
from AwesomeCRM.permission import check_perm
import re
import json
import os
import time


# Create your views here.


class Dashboard(View, LoginRequiredMixin):
    """ 首页 """

    def dispatch(self, request, *args, **kwargs):
        return getattr(self, request.method.lower())(request)

    def get(self, request):
        return render(request, "sale/dashboard.html")

    def post(self, request):
        return HttpResponse("OK")


class StuEnrollment(View, LoginRequiredMixin):
    """
    学员报名
    """
    #
    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(StuEnrollment, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        # 获取所有的客户
        customers = models.CustomerInfo.objects.select_related()
        # 获取所有的班级
        classes = models.ClassList.objects.select_related()
        return render(request, "sale/stu_enrollment.html", locals())

    def post(self, request):
        # 获取客户跟班级
        customer_id = request.POST.get("customer_id")
        class_id = request.POST.get("class_id")
        # 将数据插入数据库
        try:
            enrollment_obj = models.StudentEnrollment.objects.create(customer_id=customer_id, class_grade_id=class_id,
                                                                     consultant_id=request.user.id)
        except Exception as e:
            return HttpResponse(1)
        # 生成报名链接
        enrollment_links = reverse("enrollment_links", kwargs={
            "enrollment_id": enrollment_obj.id,
        })
        # 返回报名链接
        return HttpResponse(enrollment_links)

    def put(self, request):
        # 获取传来的参数
        put = str(request.body, encoding="utf-8")
        customer_id = re.search(r'customer_id=\d+', put, re.I).group().split("=")[1]
        class_id = re.search(r'class_id=\d+', put, re.I).group().split("=")[1]
        # 通过参数获取studentEmrollment对象
        result_dict = {"status": False, "Msg": "该客户还未同意报名"}
        try:
            enrollment_obj = models.StudentEnrollment.objects.get(customer_id=customer_id, class_grade_id=class_id)
            # 判断学员是否报名
            if enrollment_obj.contract_agree:
                # 同意报名
                result_dict["status"] = True
                result_dict["Msg"] = "客户已经同意报名，请点击下一步审核"
                result_dict["enrollment_id"] = enrollment_obj.id
                return HttpResponse(json.dumps(result_dict))
        except Exception as e:
            return HttpResponse(json.dumps(result_dict))
        return HttpResponse(json.dumps(result_dict))


class EnrollmentLinks(View, LoginRequiredMixin):
    """
    学员填写报名表
    """

    def dispatch(self, request, *args, **kwargs):
        # 验证权限
        # if check_perm.permission_check(request) is False:
        #     # 没有权限
        #     return render(request, "errorpage/403.html")
        # 判断学员是否已经同意过合同，同意后就不能再进到合同签订页面了
        enrollment_obj = models.StudentEnrollment.objects.get(id=kwargs['enrollment_id'])
        if enrollment_obj.contract_agree:
            # 同意报名，不能查看
            return render(request, "sale/wait_approve.html")
        else:
            return super(EnrollmentLinks, self).dispatch(request, *args, **kwargs)

    def get(self, request, enrollment_id):
        enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
        customer_obj = model_form_cls.CustomerForm(instance=enrollment_obj.customer)

        return render(request, "sale/enrollment.html", locals())

    def post(self, request, enrollment_id):
        enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
        customer_obj = model_form_cls.CustomerForm(instance=enrollment_obj.customer, data=request.POST)
        if customer_obj.is_valid():
            customer_obj.save()
            # 学员同意合同，修改状态
            enrollment_obj.contract_agree = True
            enrollment_obj.contract_signed_date = timezone.now()
            enrollment_obj.save()
            return render(request, "sale/contract_agree_success.html")
        return render(request, "sale/enrollment.html", locals())


class FileUpload(View, LoginRequiredMixin):
    """
    用户上传文件
    """
        
    def post(self, request, enrollment_id):
        # 首先判断文件是否超过了最大限制
        path = conf.settings.UPLOAD_FILE_ENROLLMENT
        if os.path.isdir(os.path.join(path, enrollment_id)):
            file_list = os.listdir(os.path.join(path, enrollment_id))
            # 如果上传达到2个文件，不能继续上传了
            if len(file_list) >= 2:
                return HttpResponse(json.dumps({"status": False, "msg": "上传文件超过上限"}))
        # 获取上传的文件对象
        file_obj = request.FILES.get("file")
        # 为每个客户创建存放身份证照片的目录
        if not os.path.isdir(os.path.join(path, enrollment_id)):
            # 如果该目录不存在，就创建
            os.mkdir(os.path.join(path, enrollment_id))
        # 然后将照片存到该目录下
        # 首先判断该目录下是否已经存在该文件名
        if file_obj.name in os.listdir(os.path.join(path, enrollment_id)):
            # 如果在换个名字
            name_list = file_obj.name.rsplit(".", maxsplit=1)
            surfix = name_list[1]    # 获取文件的后缀名
            prefix = name_list[0]    # 文件名前缀
            # 换名字
            prefix = "%s%f" % (prefix, time.time())
            file_obj.name = "%s.%s" % (prefix, surfix)
        # 保存文件
        with open(os.path.join(path, enrollment_id, file_obj.name), r'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        # 获取文件信息
        file_info = os.stat(os.path.join(path, enrollment_id, file_obj.name))
        file_dict = {
            "file_name": file_obj.name,
            "file_size": "%s KB" % file_info.st_size,
            "file_time": time.strftime("%Y-%m-%d", time.gmtime(file_info.st_ctime)),
        }
        return HttpResponse(json.dumps({"status": True, "file_dict": file_dict}))

    def put(self, request, enrollment_id):
        # 这里拿到相关报名信息下的客户上传图片的信息
        base_path = conf.settings.UPLOAD_FILE_ENROLLMENT
        if os.path.isdir(os.path.join(base_path, enrollment_id)):
            list_dir = os.listdir(os.path.join(base_path, enrollment_id))
            return_file_list = list()
            for index, item in enumerate(list_dir):
                dict_dir = dict()
                dict_dir['index'] = index + 1
                dict_dir['file_name'] = item
                file_info = os.stat(os.path.join(base_path, enrollment_id, item))
                dict_dir['file_size'] = "{0} KB".format(file_info.st_size)
                dict_dir['upload_time'] = time.strftime("%Y-%m-%d", time.gmtime(file_info.st_ctime))
                return_file_list.append(dict_dir)
            return HttpResponse(json.dumps(return_file_list))
        return HttpResponse("0")

    def delete(self, request, enrollment_id):
        file_name = str(request.body, encoding="utf-8").split("=")[1]
        # 找到文件删除
        base_path = conf.settings.UPLOAD_FILE_ENROLLMENT
        try:
            os.remove(os.path.join(base_path, enrollment_id, file_name))
        except Exception as e:
            return HttpResponse(json.dumps({"status": False, "msg": "删除错误"}))
        return HttpResponse(json.dumps({"status": True}))


class ContractApprove(View, LoginRequiredMixin):
    """
    审核合同，是否同意学员报名
    """

    def dispatch(self, request, *args, **kwargs):
        # 验证权限
        # if check_perm.permission_check(request) is False:
        #     # 没有权限
        #     return render(request, "errorpage/403.html")
        # 判断该学员有没有报名
        enrollment_obj = models.StudentEnrollment.objects.get(id=kwargs['enrollment_id'])
        if enrollment_obj.contract_agree:
            return super(ContractApprove, self).dispatch(request, *args, **kwargs)
        else:
            url_path = reverse("stu_enrollment")
            return redirect(url_path)

    def get(self, request, enrollment_id):
        # 获取报名表信息
        enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
        enrollment_form = model_form_cls.StudentEnrollmentForm(instance=enrollment_obj)
        # 获取学生信息
        customer_form = model_form_cls.CustomerForm(instance=enrollment_obj.customer)
        return render(request, "sale/enrollment_contract_aprove.html", locals())

    def post(self, request, enrollment_id):
        pass

    def put(self, request, enrollment_id):
        put = str(request.body, encoding="utf-8")
        put_list = put.split("&")
        enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
        for item in put_list:
            put_split = item.split("=")
            if put_split[1] == "true":
                setattr(enrollment_obj, put_split[0], True)
            elif put_split[1] == "false":
                setattr(enrollment_obj, put_split[0], False)
        # 同意时间
        enrollment_obj.contract_approved_date = timezone.now()
        enrollment_obj.save()
        # 报名成功，为该学员创建一条用户信息，初始密码0000
        user_obj = models.UserProfile.objects.create(name=enrollment_obj.customer.name,
                                                     email=enrollment_obj.customer.email)
        user_obj.set_password("0000")   # 设置密码，hash后存入
        user_obj.save()
        # 获取学员角色
        student_role = models.Role.objects.filter(id=2)
        user_obj.role.add(student_role[0])
        # 为客户创建一条学员记录
        stu_obj = models.Student.objects.create(user=user_obj, customer=enrollment_obj.customer)
        # 获取报名课程
        class_obj = enrollment_obj.class_grade
        stu_obj.class_grade.add(class_obj)
        return HttpResponse(enrollment_id)


class EnrollmentSuccess(View, LoginRequiredMixin):
    """
    报名成功
    """

    def dispatch(self, request, *args, **kwargs):
        # 验证权限
        # if check_perm.permission_check(request) is False:
        #     # 没有权限
        #     return render(request, "errorpage/403.html")
        # 判断销售有没有同意审核
        enrollment_obj = models.StudentEnrollment.objects.get(id=kwargs['enrollment_id'])
        if enrollment_obj.contract_approved:
            return super(EnrollmentSuccess, self).dispatch(request, *args, **kwargs)
        else:
            url_path = reverse("contract_approve", kwargs={"enrollment_id": kwargs["enrollment_id"]})
            return redirect(url_path)

    def get(self, request, enrollment_id):
        enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
        return render(request, "sale/enrollment_success.html", {"enrollment_obj": enrollment_obj})

    def post(self, request, enrollment_id):
        enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
        # 发送邮件
        # 获取发送方的邮件地址
        email_to = models.StudentEnrollment.objects.get(id=enrollment_id).customer.email
        subject, from_email, to = "报名成功", conf.settings.EMAIL_HOST_USER, email_to
        text_content = "恭喜您报名成功，您的账户名是：{0}，账户密码为：0000，请你收到这封邮件后尽快前往官网登录修改初始密码".format(enrollment_id)
        html_content = """<p>恭喜您报名成功，您的账户名是：<strong style="color: #f00; font-weight: 700;">{0}</strong>，
        账户密码为：<strong style="color: #f00; font-weight: 700;">0000</strong>，
        请你收到这封邮件后尽快前往官网登录修改初始密码</p>""".format(enrollment_obj.customer.email)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email_to])
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            return HttpResponse(json.dumps({"status": True, "msg": "发送成功"}))
        except Exception as e:
            return HttpResponse(json.dumps({"status": False, "msg": "发送失败，请重试"}))

