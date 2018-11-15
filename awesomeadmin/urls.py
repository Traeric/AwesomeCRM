from django.conf.urls import url
from . import views

urlpatterns = [
    url('^login/$', views.account_login, name="adminlogin"),
    url('^logout/$', views.account_logout, name="adminlogout"),
    url("^$", views.app_index, name="app_index"),
    url("^(?P<app_name>\w+)/(?P<table_name>\w+)/$", views.table_list, name="table_list"),
    url("^(?P<app_name>\w+)/(?P<table_name>\w+)/(?P<table_id>\d+)/change/$", views.table_change, name="table_change"),
    url("^(?P<app_name>\w+)/(?P<table_name>\w+)/add/$", views.table_add, name="table_add"),
    url("^(?P<app_name>\w+)/(?P<table_name>\w+)/(?P<table_id>\d+)/delete/$", views.table_delete, name="table_delete"),
]
