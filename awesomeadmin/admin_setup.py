from django import conf
from . import site


# 自动执行
def awesomeadmin_auto_descover():
    for app_path in conf.settings.INSTALLED_APPS:
        try:
            app = __import__("%s.awesomeadmin" % app_path)
        except ImportError:
            pass
    # 返回整个全局字典
    return site.site.global_dict




