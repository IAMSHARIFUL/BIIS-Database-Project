"""CSE_216_Test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import hr.views as hr_views
import student_login.views as student_login_views

urlpatterns = [
    path('admin/', admin.site.urls),
	path('jobs', hr_views.list_jobs),
    path('term_result', hr_views.term_result),
    path('student_marksheet', hr_views.student_marksheet),
    path('marks_are_set', hr_views.marks_are_set),
    path('login',student_login_views.login),
    path('logout',student_login_views.logout),
    path('home', student_login_views.home),
    path('result', student_login_views.result),
    path('go_for_register', student_login_views.go_for_register),
    path('go_for_result', student_login_views.go_for_result),
    path('go_for_drop', student_login_views.go_for_drop),
    path('go_for_ongoing_courses', student_login_views.go_for_ongoing_courses),
    path('go_for_advisor', student_login_views.go_for_advisor),
    path('drop', student_login_views.drop),
    path('homepage', student_login_views.homepage),
    path('course_registration', student_login_views.course_registration),
    path('course_drop', student_login_views.course_drop),
    path('my_courses', student_login_views.my_courses),
    path('my_advisor', student_login_views.my_advisor),
    path('my_result', student_login_views.my_result),
    path('registration', student_login_views.registration),
    path('marksheet_menu',hr_views.marksheet_menu),
    path('select_course',hr_views.select_course),
    path('adminlogin', hr_views.adminlogin),
    path('adminhome', hr_views.home),
    path('get_marksheet', hr_views.get_marksheet),
    path('course_marks_are_set', hr_views.course_marks_are_set),
    path('menu', hr_views.menu),
    path('go_term_result', hr_views.gotermresult),
    path('go_term_result2', hr_views.term_resultsubj),
    path('go_adminlogout', hr_views.logout),
    path('go_opreg', hr_views.opreg),
    path('go_closreg', hr_views.closreg),
    path('go_nxttermbegin', hr_views.termcheng),
    path('update_result', hr_views.update_result),
    #update_result
]
