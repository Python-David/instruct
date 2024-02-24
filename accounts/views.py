from datetime import timedelta

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode

from .config import LOGIN_ERROR_MESSAGE, LOGIN_SUCCESS_MESSAGE, ACCOUNT_ACTIVATION_SUBJECT, \
    ACCOUNT_VERIFICATION_SUCCESS_MESSAGE, ACCOUNT_VERIFICATION_FAILURE_MESSAGE, RESET_PASSWORD_SUBJECT, \
    PASSWORD_RESET_SUCCESS_EMAIL, ACCOUNT_DOES_NOT_EXIST_MESSAGE, RESET_PASSWORD_SUCCESS_MESSAGE, \
    RESET_PASSWORD_ERROR_MESSAGE, PASSWORD_RESET_SUCCESS_MESSAGE, PASSWORDS_DO_NOT_MATCH, LOGOUT_SUCCESS_MESSAGE
from .forms import RegistrationForm
from .models import Account
from .utils import send_email
from scheduling.models import Schedule

from curriculum.models import AcademicYear, Subject


def login(request):
    if request.method != "POST":
        return render(request, "accounts/login.html")

    email = request.POST.get("email")
    password = request.POST.get("password")
    user = auth.authenticate(email=email, password=password)

    if not user:
        messages.error(request, LOGIN_ERROR_MESSAGE)
        return redirect("login")

    auth.login(request, user)
    messages.success(request, LOGIN_SUCCESS_MESSAGE)
    return redirect("dashboard")


@login_required(login_url="login")
def dashboard(request):
    today = timezone.localdate()

    # Fetch today's scheduled time slots for the logged-in user's lessons
    todays_schedules = Schedule.objects.filter(
        scheduled_date=today,
        time_slot__lesson__lesson_plan__term__academic_year__user=request.user
    ).select_related(
        'time_slot',
        'time_slot__lesson',
        'time_slot__lesson__lesson_plan',
        'time_slot__lesson__lesson_plan__subject',
    ).order_by('time_slot__start_time')

    # Format today's schedules for the template
    todays_lessons_formatted = [
        {
            'time_slot': f"{schedule.time_slot.start_time.strftime('%H:%M')} - {schedule.time_slot.end_time.strftime('%H:%M')}",
            'lesson_title': schedule.time_slot.lesson.title,
            'subject_name': schedule.time_slot.lesson.lesson_plan.subject.name,
        }
        for schedule in todays_schedules
    ]

    # Fetch academic year overviews for the logged-in user
    academic_years = AcademicYear.objects.filter(
        user=request.user
    ).prefetch_related(
        'curriculum__subjects',  # Assuming Curriculum has a related_name 'subjects' to Subject
        'term_set'  # Fetch terms related to the academic year
    )

    academic_year_overviews = []
    for year in academic_years:
        terms = year.term_set.all()
        for term in terms:
            subjects = Subject.objects.filter(curriculum=year.curriculum).values_list('name', flat=True)
            academic_year_overviews.append({
                'term': f"Term {term.term_number} Overview",
                'curriculum': year.curriculum.name,
                'duration': f"{term.start_date.strftime('%b')} - {term.end_date.strftime('%b')}",
                'subjects': list(subjects),
            })

    context = {
        'todays_lessons': todays_lessons_formatted,
        'academic_year_overviews': academic_year_overviews,
    }
    return render(request, "accounts/dashboard.html", context)


def register(request):
    # Pull data from form and create a new user
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )

            user.phone_number = phone_number

            user.save()

            # User activation

            send_email(
                request=request,
                user=user,
                subject=ACCOUNT_ACTIVATION_SUBJECT,
                template="accounts/account_verification_email.html",
                redirect_url="/accounts/login/?command=verification&email=" + email,
            )
            messages.success(request, "Registration successful")

            return redirect("/accounts/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, ACCOUNT_VERIFICATION_SUCCESS_MESSAGE)
        return redirect("login")
    else:
        messages.error(request, ACCOUNT_VERIFICATION_FAILURE_MESSAGE)
        return redirect("register")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, LOGOUT_SUCCESS_MESSAGE)

    return redirect("login")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            send_email(
                request=request,
                user=user,
                subject=RESET_PASSWORD_SUBJECT,
                template="accounts/reset_password_email.html",
                redirect_url="login",
            )
            messages.success(request, PASSWORD_RESET_SUCCESS_EMAIL)
            return redirect("login")
        else:
            messages.error(request, ACCOUNT_DOES_NOT_EXIST_MESSAGE)

            return redirect("forgot_password")

    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    uid = ""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, RESET_PASSWORD_SUCCESS_MESSAGE)
        return redirect("reset_password")  # login
    else:
        messages.error(request, RESET_PASSWORD_ERROR_MESSAGE)
        return redirect("login")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, PASSWORD_RESET_SUCCESS_MESSAGE)
            return redirect("login")
        else:
            messages.error(request, PASSWORDS_DO_NOT_MATCH)
            return redirect("reset_password")

    else:
        return render(request, "accounts/reset_password.html")
