from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from ..forms import parameter_form
from ..models import prameter_info
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def parameter_add(request,param_id=0):
    if request.method == "GET":
        if param_id == 0:
            p_form = parameter_form
        else:
            parameter=prameter_info.objects.get(pk=param_id)
            p_form = parameter_form(instance=parameter)
        context={
                'p_form': p_form,
                }
        return render(request, "epe_app/parameter_add.html", context)
    else:
        if param_id == 0:
            p_form = parameter_form(request.POST)
            if p_form.is_valid():
                parameter_instance = p_form.save(commit=False)
                parameter_instance.save()
                parameter_instance.p_id = f"S_{1000000 + parameter_instance.id}"
                parameter_instance.save(update_fields=['p_id'])
                messages.success(request, 'Record Updated Successfully')
                return redirect(f'/epe/parameter_update/{parameter_instance.id}')
            else:
                print("Requirement parameter_form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            parameter = prameter_info.objects.get(pk=param_id)
            p_form = parameter_form(request.POST,instance=parameter)
            if p_form.is_valid():
                p_form.save()
                print("Requirement Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def parameter_list(request):
    first_name = request.session.get('first_name')
    param_list= (prameter_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(param_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
                'param_list' : param_list,
                'first_name': first_name,
                'page_obj': page_obj,
                }
    return render(request,"epe_app/parameter_list.html",context)

@login_required(login_url='login_page')
def parameter_search(request):
    global param_list
    first_name = request.session.get('first_name')
    param_number = request.GET.get('param_number')
    print('param_number',param_number)
    if not param_number:
        param_number = ""
    param_list = prameter_info.objects.filter((Q(p_id__icontains=param_number)) | (Q(p_id__isnull=True))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(param_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'param_list' : param_list,
            'first_name': first_name,
            'page_obj': page_obj,
            }
    return render(request,"epe_app/parameter_list.html",context)
#Delete param
@login_required(login_url='login_page')
def parameter_delete(request,param_id):
    param = prameter_info.objects.get(pk=param_id)
    param.delete()
    return redirect('/epe/parameter_search')