from django.contrib import admin
from .models import equipment_shortInfo,uom_info,parameter_definition_lov_info,system_Info,equipmentInfo
# Register your models here.
admin.site.register(uom_info)
admin.site.register(parameter_definition_lov_info)
admin.site.register(equipmentInfo)
admin.site.register(equipment_shortInfo)
admin.site.register(system_Info)
