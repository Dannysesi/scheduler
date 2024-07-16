from django.urls import path
from .views import *

urlpatterns = [
    path('generate/', generate_timetable_view, name='generate_timetable'),
    path('', timetable_view, name='timetable'),
    path('course', add_course, name='course'),
    path('classroom', add_classroom, name='classroom'),
    path('instructor', add_instructor, name='instructor'),
]
