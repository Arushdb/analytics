# analytics/views.py
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.db.models import Avg, Count, F, FloatField
from .models import Student, TestScore, ClassTest, Course, Program, Teacher

def subject_detail_api(request, program_id, year, subject_id):
    """
    Returns per-student averages for a subject (for the class program/year).
    Response:
    {
      "subject": {"id": ..., "name": "..."},
      "students": [{ "student_id": int, "roll_number": "...", "name": "...", "avg_percent": 78.5 }],
      "summary": {"avg_percent": 75.2, "median_percent": 76.0, "count": 24}
    }
    """
    # find subject/course
    course = get_object_or_404(Course, id=subject_id)
    # students in the class (program + admission_year)
    students_qs = Student.objects.filter(program__id=program_id, admission_year=year).select_related('user')
    student_ids = list(students_qs.values_list('id', flat=True))
    # gather per-student average percent for this subject
    # join TestScore -> ClassTest(max_marks)
    rows = (TestScore.objects
            .filter(student__in=student_ids, classtest__course__id=subject_id)
            .values('student')
            .annotate(avg_marks=Avg('marks_obtained'),
                      avg_max=Avg(F('classtest__max_marks'), output_field=FloatField()),
                      count=Count('id')))
    # Build dictionary mapping student id -> avg percent
    per_student = {}
    for r in rows:
        sid = r['student']
        avg_pct = None
        if r['avg_max'] and r['avg_max'] > 0:
            avg_pct = round((r['avg_marks'] / r['avg_max']) * 100, 1)
        per_student[sid] = {"avg_percent": avg_pct, "tests_count": r['count']}

    students = []
    percent_list = []
    for s in students_qs:
        info = per_student.get(s.id)
        avg = info['avg_percent'] if info else None
        if avg is not None: percent_list.append(avg)
        students.append({
            "student_id": s.id,
            "roll_number": s.roll_number,
            "name": s.user.get_full_name() or s.user.username,
            "avg_percent": avg
        })

    # summary
    count = len(percent_list)
    avg_percent = round(sum(percent_list) / count, 1) if count else None
    median_percent = None
    if count:
        sorted_p = sorted(percent_list)
        mid = count // 2
        median_percent = sorted_p[mid] if count % 2 == 1 else round((sorted_p[mid-1]+sorted_p[mid])/2, 1)

    return JsonResponse({
        "subject": {"id": course.id, "name": course.name},
        "students": students,
        "summary": {"avg_percent": avg_percent, "median_percent": median_percent, "count": len(students)}
    })


def teacher_performance_api(request, teacher_id, months=12):
    """
    Returns time series of average scores across the teacher's subjects for the past `months`.
    Response:
    {
      "teacher": {id, name},
      "series": [{"month":"2025-09","avg_percent":75.3}, ...]
    }
    """
    from django.utils import timezone
    import datetime
    teacher = get_object_or_404(Teacher, id=teacher_id)
    end = timezone.now().date()
    start = end - datetime.timedelta(days=months*31)  # approx months
    # find class tests taught by this teacher (assumes ClassTest has teacher FK; if not, adapt)
    # If ClassTest doesn't have teacher, instead lookup by Course->teacher relationship.
    tests_qs = ClassTest.objects.filter(course__in=Course.objects.filter(teacher=teacher), date__gte=start, date__lte=end)
    # annotate month and average percent across test scores
    from django.db.models.functions import TruncMonth
    qs = (tests_qs
          .annotate(month=TruncMonth('date'))
          .values('month')
          .annotate(avg_percent=Avg(F('scores__marks_obtained') * 100.0 / F('max_marks'), output_field=FloatField()))
          .order_by('month'))
    series = []
    for r in qs:
        series.append({"month": r['month'].date().isoformat(), "avg_percent": round(r['avg_percent'] or 0, 1)})
    return JsonResponse({"teacher": {"id": teacher.id, "name": teacher.user.get_full_name() if hasattr(teacher,'user') else str(teacher)}, "series": series})
