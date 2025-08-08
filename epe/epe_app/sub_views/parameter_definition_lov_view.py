import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse

from ..forms import parameter_definition_lov_form
from ..models import parameter_definition_lov_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def parameter_definition_lov_add(request,param_def_lov_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if param_def_lov_id == 0:
            pd_lov_form = parameter_definition_lov_form
        else:
            print("Inside edit add")
            parameter_definition_lov=parameter_definition_lov_info.objects.get(pk=param_def_lov_id)
            pd_lov_form = parameter_definition_lov_form(instance=parameter_definition_lov)
        context={
                'pd_lov_form': pd_lov_form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "epe_app/parameter_definition_lov_add.html", context)
    else:
        if param_def_lov_id == 0:
            pd_lov_form = parameter_definition_lov_form(request.POST)
            if pd_lov_form.is_valid():
                pd_lov_form.save()
                messages.success(request, 'Record Updated Successfully')
                param_def_id = request.session.get('ses_parameter_definition_id')
                return redirect(f'/epe/param_def_update/{param_def_id}')
                # return redirect(request.META['HTTP_REFERER'])
            else:
                print("Requirement parameter definition lov form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Inside edit save")
            parameter_definition_lov = parameter_definition_lov_info.objects.get(pk=param_def_lov_id)
            pd_lov_form = parameter_definition_lov_form(request.POST,instance=parameter_definition_lov)
            if pd_lov_form.is_valid():
                pd_lov_form.save()
                print("Requirement Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            # return redirect(request.META['HTTP_REFERER'])
            param_def_id = request.session.get('ses_parameter_definition_id')
            return redirect(f'/epe/param_def_update/{param_def_id}')
@login_required(login_url='login_page')
def parameter_definition_lov_list(request):
    first_name = request.session.get('first_name')
    param_def_lov_list= (parameter_definition_lov_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(param_def_lov_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
                'param_def_lov_list' : param_def_lov_list,
                'first_name': first_name,
                'page_obj': page_obj,
                }
    return render(request,"epe_app/parameter_definition_lov_list_woh.html",context)

@login_required(login_url='login_page')
def parameter_definition_lov_search(request):
    global param_def_lov_list
    first_name = request.session.get('first_name')
    param_number = request.GET.get('param_number')
    print('param_number',param_number)
    if not param_number:
        param_number = ""
    param_def_lov_list = parameter_definition_lov_info.objects.filter((Q(pd_id__icontains=param_number)) | (Q(pd_id__isnull=True))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(param_def_lov_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'param_def_lov_list' : param_def_lov_list,
            'first_name': first_name,
            'page_obj': page_obj,
            }
    return render(request,"epe_app/parameter_definition_lov_list_woh.html",context)
#Delete param_def
@login_required(login_url='login_page')
def parameter_definition_lov_delete(request,param_def_lov_id):
    param_def = parameter_definition_lov_info.objects.get(pk=param_def_lov_id)
    param_def.delete()
    return redirect('/epe/parameter_definition_lov_list')

@login_required(login_url='login_page')
def load_lov(request):

    lov_id = request.GET.get('lov_id')
    print('lov_id',lov_id)
    pdl_parameter_definition=parameter_definition_lov_info.objects.get(pk=lov_id).pdl_parameter_definition.id
    pdl_lov=parameter_definition_lov_info.objects.get(pk=lov_id).pdl_lov
    # Fetch Unit Details

    data = {
        'lov_id':lov_id,
        'pdl_parameter_definition':str(pdl_parameter_definition),
        'pdl_lov':pdl_lov,
    }
    return HttpResponse(json.dumps(data))

@login_required(login_url='login_page')
def parameter_definition_lov_cancel(request):
    param_def_id = request.session.get('ses_parameter_definition_id')

    return redirect(f'/epe/param_def_update/{param_def_id}')

