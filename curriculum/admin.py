from django.contrib import admin

from .models import Curriculum, Subject, Lesson, AcademicYear, Term, LessonPlan

admin.site.register(Curriculum)
admin.site.register(AcademicYear)
admin.site.register(Term)
admin.site.register(Subject)
admin.site.register(LessonPlan)
admin.site.register(Lesson)
