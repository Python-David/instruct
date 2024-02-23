from django.db import models


class Curriculum(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=50)
    education_level = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Subject(models.Model):
    curriculum = models.ForeignKey(Curriculum, related_name='subjects', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    week = models.IntegerField()
    # goals
    duration = models.IntegerField(null=True, blank=True)  # Duration in minutes

    def __str__(self):
        return self.title
