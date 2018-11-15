from django.core.exceptions import ValidationError
from django.forms import ModelForm
from repository import models

# 生成model form类


class CustomerForm(ModelForm):
    """
    关于客户的表单
    """
    class Meta:
        model = models.CustomerInfo
        fields = "__all__"
        exclude = ["consult_content"]
        read_only = ["contact_type", "contact", "source", "referral_from", "consult_courses", "consultant", "status"]

    def __new__(cls, *args, **kwargs):
        # 循环所有字段添加样式
        for field in cls.base_fields:
            field_obj = cls.base_fields[field]
            if field in cls.Meta.read_only:
                field_obj.widget.attrs.update({"disabled": "disabled"})
            field_obj.widget.attrs.update({'class': 'form-control'})
        return ModelForm.__new__(cls)

    def clean(self):
        """
        重写clean方法，验证不能修改的字段是否被用户修改了
        如果修改了，给用户报错
        :return:
        """
        if self.errors:
            raise ValidationError("某些字段错误错误")
        if self.instance.id is not None:    # id不为空说明在修改数据
            for field in self.Meta.read_only:
                new_field_val = self.cleaned_data.get(field)   # 用户提交的数据
                if self.Meta.model._meta.get_field(field) in self.instance._meta.many_to_many:  # 如果当前字段是many2many字段
                    old_field_val = getattr(self.instance, field).all()
                    if set(old_field_val) - set(new_field_val):     # 差集不为空，说明修改了数据
                        self.add_error(field, "这个字段不能被修改")
                else:
                    old_field_val = getattr(self.instance, field)  # 数据库中原来的数据
                    if not old_field_val == new_field_val:    # 如果不同，说明不能修改的字段被更改了
                        self.add_error(field, "这个字段不能被修改")


class StudentEnrollmentForm(ModelForm):
    class Meta:
        model = models.StudentEnrollment
        fields = "__all__"
        exclude = ["contract_approved_date"]
        read_only = ["customer", "class_grade", "consultant", "contract_signed_date"]

    def __new__(cls, *args, **kwargs):
        # 循环所有字段
        for field in cls.base_fields:
            field_obj = cls.base_fields[field]
            if field in cls.Meta.read_only:
                field_obj.widget.attrs.update({"disabled": "disabled"})
            field_obj.widget.attrs.update({"class": "form-control"})
        return ModelForm.__new__(cls)



