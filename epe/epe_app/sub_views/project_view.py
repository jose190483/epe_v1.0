from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from ..forms import project_form
from ..models import project_info
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def project_add(request,project_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print('first_name',first_name)
    if request.method == "GET":
        if project_id == 0:
            p_form = project_form
        else:
            parameter=project_info.objects.get(pk=project_id)
            p_form = project_form(instance=parameter)
        context={
                'p_form': p_form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "epe_app/project_add.html", context)
    else:
        if project_id == 0:
            p_form = project_form(request.POST)
            if p_form.is_valid():
                # Generate Random requirement number
                p_form.save()
                # try:
                #     last_id = project_info.objects.latest('id').id
                #     project_number=100000+last_id
                # except ObjectDoesNotExist:
                #     project_number=100000
                #     # project_num_next = str('project_') + str(randint(10000, 99999))
                # project_num_next=str('pro_') + str(project_number)
                # print("Requirement project_form is Valid")
                # last_id = project_info.objects.latest('id').id
                # project_info.objects.filter(id=last_id).update(p_id=project_num_next)
                # project_id = project_info.objects.get(p_id=project_num_next).id
                messages.success(request, 'Record Updated Successfully')                #     last_id = project_info.objects.latest('id').id
                last_id = project_info.objects.latest('id').id

                return redirect('/epe/project_update/'+ str(last_id))
            else:
                print("Requirement project_form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            parameter = project_info.objects.get(pk=project_id)
            p_form = project_form(request.POST,instance=parameter)
            if p_form.is_valid():
                p_form.save()
                print("Requirement Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def project_list(request):
    first_name = request.session.get('first_name')
    project_list= (project_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(project_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
                'project_list' : project_list,
                'first_name': first_name,
                'page_obj': page_obj,
                }
    return render(request,"epe_app/project_list.html",context)

@login_required(login_url='login_page')
def project_search(request):
    global project_list
    first_name = request.session.get('first_name')
    project_number = request.GET.get('project_number')
    print('project_number',project_number)
    if not project_number:
        project_number = ""
    project_list = project_info.objects.filter((Q(p_project_id__icontains=project_number)) | (Q(p_project_id__isnull=True))).order_by('-id')
    # project_list = project_info.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(project_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'project_list' : project_list,
            'first_name': first_name,
            'page_obj': page_obj,
            }
    return render(request,"epe_app/project_list.html",context)
#Delete param
@login_required(login_url='login_page')
def project_delete(request,project_id):
    param = project_info.objects.get(pk=project_id)
    param.delete()
    return redirect('/epe/project_search')