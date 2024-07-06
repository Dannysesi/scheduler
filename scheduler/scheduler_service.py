from .models import Course, Instructor, Classroom, Timetable
import random
from datetime import time

def generate_timeslots():
    timeslots = []
    hours = [(9, 0), (10, 0), (11, 0), (12, 0), (14, 0), (15, 0),]  # Exclude break time at 13:00-14:00
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    for day in days:
        for hour, minute in hours:
            if not (day == 'Monday' and hour == 9):  # Skip Monday assembly period
                timeslots.append({"day": day, "time": time(hour, minute)})
    return timeslots

def is_timeslot_available(timetable, timeslot, course):
    instructor_courses = [t for t in timetable if t.course.instructor == course.instructor and t.day == timeslot["day"] and t.time == timeslot["time"]]
    return not instructor_courses

def is_classroom_available(timetable, timeslot, classroom):
    classroom_courses = [t for t in timetable if t.classroom == classroom and t.day == timeslot["day"] and t.time == timeslot["time"]]
    return not classroom_courses  # Ensure the classroom is completely free at this time

def select_classroom(timetable, timeslot, classrooms, level):
    available_classrooms = [c for c in classrooms if is_classroom_available(timetable, timeslot, c)]
    return random.choice(available_classrooms) if available_classrooms else None

def generate_timetable():
    courses = list(Course.objects.all())
    classrooms = list(Classroom.objects.all())
    timeslots = generate_timeslots()
    timetable = []

    # Shuffle courses to distribute them more evenly
    random.shuffle(courses)

    day_counts = {day: 0 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    course_distribution = {course: {day: 0 for day in day_counts} for course in courses}
    instructor_distribution = {instructor: {day: 0 for day in day_counts} for instructor in Instructor.objects.all()}

    # Schedule each course at least 3 times a week
    for course in courses:
        scheduled_times = 0
        days = list(day_counts.keys())
        random.shuffle(days)  # Shuffle days to ensure even distribution
        for day in days:
            if scheduled_times >= 3:
                break
            available_timeslots = [ts for ts in timeslots if ts["day"] == day]
            random.shuffle(available_timeslots)  # Shuffle timeslots to ensure even distribution
            for timeslot in available_timeslots:
                if is_timeslot_available(timetable, timeslot, course) and is_classroom_available(timetable, timeslot, classrooms):
                    classroom = select_classroom(timetable, timeslot, classrooms, course.level)
                    if classroom:
                        timetable.append(Timetable(course=course, classroom=classroom, day=day, time=timeslot["time"]))
                        day_counts[day] += 1
                        course_distribution[course][day] += 1
                        instructor_distribution[course.instructor][day] += 1
                        scheduled_times += 1
                        break

    # Ensure at least 5 lectures per day but not more than 10
    for day in day_counts:
        while day_counts[day] < 5:
            available_timeslot = random.choice([ts for ts in timeslots if ts["day"] == day])
            random.shuffle(courses)  # Shuffle courses to ensure even distribution
            for course in courses:
                if is_timeslot_available(timetable, available_timeslot, course) and is_classroom_available(timetable, available_timeslot, classrooms):
                    classroom = select_classroom(timetable, available_timeslot, classrooms, course.level)
                    if classroom:
                        timetable.append(Timetable(course=course, classroom=classroom, day=day, time=available_timeslot["time"]))
                        day_counts[day] += 1
                        course_distribution[course][day] += 1
                        instructor_distribution[course.instructor][day] += 1
                        break

    for day in day_counts:
        while day_counts[day] < 10:
            available_timeslot = random.choice([ts for ts in timeslots if ts["day"] == day])
            available_courses = [course for course in courses if course_distribution[course][day] < 3 and instructor_distribution[course.instructor][day] < 3]
            if not available_courses:
                break
            random.shuffle(available_courses)  # Shuffle available courses to ensure even distribution
            for course in available_courses:
                if is_timeslot_available(timetable, available_timeslot, course) and is_classroom_available(timetable, available_timeslot, classrooms):
                    classroom = select_classroom(timetable, available_timeslot, classrooms, course.level)
                    if classroom:
                        timetable.append(Timetable(course=course, classroom=classroom, day=day, time=available_timeslot["time"]))
                        day_counts[day] += 1
                        course_distribution[course][day] += 1
                        instructor_distribution[course.instructor][day] += 1
                        break

    Timetable.objects.bulk_create(timetable)
