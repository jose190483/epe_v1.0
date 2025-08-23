import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from ..forms import parameter_definition_lov_form
from ..models import parameter_definition_lov_info
from ..forms import parameter_form
from ..models import prameter_definition_info,equipment_shortInfo,equipmentInfo,system_short_Info,unit_type_info,uom_info,prameter_info
from django.shortcuts import render, redirect
from django.contrib import messages


def normalize_combo(system, equipment, name):
    return f"{str(system).strip().upper()}_{str(equipment).strip().upper()}_{str(name).strip().upper()}"

@login_required(login_url='login_page')
def parameter_add(request,param_id=0):
    if request.method == "GET":
        if param_id == 0:
            p_form = parameter_form
            context = {
                'p_form': p_form,
            }
        else:
            parameter=prameter_info.objects.get(pk=param_id)
            p_form = parameter_form(instance=parameter)
            pd_lov_form = parameter_definition_lov_form
            parameter_definition_instance=prameter_info.objects.get(pk=param_id)
            parameter_definition=parameter_definition_instance.p_definition
            parameter_definition_id=parameter_definition_instance.p_definition.id
            request.session['ses_parameter_id'] = param_id
            parameter_definition_lov_list = parameter_definition_lov_info.objects.filter(pdl_parameter_definition=parameter_definition)
            parameter_data_type=prameter_definition_info.objects.get(pk=parameter_definition_id).pd_datatype.id
            context={
                'p_form': p_form,
                'pd_lov_form': pd_lov_form,
                'parameter_definition_lov_list': parameter_definition_lov_list,
                'parameter_data_type': parameter_data_type,
            }
        return render(request, "epe_app/parameter_add.html", context)
    else:
        if param_id == 0:
            p_form = parameter_form(request.POST)
            if p_form.is_valid():
                parameter_instance = p_form.save(commit=False)
                parameter_instance.save()
                parameter_instance.p_id = f"P_{1000000 + parameter_instance.id}"
                parameter_instance.save(update_fields=['p_id'])

                system_short_name = (system_short_Info.objects.get(ss_system_name=request.POST.get('p_system'))).ss_system_short_name
                equipment_short_name = equipment_shortInfo.objects.get(es_equipment_name=request.POST.get('p_equipment_short')).es_equipment_short_name
                parameter_name = request.POST.get('p_name')

                parameter_combo = normalize_combo(system_short_name, equipment_short_name, parameter_name)
                print("parameter_combo_add", parameter_combo)
                if prameter_info.objects.filter(p_parameter_name_combo__iexact=parameter_combo).exclude(pk=param_id).exists():
                    # Already exists for a different record
                    messages.error(request, f"Parameter combo '{parameter_combo}' already exists.")
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                else:
                    p_form.save()
                    prameter_info.objects.filter(pk=parameter_instance.id).update(p_parameter_name_combo=parameter_combo)
                messages.success(request, 'Record Updated Successfully')
                return redirect(f'/epe/parameter_update/{parameter_instance.id}')
            else:
                print("Parameter_form is Not Valid")
                for field, errors in p_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            parameter = prameter_info.objects.get(pk=param_id)
            p_form = parameter_form(request.POST,instance=parameter)
            if p_form.is_valid():
                system_short_name = (system_short_Info.objects.get(ss_system_name=request.POST.get('p_system'))).ss_system_short_name
                equipment_short_name = equipment_shortInfo.objects.get(es_equipment_name=request.POST.get('p_equipment_short')).es_equipment_short_name
                parameter_name = request.POST.get('p_name')
                # parameter_combo=str(system_short_name)+str('_')+str(equipment_short_name)+str('_')+str(parameter_name)
                parameter_combo = normalize_combo(system_short_name, equipment_short_name, parameter_name)
                print("Edit_parameter_combo",parameter_combo)
                if prameter_info.objects.filter(p_parameter_name_combo__iexact=parameter_combo).exclude(pk=param_id).exists():
                    # Already exists for a different record
                    messages.error(request, f"Parameter combo '{parameter_combo}' already exists.")
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                else:
                    p_form.save()
                    prameter_info.objects.filter(pk=param_id).update(p_parameter_name_combo=parameter_combo)
                print("Parameter Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Parameter Form is Not Valid")
                for field, errors in p_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
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

@login_required(login_url='login_page')
def load_equipment_short_name(request):
    equipment_id = request.GET.get('equipment_id')

    try:
        equipment_short = equipment_shortInfo.objects.get(es_equipment_name=equipment_id)
        data = {
            'equipment_short_name': equipment_short.es_equipment_short_name,
            'equipment_short_name_id': equipment_short.id,
        }
        return JsonResponse(data)
    except equipment_shortInfo.DoesNotExist:
        return JsonResponse({'error': 'Equipment not found'}, status=404)

@login_required(login_url='login_page')
def load_system_short_name_equipment_name(request):
    # Fetch unit Type
    system_id = request.GET.get('system_id')
    print('system_id',system_id)
    # Fetch Unit Details
    system_short_name_id = system_short_Info.objects.get(ss_system_name=system_id).id
    system_short_name = system_short_Info.objects.get(ss_system_name=system_id).ss_system_short_name
    equipment_name=list(equipmentInfo.objects.filter(equipment_system_name=system_id).values_list('equipment_name',flat=True).distinct())
    equipment_name_id=list(equipmentInfo.objects.filter(equipment_name__in=equipment_name).values_list('id',flat=True))
    print('system_short_name_id',system_short_name_id)
    data = {
        'system_short_name_id':system_short_name_id,
        'system_short_name':system_short_name,
        'equipment_name': equipment_name,
        'equipment_name_id': equipment_name_id,
    }
    # return HttpResponse(json.dumps(data))
    return JsonResponse(data)

@login_required(login_url='login_page')

def load_units_type(request):
    parameter_definition_id = request.GET.get('parameter_definition_id')

    try:
        # Fetch Unit Type ID from parameter definition
        unit_type_id = prameter_definition_info.objects.get(pk=parameter_definition_id).pd_unit_type.id
        unit_type= prameter_definition_info.objects.get(pk=parameter_definition_id).pd_unit_type.ut_name
        print('unit_type_id', unit_type_id)
        print('unit_type',unit_type)
        # Fetch UOMs for the unit type
        uoms = uom_info.objects.filter(uom_unit_type=unit_type_id).values('id', 'uom_symbol')

        # Prepare lists
        uom_id = [uom['id'] for uom in uoms]
        uom_name = [uom['uom_symbol'] for uom in uoms]
        data = {
            'unit_type_id': unit_type_id,
            'unit_type': unit_type,
            'uom_id': uom_id,
            'uom_name': uom_name,
        }

        return JsonResponse(data)

    except prameter_definition_info.DoesNotExist:
        return JsonResponse({'error': 'Parameter definition not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


