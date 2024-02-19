from django.db import models

from instruct.curriculum.models import Lesson


class Resource(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='resources', on_delete=models.CASCADE)
    type = models.CharField(max_length=50)  # audio, video, article, quiz etc.
    url = models.URLField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.type} for {self.lesson.title}"
