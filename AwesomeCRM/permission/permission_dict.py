from . import permission_hook

# 所有权限的列表
perm_dict = {
    'sale_stu_enrollment': ['stu_enrollment', 'GET', [], {}, permission_hook.permission_clear],
    'sale_enrollment_links': ['enrollment_links', 'GET', [], {}],
    'sale_contract_approve': ['contract_approve', 'GET', [], {}],
    'sale_enrollment_success': ['enrollment_success', 'GET', [], {}],
    'student_my_course': ['my_course', 'GET', [], {}],
    'student_my_class': ['my_class', 'GET', [], {}],
    'student_homework': ['homework', 'GET', [], {}],
    'student_submit_homework': ['submit_homework', 'GET', [], {}],
    'student_course_record': ['course_record', 'GET', [], {}],
    'teacher_manage_class': ['manage_class', 'GET', [], {}],
    'teacher_student_list': ['student_list', 'GET', [], {}],
    'teacher_course_record': ['course_record', 'GET', [], {}],
    'teacher_check_homework': ['check_homework', 'GET', [], {}],
    'teacher_check_homework_detail': ['check_homework_detail', 'GET', [], {}],
    'teacher_download_file': ['download_file', 'GET', [], {}],
}





