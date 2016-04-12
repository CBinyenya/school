from __future__ import division
from django.db import models
from django.forms import ModelForm
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from django import forms
LEVEL_CHOICES = (
    ('G', "Gold"),
    ('S', "Silver"),
    ('T', "Titanium"),
)
GENDER_CHOICES = (
    ('B', "Boy's School"),
    ('G', "Girl's School"),
    ('M', "Mixed"),
)
GENDER = (
    ('M', "Male"),
    ('F', "Female")
)
PRIVATE_PUBLIC_CHOICE = (
    ('Private', "Private"),
    ('Public', "Public")
)
POSITION_CHOICES = (
    ('HM', "Head Teacher"),
    ('DP', "Deputy teacher"),
    ('SM', "Senior Master"),
    ('CT', "Class Teacher"),
    ('EH', "Examination Head"),
    ('AA', "Academic Affairs"),
    ('HOS', "Head of Sciences"),
    ('HOH', "Head of Humanities"),
    ('HOL', "Head of Languages"),
    ('HOM', "Head of Mathematics"),

)
LETTER_CHOICES = (
    ('A', "A"),
    ('B', "B"),
    ('C', "C"),
    ('D', "D"),
)
QUESTION_LEVEL = (
    ('E', "Easy"),
    ('M', "Medium"),
    ('H', "Hard")
)
HOURS_CHOICES = (
    (1, "1 Hour"),
    (2, "2 Hours"),
    (3, "3 Hours"),
)
MINUTES_CHOICES = (
    (15, "15 Minutes"),
    (30, "30 Minutes"),
    (45, "45 Minutes"),
)


class School(models.Model):
    school_name = models.CharField(max_length=50)
    mission = models.TextField(max_length=200)
    vision = models.TextField(max_length=200)
    code = models.CharField(max_length=8)
    telephone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=13)
    logo = models.ImageField(null=True, blank=True)
    email = models.EmailField(null=True)
    website = models.URLField(null=True)
    country = models.CharField(max_length=50, default="Kenya")
    county = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50)
    location = models.CharField(max_length=50, null=True)
    description = models.TextField(max_length=500, null=True)
    gender_type = models.CharField(max_length=1, choices=GENDER_CHOICES)
    private = models.CharField(max_length=7, choices=PRIVATE_PUBLIC_CHOICE)
    approved = models.BooleanField(default=False)
    credit = models.PositiveIntegerField(default=0)
    head = models.ForeignKey('Teacher', related_name="skull", null=True)
    subjects = models.ManyToManyField('Subject', blank=True)
    kindergarten = models.BooleanField(default=False)
    level = models.ForeignKey('SchoolLevel', null=True, blank=True)
    stream = models.ManyToManyField('Stream', blank=True)
    directors = models.ManyToManyField('Director', blank=True)
    date = models.DateTimeField(default=timezone.now)
    no_of_students = models.PositiveIntegerField(null=True, blank=True)
    app_level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    payed_status = models.BooleanField()

    def __str__(self):
        return self.school_name

    class Meta:
        db_table = "schools"


class Director(User):
    pass

    def __str__(self):
        return self.first_name

    class Meta:
        db_table = "directors"


class Staff(User):
    photo = models.ImageField(null=True, blank=True)
    phone = models.CharField(max_length=13, null=True)
    gender = models.CharField(max_length=1, choices=GENDER, null=True, blank=True)
    school = models.ForeignKey(
        School,
        db_column="school_name",
        related_name="staff",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Teacher(Staff):
    linkdin = models.URLField(null=True, blank=True)
    subjects = models.ManyToManyField('Subject', blank=True)
    classes = models.ManyToManyField('Stream', blank=True)
    position = models.CharField(max_length=4, choices=POSITION_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('easy.views.teacher_home_page', kwargs={'pk': self.pk})

    class Meta:
        db_table = "teachers"


class TeacherForm(ModelForm):
    def clean(self):
        clean_data = super(TeacherForm, self).clean()
        username = clean_data.get('username')
        try:
            User.objects.get(username=username)
            raise forms.ValidationError("This username is not available for use")
        except User.DoesNotExist:
            pass

    class Meta:
        model = Teacher
        success_url = "/admin1/login"
        fields = ['first_name', 'last_name', 'photo', 'gender', 'position', 'linkdin', 'password']


class Subject(models.Model):
    subject_name = models.CharField(max_length=20)
    topics = models.ManyToManyField('Topic', blank=True)
    # Redundant relationship
    class_level = models.ForeignKey('ClassLevel', db_column="level_name", null=True)

    def __str__(self):
        return "%s for %s" % (self.subject_name, self.class_level)

    class Meta:
        db_table = "subjects"


class Topic(models.Model):
    topic_name = models.CharField(max_length=50)
    class_level = models.ForeignKey('ClassLevel', db_column="level_name", null=True)
    subjects = models.ForeignKey(Subject, null=True)

    def __str__(self):
        return "%s for %s" % (self.topic_name, self.class_level)

    class Meta:
        db_table = "topics"


class SchoolLevel(models.Model):
    level_name = models.CharField(max_length=20)
    class_level = models.ManyToManyField('ClassLevel')

    def __str__(self):
        return self.level_name

    class Meta:
        db_table = "school_levels"


class ClassLevel(models.Model):
    level_name = models.CharField(max_length=10)
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.level_name

    class Meta:
        db_table = "class_levels"


class Stream(models.Model):
    level_name = models.ForeignKey(ClassLevel)
    stream_name = models.CharField(max_length=20)
    class_teacher = models.ForeignKey(Teacher, null=True)

    def __str__(self):
        return "%s %s" % (self.level_name, self.stream_name)

    class Meta:
        db_table = "streams"

        
class Student(User):
    reg_number = models.CharField(max_length=30)
    phone = models.CharField(max_length=13)
    school = models.ForeignKey(School, null=True, blank=True)
    parents = models.ManyToManyField('Parent')
    stream = models.ForeignKey(Stream, null=True, blank=True)
    exam_subject = models.ForeignKey(Subject, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "students"

class StudentForm(ModelForm):
    def clean(self):
        clean_data = super(StudentForm, self).clean()
        username = clean_data.get('username')
        try:
            User.objects.get(username=username)
            raise forms.ValidationError("This username is not available for use")
        except User.DoesNotExist:
            pass

    class Meta:
        model = Student
        success_url = "easy/student"
        fields = ['first_name', 'last_name']



class Parent(User):
    phone = models.CharField(max_length=13)

    def __str__(self):
        return "%s %s %s" % (self.username, self.first_name, self.last_name)

    class Meta:
        db_table = "parents"


class ParentForm(ModelForm):
    def clean(self):
        clean_data = super(ParentForm, self).clean()
        username = clean_data.get('username')
        try:
            User.objects.get(username=username)
            raise forms.ValidationError("This username is not available for use")
        except User.DoesNotExist:
            pass

    class Meta:
        model = Parent
        success_url = "easy/parent"
        fields = ['first_name', 'last_name']



class Answer(models.Model):
    answer = models.CharField(max_length=30)
    letter = models.CharField(max_length=1, choices=LETTER_CHOICES)
    marks = models.PositiveIntegerField()
    text_field = models.TextField(max_length=100, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.answer

    class Meta:
        db_table = "answers"


class Question(models.Model):
    question = models.TextField(max_length=200)
    number = models.PositiveSmallIntegerField()
    class_level = models.ForeignKey(ClassLevel)
    question_subject = models.ForeignKey(Subject)
    question_topic = models.ForeignKey(Topic, null=True)
    level = models.CharField(max_length=1, choices=QUESTION_LEVEL, null=True)
    answer = models.CharField(max_length=100, null=True, blank=True)
    correct_answer = models.ForeignKey(Answer)

    def __str__(self):
        return self.question

    class Meta:
        db_table = "questions"


class MultipleChoiceQuestion(Question):
    choices = models.ManyToManyField(Answer, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.question

    class Meta:
        db_table = "multiple_choices"


class CompletedTests(models.Model):
    student = models.ForeignKey(Student)
    test = models.ForeignKey('Exam')
    question = models.ForeignKey(MultipleChoiceQuestion)
    answer = models.ForeignKey(Answer, null=True)
    value = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.student.get_full_name()

    def full_name(self):
        return self.student.get_full_name()

    class Meta:
        db_table = "completed_tests"


class Exam(models.Model):
    exam_name = models.CharField(max_length=30)
    school = models.ForeignKey(School, blank=True)
    class_level = models.ForeignKey(ClassLevel)
    stream = models.ManyToManyField(Stream, blank=True)
    exam_subject = models.ForeignKey(Subject)
    supervisor = models.ForeignKey(Teacher)
    questions_ans = models.ManyToManyField(MultipleChoiceQuestion, blank=True)
    date_available = models.DateTimeField(default=timezone.now)
    hours = models.PositiveSmallIntegerField(choices=HOURS_CHOICES, null=True, blank=True)
    minutes = models.PositiveSmallIntegerField(choices=MINUTES_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.exam_name

    class Meta:
        db_table = "exams"

class ExamUploads(models.Model):
    exam_name = models.CharField(max_length=56)
    excel_file = models.FileField(upload_to='files/uploads')

    class Meta:
        # abstract = True
        db_table = "uploads"
        
class StudentUploads(models.Model):
    stream = models.ForeignKey(Stream)
    excel_file = models.FileField(upload_to='files/uploads')

    class Meta:
        # abstract = True
        db_table = "student_uploads"


class Results(models.Model):
    exam_name = models.ForeignKey(Exam)
    student_id = models.ForeignKey(Student)
    total_marks = models.PositiveSmallIntegerField()
    out_off = models.PositiveSmallIntegerField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.exam_name.exam_name

    class Meta:
        db_table = "results"


class ResultObjects(models.Model):
    name = models.OneToOneField(Exam, primary_key=True)
    subject = models.ForeignKey(Subject)
    supervisor = models.ForeignKey(Teacher)
    results = models.ForeignKey(Results)
    average_marks = models.DecimalField(null=True, max_digits=5, decimal_places=2)

    def average(self):
        try:
            results = Results.objects.filter(exam_name=self.name)
        except Results.DoesNotExist:
            return 0
        num_of_students = len(results)
        marks = 0
        for result in results:
            total = result.out_off
            marks += result.total_marks
        if marks > 0:
            average = marks/num_of_students
            percentage = (100//total) * average
            average = percentage
        else:
            average = 0
        return average

    def convert(self):
        pass

    class Meta:
        db_table = "averages"



class Activity(models.Model):
    school = models.ForeignKey(School)
    type = models.CharField(max_length=30)

    class Meta:
        db_table = "activities"


class Gallery(models.Model):
    school = models.ForeignKey(School)
    type = models.CharField(max_length=30)
    image = models.ImageField(upload_to="galary")

    class Meta:
        db_table = "galleries"


class Sponsor(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "sponsors"


class EventOrganizer(models.Model):
    organizer_name = models.CharField(max_length=50)
    sponsors = models.ForeignKey(Sponsor)

    class Meta:
        db_table = "organizers"


class Event(models.Model):
    school = models.ForeignKey(School)
    date = models.DateTimeField(default=timezone.now)
    organizer = models.ManyToManyField(EventOrganizer)
    location = models.CharField(max_length=30)

    class Meta:
        db_table = "events"


class FeeElement(models.Model):
    school = models.ForeignKey(School)
    element_name = models.CharField(max_length=50)
    class_level = models.ForeignKey(ClassLevel)
    amount = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "fee_elements"


class FeeStructure(models.Model):
    school = models.ForeignKey(School)
    elements = models.ForeignKey(FeeElement)
    class_level = models.ForeignKey(ClassLevel)

    class Meta:
        db_table = "fee_structure"



class AdminModel(models.Model):
    pass
