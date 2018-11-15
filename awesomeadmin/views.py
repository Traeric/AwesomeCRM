from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from . import admin_setup
from . import form_handle
import json


# 自动扫描awesomeadmin文件
GLOBAL_DICT = admin_setup.awesomeadmin_auto_descover()
PER_RECORED = 10


def account_login(request):
    """
    用户登录
    :param request:
    :return:
    """
    error_msg = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # 认证
        user = authenticate(username=username, password=password)
        if user:
            # 登录
            login(request, user)
            path = reverse("app_index")
            return redirect(request.GET.get("next", path))
        else:
            error_msg = "Wrong username or password !"
    return render(request, "awesomeadmin/login.html", {'error_msg': error_msg})


def account_logout(request):
    """
    登出操作
    :param request:
    :return:
    """
    logout(request)
    path = reverse("adminlogin")
    return redirect(path)


@login_required
def app_index(request):
    """
    awesomeadmin的首页
    :param request:
    :return:
    """
    return render(request, "awesomeadmin/app_index.html", {
        "site": GLOBAL_DICT,
    })


@login_required
def table_list(request, app_name, table_name):
    """
    展示表的详细列
    取出指定表中的数据返回给前端
    并做一系列的过滤、排序、搜索等操作
    :param request:
    :param app_name:
    :param table_name:
    :return:
    """
    page = request.GET.get("page", None)
    # 取出对应的自定义的admin
    admin_obj = GLOBAL_DICT[app_name][table_name]
    model_obj = admin_obj.model
    # 取出所有的数据
    query_data = model_obj.objects.select_related()
    # 进行过滤
    query_data, filter_dict = execute_filter(request, query_data)
    admin_obj.filter_dict = filter_dict
    # 搜索
    query_data, source = search_query(request, query_data, admin_obj)
    # 排序
    query_data = sorted_query_by_o(request, query_data, admin_obj)
    # 分页
    paginator = Paginator(query_data, PER_RECORED)  # show 2 contacts per page
    try:
        query_data = paginator.get_page(page)
    except PageNotAnInteger:
        query_data = paginator.get_page(1)  # If page is not an integer, deliver first page
    except EmptyPage:
        query_data = paginator.get_page(paginator.num_pages)
    # 实现action
    if request.method == "POST":
        action = request.POST.get("action")
        if action:
            check_item = request.POST.get("checkedItem")    # [1, 2, 5, 8]
            # 获取要操作的记录 # SELECT * FROM table WHERE id in [1, 2, 5]
            querysets = model_obj.objects.filter(id__in=json.loads(check_item))
            # 执行钩子
            getattr(admin_obj, action)(request, querysets)
    return render(request, "awesomeadmin/table_list.html", {
        "query_data": query_data,
        "admin_obj": admin_obj,
        "source": source,
        "app_name": app_name,
        "table_name": table_name,
    })


def execute_filter(request, queryset):
    """
    实现过滤
    :param request:
    :param queryset:
    :return:
    """
    black_list = ["page", "_o", "source"]   # 前端传来的参数黑名单，即有一些参数不能被放到字典里面
    filter_dict = {}
    pro_filter_dict = {}
    # 将GET中的条件放到字典中
    for key, val in request.GET.items():
        if key not in black_list:   # 不在黑名单中的参数才能被添加
            # val有值才放
            if val:
                # 对时间做处理
                if len(val.split("-")) > 1:
                    filter_dict["%s__gte" % key] = val
                else:
                    filter_dict[key] = val
                # 不对时间做处理
                pro_filter_dict[key] = val
    # 返回删选的值
    return queryset.filter(**filter_dict), pro_filter_dict


def sorted_query_by_o(request, query_data, admin_obj):
    """
    实现排序功能
    :param request:
    :param query_data:
    :param admin_obj:
    :return:
    """
    order_index = request.GET.get("_o")
    # 将这次点击的列存到SESSION中
    request.session['click_cloumn'] = order_index
    if order_index:
        order_key = admin_obj.list_display[abs(int(order_index))]
        # 排序
        return query_data.order_by("{0}{1}".format("" if len(order_index) < 2 else "-", order_key))
    else:
        return query_data


def search_query(request, query_data, admin_obj):
    """
    实现搜索功能
    :param request:
    :param query_data:
    :param admin_obj:
    :return:
    """
    # 获取搜索参数
    source = request.GET.get("source", "")
    if source:
        # 添加搜索条件
        q = Q()
        q.connector = 'OR'
        for item in admin_obj.search_fields:
            q.children.append(("%s__contains" % item, source))
        # 返回搜索条件
        return query_data.filter(q), source
    return query_data, source


@login_required
def table_add(request, app_name, table_name):
    """
    添加表
    :param request:
    :param app_name:
    :param table_name:
    :return:
    """
    # 获取admin_class
    admin_class = GLOBAL_DICT[app_name][table_name]
    # 生成动态的ModelForm
    dynamic_form = form_handle.create_dynamic_model_form(admin_class, form_change=False)
    form = None
    if request.method == "GET":
        form = dynamic_form()
    elif request.method == "POST":
        form = dynamic_form(data=request.POST)
        if form.is_valid():
            # 验证正确，保存数据
            form.save()
            # 执行钩子函数
            if admin_class.hook_func:
                # 如果定义了钩子函数就执行
                admin_class.hook_func(admin_class.model)
            # 跳转
            path = reverse("table_list", kwargs={
                'app_name': app_name,
                'table_name': table_name,
            })
            return redirect(path)
    return render(request, "awesomeadmin/table_add.html", {
        "form": form,
        "admin_obj": admin_class,
    })


@login_required
def table_change(request, app_name, table_name, table_id):
    """
    为表添加内容
    :param request:
    :param app_name:
    :param table_name:
    :param table_id:
    :return:
    """
    # 获取admin_class
    admin_class = GLOBAL_DICT[app_name][table_name]
    # 生成动态的ModelForm
    dynamic_form = form_handle.create_dynamic_model_form(admin_class)
    obj = admin_class.model.objects.get(id=table_id)
    form = None
    if request.method == "GET":
        form = dynamic_form(instance=obj)
    elif request.method == "POST":
        form = dynamic_form(instance=obj, data=request.POST)
        if form.is_valid():
            # 验证正确，保存数据
            form.save()
            path = reverse("table_list", kwargs={
                'app_name': app_name,
                'table_name': table_name,
            })
            return redirect(path)
    return render(request, "awesomeadmin/table_change.html", {
        "form": form,
        "admin_obj": admin_class,
        "app_name": app_name,
        "table_name": table_name,
    })


@login_required
def table_delete(request, app_name, table_name, table_id):
    # 获取当前要删除的对象
    model_obj = GLOBAL_DICT[app_name][table_name]
    obj = model_obj.model.objects.get(id=table_id)
    # 如果提交post请求，直接删除数据
    if request.method == "POST":
        obj.delete()
        # 跳转到表的首页
        path = reverse("table_list", kwargs={
            "app_name": app_name,
            "table_name": table_name
        })
        return redirect(path)
    return render(request, "awesomeadmin/table_delete.html", locals())


