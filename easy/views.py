from __future__ import division
__author__ = 'Monte'
import os
import csv
import json
import random

from xlrd import open_workbook

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.forms.formsets import formset_factory
from django.template import RequestContext
from django.db import IntegrityError
from django.db.models import Q
from django.views.generic.edit import ProcessFormView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic import View, UpdateView
from django.forms import ValidationError
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from easy.models import *

from smsleopard import SMShandler, PhoneNumber


def api_login_view(request):
    username = request.POST['username']
    request.user = User(username=username)
    password = request.POST['password']
    HttpResponse(request.user.check_password(raw_password=password))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/easy/login")

class SignUpView(ProcessFormView):
    form_class = TeacherForm
    initial = {'key': "value"}
    template_name = "admin1/signup.html"
    tday = timezone.now()
    year = tday.year

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        account = request.POST['user_account']
        passwd1 = request.POST['password1']
        passwd2 = request.POST['password2']

        if passwd1 != passwd2:
            error = "Passwords do not match"
            return render(request, self.template_name, {'errors': error})

        try:
            User.objects.get(username=username)
            form_errors = "This username is not available for use"
            return render(request, self.template_name, {'errors': form_errors})

        except ObjectDoesNotExist:
            request.user.username = username

        if account == "teacher":            
            teacher = Teacher.objects.create_user(username=request.user.username)
            teacher.set_password(passwd1)
            request.user.is_staff = True
            teacher.save()
            group = Group.objects.get(name="Teachers")
            group.user_set.add(teacher)
            group.save()
            return HttpResponseRedirect("/easy/teacher/%d" % teacher.id)
        elif account == "parent":
            parent = Parent.objects.create_user(username=request.user.username)
            parent.set_password(passwd1)
            parent.save()
            group = Group.objects.get(name="Parents")
            group.user_set.add(parent)
            group.save()
            logout(request)
            return HttpResponse("Your account has been created. Please download our app from google play to start using"
                                " easy school")
        elif account == "student":
            student = Student.objects.create_user(username=request.user.username)
            student.set_password(passwd1)
            student.save()
            group = Group.objects.get(name="Students")
            group.user_set.add(student)
            group.save()
            logout(request)
            return HttpResponse("Success! your account has been created. Contact your class teacher to upload your"
                                " details")
        elif account == "both":
            return HttpResponse("Teacher parent account is not available at the moment well notify you when its ready"
                                "Please sign in as either a teacher or parent")
        else:
            error = "Please select an account type"
            return render(request, self.template_name, {'errors': error})


class UpdateTeacherView(UpdateView):
    class Meta:
        model = Teacher
        fields = ['password', 'last_name', 'gender']
        template_name = "admin1/sign_up.html"

def details_view(request):
    username = request.user.username
    try:
        teacher = Teacher.objects.get(username=username)
        new = dict()
        new['username'] = username
        new['email'] = teacher.email
        new['phone'] = teacher.phone
        new['passwd'] = teacher.password
        teacher.delete()
        _formset = formset_factory(TeacherForm)
        formset = _formset(request.POST, request.FILES)
        form = formset[0]
        if form.is_valid():
            form.save()
            obj = Teacher.objects.update_or_create(username="", defaults=new)
            logout(request)
            return HttpResponseRedirect("/easy/login")
        else:
            form = _formset()
            return render(request, "pages/sign_up.html", {'form': form})
    except ObjectDoesNotExist:
        try:
            parent = Parent.objects.get(username=username)
            parent.delete()
            _formset = formset_factory(ParentForm)
            formset = _formset(request.POST, request.FILES)
        except ObjectDoesNotExist:
            try:
                student = Student.objects.get(username=username)
                student.delete()
                _formset = formset_factory(StudentForm)
                formset = _formset(request.POST, request.FILES)
            except ObjectDoesNotExist:
                return HttpResponse("Fatal Error")

    for form in formset:
        if form.is_valid():
            form.save()
            request.user.objects.update_or_create(username="")
        else:
            form = _formset()
            return render(request, "pages/sign_up.html", {'form': form})
    logout(request)
    return HttpResponseRedirect("/easy/login")

def my_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/easy/login")
    else:
        if request.user.is_staff:
            try:
                username = request.user.username
                teacher = Teacher.objects.get(username=username)
                return HttpResponseRedirect("/easy/teacher/%d" % teacher.id)
            except ObjectDoesNotExist:
                return HttpResponseRedirect("/admin")
        else:
            username = request.user.username
            try:
                teacher = Teacher.objects.get(username=username)
                return HttpResponseRedirect("/easy/teacher/%d" % teacher.id)
            except ObjectDoesNotExist:
                try:
                    Student.objects.get(username=username)
                    return HttpResponseRedirect("/easy/student")
                except ObjectDoesNotExist:
                    return HttpResponse("Please download our app from play store to view your child's records")

@login_required(login_url='/easy/login/')
def teacher_home_page(request, pk=None):
    username = request.user.username
    tday = timezone.now()
    year = tday.year
    full_name = request.user.get_full_name()
    teacher = Teacher.objects.get(username=str(username))
    content = dict()
    last = teacher.last_login
    if last:
        if tday.day == last.day and tday.month == last.month:
            pass
        else:
            content['message'] = "Hello %s " % teacher.first_name
    else:
        content['message'] = "Welcome to EasySchool Teachers' Panel. Update your profile to have more functionality"

    tests = list()
    test_results = list()
    content['teacher'] = teacher
    content['full_name'] = full_name
    content['year'] = tday.year
    content['subjects'] = teacher.subjects.all()
    for subject in teacher.subjects.all():
        test = Exam.objects.filter(supervisor=teacher, exam_subject=subject)
        max_loop = 0
        for each in test:
            details = dict()
            if max_loop > 3:
                break
            details["name"] = each.exam_name
            details['date_available'] = each.date_available
            results = Results.objects.filter(exam_name=each)
            num_of_students = len(results)
            details['students'] = num_of_students
            for result in results:
                avg = average(each)
                if each.date_available > tday:
                    try:
                        ResultObjects.objects.create(name=each, subject=subject, results=result, supervisor=teacher,
                                                     average_marks=avg)
                    except IntegrityError:
                        obj = ResultObjects(name=each, subject=subject, results=result, supervisor=teacher)
                        obj.average = avg
                        obj.save()
                else:
                    obj = ResultObjects(name=each, subject=subject, results=result, supervisor=teacher)
                    if obj.average != avg:
                        obj.average = avg
                        obj.save()

            test_results.append(each.exam_name)
        tests.append(test_results)
    content['results'] = ResultObjects.objects.filter(supervisor=teacher)
    content['tests'] = tests
    content['year'] = year
    content['classteacher'] = teacher.classes.all()
    content['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
    content['num_of_students'] = len(Student.objects.filter(school=teacher.school))
    return render(request, "pages/teachers_dashboard.html", content)

class TeachersUpdateView(UpdateView):
    model = Teacher
    fields = ["first_name", "last_name", "phone", "email", "gender", "subjects"]
    template_name = "pages/teacher_update_form.html"
    template_name_suffix = '_update_form'


class CreateTestView(View):
    tday = timezone.datetime.today()
    year = tday.year

    def get(self, request, *args, **kwargs):
        username = request.user.username
        full_name = request.user.get_full_name()
        teacher = Teacher.objects.get(username=username)
        context = dict()
        context['teacher'] = teacher
        context['full_name'] = full_name
        context['page'] = "create"
        if not teacher.school:
            context['error'] = "You don't have any school details. Contact the Head Teacher to include you"
            return render(request, "pages/create.html", context)
        school = School.objects.get(id=teacher.school.id)
        streams = school.stream.all()
        subjects = teacher.subjects.all()

        context['page'] = "create"
        context['subjects'] = subjects
        context['streams'] = streams
        context['school'] = school
        context['year'] = self.year
        context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
        context['num_of_students'] = len(Student.objects.filter(school=teacher.school))

        return render(request, "pages/create.html", context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        f = request.FILES.get('file')
        subject = request.POST.get('subject')
        school = request.POST.get('school')
        streams = request.POST.getlist('streams[]')
        teacher = Teacher.objects.get(username=request.user.username)
        context = dict()
        context['teacher'] = teacher
        context['full_name'] = teacher.get_full_name()
        context['page'] = "create"
        all_subjects = Subject.objects.all()
        if not f:
            context['error'] = "Question file has not been attached"
            return render(request, "pages/create.html", context)
        if not school:
            context['error'] = "You have not registered to any school. Contact admin for help"
            return render(request, "pages/create.html", context)
        school = School.objects.get(school_name=str(school))
        levels = list()
        for level in school.stream.all():
            for each in streams:
                if str(each) == str(level.__str__()):
                    levels.append(level)
        if not levels:
            levels = school.stream.all()
        for each in all_subjects:
            if str(subject) == each.__str__():
                sub = each
                break
        if not sub:
            context['error'] = "Error the subject is not available"
            return render(request, "pages/create.html", context)

        subject = sub.subject_name
        class_level = sub.class_level
        streams = list()
        for level in levels:
            if level.level_name == class_level:
                streams.append(level)

        filename = 'files/uploads/' + name + '.xlsx'
        try:
            obj = ExamUploads.objects.get(exam_name=name)
            obj.excel_file = f
        except ObjectDoesNotExist:
            obj = ExamUploads(exam_name=name, excel_file=f)
        obj.save()
        filename = ExamUploads.objects.get(exam_name=name)
        response = extract_questions(filename.excel_file.url)
        answers = response[1:]
        answers_with_choices = list()
        for ans in answers:
            details = dict()
            letters = ['A', 'B', 'C', 'D']
            choice_answers = list()
            choices = ans[-3:]
            choices.insert(0, ans[-5])
            for evry in enumerate(choices):
                let = random.choice(letters)
                letters.remove(let)
                choice_answers.append((evry[1], let))
            details["question"] = ans[0]
            details['number'] = ans[1]
            details['topic'] = ans[2]
            details['level'] = ans[3]
            details['correct'] = choice_answers[0]
            details['marks'] = ans[5]
            details['choices'] = choice_answers
            answers_with_choices.append(details)
        questions = list()
        for quiz in answers_with_choices:
            try:
                topic = Topic.objects.get(topic_name=quiz['topic'], class_level=class_level, subjects=sub)
            except ObjectDoesNotExist:
                topic = Topic.objects.create(topic_name=quiz['topic'], class_level=class_level, subjects=sub)
            try:
                correct = Answer.objects.create(answer=quiz['correct'][0], letter=quiz['correct'][1],
                                                marks=int(float(quiz['marks'])))
            except:
                context['error'] = "Invalid details for answer: \"%s\". make sure you have specified the marks"\
                                   % quiz['correct'][0]
                return render(request, "pages/create.html", context)
            _answers = list()
            for choice in quiz['choices'][1:]:
                choice = Answer.objects.create(answer=choice[0], letter=choice[1], marks=0)
                _answers.append(choice)
            question = MultipleChoiceQuestion.objects.create(
                question=quiz['question'],
                number=int(float(quiz['number'])),
                class_level=class_level,
                question_subject=sub,
                question_topic=topic,
                level=str(quiz['level'])[0].upper(),
                correct_answer=correct,
            )
            question.choices.add(correct, _answers[0], _answers[1], _answers[2])
            questions.append(question)
        now = timezone.now()
        delta = timezone.timedelta(days=14)
        latter = now + delta
        # hours = models.PositiveSmallIntegerField(choices=HOURS_CHOICES, null=True, blank=True)
        # minutes = models.PositiveSmallIntegerField(choices=MINUTES_CHOICES, null=True, blank=True)

        exam = Exam.objects.create(
            exam_name=name,
            school=school,
            class_level=class_level,
            exam_subject=sub,
            supervisor=teacher,
            date_available=latter,
        )
        for _stream in streams:
            exam.stream.add(_stream)

        for _question in questions:
            exam.questions_ans.add(_question)

        context['message'] = "%s test has been created" % name
        return render(request, "pages/create.html", context)


def create_test_view(request):
    pass

def tests_view(request):
    teacher = Teacher.objects.get(username=request.user.username)
    full_name = request.user.get_full_name()
    tday = timezone.now()
    year = tday.year
    context = dict()
    context['teacher'] = teacher
    tests = Results.objects.all()
    context['tests'] = tests
    context['year'] = year
    context['page'] = "tests"
    context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
    context['num_of_students'] = len(Student.objects.filter(school=teacher.school))
    context['full_name'] = full_name
    return render(request, "pages/tests.html", context)

def average(name):
    try:
        results = Results.objects.filter(exam_name=name)
    except Results.DoesNotExist:
        return 0
    num_of_students = len(results)
    marks = 0
    for result in results:
        marks += result.total_marks
    if marks > 0:
        average = marks/num_of_students
    else:
        average = 0
    return average

class StatisticsPageView(TemplateView):
    template_name = "pages/statistics.html"
    tday = timezone.now()
    year = tday.year

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StatisticsPageView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()
        context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
        context['num_of_students'] = len(Student.objects.filter(school=teacher.school))
        context['full_name'] = full_name
        context['teacher'] = teacher
        return super(StatisticsPageView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(StatisticsPageView, self).get_context_data(**kwargs)
        context["year"] = self.year
        context['page'] = "statistics"
        return context

class ManageStudentsView(TemplateView):
    template_name = "pages/manage.html"
    tday = timezone.now()
    year = tday.year

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        streams = list()
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()

        for stream in teacher.classes.all():
            streams.append(stream.__str__())

        context['full_name'] = full_name
        context['teacher'] = teacher
        context['streams'] = json.dumps(streams)
        return super(ManageStudentsView, self).render_to_response(context)
        
    def post(self, request, *args, **kwargs):
        stream = request.POST.get('stream')
        teacher = Teacher.objects.get(username=request.user.username)
        school = teacher.school
        for _stream in teacher.classes.all():
            stream = _stream
        f = request.FILES.get('file')
        if not stream or not f:
            return HttpResponse("Please add stream and student file to upload. Download Sample from below")
        
        try:
            filename = StudentUploads.objects.get(stream=stream)
        except ObjectDoesNotExist:
            pass
        else:
            return HttpResponse("Students for this class already exists")
        filename = StudentUploads.objects.create(stream=stream, excel_file=f)
        response = extract_questions(filename.excel_file.url)
        students = response[1:]
        counter = 0
        for student in students:
            fname = student[0]
            lname = student[1]
            _username = str(int(float(student[2])))
            parents_username = _username + str(int(float(student[3])))
            phone = '0' + str(int(float(student[4])))
            try:
                parent = Parent.objects.create(username=parents_username, phone =phone)
                msg = "You have been signed up in EasySchool App username %s" % username
                phn = PhoneNumber(phone)
                phn = phn.list_of_numbers()[0]
                t=SMShandler([phn],msg)
                t.sendMessage()
            except IntegrityError:
                parent = Parent.objects.get(username=parents_username)
            
            try:
                std = Student.objects.create(username=_username, phone=phone, school=school,
                first_name=fname, last_name=lname, stream=stream)
                std.set_password("easyschool")
                std.parents.add(parent)
                std.save()
                counter += 1
            except IntegrityError:
                pass
        response = "%d students uploaded" % counter
        return HttpResponse(response)

    def get_context_data(self, **kwargs):
        context = super(ManageStudentsView, self).get_context_data(**kwargs)
        context["year"] = self.year
        context['page'] = "manage"
        return context


class StudentsPageView(TemplateView):
    template_name = "pages/students.html"
    tday = timezone.now()
    year = tday.year

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        students = list()
        tests = list()
        subjects = list()
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()
        _subjects = teacher.subjects.all()
        all_students = Student.objects.filter(school=teacher.school)
        for subject in _subjects:
            for each in all_students:
                if not subject.class_level or not each.stream:
                    continue
                if subject.class_level == each.stream.level_name:
                    students.append(str(each.get_full_name()))
        for test in Exam.objects.filter(supervisor=teacher):
            tests.append(test.exam_name)
        for sub in _subjects:
            subjects.append(sub.subject_name)
        context['teacher'] = teacher
        context['students'] = json.dumps(list(set(students)))
        context['classes'] = json.dumps(subjects)
        context['tests'] = json.dumps(tests)
        context['num_of_tests'] = len(tests)
        context['num_of_students'] = len(Student.objects.filter(school=teacher.school))
        context['full_name'] = full_name
        return super(StudentsPageView, self).render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        student = request.POST.get('student')
        teacher = Teacher.objects.get(username=request.user.username)
        full_name = request.user.get_full_name()
        split = str(student).split(" ")[:2]
        if len(split) < 2:
            fname = split[0]
            sname = ""
        else:
            fname, sname = split
        context['teacher'] = teacher
        context['full_name'] = full_name
        test_name = request.POST.get('test')
        try:
            test = Exam.objects.get(exam_name=test_name)
        except ObjectDoesNotExist:
            context['error'] = "There is no test with the specified name. Have you created any test so far?"
            return super(StudentsPageView, self).render_to_response(context)
        student = Student.objects.filter(Q(first_name__startswith=fname), Q(last_name__startswith=sname))
        if len(student) > 1:
            students = list()
        elif len(student) == 1:
            student = student[0]
        else:
            context["error"] = "No student has been found with the specified name. Give both the first and the last name" \
                               "in that order"
        results = CompletedTests.objects.filter(test=test, student=student)
        context['student'] = student
        context['exam'] = test_name
        context['results'] = results
        context['num_of_tests'] = len(Exam.objects.filter(supervisor=teacher))
        context['num_of_students'] = len(Student.objects.filter(school=teacher.school))
        return super(StudentsPageView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(StudentsPageView, self).get_context_data(**kwargs)
        context["year"] = self.year
        context['page'] = "students"
        return context


@login_required(login_url='easy/login')
def student_home_page(request):
    tday = timezone.datetime.today()
    year = tday.year
    username = request.user.username
    details = dict()
    try:
        student = Student.objects.get(username=username)
        fullname = student.get_full_name()
        stream = student.stream
        if stream:
            class_level = stream.level_name
        else:
            class_level = 0
        details['fullname'] = fullname
        details['stream'] = stream
        details['year'] = year
    except ObjectDoesNotExist:
        return HttpResponse("Your account as a student is not available. Please contact your class teacher")

    available_tests = list()
    try:
        tests = Exam.objects.filter(class_level=class_level)
        now = timezone.now()
        for test in tests:
            try:
                Results.objects.get(exam_name=test, student_id=student)
                continue
            except ObjectDoesNotExist:
                pass
            available = test.date_available
            if available > now and ([x for x in test.stream.all() if x.stream_name == stream.stream_name]
                                    or not test.stream):
                available_tests.append(test)
        if len(available_tests) < 1:
            info = "There are no available tests at the moment"
        elif len(available_tests) == 1:
            info = "One test available for %s" % stream.stream_name
        else:
            info = "%d tests available for %s" % (len(available_tests), stream.stream_name)

    except ObjectDoesNotExist:
        info = info = "There are no available tests at the moment"
    details = {
        'tests': available_tests,
        'info': info,
        'fullname': fullname,
        'stream': stream,
        'year': year,
    }
    return render_to_response("pages/units.html", details)


class FormPageView(TemplateView):
    template_name = "pages/formpage.html"
    tday = timezone.datetime.today()
    year = tday.year

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FormPageView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        test = request.GET.get('test_code')
        self.exam = Exam.objects.get(exam_name=test)
        context = self.get_context_data()
        context['year'] = self.year
        return super(FormPageView, self).render_to_response(context)

    def post(self, request, *args, **kwargs):
        student_name = request.user.username
        try:
            student = Student.objects.get(username=student_name)
        except ObjectDoesNotExist:
            return HttpResponse("Your details are not available")
        test = request.POST['test_code']
        exam = Exam.objects.get(exam_name=test)
        try:
            Results.objects.get(exam_name=exam, student_id=student)
            return HttpResponse("You have already submitted your answers")
        except ObjectDoesNotExist:
            pass
        questions = exam.questions_ans.all()
        txt = ""
        correct = 0
        wrong = 0
        marks = 0
        total_marks = 0
        for quiz in questions:
            answer = request.POST.get(str(quiz.number))
            if answer is not None:
                txt = txt + request.POST.get(str(quiz.number))
                total_marks += quiz.correct_answer.marks                
                if quiz.correct_answer.id == int(answer):                    
                    test = CompletedTests(test=exam, student=student, question=quiz, answer=quiz.correct_answer,
                                          value=True)
                    correct += 1
                    try:
                        marks += quiz.correct_answer.marks
                    except (ValueError, TypeError):
                        marks += 3
                    test.save()
                else:
                    for choice in quiz.choices.all():
                        if choice.id == int(answer):
                            answer = Answer.objects.get(id=choice.id)
                            break
                    if not isinstance(answer, unicode):
                        test = CompletedTests(test=exam, student=student, question=quiz, answer=answer, value=False)
                    wrong += 1
                    test.save()
        results = Results(exam_name=exam, student_id=student, total_marks=marks, out_off=total_marks)
        results.save()
        _name = student.get_full_name()
        msg = "%s has completed %s and has scored %d out of %d" % (_name, str(exam.exam_name), int(marks), int(total_marks))
        phone = str(student.phone)
        phn = PhoneNumber(phone)
        phn = phn.list_of_numbers()[0]
        #try:
        t=SMShandler([phn],msg)
        t.sendMessage()
        return HttpResponse(t.sendMessage())
        #except:
        #    pass
        return HttpResponse("You got %d question(s) correct and %d question(s) wrong %s" % (correct, wrong, ))

    def get_context_data(self, **kwargs):
        context = super(FormPageView, self).get_context_data(**kwargs)
        questions = self.exam.questions_ans
        context['exam'] = self.exam
        context['questions'] = questions.all().order_by('number')
        context['year'] = self.year
        return context

def extract_questions(name):
    filename = name
    try:
        wb = open_workbook(filename)
    except IOError, e:
        return False, e
    questions = []
    s = wb.sheets()[0]
    for row in range(s.nrows):
        column_values = []
        for col in range(s.ncols):
            value = s.cell(row, col).value
            column_values.append(str(value))
        questions.append(column_values)
    return questions

def download_student_excel_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Question', 'Number', 'Topic', 'Level', 'Correct Answer', 'Answer 1', 'Answer 2', 'Answer 3'])
    return response


def download_question_excel_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questions.csv"'
    writer = csv.writer(response)
    writer.writerow(['QUESTION', 'NUMBER', 'TOPIC', 'LEVEL', 'CORRECT ANSWER', 'MARKS', 'ANSWER 1',
                     'ANSWER 2', 'ANSWER 3'])
    return response

