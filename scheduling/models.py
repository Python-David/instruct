from django.db import models

from curriculum.models import Lesson


class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='time_slots')

    def __str__(self):
        return f"{self.lesson.title}: {self.start_time} - {self.end_time}"


class Schedule(models.Model):
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='schedules')
    scheduled_date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        lesson_title = self.time_slot.lesson.title
        start_time = self.time_slot.start_time.strftime('%H:%M')
        end_time = self.time_slot.end_time.strftime('%H:%M')
        return f"{lesson_title} scheduled for {self.scheduled_date} from {start_time} to {end_time}"

