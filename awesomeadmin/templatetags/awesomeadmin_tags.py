from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
import datetime


register = template.Library()


@register.simple_tag
def get_column(model_class, list_display):
    """
    通过反射获取display_list中的列对应在models中的值
    :param model_class:
    :param list_display:
    :return:
    """
    element = "<td><input type='checkbox' check-tag value='%s'></td>" % model_class.id
    if list_display:
        for index, col in enumerate(list_display):
            # 获取每个字段的对象，判断需不需要对choices进行转换
            field_obj = model_class._meta.get_field(col)
            if field_obj.choices:
                # 如果choices有值，进行转换
                col_data = getattr(model_class, "get_%s_display" % col)()
            else:
                col_data = getattr(model_class, col)
            if index == 0:
                element += "<td><a href='{1}/change'>{0}</a></td>".format(col_data, model_class.id)
            else:
                element += "<td>{0}</td>".format(col_data)
    else:
        element += "<td><a href='{1}/change'>{0}</a></td>".format(model_class, model_class.id)
    return mark_safe(element)


@register.simple_tag
def filter_col(filter_column, admin_class):
    filter_ele = "<select name='%s' class='form-control'>" % filter_column
    # 获取该filter_column对应的字段对象
    column_obj = admin_class.model._meta.get_field(filter_column)
    try:
        for choice in column_obj.get_choices():
            selected = ""
            if filter_column in admin_class.filter_dict:
                if str(choice[0]) == admin_class.filter_dict.get(filter_column):
                    selected = "selected"
            option = "<option value='{0}' {1}>{2}</option>".format(choice[0], selected, choice[1])
            filter_ele += option
    except AttributeError as e:
        if column_obj.get_internal_type() in ('DateField', "DateTimeField"):
            time_obj = datetime.datetime.now()
            time_list = [
                ["", "ALL"],  # 所有
                [time_obj, "今天"],  # 当前时间
                [time_obj - datetime.timedelta(7), "7天前"],  # 7天前
                [time_obj.replace(day=1), "本月"],  # 本月,将day换成1表示本月的第一天
                [time_obj - datetime.timedelta(90), "3个月内"],  # 3个月内
                [time_obj.replace(month=1, day=1), "本年"],  # 本年，月跟天都换成1
            ]
            for item in time_list:
                item[0] = "" if not item[0] else item[0].strftime("%Y-%m-%d")
                selected = ""
                if filter_column in admin_class.filter_dict:
                    if item[0] == admin_class.filter_dict.get(filter_column):
                        selected = "selected"
                option = "<option value='{0}' {1}>{2}</option>".format(item[0], selected, item[1])
                filter_ele += option
    filter_ele += "</select>"
    return mark_safe(filter_ele)


@register.simple_tag
def get_table_name(admin_obj):
    """
    根据自定义的admin获取表名
    :param admin_obj:
    :return:
    """
    return admin_obj.model._meta.model_name


@register.simple_tag
def paginator_button(querysets, block_num, request, admin_obj):
    """
    生成分页按钮
    :param querysets:
    :param block_num:
    :param request:
    :param admin_obj:
    :return:
    """
    # 获取过滤跟排序的参数
    others_param_str = union_params(request, querysets, admin_obj, 2)
    ele = '<ul class="pagination">'
    # 做前一页
    disabled = "" if querysets.number != 1 else 'class=disabled'
    ele += ('<li {0}><a href="?page={1}{2}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.
            format(disabled, querysets.number-1 or 1, others_param_str))
    active = ""
    for item in querysets.paginator.page_range:
        if abs(querysets.number - item) < block_num:
            # 如果在自定范围内就生成相应的页数按钮
            if item == querysets.number:    # current page
                active = 'class="active"'
            button = '<li {1}><a href="?page={2}{3}">{0}</a></li>'.format(item, active, item, others_param_str)
            active = ""   # 清空
            ele += button
    # 做后一页
    disabled, last_page = (("", querysets.number+1) if querysets.number != querysets.paginator.num_pages
                           else ('class=disabled', querysets.paginator.num_pages))
    ele += ('<li {0}><a href="?page={1}{2}" aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>'
            '</ul>'.format(disabled, last_page, others_param_str))
    return mark_safe(ele)


@register.simple_tag
def sorted_regulation(request, forloop):
    """
    获取当前排序的规则，即是否需要加上符号
    :param request:
    :param forloop:
    :return:
    """
    try:
        # 获取session中上一次点击的位置以及状态
        sorted_index = request.session.get('click_cloumn')
        if forloop == abs(int(sorted_index)):
            return ("-%d" % forloop) if len(sorted_index) <= 1 else forloop
    except Exception as e:
        print("awesomeadmin_tags---129", e)
    return forloop


@register.simple_tag
def arrow_display(request, forloop):
    """
    显示排序图标
    :param request:
    :param forloop:
    :return:
    """
    try:
        ele = '<span class="arrow-icon glyphicon glyphicon-triangle-%s"></span>'
        # 获取session中上一次点击的位置以及状态
        sorted_index = request.session.get('click_cloumn')
        if forloop == abs(int(sorted_index)):
            arrow = 'bottom' if len(sorted_index) <= 1 else 'top'
            return mark_safe(ele % arrow)
        else:
            return ""
    except Exception as e:
        return ""


@register.simple_tag
def union_params(request, querysets, admin_obj, status):
    """
    将分页，排序，筛选的信息包装起来
    :param request:
    :param querysets:
    :param admin_obj:
    :param status:
    :return:
    """
    try:
        # 获取排序参数
        sorted_index = request.session.get('click_cloumn')
        sorted_index = '' if not sorted_index else sorted_index
        sorted_str = "&_o=%s" % sorted_index
    except Exception:
        sorted_index = ''
        sorted_str = ""

    # 获取过滤参数
    filter_dict = admin_obj.filter_dict
    filter_str = ''
    if filter_dict:
        for key, val in filter_dict.items():
            filter_str += "&%s=%s" % (key, val)
    # 获取分页参数
    page_num = querysets.number
    page_str = "&page=%s" % page_num
    # 将各个参数组合成列表
    params_list = [sorted_index,
                   page_num,
                   sorted_str + filter_str,     # 在分页后面添加
                   page_str + filter_str    # 在排序后面添加
    ]
    # 按照status的值返回各个参数
    return params_list[status]


@register.simple_tag
def get_read_only_name(form, field):
    """
    获取只读字段的值
    :param form:
    :param field:
    :return:
    """
    return getattr(form.instance, field)


@register.simple_tag
def get_related_field(field_name, admin_obj, form_obj):
    """
    获取该字段关联的另外一张表的所有字段
    :param field_name:
    :param admin_obj:
    :param form_obj:
    :return:
    """
    model_class = admin_obj.model
    field_obj = model_class._meta.get_field(field_name)
    related_class = field_obj.related_model
    query_set = set(related_class.objects.select_related())
    # 获取还没有选中的项
    selected_set = set(get_selected_data(field_name, form_obj))
    return query_set - selected_set


@register.simple_tag
def get_selected_data(field_name, form_obj):
    """
    获取所有已经选中的字段
    :param field_name:
    :param form_obj:
    :return:
    """
    try:
        return getattr(form_obj.instance, field_name).all()
    except Exception as e:
        return []


@register.simple_tag
def display_delete_info(obj):
    """
    展示删除相关的信息
    :param obj: 
    :return: 
    """
    ele = "<ul>"
    # 获取所有的反向关联Many2One
    for m2a in obj._meta.related_objects:
        # 获取所有预置反向关联的表名
        related_table_name = m2a.name
        # 通过 表名_set反向查询出预置关联的对象，同时要注意一对一的情况不需要set
        if m2a.one_to_one:
            select_key = "%s" % related_table_name
            # 如果没有与之关联一对一数据，直接break
            try:
                related_obj = getattr(obj, select_key)
            except Exception:
                break
        else:
            select_key = "%s_set" % related_table_name
            related_obj = getattr(obj, select_key).all()
        if related_obj:
            ele += "<li style='color: red;'>{0}<ol>".format(related_table_name.upper())
        # 循环这些对象打印,如果是一对一，不能循环，会直接跳到except里面
        try:
            for i in related_obj:
                ele += ("<li style='color: #000;'>应用{0}里面{1}表的"
                        "<a href='/awesomeadmin/{0}/{1}/{4}/change/'>{2}</a>"
                        "记录与{3}相关，会被一起删除</li>".format(i._meta.app_label, i._meta.model_name, i, obj,
                                                      i.id))
                ele += display_delete_info(i)
        except Exception:
            ele += ("<li style='color: #000;'>应用{0}里面{1}表的"
                    "<a href='/awesomeadmin/{0}/{1}/{4}/change/'>{2}</a>"
                    "记录与{3}相关，会被一起删除</li>".format(related_obj._meta.app_label, related_obj._meta.model_name, related_obj, obj,
                                                  related_obj.id))
        ele += "</ol></li>"

    # 列出ManyToMany
    # 获取manytomany字段名
    m2m = obj._meta.many_to_many
    if m2m:
        for m2m_item in m2m:
            # 获取m2m字段的名称
            m2m_item_name = m2m_item.name
            # 查询所有相关的m2m记录
            m2m_obj_set = getattr(obj, m2m_item_name).select_related()
            # 将这些信息打印即可，不必要做深入的查询
            ele += "<ul style='color: #000;'>M2M：%s<ol>" % m2m_item_name
            for m in m2m_obj_set:
                ele += "<li>%s</li>" % m
            ele += "</ol></ul>"
    ele += "</ul>"
    return ele


@register.simple_tag
def get_dynamic_url(menu_url, url_type):
    """
    获取动态url的值
    :param menu_url:
    :param url_type:
    :return:
    """
    return menu_url if url_type == 0 else reverse(menu_url)



