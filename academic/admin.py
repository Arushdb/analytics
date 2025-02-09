# academic/admin.py
from django.contrib import admin
from .models import ProgramMaster, CourseEvaluationComponent, StudentMarks, StudentMarksSummary

admin.site.register(ProgramMaster)
admin.site.register(CourseEvaluationComponent)
admin.site.register(StudentMarks)
admin.site.register(StudentMarksSummary)