from django.db import models

from accounts.models import Account


class Curriculum(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=50)
    education_level = models.CharField(max_length=50)
    starting_age = models.IntegerField()
    publisher = models.CharField(max_length=50)
    users = models.ManyToManyField(Account, related_name='curriculums')

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.start_date.year} - {self.end_date.year})"

    def get_term_dates(self):
        # Logic to dynamically fetch term dates for display in templates
        pass


class Term(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term_number = models.IntegerField()  # e.g., 1 for Term 1
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Term {self.term_number} of {self.academic_year}"


class Subject(models.Model):
    curriculum = models.ForeignKey(Curriculum, related_name='subjects', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class LessonPlan(models.Model):
    subject = models.ForeignKey(Subject, related_name='lesson_plans', on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    week_number = models.IntegerField()
    overview = models.TextField(blank=True)
    # duration = models.DurationField(default=datetime.timedelta(hours=1))  # Default duration 1 hour

    def __str__(self):
        return f"Week {self.week_number} - {self.subject.name}"


class Lesson(models.Model):
    lesson_plan = models.ForeignKey(LessonPlan, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


# class UserProgress(models.Model):
#     lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
#     user = models.ForeignKey(Account, on_delete=models.CASCADE)
#     date_completed = models.DateField(null=True, blank=True)
#     status = models.CharField(max_length=50, choices=[('Completed', 'Completed'), ('In Progress', 'In Progress'), ('Not Started', 'Not Started')])
#     notes = models.TextField(blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.user.username} - {self.lesson.title} ({self.status})"
