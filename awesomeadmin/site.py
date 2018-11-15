from .admin_base import BaseAwesomeAdmin


# 初始化全局字典
class AwesomeAdmin(object):
    def __init__(self):
        """
        {
            "sale": {
                "CustomerInfo": CustomerInfoAdmin,
            },
        }
        """
        self.global_dict = {}

    def register(self, model_class, admin_class=None, hook_func=None):
        """
        注册表
        :param model_class:
        :param admin_class:
        :param hook_func:
        :return:
        """
        app_name = model_class._meta.app_label     # 获取所在app的名字
        table_name = model_class._meta.model_name  # 获取表名
        # 实例化admin_class,避免素有使用BaseAdmin的表使用同一段内存
        admin_class = BaseAwesomeAdmin() if not admin_class else admin_class()
        # 将model中的类与自定义的相关admin进行绑定，方便视图函数去model下取数据
        admin_class.model = model_class
        # 将钩子函数绑定
        admin_class.hook_func = hook_func
        # 将该app的信息放到全局字典中，前提是该app没有在全局字典中注册
        if app_name not in self.global_dict:
            self.global_dict[app_name] = {}
        # 将该表的Admin的相关信息放到全局字典的app下的字典中
        self.global_dict[app_name][table_name] = admin_class


# 实例化AwesomeAdmin,方便调用
site = AwesomeAdmin()




