from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm 
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm,CustomPasswordChangeForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()  # ✅ Use custom form here too
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = CustomPasswordChangeForm(request.user, request.POST)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            user = p_form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/profile_update.html', {
        'u_form': u_form,
        'p_form': p_form
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')