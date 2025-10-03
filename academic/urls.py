# academic/urls.py
from django.urls import path

from academic import queries
from . import views

app_name = 'academic'

urlpatterns = [
    #path('results/', views.academic_results, name='results'),
    
    path('login/', views.login_view, name='login'),
    path('main/', views.main_view, name='main'),
    #path('management-dashboard/', views.component_performance, name='management_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    #path('component-performance/', views.component_performance, name='component_performance'),
    #path('student/', views.component_charts, name='component_charts'),
    #path('api/student/', views.component_charts, name='component_charts'),
    path('login/api/student/get-programs/', views.get_programs, name='get_programs'),
    path('login/api/student/get-sessions/', views.get_univ_sessions, name='get_sessions'),
    path('login/api/student/get-students/', queries.get_students, name='get_students'),
   
    
    # New AJAX endpoints for dynamic filtering
    #path('get-sessions/', views.get_sessions, name='get_sessions'),
    #path('get-courses/', views.get_courses, name='get_courses'),
    #path('get-components/', views.get_components, name='get_components'),
    path('api/marks_analysis/', queries.marks_analysis_api, name='marks_analysis_api'),
    path('api/components/', queries.components_api, name='components_api'),
    path('api/components_avg_marks/', queries.components_avg_marks_api, name='components_marks_api'),
    path('api/get_grades/', queries.get_grades, name='get_grades'),
    path('api/get_components_marks/', queries.get_components_marks, name='get_components_marks'),
    path('api/get_sgpa_average/', queries.get_sgpa_average, name='get_sgpa_average'),
    path('api/get_sub_gradepoint/', queries.get_sub_gradepoint, name='get_sub_gradepoint'),
    
    

    #path('student-performance/', views.student_performance, name='student_performance'),
    #path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),


]