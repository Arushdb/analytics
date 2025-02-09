from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_GET
from django.db.models import Q, Avg, Count
from django.db.models.functions import ExtractYear
from django.shortcuts import render
from django.contrib import messages
from django.db import connection
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import ExtractYear
# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InstructorCourse, StudentMarks, StudentMarksSummary

import json
import logging
from .models import (
    ProgramMaster,
    CourseEvaluationComponent,
    StudentMarks,
    StudentMarksSummary,
    User,
    StudentRegistrationSemesterHeader,
    ProgramCourseHeader  
)
from .forms import LoginForm
from .decorators import login_required


@login_required
@require_GET
def get_years(request):
    """
    Get available academic years for a given program
    """
    program = request.GET.get('program', '')
    
    try:
        # Get program ID
        program_obj = ProgramMaster.objects.get(
            program_name=program, 
            active='Y'
        )

        # Get years
        years_query = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program_obj.program_id
        ).annotate(
            year=ExtractYear('semester_start_date')
        ).values_list('year', flat=True).distinct()
        
        years = sorted(list(years_query))
        
        return JsonResponse({
            'years': years,
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

@login_required
@require_GET
def get_courses(request):
    """
    Get available courses for a given program and year
    """
    program = request.GET.get('program', '')
    year = request.GET.get('year', '')
    
    try:
        # Get program ID
        program_obj = ProgramMaster.objects.get(
            program_name=program, 
            active='Y'
        )

        # Get courses
        courses_query = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program_obj.program_id,
            semester_start_date__year=year
        ).values_list('course_code', flat=True).distinct()
        
        courses = list(courses_query)
        
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
            program_name=program, 
            active='Y'
        )

        # Get evaluation components
        components_query = CourseEvaluationComponent.objects.filter(
            course_code=course,
            program_id=program_obj.program_id
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


    
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username, password=password)
                request.session['user_id'] = user.id  # Store user ID in session
                return redirect('academic:component_performance')  # Redirect to the component performance page
            except User.DoesNotExist:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'academic/login.html', {'form': form})

def logout_view(request):
    request.session.flush()  # Clear the session
    return redirect('academic:login')  # Redirect to login page

@login_required
def course_performance(request):
    # Get unique academic years and course codes for the filter
    academic_years = StudentMarksSummary.objects.dates('semester_start_date', 'year')
    course_codes = StudentMarksSummary.objects.values_list('course_code', flat=True).distinct()
    
    selected_year = request.GET.get('year')
    selected_course = request.GET.get('course')
    
    context = {
        'academic_years': academic_years,
        'course_codes': course_codes,
        'selected_year': selected_year,
        'selected_course': selected_course,
    }
    
    return render(request, 'academic/course_performance.html', context)

@login_required
def component_performance(request):
    try:
        # Predefined evaluation components
        all_components = ['CT1', 'CT2', 'DA1', 'DA2', 'EXT', 'REM', 'ATT', 'AA']

        # Get filter parameters from request
        selected_program = request.GET.get('program', '')
        selected_year = request.GET.get('year', '')
        selected_course = request.GET.get('course_code', '')
        selected_components = request.GET.getlist('evaluation_components')

        # Base context setup
        context = {
            'programs': ProgramMaster.objects.filter(
                Q(program_name__icontains='B.TECH') & 
                Q(active='Y')
            ).values_list('program_name', flat=True).distinct(),
            'selected_program': selected_program,
            'years': [],
            'courses': [],
            'selected_year': selected_year,
            'selected_course': selected_course,
            'all_components': all_components,
            'selected_components': selected_components,
            'evaluation_components': all_components,  # Make all components available for selection
        }

        if not selected_program:
            return render(request, 'academic/component_performance.html', context)

        # Program validation and retrieval
        try:
            program_obj = ProgramMaster.objects.get(
                program_name=selected_program, 
                active='Y'
            )
        except ProgramMaster.DoesNotExist:
            context['error_message'] = "Invalid program selected."
            return render(request, 'academic/component_performance.html', context)

        # Get years
        years_query = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program_obj.program_id
        ).annotate(
            year=ExtractYear('semester_start_date')
        ).values_list('year', flat=True).distinct()
        
        context['years'] = sorted(list(years_query))

        if not selected_year:
            return render(request, 'academic/component_performance.html', context)

        # Year validation
        try:
            selected_year = int(selected_year)
            if selected_year not in context['years']:
                context['error_message'] = "Invalid year selected."
                return render(request, 'academic/component_performance.html', context)
        except (ValueError, TypeError):
            context['error_message'] = "Invalid year format."
            return render(request, 'academic/component_performance.html', context)

        # Get courses
        courses_query = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program_obj.program_id,
            semester_start_date__year=selected_year
        ).values_list('course_code', flat=True).distinct()
        
        context['courses'] = list(courses_query)

        if not selected_course or not selected_components:
            return render(request, 'academic/component_performance.html', context)

        # Course validation
        if selected_course not in context['courses']:
            context['error_message'] = "Invalid course selected."
            return render(request, 'academic/component_performance.html', context)

        # Fetch and process component data
        evaluation_components = CourseEvaluationComponent.objects.filter(
            course_code=selected_course,
            program_id=program_obj.program_id,
            evaluation_id_name__in=selected_components
        ).values('evaluation_id', 'evaluation_id_name', 'maximum_marks')

        # Calculate performance metrics for selected components
        component_performance = {}
        for component in evaluation_components:
            avg_marks = StudentMarks.objects.filter(
                evaluation_id=component['evaluation_id'],
                course_code=selected_course,
                program_course_key__startswith=program_obj.program_id
            ).aggregate(Avg('marks'))['marks__avg'] or 0
            
            component_performance[component['evaluation_id_name']] = round(avg_marks, 2)

        # Prepare chart data
        context['component_performance'] = {
            'labels': list(component_performance.keys()),
            'data': list(component_performance.values())
        }

        # Calculate grade distribution for the course
        grade_distribution = StudentMarksSummary.objects.filter(
            course_code=selected_course,
            semester_start_date__year=selected_year,
            program_course_key__startswith=program_obj.program_id
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
                semester_start_date__year=selected_year,
                program_course_key__startswith=program_obj.program_id
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
            program_course_key__startswith=program_obj.program_id
        ).values_list('roll_number', flat=True).distinct().order_by('roll_number')

        # Initialize datasets for each component
        component_datasets = {}
        for component in evaluation_components:
            marks_data = StudentMarks.objects.filter(
                evaluation_id=component['evaluation_id'],
                course_code=selected_course,
                program_course_key__startswith=program_obj.program_id
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

        return render(request, 'academic/component_performance.html', context)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in component_performance: {str(e)}", exc_info=True)
        
        context = {
            'error_message': f'An unexpected error occurred: {str(e)}',
            'programs': ProgramMaster.objects.filter(
                Q(program_name__icontains='B.TECH') & 
                Q(active='Y')
            ).values_list('program_name', flat=True).distinct(),
        }
        return render(request, 'academic/component_performance.html', context)
def generate_colors(n):
    """Generate n distinct colors"""
    colors = []
    for i in range(n):
        hue = i * 360 // n
        colors.append(f'hsl({hue}, 70%, 50%)')
    return colors

def process_marks_data(marks_data, summary_data, eval_components, selected_program, program, selected_course, selected_year):
    """
    Helper function to process marks data and create consolidated records with PCK-wise analysis
    """
    # Create evaluation ID to name mapping
    eval_name_lookup = {
        comp['evaluation_id']: comp['evaluation_id_name']
        for comp in eval_components
    }

    # Create marks lookup by PCK, roll number and evaluation
    marks_lookup = {}
    for mark in marks_data:
        pck = mark['program_course_key']
        roll_num = mark['roll_number']
        if pck not in marks_lookup:
            marks_lookup[pck] = {}
        if roll_num not in marks_lookup[pck]:
            marks_lookup[pck][roll_num] = {}
        marks_lookup[pck][roll_num][mark['evaluation_id']] = mark['marks']

    # Process consolidated data
    consolidated_data = []
    for summary in summary_data:
        roll_number = summary['roll_number']
        pck = summary['program_course_key']
        student_marks = marks_lookup.get(pck, {}).get(roll_number, {})
        
        eval_details = []
        for eval_type in ['CT1', 'CT2', 'DA1', 'DA2', 'AA', 'ATT', 'EXT', 'REM']:
            eval_id = next(
                (k for k, v in eval_name_lookup.items() if v == eval_type),
                None
            )
            if eval_id:
                max_marks = next(
                    (comp['maximum_marks'] for comp in eval_components 
                     if comp['evaluation_id'] == eval_id),
                    0
                )
                eval_details.append({
                    'evaluation_name': eval_type,
                    'marks_obtained': student_marks.get(eval_id),
                    'maximum_marks': max_marks
                })

        record = {
            'program_name': selected_program,
            'program_type': 'Full-Time' if program.program_type == 'F' else 'Part-Time',
            'course_code': selected_course,
            'year': selected_year,
            'roll_number': roll_number,
            'program_course_key': pck,
            'internal_marks': summary['total_internal'],
            'external_marks': summary['total_external'],
            'total_marks': summary['total_marks'],
            'grades': summary['internal_grade'],
            'credits_earned': summary['earned_credits'],
            'evaluation_details': eval_details
        }
        
        consolidated_data.append(record)

    return consolidated_data

def process_charts_data(consolidated_data, selected_components):
    """
    Process data for all charts
    """
    # Grade Distribution
    grade_counts = {}
    for record in consolidated_data:
        grade = record['grades']
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    grade_data = [
        {'grade': grade, 'count': count}
        for grade, count in sorted(grade_counts.items())
    ]

    # Group by PCK for trend analysis
    pck_groups = {}
    for record in consolidated_data:
        pck = record['program_course_key']
        if pck not in pck_groups:
            pck_groups[pck] = []
        pck_groups[pck].append(record)
    
    # Component Performance Trend
    trend_data = {
        'labels': selected_components,
        'datasets': []
    }
    
    # Create datasets for each PCK
    colors = generate_colors(len(pck_groups))
    for i, (pck, records) in enumerate(pck_groups.items()):
        averages = []
        for component in selected_components:
            component_scores = [
                next((detail['marks_obtained'] for detail in record['evaluation_details']
                      if detail['evaluation_name'] == component), 0)
                for record in records
            ]
            avg = sum(filter(None, component_scores)) / len(list(filter(None, component_scores))) if any(component_scores) else 0
            averages.append(avg)
        
        trend_data['datasets'].append({
            'label': f'PCK: {pck}',
            'data': averages,
            'borderColor': colors[i],
            'fill': False
        })

    # Roll Number Performance Data
    roll_data = {
        'labels': [record['roll_number'] for record in consolidated_data],
        'datasets': [{
            'label': 'Total Marks',
            'data': [record['total_marks'] for record in consolidated_data],
            'borderColor': 'rgb(75, 192, 192)',
            'fill': False
        }]
    }

    # Component Distribution (Radar) Data
    component_data = {
        'labels': selected_components,
        'datasets': []
    }
    
    for pck, records in pck_groups.items():
        avg_scores = []
        for component in selected_components:
            scores = [
                next((detail['marks_obtained'] for detail in record['evaluation_details']
                      if detail['evaluation_name'] == component), 0)
                for record in records
            ]
            avg = sum(filter(None, scores)) / len(list(filter(None, scores))) if any(scores) else 0
            avg_scores.append(avg)
        
        component_data['datasets'].append({
            'label': f'PCK: {pck}',
            'data': avg_scores,
            'backgroundColor': f'rgba(75, 192, 192, 0.2)',
            'borderColor': f'rgb(75, 192, 192)',
            'pointBackgroundColor': f'rgb(75, 192, 192)'
        })

    # Scatter Plot Data
    scatter_data = []
    for component in selected_components:
        for record in consolidated_data:
            score = next((detail['marks_obtained'] for detail in record['evaluation_details']
                         if detail['evaluation_name'] == component), None)
            if score is not None:
                scatter_data.append({
                    'x': component,
                    'y': score,
                    'roll_number': record['roll_number']
                })

    return {
        'grade_data': grade_data,
        'trend_data': trend_data,
        'roll_data': roll_data,
        'component_data': component_data,
        'scatter_data': scatter_data
    }

@login_required
def academic_results(request):
    logger = logging.getLogger(__name__)
    try:
        # Get filter parameters from request
        selected_program = request.GET.get('program', '')
        selected_year = request.GET.get('year', '')
        selected_course = request.GET.get('course_code', '')
        selected_pck = request.GET.get('pck', '')
        
        # Get selected evaluation components from request
        default_components = ['CT1', 'CT2', 'DA1', 'DA2', 'AA', 'ATT', 'EXT', 'REM']
        selected_components = request.GET.getlist('eval_components') or []

        # Initialize base context
        context = {
            'programs': ProgramMaster.objects.filter(
                Q(program_name__icontains='B.TECH') & 
                Q(active='Y')
            ).values_list('program_name', flat=True).distinct(),
            'selected_program': selected_program,
            'years': [],
            'courses': [],
            'pcks': [],
            'eval_components': default_components,
            'selected_components': selected_components,
        }

        if not selected_program:
            return render(request, 'academic/results.html', context)

        try:
            program = ProgramMaster.objects.get(program_name=selected_program)
        except ProgramMaster.DoesNotExist:
            context['error_message'] = 'Selected program not found.'
            return render(request, 'academic/results.html', context)

        # Get available years
        years_query = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program.program_id
        ).annotate(
            year=ExtractYear('semester_start_date')
        ).values_list('year', flat=True).distinct()

        context.update({
            'years': sorted(list(years_query)),
            'selected_year': selected_year
        })

        if not selected_year:
            return render(request, 'academic/results.html', context)

        # Get available courses
        courses = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program.program_id,
            semester_start_date__year=selected_year
        ).values_list('course_code', flat=True).distinct()

        # Get available PCKs for filtering
        pcks = StudentMarksSummary.objects.filter(
            program_course_key__startswith=program.program_id,
            semester_start_date__year=selected_year,
            course_code=selected_course if selected_course else None
        ).values_list('program_course_key', flat=True).distinct()

        context.update({
            'courses': sorted(list(courses)),
            'selected_course': selected_course,
            'pcks': sorted(list(pcks)),
            'selected_pck': selected_pck
        })

        if not selected_course:
            return render(request, 'academic/results.html', context)

        # Get all evaluation components for the course
        eval_components = CourseEvaluationComponent.objects.filter(
            program_id=program.program_id,
            course_code=selected_course
        ).values('evaluation_id', 'evaluation_id_name', 'maximum_marks')

        # Base query for marks
        marks_query = StudentMarks.objects.filter(
            course_code=selected_course,
            semester_start_date__year=selected_year,
            program_course_key__startswith=program.program_id
        )

        if selected_pck:
            marks_query = marks_query.filter(program_course_key=selected_pck)

        # Get all marks data
        marks_data = marks_query.values(
            'roll_number', 'evaluation_id', 'marks',
            'program_course_key', 'semester_start_date'
        )

        # Get summary data
        summary_query = StudentMarksSummary.objects.filter(
            course_code=selected_course,
            semester_start_date__year=selected_year,
            program_course_key__startswith=program.program_id
        )

        if selected_pck:
            summary_query = summary_query.filter(program_course_key=selected_pck)

        summary_data = summary_query.values(
            'roll_number', 'program_course_key',
            'total_internal', 'total_external', 'total_marks',
            'internal_grade', 'earned_credits'
        )

        # Process consolidated data
        consolidated_data = process_marks_data(
            marks_data, summary_data, eval_components,
            selected_program, program, selected_course,
            selected_year
        )

        # Process data for all charts
        charts_data = process_charts_data(consolidated_data, selected_components)

        # Calculate PCK-wise averages for original chart
        pck_eval_averages = {}
        for pck in pcks:
            pck_marks = [m for m in marks_data if m['program_course_key'] == pck]
            pck_eval_averages[pck] = {}
            
            for eval_comp in eval_components:
                eval_id = eval_comp['evaluation_id']
                eval_name = eval_comp['evaluation_id_name']
                
                if selected_components and eval_name in selected_components:
                    marks_for_eval = [m['marks'] for m in pck_marks if m['evaluation_id'] == eval_id]
                    
                    if marks_for_eval:
                        pck_eval_averages[pck][eval_name] = {
                            'average': round(sum(marks_for_eval) / len(marks_for_eval), 2),
                            'maximum': eval_comp['maximum_marks'],
                            'pck': pck
                        }

        # Prepare original chart data
        chart_data = []
        for component in selected_components:
            component_data = {
                'component': component,
                'pcks': [
                    {
                        'pck': pck,
                        'average': pck_eval_averages[pck].get(component, {}).get('average', 0),
                        'maximum': pck_eval_averages[pck].get(component, {}).get('maximum', 0)
                    }
                    for pck in pcks
                ]
            }
            chart_data.append(component_data)

        # Update context with all data
        context.update({
            'consolidated_data': consolidated_data,
            'total_students': len(consolidated_data),
            'chart_data': json.dumps(chart_data),
            'grade_data': json.dumps(charts_data['grade_data']),
            'trend_data': json.dumps(charts_data['trend_data']),
            'roll_data': json.dumps(charts_data['roll_data']),
            'component_data': json.dumps(charts_data['component_data']),
            'scatter_data': json.dumps(charts_data['scatter_data'])
        })

        return render(request, 'academic/results.html', context)

    except Exception as e:
        logger.error(f"Error in academic_results: {str(e)}", exc_info=True)
        context.update({
            'error_message': f'An error occurred: {str(e)}',
        })
        return render(request, 'academic/results.html', context)

# Additional utility functions if needed
def get_evaluation_statistics(marks_data, eval_components):
    """
    Calculate detailed statistics for evaluation components
    """
    statistics = {}
    
    for comp in eval_components:
        eval_id = comp['evaluation_id']
        eval_name = comp['evaluation_id_name']
        marks = [m['marks'] for m in marks_data if m['evaluation_id'] == eval_id]
        
        if marks:
            statistics[eval_name] = {
                'average': round(sum(marks) / len(marks), 2),
                'maximum': comp['maximum_marks'],
                'highest': max(marks),
                'lowest': min(marks),
                'count': len(marks)
            }
    
    return statistics

def calculate_semester_analysis(semester_marks):
    """Helper function to calculate semester analysis metrics"""
    if not semester_marks:
        return {
            'total_courses': 0,
            'passed_courses': 0,
            'highest_grade': 0,
            'lowest_grade': 0,
            'average_grade': 0,
            'grade_distribution': {
                'outstanding': 0,
                'excellent': 0,
                'good': 0,
                'average': 0,
                'pass': 0,
                'fail': 0
            }
        }

    analysis = {
        'total_courses': len(semester_marks),
        'passed_courses': sum(1 for mark in semester_marks if mark['final_grade_point'] >= 4.0),
        'highest_grade': max((mark['final_grade_point'] for mark in semester_marks), default=0),
        'lowest_grade': min((mark['final_grade_point'] for mark in semester_marks), default=0),
        'average_grade': sum(mark['final_grade_point'] for mark in semester_marks) / len(semester_marks) if semester_marks else 0,
        'grade_distribution': {
            'outstanding': sum(1 for mark in semester_marks if mark['final_grade_point'] >= 9.0),
            'excellent': sum(1 for mark in semester_marks if 8.0 <= mark['final_grade_point'] < 9.0),
            'good': sum(1 for mark in semester_marks if 7.0 <= mark['final_grade_point'] < 8.0),
            'average': sum(1 for mark in semester_marks if 6.0 <= mark['final_grade_point'] < 7.0),
            'pass': sum(1 for mark in semester_marks if 4.0 <= mark['final_grade_point'] < 6.0),
            'fail': sum(1 for mark in semester_marks if mark['final_grade_point'] < 4.0)
        }
    }
    
    # Add performance indicators
    analysis['performance_trend'] = (
        'Improving' if analysis['highest_grade'] > analysis['average_grade'] 
        else 'Declining' if analysis['lowest_grade'] < analysis['average_grade']
        else 'Stable'
    )
    
    # Add success rate
    analysis['success_rate'] = (analysis['passed_courses'] / analysis['total_courses'] * 100) if analysis['total_courses'] > 0 else 0
    
    return analysis

@login_required
def student_performance(request):
    try:
        roll_number = request.GET.get('roll_number')
        context = {}

        if roll_number:
            # Get the semester header data with related marks
            semester_data = StudentRegistrationSemesterHeader.objects.filter(
                roll_number=roll_number
            ).values(
                'roll_number',
                'program_course_key',
                'session_start_date',
                'session_end_date',
                'sgpa',
                'total_credit_earned',
                'status'
            ).order_by('session_start_date')

            if not semester_data:
                messages.error(request, "No data found for this roll number.")
                return render(request, 'academic/student_performance.html', context)

            # Get program details
            first_semester = semester_data[0]
            program_key = first_semester['program_course_key'][:7]
            
            try:
                program = ProgramMaster.objects.get(program_id=program_key)
                program_name = program.program_name
            except ProgramMaster.DoesNotExist:
                program_name = "Unknown Program"
                messages.warning(request, "Program information not found.")

            program_course_keys = [sem['program_course_key'] for sem in semester_data]
            
            # Get course headers
            course_headers = ProgramCourseHeader.objects.filter(
                program_course_key__in=program_course_keys
            ).values('program_course_key', 'semtype', 'semester_code')
            
            course_header_lookup = {
                header['program_course_key']: header 
                for header in course_headers
            }

            # Get marks data for all semesters
            marks_data = StudentMarksSummary.objects.filter(
                roll_number=roll_number,
                program_course_key__in=program_course_keys
            ).values(
                'program_course_key',
                'course_code',
                # 'course_name',
                'total_internal',
                'total_external',
                'total_marks',
                'internal_grade',
                'external_grade',
                'final_grade_point',
                'earned_credits'
            )

            # Create marks lookup dictionary
            marks_lookup = {}
            for mark in marks_data:
                if mark['program_course_key'] not in marks_lookup:
                    marks_lookup[mark['program_course_key']] = []
                marks_lookup[mark['program_course_key']].append(mark)

            # Process semester data
            semesters = []
            sgpa_data = []
            labels = []
            cumulative_credits = 0
            total_grade_points = 0

            for semester in semester_data:
                if semester['sgpa'] is not None:
                    course_header = course_header_lookup.get(semester['program_course_key'], {})
                    semester_marks = marks_lookup.get(semester['program_course_key'], [])
                    
                    # Calculate semester analysis
                    semester_analysis = calculate_semester_analysis(semester_marks)
                    
                    # Update cumulative data
                    semester_credits = float(semester['total_credit_earned'])
                    cumulative_credits += semester_credits
                    total_grade_points += float(semester['sgpa']) * semester_credits
                    
                    semester_info = {
                        'session_start_date': semester['session_start_date'],
                        'session_end_date': semester['session_end_date'],
                        'sgpa': round(float(semester['sgpa']), 2),
                        'total_credit_earned': semester_credits,
                        'cumulative_credits': cumulative_credits,
                        'cgpa': round(total_grade_points / cumulative_credits, 2) if cumulative_credits > 0 else 0,
                        'status': semester['status'],
                        'semtype': course_header.get('semtype', ''),
                        'semester_code': course_header.get('semester_code', ''),
                        'marks_detail': sorted(semester_marks, key=lambda x: x['course_code']),
                        'analysis': semester_analysis,
                        'get_status_display': {
                            'P': 'Pass',
                            'F': 'Fail',
                            'B': 'Backlog'
                        }.get(semester['status'], 'Unknown')
                    }
                    semesters.append(semester_info)
                    sgpa_data.append(float(semester['sgpa']))
                    
                    semester_label = (
                        f"{course_header.get('semester_code', '')} - {semester['session_start_date'].strftime('%b %Y')}"
                        if course_header.get('semester_code')
                        else semester['session_start_date'].strftime('%b %Y')
                    )
                    labels.append(semester_label)

            # Calculate overall performance metrics
            overall_cgpa = round(total_grade_points / cumulative_credits, 2) if cumulative_credits > 0 else 0
            
            student_data = {
                'roll_number': roll_number,
                'program_name': program_name,
                'total_semesters': len(semesters),
                'cumulative_credits': cumulative_credits,
                'overall_cgpa': overall_cgpa,
                'current_sgpa': round(sgpa_data[-1], 2) if sgpa_data else 0,
                'semesters': semesters,
                'chart_labels': labels,
                'chart_data': sgpa_data
            }

            context['student_data'] = student_data

        return render(request, 'academic/student_performance.html', context)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in student_performance view: {str(e)}", exc_info=True)
        messages.error(request, f"An error occurred while fetching student performance data: {str(e)}")
        return render(request, 'academic/student_performance.html', {})
from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages
from academic.models import InstructorCourse, ProgramCourseHeader, StudentMarks, StudentMarksSummary

def teacher_dashboard(request):
    employee_id = request.GET.get('employee_id')
    context = {'employee_id': employee_id}
    
    if employee_id:
        try:
            # Get all courses assigned to the instructor
            instructor_courses = InstructorCourse.objects.filter(
                employee_id=employee_id
            ).values(
                'course_code',
                'program_course_key',
                'semester_start_date',
                'semester_end_date'
            ).distinct()

            # Get program course details
            program_courses = ProgramCourseHeader.objects.filter(
                program_course_key__in=[ic['program_course_key'] for ic in instructor_courses]
            ).values(
                'program_course_key',
                'semester_code'
            )

            # Create a lookup dictionary for semester codes
            semester_codes = {
                pc['program_course_key']: pc['semester_code']
                for pc in program_courses
            }

            # Expanded grade categories to include variations
            grade_categories = {
                'A+': ['A+'], 'A': ['A'], 'A-': ['A-'],
                'B+': ['B+'], 'B': ['B'], 'B-': ['B-'],
                'C+': ['C+'], 'C': ['C'], 'C-': ['C-'],
                'D+': ['D+'], 'D': ['D'], 'D-': ['D-'],
                'F': ['F']
            }

            # Get all student marks for these courses
            student_marks = StudentMarks.objects.filter(
                Q(program_course_key__in=[ic['program_course_key'] for ic in instructor_courses]) &
                Q(course_code__in=[ic['course_code'] for ic in instructor_courses])
            ).values(
                'program_course_key',
                'course_code',
                'roll_number',
                'grades',
                'pass_fail',
                'semester_start_date',
                'semester_end_date'
            ).order_by('roll_number', '-semester_start_date')

            # Get student marks summary
            marks_summary = StudentMarksSummary.objects.filter(
                Q(program_course_key__in=[ic['program_course_key'] for ic in instructor_courses]) &
                Q(course_code__in=[ic['course_code'] for ic in instructor_courses])
            ).values(
                'program_course_key',
                'course_code',
                'roll_number',
                'internal_grade',
                'external_grade',
                'semester_start_date',
                'semester_end_date'
            ).order_by('roll_number', '-semester_start_date')

            # Create a lookup dictionary for marks summary
            summary_lookup = {}
            for ms in marks_summary:
                key = f"{ms['roll_number']}"
                if key not in summary_lookup:
                    summary_lookup[key] = ms

            # Combine all data with distinct roll numbers
            seen_roll_numbers = set()
            combined_data = []
            pass_count = 0
            fail_count = 0

            # Initialize grade category counts for internal and external
            grade_counts = {key: {'internal': 0, 'external': 0} for key in grade_categories.keys()}

            for mark in student_marks:
                if mark['roll_number'] not in seen_roll_numbers:
                    seen_roll_numbers.add(mark['roll_number'])
                    summary = summary_lookup.get(str(mark['roll_number']), {})
                    
                    combined_data.append({
                        'employee_id': employee_id,
                        'course_code': mark['course_code'],
                        'program_course_key': mark['program_course_key'],
                        'semester_code': semester_codes.get(mark['program_course_key'], 'N/A'),
                        'roll_number': mark['roll_number'],
                        'grades': mark['grades'],
                        'pass_fail': mark['pass_fail'],
                        'semester_start_date': mark['semester_start_date'],
                        'semester_end_date': mark['semester_end_date'],
                        'internal_grade': summary.get('internal_grade', 'N/A'),
                        'external_grade': summary.get('external_grade', 'N/A')
                    })

                    # Count pass/fail
                    if mark['pass_fail'] == 'Pass':
                        pass_count += 1
                    else:
                        fail_count += 1

                    # Count internal grades
                    internal_grade = summary.get('internal_grade', 'N/A')
                    for grade_key, grade_list in grade_categories.items():
                        if internal_grade in grade_list:
                            grade_counts[grade_key]['internal'] += 1

                    # Count external grades
                    external_grade = summary.get('external_grade', 'N/A')
                    for grade_key, grade_list in grade_categories.items():
                        if external_grade in grade_list:
                            grade_counts[grade_key]['external'] += 1

            # Sort the combined data by roll number
            combined_data.sort(key=lambda x: x['roll_number'])

            # Prepare grade data for charts
            sorted_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
            internal_grade_data = [grade_counts[grade]['internal'] for grade in sorted_grades]
            external_grade_data = [grade_counts[grade]['external'] for grade in sorted_grades]

            context.update({
                'data': combined_data,
                'total_courses': len(instructor_courses),
                'total_students': len(seen_roll_numbers),
                'pass_count': pass_count,
                'fail_count': fail_count,
                'sorted_grades': sorted_grades,
                'internal_grade_data': internal_grade_data,
                'external_grade_data': external_grade_data,
            })
            
        except Exception as e:
            messages.error(request, f"Error fetching data: {str(e)}")
    
    return render(request, 'academic/teacher.html', context)