from django.shortcuts import render, redirect
from .scheduler_service import generate_timetable
from .models import *
from .forms import *

def generate_timetable_view(request):
    instructors = Instructor.objects.all()
    classrooms = Classroom.objects.all()
    context = {
        'instructors': instructors,
        'classrooms': classrooms
    }

    if request.method == 'POST':
        Timetable.objects.all().delete()
        generate_timetable()
        return redirect('timetable')

    return render(request, 'scheduler/generate.html', context)

def timetable_view(request):
    timetable = Timetable.objects.all()
    hours = range(9, 17)  # Hours from 9 AM to 5 PM
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    context = {
        'timetable': timetable,
        'hours': hours,
        'days': days,
    }
    return render(request, 'scheduler/timetable.html', context)

def add_course(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.save()
            return redirect('/generate')
    else:
        form = CourseForm()

    return render(request, 'scheduler/course.html', {'form':form, 'courses': courses})

def add_instructor(request):
    instructors = Instructor.objects.all()
    if request.method == 'POST':
        form = InstructorForm(request.POST)
        if form.is_valid():
            instructor = form.save(commit=False)
            instructor.save()
            return redirect('/generate')
    else:
        form = InstructorForm()

    return render(request, 'scheduler/instructor.html', {'form':form, 'instructors': instructors})

def add_classroom(request):
    classrooms = Classroom.objects.all()
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.save()
            return redirect('/generate')
    else:
        form = ClassroomForm()

    return render(request, 'scheduler/classroom.html', {'form':form, 'classrooms': classrooms})
