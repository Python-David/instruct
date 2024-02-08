from django.contrib import auth, messages
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode

from .config import LOGIN_ERROR_MESSAGE, LOGIN_SUCCESS_MESSAGE, ACCOUNT_ACTIVATION_SUBJECT, \
    ACCOUNT_VERIFICATION_SUCCESS_MESSAGE, ACCOUNT_VERIFICATION_FAILURE_MESSAGE
from .forms import RegistrationForm
from .models import Account
from .utils import send_email


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
    return redirect("home")


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


def logout(request):
    return
