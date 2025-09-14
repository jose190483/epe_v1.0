from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render, redirect
from ..forms import mrt_parameter_form
from ..models import prameter_info,mrt_prameter_info
@login_required(login_url='login_page')
def mrt_parameter_add(request, mrt_param_id=0,):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if mrt_param_id == 0:
            mrt_param_form = mrt_parameter_form()
        else:
            mrt_parameter = mrt_prameter_info.objects.get(pk=mrt_param_id)
            mrt_param_form = mrt_parameter_form(instance=mrt_parameter)

        context = {
            'mrt_param_form': mrt_param_form,
            'first_name': first_name,
            'user_id': user_id,
            'mrt_param_id': mrt_param_id,
        }
        return render(request, "epe_app/mrt_parameter_add.html", context)

    else:
        if mrt_param_id == 0:
            mrt_param_form = mrt_parameter_form(request.POST)
            if mrt_param_form.is_valid():
                mrt_parameter_instance = mrt_param_form.save(commit=False)
                mrt_parameter_instance.save()
                # parameter_instance.mrt_param_id = f"mrt_param_{1000000 + parameter_instance.id}"
                # parameter_instance.save(update_fields=['mrt_param_id'])
                messages.success(request, 'Record Updated Successfully')
                return redirect(f'/epe/mrt_parameter_update/{mrt_parameter_instance.id}')
            else:
                messages.error(request, 'Record Not Updated Successfully')

            # ✅ Re-render form with errors
            context = {
                'mrt_param_form': mrt_param_form,
                'first_name': first_name,
                'user_id': user_id,
            }
            return render(request, "epe_app/mrt_parameter_add.html", context)

        else:
            mrt_parameter = mrt_prameter_info.objects.get(pk=mrt_param_id)
            mrt_param_form = mrt_parameter_form(request.POST, instance=mrt_parameter)
            if mrt_param_form.is_valid():
                try:
                    mrt_param_form.save()
                    messages.success(request, 'Record Updated Successfully')
                except IntegrityError:
                    mrt_param_form.add_error('mrt_param_name', "This name already exists. Please choose a different one.")
                    messages.error(request, 'Record Not Updated Successfully')
            else:
                messages.error(request, 'Record Not Updated Successfully')

            # ✅ Re-render form with errors
            context = {
                'mrt_param_form': mrt_param_form,
                'first_name': first_name,
                'user_id': user_id,
            }
            return render(request, "epe_app/mrt_parameter_add.html", context)

@login_required(login_url='login_page')
def mrt_parameter_list(request):
    first_name = request.session.get('first_name')
    mrt_param_list= (mrt_prameter_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(mrt_param_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
                'mrt_param_list' : mrt_param_list,
                'first_name': first_name,
                'page_obj': page_obj,
                'request_user': request.user,
                }
    return render(request,"epe_app/mrt_parameter_list.html",context)

@login_required(login_url='login_page')
def mrt_parameter_search(request):
    global mrt_param_list
    first_name = request.session.get('first_name')
    param_number = request.GET.get('param_number')
    print('param_number',param_number)
    if not param_number:
        param_number = ""
    mrt_param_list = mrt_prameter_info.objects.filter((Q(mrt_parameter__icontains=param_number)) | (Q(mrt_parameter__isnull=True))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(mrt_param_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'mrt_param_list' : mrt_param_list,
            'first_name': first_name,
            'page_obj': page_obj,
            }
    return render(request,"epe_app/mrt_parameter_list.html",context)
#Delete mrt_param
@login_required(login_url='login_page')
def mrt_parameter_delete(request,mrt_param_id):
    mrt_param = mrt_prameter_info.objects.get(pk=mrt_param_id)
    mrt_param.delete()
    return redirect('/epe/mrt_parameter_search')


@login_required(login_url='login_page')
def mrt_parameter_master_list(request):
    first_name = request.session.get('first_name')
    param_list = prameter_info.objects.filter(p_digital_source=7, p_status=4).order_by('-id')

    # Annotate each parameter with its MRT info if exists
    for param in param_list:
        param.mrt_info = mrt_prameter_info.objects.filter(mrt_parameter_ref=param).first()

    page_number = request.GET.get('page')
    paginator = Paginator(param_list, 50)
    page_obj = paginator.get_page(page_number)

    context = {
        'param_list': param_list,
        'first_name': first_name,
        'page_obj': page_obj,
        'request_user': request.user,
    }
    return render(request, "epe_app/mrt_parameter_master_list.html", context)


