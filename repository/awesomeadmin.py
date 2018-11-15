from awesomeadmin.site import site
from . import models
from awesomeadmin.admin_base import BaseAwesomeAdmin
from teacher import views

# Register your models here.


class CustomerAdmin(BaseAwesomeAdmin):
    list_display = ["id", "name", "contact_type", "contact", "source", "consult_content", "consultant", "status", "date"]
    filter_list = ["contact_type", "status", "consultant", "date"]
    search_fields = ["name", "consultant__name"]
    read_only = ["status", "contact"]
    filter_horizental = ["consult_courses"]
    action = {
        'change_status': "更改状态",
    }

    def change_status(self, request, querysets):
        querysets.update(status=2)


class UserProfileAdmin(BaseAwesomeAdmin):
    list_display = ["name"]


site.register(models.CustomerInfo, CustomerAdmin)
site.register(models.UserProfile, UserProfileAdmin)
site.register(models.Menu)
site.register(models.CustomerFollowUp)
site.register(models.StudyRecord)
site.register(models.CourseRecord, hook_func=views.create_study_record)

