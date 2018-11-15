class BaseAwesomeAdmin(object):
    """
    Admin基类，如果用户没有自定制Admin，可以使用这个，
    防止Admin为默认值None,导致在给Admin的model赋值时报错
    """
    list_display = []
    filter_list = []
    search_fields = []
    read_only = []
    filter_horizental = []
    action = {}

    def __init__(self):
        self.action.update({'delete_selected': "删除所选列"})

    def delete_selected(self, request, querysets):
        querysets.delete()


