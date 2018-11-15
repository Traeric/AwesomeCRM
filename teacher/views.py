from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.shortcuts import render, render_to_response, HttpResponse

from AwesomeCRM.permission import check_perm
from repository import models
from django import conf
import os
import time
import json

# Create your views here.
from django.views import View


class ManageClass(View, LoginRequiredMixin):
    """我管理的班级"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(ManageClass, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        # 获取当前老师的所有课程
        user = request.user
        class_list = models.ClassList.objects.filter(teachers=user)
        return render_to_response("teacher/manage_class.html", locals())


class StudentList(View, LoginRequiredMixin):
    """学员列表"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(StudentList, self).dispatch(request, *args, **kwargs)

    def get(self, request, class_id):
        clazz = models.ClassList.objects.get(id=class_id)
        # 获取课程
        course = clazz.course
        # 获取学生列表
        student_list = clazz.student_set.all()
        return render(request, "teacher/student_list.html", locals())


def create_study_record(course_record_modedl):
    """
    当学习记录创建成功后，为所有的学生创建学习记录
    :param course_record_modedl:
    :return:
    """
    # 获取最后一条学习记录
    last_course_record = course_record_modedl.objects.last()
    # 获取课程
    course = last_course_record.class_grade.course
    # 为所有的学生创建一条学习记录
    # 获取到所有的学生
    students = last_course_record.class_grade.student_set.all()
    # 循环添加学习记录
    for student in students:
        models.StudyRecord.objects.create(course_record=last_course_record, course=course, student=student)


class CourseRecord(View, LoginRequiredMixin):
    """查看上课记录"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(CourseRecord, self).dispatch(request, *args, **kwargs)

    def get(self, request, class_id):
        """
        展示该课程的所有上课记录
        :param request:
        :param class_id:
        :return:
        """
        course_record = models.CourseRecord.objects.filter(class_grade_id=class_id)
        return render(request, "teacher/class_record.html", locals())


class CheckHomework(View, LoginRequiredMixin):
    """检查作业"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(CheckHomework, self).dispatch(request, *args, **kwargs)

    def get(self, request, course_record_id):
        current_course_record = models.CourseRecord.objects.get(id=course_record_id)
        # 获取所有的学员
        student_list = current_course_record.class_grade.student_set.select_related()
        return render(request, "teacher/check_homework.html", locals())


class CheckHomeworkDetail(View, LoginRequiredMixin):
    """检查每个学生的作业"""

    # def dispatch(self, request, *args, **kwargs):
    #     # 验证权限
    #     if check_perm.permission_check(request) is False:
    #         # 没有权限
    #         return render(request, "errorpage/403.html")
    #     return super(CheckHomeworkDetail, self).dispatch(request, *args, **kwargs)

    def get(self, request, course_record_id, student_id):
        study_record = (models.StudyRecord.objects
                        .filter(course_record_id=course_record_id, student_id=student_id).first())
        # 获取该学生所有的
        base_path = conf.settings.STU_HOMEWORK_FILE
        # 获取课程名字
        course_name = study_record.course.name
        # 学生信息
        student = study_record.student.user
        study_identify = "{name}-{stu_id}".format(name=student.name, stu_id=student.id)
        # 拼接路径
        full_path = os.path.join(base_path, course_name, "第{0}次上课作业".format(course_record_id), study_identify)
        # 检查路径是否存在
        file_list = list()
        if os.path.isdir(full_path):
            # 获取文件信息
            file_name_list = os.listdir(full_path)
            for file_name in file_name_list:
                file_obj = os.stat(os.path.join(full_path, file_name))
                file_list.append({
                    "file_name": file_name,
                    "file_size": file_obj.st_size,    # KB
                    "file_ctime": time.strftime("%Y-%m-%d", time.gmtime(file_obj.st_ctime))
                })
        return render(request, "teacher/check_homework_detail.html", locals())

    def post(self, request, course_record_id, student_id):
        # 接收成绩
        score = request.POST.get("score", None)
        ret_dic = {"status": False, "msg": "成绩修改失败"}
        if score:
            # 将成绩保存
            lines = (models.StudyRecord.objects
                     .filter(course_record_id=course_record_id, student_id=student_id).update(score=score))
            if lines:
                ret_dic['status'] = True
                ret_dic['msg'] = "成绩修改成功"
                return HttpResponse(json.dumps(ret_dic))
            return HttpResponse(json.dumps(ret_dic))
        return HttpResponse(json.dumps(ret_dic))


# @check_perm.has_permission
def down_file(request, course_record_id, student_id):
    """
    下载文件
    :param request:
    :param course_record_id:
    :param student_id:
    :return:
    """
    # 获取下载文件名
    file_name = request.GET.get("file_name")
    study_record = (models.StudyRecord.objects
                    .filter(course_record_id=course_record_id, student_id=student_id).first())
    # 获取该学生所有的
    base_path = conf.settings.STU_HOMEWORK_FILE
    # 获取课程名字
    course_name = study_record.course.name
    # 学生信息
    student = study_record.student.user
    study_identify = "{name}-{stu_id}".format(name=student.name, stu_id=student.id)
    # 拼接路径
    full_path = os.path.join(base_path, course_name, "第{0}次上课作业".format(course_record_id), study_identify)
    # 打开文件
    file = open(os.path.join(full_path, file_name), "rb")
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % file_name
    return response

