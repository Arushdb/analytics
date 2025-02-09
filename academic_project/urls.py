# academic_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('academic/', include('academic.urls')),
    path('', RedirectView.as_view(url='/academic/results/', permanent=True)),

]