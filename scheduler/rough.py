from .models import Course, Instructor, Classroom, Timetable
import random
from datetime import time


def generate_timeslots():
    timeslots = []
    hours = [(9, 0), (10, 0), (11, 0), (12, 0), (14, 0), (15, 0), (16, 0)]  # Exclude break time at 13:00-14:00
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    for day in days:
        for hour, minute in hours:
            if not (day == 'Monday' and hour == 9):  # Skip Monday assembly period
                timeslots.append({"day": day, "time": time(hour, minute)})
    return timeslots

def is_timeslot_available(timetable, timeslot, course):
    instructor_courses = [t for t in timetable if t.course.instructor == course.instructor and t.day == timeslot["day"] and t.time == timeslot["time"]]
    if instructor_courses:
        return False
    return True


def is_classroom_available(timetable, timeslot, classrooms, level):
    classroom_courses = [t for t in timetable if t.classroom == classrooms and t.day == timeslot["day"] and t.time == timeslot["time"]]
    for c in classroom_courses:
        if c.course.level == level:
            return False  # Existing course at the same level using the classroom
    return True


def select_classroom(timetable, timeslot, classrooms, level):
    available_classrooms = [c for c in classrooms if is_classroom_available(timetable, timeslot, c, level)]
    return random.choice(available_classrooms) if available_classrooms else None


def generate_timetable():
    courses = list(Course.objects.all())
    classrooms = Classroom.objects.all()
    timeslots = generate_timeslots()
    timetable = []

    # Shuffle courses to distribute them more evenly
    random.shuffle(courses)

    day_counts = {day: 0 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    course_distribution = {course: {day: 0 for day in day_counts} for course in courses}
    instructor_distribution = {instructor: {day: 0 for day in day_counts} for instructor in Instructor.objects.all()}

    for course in courses:
        for timeslot in timeslots:
            day = timeslot["day"]

            # Ensure at least 5 lectures per day
            if day_counts[day] >= 5:
                continue

            if is_timeslot_available(timetable, timeslot, course) and is_classroom_available(timetable, timeslot, classrooms, course.level):
                classroom = select_classroom(timetable, timeslot, classrooms, course.level)
                if classroom:
                    timetable.append(Timetable(course=course, classroom=classroom, day=day, time=timeslot["time"]))
                    day_counts[day] += 1
                    course_distribution[course][day] += 1
                    instructor_distribution[course.instructor][day] += 1
                    break

    # Check and add missing lectures if any day has less than 5 lectures
    for day in day_counts:
        while day_counts[day] < 5:
            for course in courses:
                available_timeslot = next((ts for ts in timeslots if ts["day"] == day and is_timeslot_available(timetable, ts, course)), None)
                if available_timeslot:
                    if is_classroom_available(timetable, available_timeslot, classrooms, course.level):
                        classroom = select_classroom(timetable, available_timeslot, classrooms, course.level)
                        if classroom:
                            timetable.append(Timetable(course=course, classroom=classroom, day=day, time=available_timeslot["time"]))
                            day_counts[day] += 1
                            course_distribution[course][day] += 1
                            instructor_distribution[course.instructor][day] += 1
                            break

    # Further refine the distribution to avoid redundancy
    for day in ["Thursday", "Friday"]:
        for timeslot in timeslots:
            if timeslot["day"] == day:
                scheduled_entries = [entry for entry in timetable if entry.day == day and entry.time == timeslot["time"]]
                if scheduled_entries:
                    for entry in scheduled_entries:
                        if course_distribution[entry.course][day] > 1 or instructor_distribution[entry.course.instructor][day] > 1:
                            available_courses = [course for course in courses if course_distribution[course][day] == 0 and instructor_distribution[course.instructor][day] == 0]
                            if available_courses:
                                new_course = random.choice(available_courses)
                                if is_timeslot_available(timetable, timeslot, new_course) and is_classroom_available(timetable, timeslot, classrooms, new_course.level):
                                    classroom = select_classroom(timetable, timeslot, classrooms, new_course.level)
                                    if classroom:
                                        # Replace the redundant entry
                                        timetable.remove(entry)
                                        timetable.append(Timetable(course=new_course, classroom=classroom, day=day, time=timeslot["time"]))
                                        course_distribution[entry.course][day] -= 1
                                        instructor_distribution[entry.course.instructor][day] -= 1
                                        course_distribution[new_course][day] += 1
                                        instructor_distribution[new_course.instructor][day] += 1

    Timetable.objects.bulk_create(timetable)

