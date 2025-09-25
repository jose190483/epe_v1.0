from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import prameter_definition_info,prameter_info,system_Info,equipmentInfo
@login_required(login_url='login_page')
def home_view(request):
    parameter_definition_count=prameter_definition_info.objects.count()
    parameter_count=prameter_info.objects.count()
    systems_count=system_Info.objects.count()
    equipments_count=equipmentInfo.objects.count()
    print(parameter_definition_count)
    context={''
             'parameter_definition_count':parameter_definition_count,
             'parameter_count':parameter_count,
             'systems_count':systems_count,
             'equipments_count':equipments_count,
             }
    return render(request, "epe_app/home.html",context)