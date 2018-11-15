from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^manage_class/$", views.ManageClass.as_view(), name="manage_class"),
    url(r'^student_list/(?P<class_id>\d+)/$', views.StudentList.as_view(), name="student_list"),
    url(r'^course_record/(?P<class_id>\d+)/$', views.CourseRecord.as_view(), name="course_record"),
    url(r'^check_homework/(?P<course_record_id>\d+)/$', views.CheckHomework.as_view(), name="check_homework"),
    url(r'^check_homework/(?P<course_record_id>\d+)/(?P<student_id>\d+)/$',
        views.CheckHomeworkDetail.as_view(), name="check_homework_detail"),
    url(r'download_file/(?P<course_record_id>\d+)/(?P<student_id>\d+)/$', views.down_file, name="download_file"),
]



