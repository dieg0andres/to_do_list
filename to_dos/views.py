from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_list_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.mail import send_mail
from django.conf import settings

from .models import DoItem, ProfileUser
from .forms import MyUserCreationForm, MyAuthenticationForm

from django.contrib.auth import views as auth_views


def send_test_email(request):
    subject = 'Test Email'
    message = 'This is a test email sent using SendGrid from Django.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['diego.a.galindo@gmail.com']

    send_mail(subject, message, from_email, recipient_list)
    print('im here')
    return HttpResponse('Email sent successfully!')


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/my_password_reset_confirm.html'


def home(request):
    return HttpResponse('welcome to diegos first app')


@login_required
def to_dos(request, tag):

    ProfileUser.objects.filter(user=request.user).update(tag_selected=tag)

    if request.method == 'POST':
        new_to_do = request.POST.get('new_to_do')
        if new_to_do:
            DoItem(title=new_to_do).save()

        selected_to_do = request.POST.get('selected_to_do')
        if selected_to_do:
            do_completed = DoItem.objects.get(pk=selected_to_do)
            do_completed.complete=True
            do_completed.save()

    do_items = DoItem.objects.filter(complete=False, user=request.user, tag=request.user.profile.tag_selected)
    context = {'to_do_list' : do_items}
    
    return render(request, "to_dos/to_dos.html", context)


@login_required
def details(request, id):
    
    do_item = get_list_or_404(DoItem, pk=id)[0]
    tag = request.user.profile.tag_selected
    context = {'to_do' : do_item }

    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            do_item.title=new_title
            do_item.save()

        new_desc = request.POST.get('description')
        if new_desc:
            do_item.description=new_desc
            do_item.save()

        return redirect('to_dos', tag)

    return render(request, "to_dos/details.html", context)


@login_required
def new_todo(request):

    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        tag = request.user.profile.tag_selected

        if title and not desc:
            DoItem(title=title, description="", user=request.user, tag=tag).save()

        if title and desc:
            DoItem(title=title, description=desc, user=request.user, tag=tag).save()
        
        return redirect('to_dos', tag)

    return render(request, "to_dos/new_todo.html")


@login_required
def edit_todo(request, id):
    
    do_item = get_list_or_404(DoItem, pk=id)[0]
    
    context = {
        'to_do' : do_item,
        'id' : id 
    }

    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            do_item.title=new_title
            do_item.save()

        new_desc = request.POST.get('description')
        if new_desc:
            do_item.description=new_desc
            do_item.save()

        return redirect('to_dos', request.user.profile.tag_selected)

    return render(request, "to_dos/edit_todo.html", context)


@login_required
def delete_todo(request, id):
    to_do = get_list_or_404(DoItem, id=id, user=request.user)
    to_do[0].delete()
    return redirect('to_dos', request.user.profile.tag_selected)


def signup(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('to_dos', 'home')
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
            return redirect('to_dos', 'home')
        else:
            messages.error(request, "Invalid username or password")
    else:
        logout(request)
        form = MyAuthenticationForm()

    return render(request, 'registration/login.html', {'form':form})

@login_required
def create_tag(request):
    if request.method == 'POST':
        list_title = request.POST.get('list_title')
        profile_user = request.user.profile
        profile_user.tags.append(list_title)
        profile_user.tag_selected = list_title
        profile_user.save()

        return redirect('to_dos', list_title)

    return render(request, 'to_dos/create_tag.html')


@login_required
def delete_list(request):

    profile_user = request.user.profile
    old_tag = profile_user.tag_selected
    profile_user.tags.remove(old_tag)
    profile_user.tag_selected="home"
    profile_user.save(update_fields=['tags','tag_selected'])

    dos_to_delete = DoItem.objects.filter(user=request.user, tag=old_tag)
    dos_to_delete.delete()

    return redirect('to_dos', 'home')
