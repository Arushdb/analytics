# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ProgramMaster(models.Model):
    program_id = models.CharField(primary_key=True, max_length=7)
    program_code = models.CharField(max_length=4)
    program_name = models.CharField(max_length=150)
    program_type = models.CharField(max_length=1)
    program_mode = models.CharField(max_length=1)
    no_of_terms = models.PositiveIntegerField()
    total_credits = models.DecimalField(max_digits=7, decimal_places=3, blank=True, null=True)
    number_of_attempt_allowed = models.PositiveIntegerField()
    max_number_of_fail_subjects = models.PositiveIntegerField()
    ug_pg = models.CharField(max_length=2)
    tencodes = models.CharField(max_length=2, blank=True, null=True)
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField(blank=True, null=True)
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20, blank=True, null=True)
    print_aggregate = models.CharField(max_length=3, db_comment='TAP=theory and practical and SEM means semester aggregate')
    branch_exists = models.IntegerField()
    specialization_exists = models.IntegerField()
    fixed_duration = models.CharField(max_length=1)
    program_description = models.CharField(max_length=100)
    dgpa = models.DecimalField(max_digits=5, decimal_places=3)
    max_reg_semester = models.PositiveSmallIntegerField()
    credit_required = models.PositiveIntegerField()
    fixed_or_variable_credit = models.CharField(max_length=1, db_comment='F=Fixed credit system, V=Variable credit system')
    domain = models.CharField(max_length=3, blank=True, null=True)
    preffered_choice_allowed = models.CharField(max_length=2, blank=True, null=True)
    months_duration_in_english = models.CharField(max_length=100, blank=True, null=True)
    months_duration_in_hindi = models.CharField(max_length=100, blank=True, null=True)
    roll_number_generation_by_order = models.CharField(max_length=1, blank=True, null=True, db_comment='G=Gender Wise, M=Manually, R=Regular')
    program_hindi_name = models.CharField(max_length=200, blank=True, null=True)
    active = models.CharField(max_length=4)
    first_year_title = models.CharField(max_length=50, blank=True, null=True)
    second_year_title = models.CharField(max_length=50, blank=True, null=True)
    third_year_title = models.CharField(max_length=50, blank=True, null=True)
    result_system = models.CharField(max_length=2)
    isnep = models.CharField(db_column='isNep', max_length=1, blank=True, null=True, db_comment='if program is NEP program like B.Com, B.Sc, etc. than Y, else N')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'program_master'
        unique_together = (('program_code', 'program_name'),)


class StudentMarksSummary(models.Model):
    #pk = models.CompositePrimaryKey('roll_number', 'program_course_key', 'semester_start_date', 'semester_end_date', 'course_code')
    #university_code = models.ForeignKey('UniversityMaster', models.DO_NOTHING, db_column='university_code')
    entity_id = models.CharField(max_length=8)
    roll_number = models.CharField(max_length=10, blank=True, null=True)
    program_course_key = models.CharField(max_length=16, blank=True, null=True)
    semester_start_date = models.DateField()
    semester_end_date = models.DateField()
    
    total_internal = models.PositiveIntegerField(blank=True, null=True)
    total_external = models.PositiveIntegerField(blank=True, null=True)
    total_marks = models.PositiveIntegerField(blank=True, null=True)
    course_code = models.CharField(max_length=10, blank=True, null=True)
    
    internal_grade = models.CharField(max_length=3, blank=True, null=True, db_comment='Total Internal grade')
    external_grade = models.CharField(max_length=3, blank=True, null=True, db_comment='Total External  grade')
    final_grade_point = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True, db_comment='Avg grade for course')
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField(blank=True, null=True)
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20, blank=True, null=True)
    earned_credits = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    publish_grades = models.CharField(max_length=1, blank=True, null=True)
    ref_no = models.CharField(max_length=45, blank=True, null=True)
    remarks = models.CharField(max_length=500, blank=True, null=True)
    grace_marks = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_marks_summary'


class CourseEvaluationComponent(models.Model):
    ##pk = models.CompositePrimaryKey('program_id', 'evaluation_id', 'course_code', 'group_id')
    #programid = models.CharField(max_length=10, blank=True, null=True,db_column='program_id')
    
    evaluation_id = models.CharField(max_length=10, blank=True, null=True)
    course_code = models.CharField(max_length=10, blank=True, null=True)
    group_id = models.CharField(max_length=10, blank=True, null=True)
    program = models.ForeignKey(ProgramMaster, models.DO_NOTHING)
    exam_date = models.CharField(max_length=5, blank=True, null=True)
    date_from_display_marks = models.CharField(max_length=5, blank=True, null=True)
    date_to_display_marks = models.CharField(max_length=5, blank=True, null=True)
    evaluation = models.CharField(max_length=5, blank=True, null=True)
    evaluation_id_name = models.CharField(max_length=10, blank=True, null=True)
    group_id = models.CharField(max_length=3)
    rule = models.CharField(max_length=3)
    order_in_awardsheet = models.IntegerField(blank=True, null=True)
    course_code = models.CharField(max_length=10, blank=False)
    maximum_marks = models.PositiveIntegerField()
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField(blank=True, null=True)
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20, blank=True, null=True)
    publish_marks = models.CharField(max_length=1)
    weightage = models.PositiveIntegerField(blank=True, null=True)
    component_full_name = models.CharField(max_length=255, blank=True, null=True)
    published_by = models.CharField(max_length=20, blank=True, null=True)
    published_time = models.DateTimeField(blank=True, null=True)
    component_type = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'course_evaluation_component'


class StudentMarks(models.Model):
    #pk = models.CompositePrimaryKey('roll_number', 'program_course_key', 'evaluation_id', 'course_code', 'semester_start_date', 'semester_end_date')
    university_code = models.CharField(max_length=4)
    entity_id = models.CharField(max_length=8)
    roll_number = models.CharField(max_length=10)
    program_course_key = models.CharField(max_length=14)
    evaluation_id = models.CharField(max_length=3)
    marks = models.PositiveIntegerField(blank=True, null=True)
    old_marks = models.CharField(max_length=10, blank=True, null=True)
    grades = models.CharField(max_length=2, blank=True, null=True)
    pass_fail = models.CharField(max_length=3, blank=True, null=True)
    status = models.CharField(max_length=3, blank=True, null=True)
    course_code = models.CharField(max_length=8)
    semester_start_date = models.DateField()
    semester_end_date = models.DateField()
    insert_time = models.DateField()
    modification_time = models.DateField(blank=True, null=True)
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=80, blank=True, null=True)
    attempt_number = models.PositiveIntegerField()
    requested_marks = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    requester_remarks = models.CharField(max_length=250, blank=True, null=True)
    issue_status = models.CharField(max_length=3, blank=True, null=True)
    teacher_remarks = models.CharField(max_length=200, blank=True, null=True)
    attendence = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_marks'
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CourseMaster(models.Model):
    #pk = models.CompositePrimaryKey('course_code', 'university_code')
    #university_code = models.ForeignKey('UniversityMaster', models.DO_NOTHING, db_column='university_code')
    course_code = models.CharField(max_length=8)
    course_name = models.CharField(max_length=100, blank=True, null=True)
    marks_cont_eval = models.PositiveIntegerField(blank=True, null=True)
    marks_end_semester = models.PositiveIntegerField(blank=True, null=True)
    marks_total = models.PositiveIntegerField()
    course_classification = models.CharField(max_length=1, blank=True, null=True, db_comment='C=Core, T=Theory,P=Practical,W=Work Experience')
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField(blank=True, null=True)
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20, blank=True, null=True)
    owner_program = models.CharField(max_length=7, blank=True, null=True)
    owner_branch = models.CharField(max_length=3, blank=True, null=True)
    owner_specialization = models.CharField(max_length=3, blank=True, null=True)
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    lectures = models.PositiveIntegerField(blank=True, null=True)
    tutorials = models.PositiveIntegerField(blank=True, null=True)
    practicals = models.PositiveIntegerField(blank=True, null=True)
    since_session = models.CharField(max_length=7)
    units = models.PositiveIntegerField(blank=True, null=True)
    course_type = models.CharField(max_length=2, db_comment='M=Major, H=Half')
    owner_entity = models.CharField(max_length=8)
    subject_wise_group = models.CharField(max_length=3, blank=True, null=True)
    result_system = models.CharField(max_length=2)
    internal_external_active = models.IntegerField(blank=True, null=True)
    grade_limit_active = models.IntegerField()
    edei_status = models.PositiveIntegerField(blank=True, null=True)
    core_course_status = models.CharField(max_length=1, blank=True, null=True)
    course_from_outside = models.CharField(max_length=1, blank=True, null=True, db_comment='Course is from outside DEI yes or no, default is N - no')
    outside_source_name = models.CharField(max_length=150, blank=True, null=True, db_comment='Name of outside university or institution or organization for reference.')

    class Meta:
        managed = False
        db_table = 'course_master'


class StudentCourse(models.Model):
    #pk = models.CompositePrimaryKey('roll_number', 'program_course_key', 'semester_start_date', 'semester_end_date', 'course_code', 'entity_id')
    roll_number = models.CharField(max_length=16, blank=True, null=True)
    program_course_key = models.CharField(max_length=16, blank=True, null=True)
    semester_start_date = models.DateField()
    semester_end_date = models.DateField()
    course_code = models.CharField(max_length=12, blank=True, null=True)
    course_name = models.CharField(max_length=100, blank=True, null=True)
    orginal_course_code = models.CharField(max_length=8, blank=True, null=True)
    course_status = models.CharField(max_length=3)
    student_status = models.CharField(max_length=3, blank=True, null=True)
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField(blank=True, null=True)
    creator_id = models.CharField(max_length=25)
    modifier_id = models.CharField(max_length=25, blank=True, null=True)
    attempt_number = models.PositiveSmallIntegerField()
    course_group = models.CharField(max_length=3)
    entity_id = models.CharField(max_length=8)
    old_student_status = models.CharField(max_length=3, blank=True, null=True)
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_course'
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class EvaluationComponent(models.Model):
    #pk = models.CompositePrimaryKey('evaluation_id', 'university_code')
    #university_code = models.ForeignKey('UniversityMaster', models.DO_NOTHING, db_column='university_code', db_comment='References university_master')
    evaluation_id = models.CharField(max_length=3, db_comment='E01,E02')
    id_type = models.CharField(max_length=2, db_comment='MK=Marks,Gr=Grade')
    display_type = models.CharField(max_length=1, db_comment='I:internal,E:External')
    insert_time = models.DateTimeField()
    modification_time = models.DateTimeField(blank=True, null=True)
    creator_id = models.CharField(max_length=20)
    modifier_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluation_component'

class Universitymaster(models.Model):
    university_code=models.CharField(max_length=4,primary_key=True)
    start_date=models.CharField(max_length=10)
    end_date=models.CharField(max_length=10)
    current_status=models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'university_master'
