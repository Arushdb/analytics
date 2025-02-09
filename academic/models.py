# academic/models.py
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'master'  # Ensure this matches your database table name
class ProgramMaster(models.Model):
    program_id = models.CharField(max_length=7, primary_key=True)
    program_code = models.CharField(max_length=4)
    program_name = models.CharField(max_length=150)
    program_type = models.CharField(max_length=1)
    program_mode = models.CharField(max_length=1)
    no_of_terms = models.IntegerField(null=True)
    total_credits = models.DecimalField(max_digits=7, decimal_places=3, null=True)
    max_number_of_fail_subjects = models.IntegerField(null=True)
    ug_pg = models.CharField(max_length=2)
    active = models.CharField(max_length=4)
    months_duration_in_english = models.CharField(max_length=100, null=True)
    months_duration_in_hindi = models.CharField(max_length=100, null=True)
    result_system = models.CharField(max_length=2)

    class Meta:
        db_table = 'program_master'
        managed = False

class CourseEvaluationComponent(models.Model):
    id = None

    program_id = models.CharField(max_length=7)
    exam_date = models.CharField(max_length=5)
    evaluation_id = models.CharField(max_length=3)
    evaluation_id_name = models.CharField(max_length=10)
    group_id = models.CharField(max_length=3)
    course_code = models.CharField(max_length=8)
    maximum_marks = models.IntegerField()
    weightage = models.IntegerField()
    component_full_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'course_evaluation_component'
        managed = False
        unique_together = ('program_id', 'evaluation_id', 'group_id', 'course_code')

class StudentMarks(models.Model):
    university_code = models.CharField(max_length=4)
    entity_id = models.CharField(max_length=8)
    roll_number = models.CharField(max_length=10)
    program_course_key = models.CharField(max_length=14)
    evaluation_id = models.CharField(max_length=3)
    marks = models.IntegerField(null=True)
    grades = models.CharField(max_length=2, null=True)
    pass_fail = models.CharField(max_length=3, null=True)
    course_code = models.CharField(max_length=8)
    semester_start_date = models.DateField()
    semester_end_date = models.DateField()

    class Meta:
        db_table = 'student_marks'
        managed = False
        unique_together = ('roll_number', 'program_course_key', 'evaluation_id', 
                         'course_code', 'semester_start_date', 'semester_end_date')

class StudentMarksSummary(models.Model):
    university_code = models.CharField(max_length=4)
    entity_id = models.CharField(max_length=8)
    roll_number = models.CharField(max_length=10)
    program_course_key = models.CharField(max_length=14)
    semester_start_date = models.DateField()
    semester_end_date = models.DateField()
    total_internal = models.IntegerField(null=True)
    total_external = models.IntegerField(null=True)
    total_marks = models.IntegerField(null=True)
    course_code = models.CharField(max_length=8)
    internal_grade = models.CharField(max_length=3, null=True)
    external_grade = models.CharField(max_length=3, null=True)
    final_grade_point = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    earned_credits = models.DecimalField(max_digits=6, decimal_places=3, null=True)

    class Meta:
        db_table = 'student_marks_summary'
        managed = False
        unique_together = ('roll_number', 'program_course_key', 'course_code', 
                         'semester_start_date', 'semester_end_date')
        
class StudentRegistrationSemesterHeader(models.Model):
    # Add this line to tell Django not to use 'id' as primary key
    id = None
    # Existing fields...
    register_date = models.DateField()
    number_of_remedials = models.IntegerField(null=True)
    status = models.CharField(max_length=3)
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField()
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20)
    roll_number = models.CharField(max_length=10)
    session_start_date = models.DateField()
    session_end_date = models.DateField()
    attempt_number = models.IntegerField(null=True)
    total_credit_earned = models.DecimalField(max_digits=6, decimal_places=3)
    sgpa = models.DecimalField(max_digits=6, decimal_places=3)
    weighted_percentage = models.DecimalField(max_digits=6, decimal_places=3)
    student_process_status = models.CharField(max_length=3)
    register_due_date = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=8)
    program_course_key = models.CharField(max_length=14)
    registered_credit = models.DecimalField(max_digits=6, decimal_places=3)
    registered_theory_credit_excluding_audit = models.DecimalField(max_digits=6, decimal_places=3)
    registered_practical_credit_excluding_audit = models.DecimalField(max_digits=6, decimal_places=3)
    registration_credit_excluding_audit = models.DecimalField(max_digits=6, decimal_places=3)
    reason_description = models.CharField(max_length=100)
    switch_type = models.CharField(max_length=3)
    switch_rule = models.CharField(max_length=3)
    old_status = models.CharField(max_length=3)
    dg_lkr_status = models.IntegerField()

    class Meta:
        db_table = 'student_registration_semester_header'
        managed = False
        # Define the composite primary key
        unique_together = ('roll_number', 'session_start_date', 'session_end_date', 'entity_id', 'program_course_key')
        
class UserGroup(models.Model):
    university_code = models.CharField(max_length=4)
    user_group_id = models.CharField(max_length=3)
    menu_item_id = models.CharField(max_length=6)
    authority = models.BooleanField()  # Mapping tinyint(1) to a boolean field
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField()
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20)
    application = models.CharField(max_length=15)

    class Meta:
        db_table = 'user_group'
        unique_together = ('university_code', 'user_group_id', 'menu_item_id', 'application')

class UserInfo(models.Model):
    user_id = models.CharField(max_length=150)
    user_name = models.CharField(max_length=150)
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True)
    status = models.CharField(max_length=3)
    registered_timestamp = models.DateTimeField()
    modified_timestamp = models.DateTimeField()
    university_code = models.CharField(max_length=4)
    user_group_id = models.CharField(max_length=3)
    application = models.CharField(max_length=15)
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=30)
    password2 = models.CharField(max_length=255)

    class Meta:
        db_table = 'user_info'
        unique_together = ('user_id', 'user_name', 'university_code', 'user_group_id', 'application')

class UniversityMaster(models.Model):
    university_code = models.CharField(max_length=4)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    current_status = models.BooleanField()  # Mapping tinyint(1) to a boolean field
    university_name = models.CharField(max_length=100)
    university_address = models.CharField(max_length=255)
    university_city = models.CharField(max_length=50)
    university_pincode = models.IntegerField()
    university_phone_number = models.CharField(max_length=20)
    university_other_phone = models.CharField(max_length=20, null=True)
    university_fax = models.CharField(max_length=20, null=True)
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField()
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20)
    nick_name = models.CharField(max_length=3)
    university_state = models.CharField(max_length=50)
    country = models.CharField(max_length=45)
    district = models.CharField(max_length=45)

    class Meta:
        db_table = 'university_master'
        unique_together = ('university_code', 'start_date')

from django.db import models

class ProgramCourseHeader(models.Model):
    program_id = models.CharField(max_length=7)
    branch_id = models.CharField(max_length=3)
    specialization_id = models.CharField(max_length=3)
    semester_code = models.CharField(max_length=4)
    program_course_key = models.CharField(max_length=14, primary_key=True)
    insert_time = models.DateTimeField()
    creator_id = models.CharField(max_length=20)
    modification_time = models.DateTimeField()
    modifier_id = models.CharField(max_length=20)
    semester_status = models.CharField(max_length=3)
    min_credit = models.DecimalField(max_digits=5, decimal_places=2)
    max_credit = models.DecimalField(max_digits=5, decimal_places=2)
    min_lecture_credit = models.DecimalField(max_digits=5, decimal_places=2)
    max_lecture_credit = models.DecimalField(max_digits=5, decimal_places=2)
    module_name = models.CharField(max_length=100)
    weeks_duration_in_english = models.CharField(max_length=100)
    weeks_duration_in_hindi = models.CharField(max_length=100)
    semtype = models.CharField(max_length=15)

    class Meta:
        db_table = 'program_course_header'
        managed = False  # Since this is an existing table
        # Define unique together constraints if needed based on your business logic
        unique_together = ('program_id', 'semester_code', 'program_course_key')
# models.py - Update the InstructorCourse model
class InstructorCourse(models.Model):
    # Composite primary key fields
    program_course_key = models.CharField(max_length=14, primary_key=True)
    employee_id = models.CharField(max_length=18)
    semester_start_date = models.DateField()
    semester_end_date = models.DateField()
    entity_id = models.CharField(max_length=8)
    course_code = models.CharField(max_length=8)
    display_type = models.CharField(max_length=1)

    # Regular fields
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField()
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20)
    status = models.CharField(max_length=3)
    assigned_by = models.CharField(max_length=20)
    assigned_time = models.DateTimeField()

    class Meta:
        db_table = 'instructor_course'
        managed = False
        unique_together = (
            'program_course_key', 
            'employee_id', 
            'semester_start_date', 
            'semester_end_date', 
            'entity_id', 
            'course_code',
            'display_type'
        )
