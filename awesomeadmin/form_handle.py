from django.forms import ModelForm


def create_dynamic_model_form(admin_class, form_change=True):
    """
    通过type动态的创建ModelForm类对象
    :param admin_class:
    :param form_change:
    :return:
    """
    class Meta:
        model = admin_class.model
        fields = "__all__"
        # 提交时排除只读字段
        if form_change:     # 如果form_change字段是true，则表示是修改页面，应该显示只读字段
            exclude = admin_class.read_only
            admin_class.form_change = True
        else:
            admin_class.form_change = False     # 如果不是就改变form_change的状态，以便在前端显示

    def __new__(cls, *args, **kwargs):
        # 循环所有的字段
        for filed_name in cls.base_fields:
            field_obj = cls.base_fields[filed_name]
            field_obj.widget.attrs.update({'class': 'form-control'})
        return ModelForm.__new__(cls)

    return type("DynamicModelForm", (ModelForm, ), {"Meta": Meta, '__new__': __new__})








