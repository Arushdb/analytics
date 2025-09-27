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
from academic.queries import get_user


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
def component_performance(request):
    try:
        #items=request.session.pop('temp_data',None)

        #years=items.sessions
        
        # Predefined evaluation components
        #all_components = ['CT1', 'CT2', 'DA1', 'DA2', 'EXT', 'REM', 'ATT', 'AA']

        # Get filter parameters from request
        #myitems=request.GET.get('items')
        #courses_query=[]
        #print(myitems)
        #items = request.GET.get('items', '')
        #years = request.GET.get('sessions', '')
        #sessions = get_sessions()

        selected_program = request.GET.get('program', '')
        selected_year = request.GET.get('year', '')
        
        selected_course = request.GET.get('course', '')
        #courses = request.GET.get('courses', '')
        selected_components = request.GET.getlist('evaluation_components')
        #print(selected_year)
        #courses=[]
        #if (selected_program and selected_year):

        #    courses=fetch_courses(selected_program,selected_year)
            
        
        # Base context setup
        context = {
            #'items': ProgramMaster.objects.filter(
             # Q(active='Y')
            #).values_list('program_id','program_name'),
            'program':selected_program,
            'selected_program': selected_program,
            
            #'courses': [],
            'selected_year': selected_year,
            'selected_course': selected_course,
           
            'selected_components': selected_components,
             # Make all components available for selection
        }
        #context['items'] = items
        #context['years'] = years
        #print(context.items)
        

        # Program validation and retrieval
        #try:
        #    program_obj = ProgramMaster.objects.get(
        #        program_name=selected_program, 
        #        active='Y'
        #    )
        #except ProgramMaster.DoesNotExist:
        #    context['error_message'] = "Invalid program selected."
        #    return render(request, 'academic/component_performance.html', context)

        #Get years
        #if not selected_year:
        #    return render(request, 'academic/component_performance.html', context)

        #if not selected_program  :
        #    return render(request, 'academic/component_performance.html', context)

        #print("test years", context['years'],"selected year",selected_year)
        #years_query = StudentMarksSummary.objects.filter(
        #    program_course_key__startswith=selected_program
        #).annotate(
        #    year=ExtractYear('semester_start_date')
        #).values_list('year', flat=True).distinct()
        
        #context['years'] = sorted(list(years_query))
        
        #print(context)

        #if not selected_year:
        #    return render(request, 'academic/component_performance.html', context)

        # Year validation
        #try:
        #    selected_year = int(selected_year)
        #    if selected_year not in context['years']:
        #        context['error_message'] = "Invalid year selected."
        #        return render(request, 'academic/component_performance.html', context)
        #except (ValueError, TypeError):
        #    context['error_message'] = "Invalid year format."
        #    return render(request, 'academic/component_performance.html', context)

        # Get courses
        #selected_date = datetime.strptime(selected_year, "%Y-%m-%d").date()
        #courses_query = StudentMarksSummary.objects.filter(
        #    program_course_key__startswith=selected_program,
        #    semester_start_date__year=selected_date
        #).values_list('course_code', flat=True).distinct()
        
        #context['courses'] = list(courses_query)

        if not selected_course or not selected_components:
            return render(request, 'academic/component_performance.html', context)

        # Course validation
        #if selected_course not in context['courses']:
        #    context['error_message'] = "Invalid course selected."
        #    return render(request, 'academic/component_performance.html', context)

        # Fetch and process component data
        evaluation_components = CourseEvaluationComponent.objects.filter(
            course_code=selected_course,
            program_id=selected_program,
            evaluation_id_name__in=selected_components
        ).values('evaluation_id', 'evaluation_id_name', 'maximum_marks')
        print(evaluation_components)

        # Calculate performance metrics for selected components
        component_performance = {}
        for component in evaluation_components:
            avg_marks = StudentMarks.objects.filter(
                evaluation_id=component['evaluation_id'],
                course_code=selected_course,
                program_course_key__startswith=selected_program
            ).aggregate(Avg('marks'))['marks__avg'] or 0
            
            component_performance[component['evaluation_id_name']] = round(avg_marks, 2)

        # Prepare chart data
        context['component_performance'] = {
            'labels': list(component_performance.keys()),
            'data': list(component_performance.values())
        }

        # Calculate grade distribution for the course
        
        year = int(selected_year[:4])
        grade_distribution = StudentMarksSummary.objects.filter(
            course_code=selected_course,
            semester_start_date__year=year,
            program_course_key__startswith=selected_program
        ).values('internal_grade').annotate(
            count=Count('roll_number')
        ).filter(internal_grade__isnull=False)

        # Prepare grade distribution data
        context['grade_distribution'] = {
            'labels': [grade['internal_grade'] for grade in grade_distribution],
            'data': [grade['count'] for grade in grade_distribution]
        }

        # Add summary statistics
        context.update({
            'total_students': StudentMarksSummary.objects.filter(
                course_code=selected_course,
                semester_start_date__year=year,
                program_course_key__startswith=selected_program
            ).count(),
            'course_details': {
                'course_code': selected_course,
                'program_name': selected_program,
                'academic_year': selected_year
            }
        })
        # Get unique roll numbers first
        unique_roll_numbers = StudentMarks.objects.filter(
            evaluation_id__in=[component['evaluation_id'] for component in evaluation_components],
            course_code=selected_course,
            program_course_key__startswith=selected_program
        ).values_list('roll_number', flat=True).distinct().order_by('roll_number')

        # Initialize datasets for each component
        component_datasets = {}
        for component in evaluation_components:
            marks_data = StudentMarks.objects.filter(
                evaluation_id=component['evaluation_id'],
                course_code=selected_course,
                program_course_key__startswith=selected_program
            ).order_by('roll_number').values('roll_number', 'marks')
            
            # Create a dictionary mapping roll numbers to marks
            marks_dict = {entry['roll_number']: entry['marks'] for entry in marks_data}
            
            # Ensure we have data for all roll numbers (use 0 for missing data)
            component_marks = [marks_dict.get(roll_number, 0) for roll_number in unique_roll_numbers]
            
            component_datasets[component['evaluation_id_name']] = component_marks

        # Prepare the line chart data structure
        context['line_chart_data'] = {
            'roll_numbers': list(unique_roll_numbers),
            'datasets': [{
                'label': component_name,
                'data': marks_list
            } for component_name, marks_list in component_datasets.items()]
        }

        scatter_datasets = []
        for component_name, marks_list in component_datasets.items():
            scatter_data = [
                {'x': str(roll_number), 'y': marks} 
                for roll_number, marks in zip(unique_roll_numbers, marks_list) 
                if marks > 0
            ]
            scatter_datasets.append({
            'label': component_name,
            'data': scatter_data
            })

        context['scatter_chart_data'] = {
    'datasets': scatter_datasets
}
   
        #return redirect(request, 'academic:component_performance', context)   
        return render(request, 'academic/component_charts.html', context)   
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in component_performance: {str(e)}", exc_info=True)
        
        context = {
            'error_message': f'An unexpected error occurred: {str(e)}',
            'programs': ProgramMaster.objects.filter(
                Q(program_name__icontains='Bsc') & 
                Q(active='Y')
            ).values_list('program_name', flat=True).distinct(),
        }
        return render(request, 'academic/component_performance.html', context)

           

    
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
    

@login_required
@require_GET
def get_courses(request):
    """
    Get available courses for a given program and year
    """
    
    program = request.GET.get('program', '')
    startsession = request.GET.get('year', '')
    endsession =  startsession[:4]
    endsession = str(int(endsession[:4]) + 1)
    endsession = endsession + "-06-30"
    startsession=datetime.strptime(startsession, "%Y-%m-%d").date()
    endsession=datetime.strptime(endsession, "%Y-%m-%d").date()
    
    
    
    
    print(endsession)
    print(program)
    
    
    try:
        # Get program ID
        #program_obj = ProgramMaster.objects.get(
        #    program_id=program, 
        #    active='Y'
        #)

        # Get courses
        courses_query = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program,
            semester_start_date__range=(startsession,endsession)
        ).values_list('course_code', flat=True).distinct()
        
        courses = list(courses_query)
        print(connection.queries)
        
        return JsonResponse({
            'courses': courses,
            'status': 'success'
        })
    
    except ProgramMaster.DoesNotExist:
        return JsonResponse({
            'error': 'Invalid program',
            'status': 'error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def fetch_courses(program,startsession):
    """
    Get available courses for a given program and year
    """
    
    ##program = request.GET.get('program', '')
    ##startsession = request.GET.get('year', '')
    endsession =  startsession[:4]
    endsession = str(int(endsession[:4]) + 1)
    endsession = endsession + "-06-30"
    startsession=datetime.strptime(startsession, "%Y-%m-%d").date()
    endsession=datetime.strptime(endsession, "%Y-%m-%d").date()
    
    
    
    
    print(endsession)
    print(program)
    
    
    try:
        # Get program ID
        program_obj = ProgramMaster.objects.get(
            program_id=program, 
            active='Y'
        )

        # Get courses
        courses_query = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program_obj.program_id,
            semester_start_date__range=(startsession,endsession)
        ).values_list('course_code', flat=True).distinct()
        
        courses = list(courses_query)
        print(connection.queries)
        return courses
        #return JsonResponse({
        #    'courses': courses,
        #    'status': 'success'
        #})
    
    except ProgramMaster.DoesNotExist:
        return JsonResponse({
            'error': 'Invalid program',
            'status': 'error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


@login_required
@require_GET
def get_components(request):
    """
    Get available evaluation components for a given program and course
    """
    program = request.GET.get('program', '')
    course = request.GET.get('course', '')
    
    try:
        # Get program ID
        program_obj = ProgramMaster.objects.get(
            program_id=program, 
            active='Y'
        )

        # Get evaluation components
        components_query = CourseEvaluationComponent.objects.filter(
            course_code=course,
            program_id=program
        ).values_list('evaluation_id_name', flat=True).distinct()
        
        components = list(components_query)
        
        return JsonResponse({
            'components': components,
            'status': 'success'
        })
    
    except ProgramMaster.DoesNotExist:
        return JsonResponse({
            'error': 'Invalid program',
            'status': 'error'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)
"""
def get_average(request):
     # Calculate performance metrics for selected components
        component_performance = {}
        for component in evaluation_components:
            avg_marks = StudentMarks.objects.filter(
                evaluation_id=component['evaluation_id'],
                course_code=selected_course,
                program_course_key__startswith=selected_program
            ).aggregate(Avg('marks'))['marks__avg'] or 0
            
            component_performance[component['evaluation_id_name']] = round(avg_marks, 2)

        # Prepare chart data
        context['component_performance'] = {
            'labels': list(component_performance.keys()),
            'data': list(component_performance.values())
        }
def get_grades(request):
      # Calculate grade distribution for the course
        
        year = int(selected_year[:4])
        grade_distribution = StudentMarksSummary.objects.filter(
            course_code=selected_course,
            semester_start_date__year=year,
            program_course_key__startswith=selected_program
        ).values('internal_grade').annotate(
            count=Count('roll_number')
        ).filter(internal_grade__isnull=False)

        # Prepare grade distribution data
        context['grade_distribution'] = {
            'labels': [grade['internal_grade'] for grade in grade_distribution],
            'data': [grade['count'] for grade in grade_distribution]
        }
def get_summary(request):
      # Add summary statistics
        context.update({
            'total_students': StudentMarksSummary.objects.filter(
                course_code=selected_course,
                semester_start_date__year=year,
                program_course_key__startswith=selected_program
            ).count(),
            'course_details': {
                'course_code': selected_course,
                'program_name': selected_program,
                'academic_year': selected_year
            }
        })
def get_student_marks(request):
    # Get unique roll numbers first

    unique_roll_numbers = StudentMarks.objects.filter(evaluation_id__in=[component['evaluation_id'] for component in evaluation_components],        course_code=selected_course,
            program_course_key__startswith=selected_program
        ).values_list('roll_number', flat=True).distinct().order_by('roll_number')

        # Initialize datasets for each component
        component_datasets = {}
        for component in evaluation_components:
            marks_data = StudentMarks.objects.filter(
                evaluation_id=component['evaluation_id'],
                course_code=selected_course,
                program_course_key__startswith=selected_program
            ).order_by('roll_number').values('roll_number', 'marks')
            
            # Create a dictionary mapping roll numbers to marks
            marks_dict = {entry['roll_number']: entry['marks'] for entry in marks_data}
            
            # Ensure we have data for all roll numbers (use 0 for missing data)
            component_marks = [marks_dict.get(roll_number, 0) for roll_number in unique_roll_numbers]
            
            component_datasets[component['evaluation_id_name']] = component_marks

        # Prepare the line chart data structure
        context['line_chart_data'] = {
            'roll_numbers': list(unique_roll_numbers),
            'datasets': [{
                'label': component_name,
                'data': marks_list
            } for component_name, marks_list in component_datasets.items()]
        }
                 scatter_datasets = []
        for component_name, marks_list in component_datasets.items():
            scatter_data = [
                {'x': str(roll_number), 'y': marks} 
                for roll_number, marks in zip(unique_roll_numbers, marks_list) 
                if marks > 0
            ]
            scatter_datasets.append({
            'label': component_name,
            'data': scatter_data
            })

        context['scatter_chart_data'] = {
                                'datasets': scatter_datasets
}
"""


