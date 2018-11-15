from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from . import models

# Register your models here.


class UserCreationForm(forms.ModelForm):
    """创建用户时的表单"""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.UserProfile
        fields = ('email', 'name', "role")

    def clean_password2(self):
        """
        检查两次密码输入是否一致
        :return:
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """
        将密码hash后保存
        :param commit:
        :return:
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """用户修改用户的表单"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.UserProfile
        fields = ('email', 'password', 'name', 'is_active', 'is_superuser', "role")

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(UserAdmin):
    """UserProfile的admin配置类"""
    form = UserChangeForm   # Tip: 用于修改的表单
    add_form = UserCreationForm   # Tip: 用于创建的表单

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_superuser', "role", "groups", "user_permissions")}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')},
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ("role", "user_permissions", "groups")


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_type", "contact", "source", "consult_content", "consultant", "status", "date"]
    list_filter = ["name", "consultant", "contact_type", "date"]
    search_fields = ["contact", "consultant__name"]
    filter_horizontal = ['consult_courses']


admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Role)
admin.site.register(models.CustomerInfo, CustomerAdmin)
admin.site.register(models.Student)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.Course)
admin.site.register(models.ClassList)
admin.site.register(models.CourseRecord)
admin.site.register(models.StudyRecord)
admin.site.register(models.Branch)
admin.site.register(models.Menu)
admin.site.register(models.StudentEnrollment)
admin.site.register(models.ContractTemplate)


