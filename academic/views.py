from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from academic.decorators import login_required
from academic.forms import LoginForm
from django.db.models.functions import ExtractYear
from django.db.models import Q, Avg, Count
from django.views.decorators.http import require_GET

from academic.models import CourseEvaluationComponent, ProgramMaster,StudentMarks 
from academic.models import StudentMarksSummary,Universitymaster
from academic.queries import get_components_marks, get_user
from academic.utils import analyze_marks


#@ensure_csrf_cookie
def login_view(request):
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print("Test Arush")
        print(form)
        if form.is_valid:
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user=get_user(username,password)
            if user:
                #request.session['user_id']="username"
                request.session['user_id'] = username
                #return redirect('academic:get_programs')  # Redirect to the component performance page
                return render(request, 'academic/nav-main.html', {"username":username})
            else:
                messages.error(request, "Invalid username or password.")
                              
            
    else:
        form = LoginForm()
    return render(request, 'academic/login.html', {'form': form})


@login_required
def get_programs(request):

    qs= ProgramMaster.objects.filter(
              Q(active='Y')
            ).values_list('program_id','program_name')
    programs=[]
    for pid, pname in qs:
        programs.append({'id': pid, 'name': pname})
        
    return JsonResponse({"programs":programs})
    #sessions = get_sessions()
    #context = {
    #        'items':programs,
    #        'years':sessions
    #         # Make all components available for selection
             
    #    }
    #return render(request, 'academic/component_performance.html', context)

def main_view(request):
    return render(request, 'academic/main.html', {})

@login_required

           

    
def logout_view(request):
    request.session.flush()  # Clear the session
    return redirect('academic:login')  # Redirect to login page


def get_sessions():
    sessions = Universitymaster.objects.order_by('-start_date')[:5]
    
    year_ranges = [(r.start_date.strftime("%Y-%m-%d"),f"{r.start_date.year}-{r.end_date.year}") for r in sessions]
    print(year_ranges)
    return year_ranges
    # return JsonResponse({
    #         'years': year_ranges,
            
    #     })
def get_univ_sessions(request):
    sessions = Universitymaster.objects.order_by('-start_date')[:5]
    
    year_ranges = [f"{r.start_date.year}-{r.end_date.year}" for r in sessions]
    return JsonResponse({
             'years': year_ranges})
    


