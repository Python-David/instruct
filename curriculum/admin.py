from django.contrib import admin

from .models import Curriculum, Subject, Lesson

admin.site.register(Curriculum)
admin.site.register(Subject)
admin.site.register(Lesson)
