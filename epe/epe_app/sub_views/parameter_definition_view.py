from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from ..forms import parameter_definition_form, ParameterDefinitionLovForm
from ..models import prameter_definition_info,parameter_definition_lov_info
from django.shortcuts import render, redirect, get_object_or_404


@login_required(login_url='login_page')
def parameter_definition_add(request,param_def_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if param_def_id == 0:
            pd_form = parameter_definition_form
            parameter_definition = None  # Add this line
        else:
            parameter_definition=prameter_definition_info.objects.get(pk=param_def_id)
            pd_form = parameter_definition_form(instance=parameter_definition)
        context={
            'pd_form': pd_form,
            'first_name': first_name,
            'user_id': user_id,
            'parameter': parameter_definition  # Add this to the context
        }
        return render(request, "epe_app/parameter_definition_add.html", context)
    else:
        if param_def_id == 0:
            pd_form = parameter_definition_form(request.POST,request.FILES)
            if pd_form.is_valid():
                parameter_def_instance = pd_form.save(commit=False)
                parameter_def_instance.save()
                parameter_def_instance.p_id = f"S_{1000000 + parameter_def_instance.id}"
                parameter_def_instance.save(update_fields=['p_id'])
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
def add_lov(request, parameter_id):
    parameter = get_object_or_404(prameter_definition_info, pk=parameter_id)

    if request.method == 'POST':
        form = ParameterDefinitionLovForm(request.POST, parameter=parameter)
        if form.is_valid():
            lov_instance = form.save(commit=False)
            lov_instance.pdl_parameter_definition = parameter
            lov_instance.save()
            return JsonResponse({'success': True, 'message': 'LOV added successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ParameterDefinitionLovForm()

    return render(request, 'add_lov.html', {'form': form, 'parameter': parameter})
