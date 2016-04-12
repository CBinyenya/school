__author__ = 'Monte'
from django.conf.urls import url
from django.contrib.auth.views import login, logout
import easy.views

urlpatterns = [
    url(r'^login/$', login),
    url(r'logout/$', easy.views.logout_view, name="logout"),
    url(r'^$', easy.views.my_view, name="home"),
    url(r'student/$', easy.views.student_home_page, name="home"),
    url(r'^teacher/(?P<pk>[0-9]+)/$', easy.views.teacher_home_page, name="teacher"),
    url(r'test/$', easy.views.FormPageView.as_view(), name="test"),
    url(r'tests/$', easy.views.tests_view, name="tests"),
    url(r'statistics/$', easy.views.StatisticsPageView.as_view(), name="statistics"),

    url(r'manage/$', easy.views.ManageStudentsView.as_view(), name="manage"),
    url(r'students/$', easy.views.StudentsPageView.as_view(), name="students"),
    url(r'message/$', easy.views.tests_view, name="message"),

    url(r'create/$', easy.views.CreateTestView.as_view(), name="create"),
    url(r'download/$', easy.views.download_question_excel_view, name="excel_file"),
    url(r'downloads/$', easy.views.download_student_excel_view, name="student_file"),
    url(r'student-uploads/$', easy.views.download_question_excel_view, name="upload_students"),
    url(r'details/$', easy.views.SignUpView.as_view(), name="signup"),
    url(r'profile/(?P<pk>[0-9]+)/$', easy.views.TeachersUpdateView.as_view(), name="teacher_profile"),
]


