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
    # Fetch today's date, adjusted for the current timezone
    today = timezone.localdate()

    # Fetch today's lessons for the logged-in user
    todays_lessons = Schedule.objects.filter(scheduled_date=today).select_related('lesson', 'lesson__subject')

    # Calculate the start (Monday) and end (Sunday) of the week
    start_week = today - timedelta(days=today.weekday())  # Monday
    end_week = start_week + timedelta(days=6)  # Sunday

    # Fetch lessons for the week and format the dates
    weekly_lessons = Schedule.objects.filter(scheduled_date__range=[start_week, end_week]).select_related('lesson', 'lesson__subject')
    formatted_weekly_lessons = [
        {
            'formatted_date': lesson.scheduled_date.strftime("%A, %b. %d, %Y"),
            'lesson_title': lesson.lesson.title,
            'subject_name': lesson.lesson.subject.name
        }
        for lesson in weekly_lessons
    ]

    # Pass formatted_weekly_lessons to the template
    context = {
        'todays_lessons': todays_lessons,  # Assuming you'll handle today's lessons similarly or leave as is
        'weekly_lessons': formatted_weekly_lessons,
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
