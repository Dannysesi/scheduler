from django.db import models

class Instructor(models.Model):
    name = models.CharField(max_length=100)
    availability = models.JSONField()  # Store availability as a JSON

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        (200, '200 Level'),
        (300, '300 Level'),
        (400, '400 Level'),
    ]
    name = models.CharField(max_length=100)
    requirements = models.TextField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL_CHOICES)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

class Timetable(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, blank=True, null=True)
    time = models.TimeField(blank=True, null=True)


