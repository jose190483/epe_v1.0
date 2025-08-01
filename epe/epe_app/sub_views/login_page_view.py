from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

from ..models import User_extInfo


def login_page(request):
    request.session['ses_username'] = request.POST.get('username')
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_id = User.objects.get(username=username).id
        role = User_extInfo.objects.get(user=user_id).emp_role.role_name

        first_name1 = User.objects.get(pk=user_id).first_name
        last_name=User.objects.get(pk=user_id).last_name
        first_name=first_name1+" " +last_name
        request.session['ses_userID'] = user_id
        user = authenticate(request, username=username,password=password)
        request.session['first_name'] = first_name
        request.session['ses_role'] = role
        if user is not None:
            login(request,user)
            return redirect('home_page')
        else:
            messages.error(request,'Username Or Password is Incorrect')

    context = {}
    return render(request, "epe_app/login.html", context)