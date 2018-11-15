from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.Dashboard.as_view(), name="sale_dashboard"),
    url("^stu_enrollment/$", views.StuEnrollment.as_view(), name="stu_enrollment"),
    url("^enrollment/(?P<enrollment_id>\d+)/$", views.EnrollmentLinks.as_view(), name="enrollment_links"),
    url("^file_upload/(?P<enrollment_id>\d+)/$", views.FileUpload.as_view(), name="file_upload"),
    url("^stu_enrollment/(?P<enrollment_id>\d+)/$", views.ContractApprove.as_view(), name="contract_approve"),
    url("^stu_enrollment/(?P<enrollment_id>\d+)/success$",
        views.EnrollmentSuccess.as_view(), name="enrollment_success"),
]
