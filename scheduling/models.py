from django.db import models

from instruct.curriculum.models import Lesson


class Schedule(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.lesson.title} scheduled for {self.scheduled_date}"
