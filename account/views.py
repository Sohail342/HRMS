from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import EmailLoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('HRMS:home'))

    if request.method == 'POST':
        form = EmailLoginForm(request.POST) 
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=email, password=password)

            if user is not None:
                if not user.is_approved:
                    messages.error(request, "Your account is not approved yet.")
                    return redirect(reverse('account:login'))

                login(request, user)
                return redirect('HRMS:home')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = EmailLoginForm() 

    return render(request, 'account/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('account:login')


