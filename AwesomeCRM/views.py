from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


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
        user = authenticate(username=username, password=password)
        if user:
            # 登录
            login(request, user)
            path = reverse("sale_dashboard")
            return redirect(request.GET.get("next", path))
        else:
            error_msg = "Wrong username or password !"
    return render(request, "login.html", {'error_msg': error_msg})


def account_logout(request):
    """
    登出操作
    :param request:
    :return:
    """
    logout(request)
    path = reverse("login")
    return redirect(path)

