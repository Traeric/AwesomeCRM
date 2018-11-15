from django import template
from repository import models
from django.db.models import Sum


register = template.Library()


@register.simple_tag
def get_score(student_obj):
    """
    获取某个学生的平均成绩
    :param student_obj:
    :return:
    """
    # 获取该学生所有的学习记录
    study_record_list = list(student_obj.studyrecord_set.all())
    # 获取所有的成绩列表
    score_list = list(map(lambda study_record: study_record.score, study_record_list))
    # 计算所有成绩的平均值
    count = 0
    for item in score_list:
        if item is not None:
            count += item
    return count // len(score_list)


# 用分组做
@register.simple_tag
def get_sort(student_obj, course):
    """
    将学习记录表先按指定的课程筛选，再将该门课程按照学生(外键)分组，最后获取每个分组的总成绩
    :param student_obj:
    :param course:
    :return:
    """
    info_list = list(models.StudyRecord.objects.filter(course=course)
                     .values_list("student__id").annotate(Sum("score")))
    # 提出成绩列
    score_list = list(map(lambda info: info[1], info_list))
    # 将学生成绩排序
    score_list = sorted(score_list)
    # 获取当前学生的总成绩
    stu_score = models.StudyRecord.objects.filter(course=course, student=student_obj).aggregate(Sum("score"))
    return score_list.index(stu_score["score__sum"]) + 1


@register.simple_tag
def on_time_count(student_obj, status_num):
    """
    计算该学生出勤，缺勤，迟到等的次数
    :param student_obj:
    :param status_num:
    :return:
    """
    return student_obj.studyrecord_set.filter(show_status=status_num).count()


@register.simple_tag
def get_study_record(course_record_obj, student_obj):
    """
    获取到本次课，某学生的学习记录
    :param course_record_obj:
    :param student_obj:
    :return:
    """
    return models.StudyRecord.objects.filter(course_record=course_record_obj, student=student_obj).first()





