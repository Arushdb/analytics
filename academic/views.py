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
from django.utils import timezone



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

# --- Demo data for now (replace with ORM queries later) ---
def _demo_data():
    years = [2021, 2022, 2023, 2024, 2025]
    return {
        "kpis": {
            "total_students": 23580,
            "new_admissions": 4230,
            "pass_rate": 82,
            "dropout_rate": 4,
            "placement_pct": 72,
            "avg_package_lpa": 4.8,
            "fees_collected_cr": 215,
            "pending_dues_cr": 7,
            "scholarship_cr": 18,
            "publications": 420,
            "faculty_student": "1:22",
            "avg_attendance": 72,
        },
        "years": years,
        "enrollment_trend": [
            {"year": str(y), "students": v}
            for y, v in zip(years, [18500, 19600, 21000, 22300, 23580])
        ],
        "category_split": [
            {"name": "GEN", "value": 40},
            {"name": "OBC", "value": 35},
            {"name": "SC", "value": 15},
            {"name": "ST", "value": 5},
            {"name": "EWS", "value": 5},
        ],
        "dept_attendance": [
            {"dept": "CSE", "attendance": 78},
            {"dept": "ECE", "attendance": 74},
            {"dept": "ME", "attendance": 68},
            {"dept": "CE", "attendance": 70},
            {"dept": "B.Com", "attendance": 73},
            {"dept": "MBA", "attendance": 76},
        ],
        "placement_trend": [
            {"year": str(y), "percent": p}
            for y, p in zip(years, [65, 68, 70, 71, 72])
        ],
        "placement_by_program": [
            {"program": "B.Tech", "placed": 78},
            {"program": "MBA", "placed": 70},
            {"program": "B.Com", "placed": 65},
            {"program": "MCA", "placed": 60},
        ],
        "alerts": [
            {"type": "Dropout", "msg": "Dropout > 10% in B.Sc"},
            {"type": "Pass %", "msg": "Pass Rate < 50% in Maths Dept"},
            {"type": "Attendance", "msg": "500 students below 50% attendance"},
        ],
        "generated_at": timezone.now().isoformat(),
    }

# --- Views ---
def top_level_dashboard(request):
    data = _demo_data()
    return render(request, "academic/top_level.html", context=data)

def api_summary(request):
    return JsonResponse(_demo_data())

    


