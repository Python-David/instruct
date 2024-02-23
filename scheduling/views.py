from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
from django.views.generic import TemplateView
from django.utils import timezone
from .models import Schedule


class TodaysScheduleView(TemplateView):
    template_name = 'accounts/dashboard.html'  # Assuming your dashboard template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        todays_lessons = Schedule.objects.filter(scheduled_date=today).select_related('lesson', 'lesson__subject')
        print(f"These are the day's lessons {todays_lessons}")
        context['todays_lessons'] = todays_lessons
        return context


class WeeklyOverviewView(TemplateView):
    template_name = 'dashboard.html'  # Assuming your dashboard template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        start_week = today - timedelta(today.weekday())  # Monday
        end_week = start_week + timedelta(7)  # Sunday
        weekly_lessons = Schedule.objects.filter(scheduled_date__range=[start_week, end_week]).select_related('lesson',
                                                                                                              'lesson__subject')
        context['weekly_lessons'] = weekly_lessons
        return context
