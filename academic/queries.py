from datetime import date
import json
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q, Avg, Count

from academic.models import StudentMarksSummary
from academic.utils import analyze_marks
from collections import defaultdict


#from .models import UserInfo

def get_user(user,pwd):
      
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select user_name from user_info where user_name =%s
            and password = sha1(%s)
            """
            , [user,pwd])
    
        row = cursor.fetchone()
        return row[0] if row else None
def get_students(request):
    branch=request.GET.get("branch")
    rollno=request.GET.get("rollno")
    subject=request.GET.get("subject")
    pgmid=request.GET.get("program_id")
    session=request.GET.get("year")
    s, e = session_to_dates(session)
    ssd=s.isoformat()
    sed=e.isoformat()
    pgmid=pgmid+'%'
    branch = branch+"%" if branch else '%'
    rollno = rollno+"%" if rollno else '%'
    subject = subject+"%" if subject else '%'

    #ssd=f"'{s.isoformat()}'"
    #sed=f"'{e.isoformat()}'"
    #pgmid=f"'{pgmid}%'"
    #subject=f"'{subject}'"
    
    
    limit = int(request.GET.get('limit', 100))
    offset = int(request.GET.get('offset', 0))
    #like_pattern_pgmid = f"'{pgmid}%'" if pgmid else '%'
    #subject = f"'{subject}'" if subject else '%'
    params = [ssd, sed,pgmid]
    base_sql="""
                select distinct srsh.roll_number,sm.student_first_name,srsh.status,
                semester_code,pch.branch_id,pch.specialization_id, 
                srsh.program_course_key,sc.course_code,srsh.session_start_date as startdate,
                srsh.session_end_date as enddate
                from student_registration_semester_header srsh
                join program_course_header pch on pch.program_course_key =srsh.program_course_key 
                join student_program sp on sp.roll_number=srsh.roll_number 
                join student_master sm on sm.enrollment_number=sp.enrollment_number
                and sp.program_status in ( 'ACT','PAS','FAL','DIS')

            """
    if(subject):
        base_sql+="""
                join student_course sc on sc.semester_start_date= srsh.session_start_date
                and sc.program_course_key=srsh.program_course_key
        
                """
    base_sql+="""
                where srsh.session_start_date between %s and %s
                and srsh.program_course_key like %s
                and srsh.status in ('PAS','FAL','REG','REM')            

                """
    if(subject):
        base_sql+="""
                and sc.course_code like  %s
                 """
        params.append(subject)
    if(rollno):
        base_sql+="""
                and srsh.roll_number like  %s
                 """
        params.append(rollno)
    if(branch):
        base_sql+="""
                and pch.branch_id like  %s
                 """
        params.append(branch)

    params.extend([limit, offset])
    sql_with_limit = base_sql  + " LIMIT %s OFFSET %s ;"
    print(sql_with_limit)
    print('SQL parameters:', params)
    
    with connection.cursor() as cursor:
        cursor.execute(sql_with_limit, params)
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        print('Resultset',rows)
    if connection.queries:
        last = connection.queries[-1]
        print("LAST SQL:", last['sql'])

    return JsonResponse({'count': len(rows), 'students': rows})

def session_to_dates(session_str):
    """
    session_str expected like "2024-2025"
    Returns (start_date, end_date) as datetime.date objects:
      start_date = YYYY-07-01
      end_date   = YYYY-06-30
    """
    print(session_str)
    y1_str, y2_str = session_str.split('-', 1)
    y1, y2 = int(y1_str), int(y2_str)
    return date(y1, 7, 1), date(y2, 6, 30)

def components_api(request):
    # return a JSON list of components
    subject=request.GET.get("subject")
    pgmid=request.GET.get("program_id")

    params = [subject,pgmid]
    

    base_sql="""
               select evaluation_id as id,evaluation_id_name as name from course_evaluation_component
                  where course_code = %s
                  and program_id=%s;

            """
    
    with connection.cursor() as cursor:
        cursor.execute(base_sql, params)
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        print('Resultset',rows)
    if connection.queries:
        last = connection.queries[-1]
        print("LAST SQL:", last['sql'])

    return JsonResponse({'count': len(rows), 'components': rows})

def components_avg_marks_api(request):
    subject = request.GET.get("subject", "")
    pck = request.GET.get("pck", "")
    #pgmid = request.GET.get("pgmid", "")
    pgmid = pck[:7]
    
    components=request.GET.get("components","")
    startdate=request.GET.get("startdate","")
    enddate=request.GET.get("enddate","")
    lst = tuple(components.split(","))
    #tpl = tuple(s.split(","))
    print(type(components), lst)
    print("components_marks_api called with", subject, pck, startdate, lst)
    
    params = [pgmid,pck,startdate,enddate,subject,lst]
    base_sql="""
              select sm.evaluation_id as id ,cec.evaluation_id_name as name ,round(avg(marks),2)  as avg from student_marks sm
                join course_evaluation_component cec on cec.evaluation_id=sm.evaluation_id
                and cec.program_id= %s and cec.course_code=sm.course_code
                where program_course_key= %s
                and semester_start_date =  %s and semester_end_date= %s
                and sm.course_code= %s and sm.evaluation_id in %s
                group by sm.evaluation_id;

            """
    
    with connection.cursor() as cursor:
        cursor.execute(base_sql, params)
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        print('Resultset',rows)
    if connection.queries:
        last = connection.queries[-1]
        print("LAST SQL:", last['sql'])

    return JsonResponse({'count': len(rows), 'avg_marks': rows})
    
def get_grades(request):
      # Calculate grade distribution for the course
    
    subject = request.GET.get("subject", "").strip()
    pck = request.GET.get("pck", "").strip()
   
    startdate_str=request.GET.get("startdate","").strip()
    startdate = date.fromisoformat(startdate_str)
    
    enddate_str=request.GET.get("enddate","").strip()
    enddate = date.fromisoformat(enddate_str)
    
    print("enddate",enddate)
       
    base_qs = StudentMarksSummary.objects.filter(
            course_code=subject,
            semester_start_date=startdate,
            semester_end_date=enddate,
            program_course_key =pck
        )
    # Group by internal_grade and count students
    grades_qs = (
        base_qs
        .values("internal_grade")
        .annotate(count=Count("roll_number"))
        .exclude(internal_grade__isnull=True)
        .order_by("internal_grade")
    )
    print(grades_qs.query)
    
    data = list(grades_qs)
        # Prepare grade distribution data

    return JsonResponse(data, safe=False)
       
def get_components_marks(request):
    subject = request.GET.get("subject", "")
    pck = request.GET.get("pck", "")
    #pgmid = request.GET.get("pgmid", "")
    pgmid = pck[:7]
    
    components=request.GET.get("components","")
    startdate=request.GET.get("startdate","")
    enddate=request.GET.get("enddate","")
    lst = tuple(components.split(","))
    #tpl = tuple(s.split(","))
    print(type(components), lst)
    print("components_marks_api called with", subject, pck, startdate, lst)
    
    params = [pgmid,startdate,enddate,subject,pck,lst]
    base_sql="""
              select roll_number as rollnumber,marks, evaluation_id_name  as name
                from student_marks sm join course_evaluation_component cec on 
                cec.program_id= %s and cec.course_code=sm.course_code
                and cec.evaluation_id=sm.evaluation_id
                where semester_start_date= %s
                and semester_end_date = %s and sm.course_code= %s
                and sm.program_course_key= %s 
                and sm.evaluation_id in %s
                order by roll_number, evaluation_id_name;

            """
    
    with connection.cursor() as cursor:
        cursor.execute(base_sql, params)
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        print('Resultset',rows)
        # rows -> [(roll, marks, name), ...]
       
        data = [
        {
            "rollnumber": str(r["rollnumber"]),
            "marks": int(r["marks"]),
            "name": r["name"],
        }
        for r in rows
                ]
       
    

    return JsonResponse({'count': len(rows), 'components_marks': data})         

def marks_analysis_api(request):
    pck = request.GET.get("pck", "")
    year = request.GET.get("year", "")
    subject = request.GET.get("subject", "")
    startdate = request.GET.get("startdate", "")
    enddate = request.GET.get("enddate", "")
    components=request.GET.get("components","")
    print   ("marks_analysis_api called with", subject, pck, year, startdate, components)   
    raw=get_components_marks(request)
    data = json.loads(raw.content.decode("utf-8"))  # dict
    print("data from get_components_marks",type(data),data) 
    marks = defaultdict(list)
    for item in data.get("components_marks", []):
        marks[item["name"]].append(item["marks"])
   
    
    print("marks grouped",marks)
    # Example marks (fetch these from DB in real case)
    #marks = [45, 55, 60, 70, 65, 50, 40, 80, 75,60,60,60]
   
    
    summary,hist_img = analyze_marks(marks)
    print("summary",summary)
    return JsonResponse({
             "summary": summary,
        "histogram": hist_img,
        })

def get_sgpa_average(request):
    rollno = request.GET.get("rollno", "")
    params = [rollno]
    peeravg_sql="""
               select pch.semester_code as semester,
            count(*) as totalstudents ,round(avg(srsh.sgpa),3) as sgpa
            from student_registration_semester_header srsh join program_course_header pch
            on pch.program_course_key=srsh.program_course_key
            join (
            select program_course_key,session_start_date 
            from student_registration_semester_header 
            where roll_number= %s and status ='PAS'
            )t1 on t1.program_course_key=srsh.program_course_key and 
            t1.session_start_date=srsh.session_start_date
            where srsh.status="PAS" 
            group by semester_code
            order by semester_code

            """
    rollnoavg_sql="""
               select pch.semester_code as semester,srsh.sgpa 
                from student_registration_semester_header  srsh 
                join program_course_header pch on pch.program_course_key= srsh.program_course_key
                where roll_number= %s and status ='PAS'
                order by session_start_date
                """
    
    with connection.cursor() as cursor:
        cursor.execute(peeravg_sql, params)
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        print('Resultset',rows)
              
        peeraverage = [
        {
            "semester": str(r["semester"]),
            "totalstudents": int(r["totalstudents"]),
            "sgpa": r["sgpa"],
        }
        for r in rows
                ]
        
        
    with connection.cursor() as cursor1:
        cursor1.execute(rollnoavg_sql, params)
        cols = [c[0] for c in cursor1.description]
        rows = [dict(zip(cols, r)) for r in cursor1.fetchall()]
        if connection.queries:
            last = connection.queries[-1]
            print("LAST SQL:", last['sql'])
        studentavg = [
        {
            "semester": str(r["semester"]),
            "sgpa": r["sgpa"]
         
        }
        for r in rows
                ]
    return JsonResponse({'peeraverage': peeraverage,'studentavg':studentavg})
def get_sub_gradepoint(request):
    rollno = request.GET.get("rollno", "")
    pgmid = request.GET.get("program_id", "")
    params = [pgmid,rollno]
    subgrade_sql="""
               select course_code as subject,final_grade_point as grade_point
               ,semester_code as semester
                from student_marks_summary sms 
                join program_course_header pch 
                on pch.program_course_key=sms.program_course_key
                join student_registration_semester_header srsh 
                on srsh.program_course_key=pch.program_course_key
                and srsh.roll_number=sms.roll_number
                and srsh.session_start_date=sms.semester_start_date
                where pch.program_id= %s 
                and srsh.status= "PAS" and sms.roll_number= %s
                order by semester_code,course_code;

                """
    
    with connection.cursor() as cursor:
        cursor.execute(subgrade_sql, params)
        cols = [c[0] for c in cursor.description]
        rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
        print('Resultset',rows)
              
        subgrade = [
        {
            "semester": str(r["semester"]),
            "subject": str(r["subject"]),
            "grade_point": float(r["grade_point"])
         
        }
        for r in rows
                ]
        
        
    
    return JsonResponse({'subgrade': subgrade}) 