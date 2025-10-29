# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...
    path('api/subject/<int:program_id>/<int:year>/<int:subject_id>/', views.subject_detail_api, name='subject_detail_api'),
    path('api/teacher/<int:teacher_id>/performance/', views.teacher_performance_api, name='teacher_performance_api'),
]
