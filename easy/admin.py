from django.contrib import admin
from models import *
# Register your models here.


class SchoolAdmin(admin.ModelAdmin):
    list_display = ("school_name", "code", "mobile", "email", "head", "credit")
    search_fields = ("school_name", "code", "mobile", "credit")


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "phone", "school", "linkdin", "position")
    search_fields = ("username", "first_name", "last_name", "phone", "position")


class SubjectsAdmin(admin.ModelAdmin):
    list_display = ("subject_name", "class_level")
    search_fields = ("subject_name", "class_level")


class TopicAdmin(admin.ModelAdmin):
    pass


class SchoolLevelAdmin(admin.ModelAdmin):
    pass


class ClassLevelAdmin(admin.ModelAdmin):
    pass


class StreamAdmin(admin.ModelAdmin):
    pass


class DirectorAdmin(admin.ModelAdmin):
    pass


class ExamAdmin(admin.ModelAdmin):
    list_display = ("exam_name", "class_level", "exam_subject", "supervisor", "date_available", "hours", "minutes")
    search_fields = ["exam_name", "class_level__level_name", "exam_subject__subject_name", "supervisor__first_name",
              "date_available"]


class AnswerAdmin(admin.ModelAdmin):
    pass


class QuestionAdmin(admin.ModelAdmin):
    pass


class MultiChoiceAdmin(admin.ModelAdmin):
    list_display = ("question_subject", "question", "number", "correct_answer", "level")
    search_fields = ("question_subject", "question", "number", "correct_answer")


class StudentAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "reg_number", "phone", "stream", "school")
    search_fields = ("username", "first_name", "last_name", "reg_number", "phone")


class ParentsAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "phone")
    search_fields = ("username", "first_name", "last_name", "phone")


class MyAdminSite(admin.AdminSite):
    site_header = "New Stuff"
    site_title = "Easy School"
    index_title = "Administration"
    login_template = "easyschool/registration/login.html"


class CompletedTestsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'test', 'question', 'answer', 'value')

class ResultsAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'student_id', 'total_marks', 'out_off')


class ResultObjectsAdmin(admin.ModelAdmin):
    pass

class StudentUploadsAdmin(admin.ModelAdmin):
    pass


admin.site.register(School, SchoolAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject, SubjectsAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(SchoolLevel, SchoolLevelAdmin)
admin.site.register(ClassLevel, ClassLevelAdmin)
admin.site.register(Stream, StreamAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Parent, ParentsAdmin)
admin.site.register(MultipleChoiceQuestion, MultiChoiceAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(CompletedTests, CompletedTestsAdmin)
admin.site.register(Results, ResultsAdmin)
admin.site.register(ResultObjects, ResultObjectsAdmin)
admin.site.register(StudentUploads, StudentUploadsAdmin)
admin_site = MyAdminSite(name='admin')
admin_site.register(AdminModel)
