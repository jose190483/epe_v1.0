from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from ..forms import parameter_definition_form
from ..models import prameter_definition_info
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def parameter_definition_add(request,param_def_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if param_def_id == 0:
            pd_form = parameter_definition_form
        else:
            parameter_definition=prameter_definition_info.objects.get(pk=param_def_id)
            pd_form = parameter_definition_form(instance=parameter_definition)
        context={
                'pd_form': pd_form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "epe_app/parameter_definition_add.html", context)
    else:
        if param_def_id == 0:
            pd_form = parameter_definition_form(request.POST,request.FILES)
            if pd_form.is_valid():
                # Generate Random requirement number
                pd_form.save()
                try:
                    last_id = prameter_definition_info.objects.latest('id').id
                    param_number=100000+last_id
                except ObjectDoesNotExist:
                    param_number=100000
                    # param_num_next = str('param_') + str(randint(10000, 99999))
                param_num_next=str('PD_') + str(param_number)
                print("Requirement parameter_definition_form is Valid")
                last_id = prameter_definition_info.objects.latest('id').id
                prameter_definition_info.objects.filter(id=last_id).update(pd_id=param_num_next)
                param_id = prameter_definition_info.objects.get(pd_id=param_num_next).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/epe/param_def_update/'+ str(last_id))
            else:
                print("Requirement parameter_definition_form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            parameter_definition = prameter_definition_info.objects.get(pk=param_def_id)
            pd_form = parameter_definition_form(request.POST,request.FILES,instance=parameter_definition)
            if pd_form.is_valid():
                pd_form.save()
                print("Requirement Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def parameter_definition_list(request):
    first_name = request.session.get('first_name')
    param_def_list= (prameter_definition_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(param_def_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
                'param_def_list' : param_def_list,
                'first_name': first_name,
                'page_obj': page_obj,
                }
    return render(request,"epe_app/parameter_definition_list.html",context)

@login_required(login_url='login_page')
def parameter_definition_search(request):
    global param_def_list
    first_name = request.session.get('first_name')
    param_number = request.GET.get('param_number')
    print('param_number',param_number)
    if not param_number:
        param_number = ""
    param_def_list = prameter_definition_info.objects.filter((Q(pd_id__icontains=param_number)) | (Q(pd_id__isnull=True))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(param_def_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'param_def_list' : param_def_list,
            'first_name': first_name,
            'page_obj': page_obj,
            }
    return render(request,"epe_app/parameter_definition_list.html",context)
#Delete param_def
@login_required(login_url='login_page')
def parameter_definition_delete(request,param_def_id):
    param_def = prameter_definition_info.objects.get(pk=param_def_id)
    param_def.delete()
    return redirect('/epe/parameter_definition_search')