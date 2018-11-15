from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.views import View

from AwesomeCRM.permission import check_perm
from repository import models
from django import conf
import os
import json
import time

# Create your views here.


class StudentCourse(View, LoginRequiredMixin):
    """学员的课程展示页面"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(StudentCourse, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        # 获取当前角色的所有课程
        class_objs = request.user.student.class_grade.select_related()
        return render(request, "student/my_course.html", locals())


class StudentClass(View, LoginRequiredMixin):
    """学员课程展示页面"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(StudentClass, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        # 获取当前课程
        class_obj = request.user.student.class_grade.select_related()
        return render_to_response("student/my_class.html", locals())


class StudentHomework(View, LoginRequiredMixin):
    """作业管理"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(StudentHomework, self).dispatch(request, *args, **kwargs)

    def get(self, request, course_id):
        # 获取当前课程与当前学生相关的所有作业
        student_id = request.user.student.id
        study_record = models.StudyRecord.objects.filter(student_id=student_id, course_id=course_id)
        return render_to_response("student/homework.html", locals())


class Homework(View, LoginRequiredMixin):
    """提交作业"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(Homework, self).dispatch(request, *args, **kwargs)

    def get(self, request, study_record_id):
        # 获取学习记录
        study_record = models.StudyRecord.objects.get(id=study_record_id)
        # 获取当前学生的作业目录
        homework_path = conf.settings.STU_HOMEWORK_FILE
        course_record = models.StudyRecord.objects.get(id=study_record_id).course_record
        course = course_record.class_grade.course
        course_name = course.name
        stu_name = request.user.name
        stu_id = request.user.id
        stu_identify = "{0}-{1}".format(stu_name, stu_id)
        homework_file_path = os.path.join(homework_path, course_name, "第%d次上课作业" % course_record.id, stu_identify)
        # 创建目录
        if not os.path.isdir(homework_file_path):
            # 如果没有创建目录，就创建
            os.makedirs(homework_file_path)
        # 获取已经提交的作业
        file_name_list = os.listdir(homework_file_path)
        file_list = list()
        for file_name in file_name_list:
            # 提取每一个文件的信息
            path = os.path.join(homework_file_path, file_name)
            file_obj = os.stat(path)
            file_size = file_obj.st_size  # kb
            file_ctime = time.strftime("%Y-%m-%d", time.gmtime(file_obj.st_ctime))
            file_list.append({"file_name": file_name, "file_size": file_size, "file_ctime": file_ctime})
        return render_to_response("student/homework_submit.html", locals())

    def post(self, request, study_record_id):
        # 获取用户上传作业的文件地址
        homework_path = conf.settings.STU_HOMEWORK_FILE
        # 每节课创建一个目录
        # 获取当前课程名、上课记录的id、学生姓名 + 学生id作为目录结构
        study_record = models.StudyRecord.objects.get(id=study_record_id)
        course_record = study_record.course_record
        stu_name = request.user.name
        stu_id = request.user.id
        stu_identify = "{name}-{stu_id}".format(name=stu_name, stu_id=stu_id)
        # 获取课程名
        course_name = study_record.course.name
        path = os.path.join(homework_path, course_name, "第%d次上课作业" % course_record.id, stu_identify)
        # 检查当前目录里面的文件是否已经超过了限制，最多只能上传两个文件
        if len(os.listdir(path)) >= 2:
            return HttpResponse("0")
        # 将文件存入该目录
        files = request.FILES.get("file")
        # 获取文件后缀
        suffix = files.name.split(".", maxsplit=1)[1]
        file_name = "{0}.{1}".format(time.time(), suffix)
        with open(os.path.join(path, file_name), r'wb') as f:
            for chunk in files.chunks():
                f.write(chunk)
        # 封装文件上传的信息
        # 获取文件信息
        file_obj = os.stat(os.path.join(path, file_name))
        file_size = file_obj.st_size
        file_time = time.strftime("%Y-%m-%d", time.gmtime(file_obj.st_ctime))
        return HttpResponse(json.dumps({"file_name": files.name, "file_size": file_size, "file_time": file_time}))

    def delete(self, request, study_record_id):
        del_file_name = str(request.body, encoding="utf-8").split("=")[1]
        # 删除该文件
        homework_base_dir = conf.settings.STU_HOMEWORK_FILE
        course_record = models.StudyRecord.objects.get(id=study_record_id).course_record
        course_name = course_record.class_grade.course.name
        stu_name = request.user.name
        stu_id = request.user.id
        stu_identify = "{0}-{1}".format(stu_name, stu_id)
        # 获取文件路径
        path = os.path.join(homework_base_dir, course_name, "第%d次上课作业" % course_record.id, stu_identify)
        # 删除文件
        try:
            os.remove(os.path.join(path, del_file_name))
        except Exception as e:
            return HttpResponse(json.dumps({"status": False, "msg": "删除错误"}))
        return HttpResponse(json.dumps({"status": True, "msg": "删除成功"}))


class CourseRecord(View, LoginRequiredMixin):
    """上课记录"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(CourseRecord, self).dispatch(request, *args, **kwargs)

    def get(self, request, class_id):
        # 获取当前上课的班级
        course_record = models.ClassList.objects.get(id=class_id).courserecord_set.select_related()
        return render_to_response("student/course_record.html", locals())


