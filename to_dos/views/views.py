from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_list_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.mail import send_mail
from django.conf import settings

from ..models import DoItem, ProfileUser, Tag
from ..forms import MyUserCreationForm, MyAuthenticationForm

from django.contrib.auth import views as auth_views


def send_test_email(request):
    subject = 'Test Email'
    message = 'This is a test email sent using SendGrid from Django.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['diego.a.galindo@gmail.com']

    send_mail(subject, message, from_email, recipient_list)

    return HttpResponse('Email sent successfully!')


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/my_password_reset_confirm.html'


def add_middle_space(s):
    return s[:4] + ' ' + s[4:] 

@login_required
def to_dos(request, tag_unique_str):
    
    ProfileUser.objects.filter(user=request.user).update(selected_tag_unique_str=tag_unique_str)

    if request.method == 'POST':
        new_to_do = request.POST.get('new_to_do')
        if new_to_do:
            DoItem(title=new_to_do).save()

        selected_to_do = request.POST.get('selected_to_do')
        if selected_to_do:
            do_completed = DoItem.objects.get(pk=selected_to_do)
            do_completed.complete=True
            do_completed.save()

    do_items = DoItem.objects.filter(
        complete=False, 
        users=request.user, 
        tag__unique_str=request.user.profile.selected_tag_unique_str
        )
    
    current_tag = Tag.objects.get(unique_str=request.user.profile.selected_tag_unique_str)
    context = {
        'to_do_list' : do_items,
        'current_tag' : current_tag,
        'tag_unique_str_with_space' : add_middle_space(current_tag.unique_str),
        'home_tag_unique_str' : request.user.tags.get(name='Home').unique_str
    }
    
    return render(request, "to_dos/to_dos.html", context)


@login_required
def details(request, id):
    
    do_item = get_list_or_404(DoItem, pk=id)[0]
    tag = Tag.objects.get(unique_str=request.user.profile.selected_tag_unique_str)
    context = {
        'to_do' : do_item,
        'home_tag_unique_str' : request.user.tags.get(name='Home').unique_str
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

        return redirect('to_dos', tag.unique_str)

    return render(request, "to_dos/details.html", context)


@login_required
def new_todo(request):

    if request.method == 'POST':
        desc = request.POST.get('description', "")
        tag = Tag.objects.get(unique_str=request.user.profile.selected_tag_unique_str)

        do_item = DoItem(
            title = request.POST.get('title'),
            description = desc, 
            tag = tag
        )
        do_item.save()
        do_item.users.add(request.user)

        if tag.shared:
            users = tag.users.all()

            for user in users:
                do_item.users.add(user)


        return redirect('to_dos', tag.unique_str)
    
    home_tag_unique_str = request.user.tags.get(name='Home').unique_str
    return render(request, 'to_dos/new_todo.html', {'home_tag_unique_str': home_tag_unique_str})


@login_required
def edit_todo(request, id):
    print('im here1')
    print('the stus: ', request.user.profile.selected_tag_unique_str)
    do_item = get_list_or_404(DoItem, pk=id)[0]
    
    context = {
        'to_do' : do_item,
        'id' : id,
        'home_tag_unique_str' : request.user.tags.get(name='Home').unique_str
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

        print('im here3')
        print('the stus: ', request.user.profile.selected_tag_unique_str)

        return redirect('to_dos', request.user.profile.selected_tag_unique_str)

    return render(request, "to_dos/edit_todo.html", context)


@login_required
def delete_todo(request, id):
    to_do = get_list_or_404(DoItem, id=id, users=request.user)
    to_do[0].delete()
    tag = Tag.objects.get(unique_str=request.user.profile.selected_tag_unique_str)
    return redirect('to_dos', tag.unique_str)


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

@login_required
def create_tag(request):

    if request.method == 'POST':

        shared = 'shared' in request.POST
    
        tag = Tag.objects.create(
            name=request.POST.get('list_title'),
            shared=shared,
            )
        tag.users.add(request.user)

        profile_user = request.user.profile
        profile_user.selected_tag_unique_str = tag.unique_str
        profile_user.save()

        return redirect('to_dos', tag.unique_str)

    home_tag_unique_str = request.user.tags.get(name='Home').unique_str
    return render(request, 'to_dos/create_tag.html', {'home_tag_unique_str': home_tag_unique_str})
    

@login_required
def delete_list(request):

    profile_user = request.user.profile
    old_tag = Tag.objects.get(unique_str = profile_user.selected_tag_unique_str)

    if old_tag.shared:
        user_count = old_tag.users.count()
        if user_count == 1:
            old_tag.delete()
        else:
            old_tag.users.remove(request.user)

    else:
        Tag.objects.filter(unique_str = profile_user.selected_tag_unique_str).delete()  
    
    home_tag_unique_str = Tag.objects.get(users=request.user, name='Home').unique_str
    profile_user.selected_tag_unique_str = home_tag_unique_str
    profile_user.save()

    return redirect('to_dos', home_tag_unique_str)

def validate_tag_unique_str(s):
    return s.replace(' ', '').upper().ljust(8, 'X')[:8]
    #TODO: add more validation, like ensure it is first length 8 and it is in the database... and it would be better if it is done before accespting the form

@login_required
def access_tag(request):

    if request.method == 'POST':

        tag_unique_str = request.POST.get('tag_unique_str')
        tag_unique_str = validate_tag_unique_str(tag_unique_str)

        tag = Tag.objects.get(unique_str=tag_unique_str)
        tag.users.add(request.user)

        do_items = DoItem.objects.filter(tag__unique_str=tag.unique_str)
        for do_item in do_items:
            do_item.users.add(request.user)

        profile_user = request.user.profile
        profile_user.selected_tag_unique_str = tag_unique_str
        profile_user.save()

        return redirect('to_dos', tag_unique_str)

