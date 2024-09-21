from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import MyUserCreationForm, MyAuthenticationForm
from ..models import Tag
from django.contrib.auth import views as auth_views



class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/my_password_reset_confirm.html'


def signup(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            tag_unique_str = user.profile.selected_tag_unique_str
            return redirect('to_dos', tag_unique_str)
    else:
        form = MyUserCreationForm()
        logout(request)
    return render(request, "registration/signup.html", {'form':form})


def log_in(request):
    if request.method == 'POST':
        form = MyAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            tag = Tag.objects.get(unique_str=request.user.profile.selected_tag_unique_str)

            return redirect('to_dos', tag.unique_str)
        else:
            messages.error(request, "Invalid username or password")
    else:
        logout(request)
        form = MyAuthenticationForm()

    return render(request, 'registration/login.html', {'form':form})