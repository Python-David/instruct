from django.urls import path
from .views import TodaysScheduleView, WeeklyOverviewView

urlpatterns = [
    path('dashboard/today/', TodaysScheduleView.as_view(), name='todays_schedule'),
    path('dashboard/week/', WeeklyOverviewView.as_view(), name='weekly_overview'),
    # Other paths...
]
