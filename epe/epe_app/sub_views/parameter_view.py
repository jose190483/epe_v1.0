import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from ..forms import parameter_definition_lov_form
from ..models import parameter_definition_lov_info
from ..forms import parameter_form
from ..models import datatype_Info,prameter_definition_info,equipment_shortInfo,equipmentInfo,system_short_Info,unit_type_info,uom_info,prameter_info
from django.shortcuts import render, redirect
from django.contrib import messages

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
            system_short_name=parameter_definition_instance.p_system_short
            equipment_short_name=parameter_definition_instance.p_equipment_short
            parameter_name=parameter_definition_instance.p_name
            parameter_combo=str(system_short_name)+str('_')+str(equipment_short_name)+str('_')+str(parameter_name)
            request.session['ses_parameter_id'] = param_id
            parameter_definition_lov_list = parameter_definition_lov_info.objects.filter(pdl_parameter_definition=parameter_definition)
            parameter_data_type=prameter_definition_info.objects.get(pk=parameter_definition_id).pd_datatype.id
            print('parameter_data_type',parameter_data_type)
            context={
                'p_form': p_form,
                'pd_lov_form': pd_lov_form,
                'parameter_definition_lov_list': parameter_definition_lov_list,
                'parameter_data_type': parameter_data_type,
                'parameter_combo': parameter_data_type,
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
                p_form.save()
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
    # Fetch unit Type
    equipment_id = request.GET.get('equipment_id')
    # Fetch Unit Details
    equipment_short_name = list(equipment_shortInfo.objects.filter(es_equipment_name=equipment_id).order_by('es_equipment_short_name').values_list('es_equipment_short_name',flat=True).distinct())
    equipment_short_name_id = list(equipment_shortInfo.objects.filter(es_equipment_short_name__in=equipment_short_name).values_list('id',flat=True))
    print('equipment_short_name',equipment_short_name)
    print('equipment_short_name_id',equipment_short_name_id)
    data = {

        'equipment_short_name': equipment_short_name,
        'equipment_short_name_id': equipment_short_name_id,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))
@login_required(login_url='login_page')
def load_system_short_name_equipment_name(request):
    # Fetch unit Type
    system_id = request.GET.get('system_id')
    # Fetch Unit Details
    system_short_name = list(system_short_Info.objects.filter(ss_system_name=system_id).order_by('ss_system_short_name').values_list('ss_system_short_name',flat=True).distinct())
    system_short_name_id = list(system_short_Info.objects.filter(ss_system_short_name__in=system_short_name).values_list('id',flat=True))
    # system_short_name_id = system_short_Info.objects.get(ss_system_name=system_id).id
    equipment_name=list(equipmentInfo.objects.filter(equipment_system_name=system_id).values_list('equipment_name',flat=True).distinct())
    equipment_name_id=list(equipmentInfo.objects.filter(equipment_name__in=equipment_name).values_list('id',flat=True))
    print('system_short_name_id',system_short_name_id)
    data = {
        'system_short_name':system_short_name,
        'system_short_name_id':system_short_name_id,
        'equipment_name': equipment_name,
        'equipment_name_id': equipment_name_id,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

@login_required(login_url='login_page')
def load_units_type(request):
    # Fetch unit Type
    measurement_system_id = request.GET.get('measurement_system_id')
    # Fetch Unit Details
    unit_type_id = list(uom_info.objects.filter(uom_system_of_measurement__in=measurement_system_id).order_by('uom_unit_type').values_list('uom_unit_type',flat=True).distinct())
    unit_type_name=list(unit_type_info.objects.filter(pk__in=unit_type_id).values_list('ut_name',flat=True))

    data = {
        'unit_type_id':unit_type_id,
        'unit_type_name': unit_type_name,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

@login_required(login_url='login_page')
def load_unit_of_measure(request):
    # Fetch unit Type
    unit_type_id = request.GET.get('unit_type_id')
    system_measurement = request.GET.get('system_measurement')
    print("unit_type_id",unit_type_id)
    # Fetch Unit Details
    uom_id = list(uom_info.objects.filter(uom_system_of_measurement=system_measurement,uom_unit_type__in=unit_type_id).order_by('id').values_list('id',flat=True).distinct())
    print('uom_id',list(uom_id))
    uom_name=list(uom_info.objects.filter(pk__in=uom_id).values_list('uom_symbol',flat=True))
    print('uom_name',list(uom_name))

    data = {
        'uom_id':uom_id,
        'uom_name': uom_name,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))