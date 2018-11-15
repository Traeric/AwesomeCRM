from django.shortcuts import render, redirect
from django.urls import resolve
from django import conf
from . import permission_dict


# 权限判断
def permission_check(*args, **kwargs):
    """
    1.获取当前请求的url
    2.把url解析成url的别名 url_name
    3.判断用户是否已经登录  user.is_authenticated()判断用户是否已认证
    4.拿url_name到perm_dict里面去匹配，匹配时要求包括请求方法和参数
    5.拿配到的权限对应的key去验证用户是否有该权限（使用user.has_perm(key)验证）
    :param args:
    :param kwargs:
    :return:
    """
    request = args[0]
    # 获取当前url的别名
    current_url_name = resolve(request.path).url_name
    # 判断用户是否已经登录
    if request.user.is_authenticated is False:    # 用户未登录
        # 去登陆
        return redirect(conf.settings.LOGIN_URL)
    # 等下要验证用户权限的key
    perm_key = None
    # 已经登录，循环字典进行权限判断
    for permission_key, permission_val in permission_dict.perm_dict.items():
        # 获取列表的四个参数
        perm_url = permission_val[0]
        perm_method = permission_val[1]
        perm_args = permission_val[2]
        perm_kwargs = permission_val[3]
        # 获取钩子函数
        perm_hook = permission_val[4] if len(permission_val) > 4 else None
        # 判断url是否匹配
        if current_url_name == perm_url:
            # 判断方法是否匹配
            if request.method == perm_method:
                # 逐个匹配perm_args，看看是否带了指定的参数
                # 拿到所有的匹配结果
                args_result_list = list(map(lambda item: getattr(request, perm_method).get(item, None), perm_args))
                # 判断结果
                args_matched = all(args_result_list)
                # 逐个匹配perm_kwargs，看看是否指定的参数是否是指定的值
                # 拿到所有的匹配结果
                kwargs_result_list = list(map(lambda k, v: getattr(request, perm_method).get(k, None) == str(v),
                                              perm_kwargs.keys(),
                                              perm_kwargs.values()))
                kwargs_matched = all(kwargs_result_list)
                # 开始指定自定义的钩子函数
                hook_matched = perm_hook(request) if perm_hook else True
                if args_matched and kwargs_matched and hook_matched:
                    # 都匹配匹配上了，表示字典中有这条记录
                    perm_key = permission_key   # 把字典的键交出去
                    break
    # 验证用户是否有该条权限
    if perm_key:
        # appname_matchkey
        app_name = perm_key.split("_", maxsplit=1)[0]   # 切最左边的
        perm_name = "{0}.{1}".format(app_name, perm_key)
        # 验证权限，通过user.has_perm()
        return request.user.has_perm(perm_name)
    return False


# 定义一个装饰器，用于进行权限判断
def has_permission(func):
    def inner(*args, **kwargs):
        if not permission_check(*args, **kwargs):     # 在该方法里面进行判断，是否有权限
            # 没有权限
            request = args[0]
            return render(request, "errorpage/403.html")
        return func(*args, **kwargs)
    return inner

