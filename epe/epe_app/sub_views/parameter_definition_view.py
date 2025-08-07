from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from ..forms import parameter_definition_form,parameter_definition_lov_form
from ..models import prameter_definition_info,parameter_definition_lov_info
from django.shortcuts import render, redirect

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
        pd_lov_form = parameter_definition_lov_form
        request.session['ses_parameter_definition_id'] = param_def_id
        parameter_definition_lov_list=parameter_definition_lov_info.objects.filter(pdl_parameter_definition=param_def_id)
        context={
                'pd_form': pd_form,
                'pd_lov_form': pd_lov_form,
                'first_name': first_name,
                'user_id': user_id,
                'parameter_definition_lov_list': parameter_definition_lov_list,
                }
        return render(request, "epe_app/parameter_definition_add.html", context)
    else:
        if param_def_id == 0:
            pd_form = parameter_definition_form(request.POST,request.FILES)
            if pd_form.is_valid():
                parameter_def_instance = pd_form.save(commit=False)
                parameter_def_instance.save()
                parameter_def_instance.pd_id = f"S_{1000000 + parameter_def_instance.id}"
                parameter_def_instance.save(update_fields=['pd_id'])
                messages.success(request, 'Record Updated Successfully')
                return redirect(f'/epe/param_def_update/{parameter_def_instance.id}')
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

@login_required(login_url='login_page')
def add_parameter_definition_lov(request):
    if request.method == 'POST':
        pdl_lov = request.POST.get('pdl_lov')
        # pdl_parameter_definition = request.POST.get('pdl_parameter_definition')
        if pdl_lov:
            existing = parameter_definition_lov_info.objects.filter(pdl_lov__iexact=pdl_lov).first()
            if existing:
                return JsonResponse({'id': existing.id, 'pdl_lov': existing.pdl_lov})
            new_lov = parameter_definition_lov_info.objects.create(pdl_lov=pdl_lov)
            return JsonResponse({'id': new_lov.id, 'pdl_lov': new_lov.pdl_lov})
    return JsonResponse({'error': 'Invalid request'}, status=400)