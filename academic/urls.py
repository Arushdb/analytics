# academic/urls.py
from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    path('results/', views.academic_results, name='results'),
    path('component-performance/', views.component_performance, name='component_performance'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # New AJAX endpoints for dynamic filtering
    path('get-years/', views.get_years, name='get_years'),
    path('get-courses/', views.get_courses, name='get_courses'),
    path('get-components/', views.get_components, name='get_components'),
    path('student-performance/', views.student_performance, name='student_performance'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),


]