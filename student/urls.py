from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^my_course/$', views.StudentCourse.as_view(), name="my_course"),
    url(r'^my_class/$', views.StudentClass.as_view(), name="my_class"),
    url(r'^homework/(?P<course_id>\d+)/$', views.StudentHomework.as_view(), name="homework"),
    url(r'^homework/submit/(?P<study_record_id>\d+)/$', views.Homework.as_view(), name="submit_homework"),
    url(r'^course_record/(?P<class_id>\d+)/$', views.CourseRecord.as_view(), name="course_record"),
]



