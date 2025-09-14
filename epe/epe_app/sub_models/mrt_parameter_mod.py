from django.db import models
from ..models import MyUser,status_Info,prameter_info

class mrt_prameter_info(models.Model):
    mrt_parameter_ref = models.ForeignKey(prameter_info,on_delete=models.PROTECT)
    mrt_parameter = models.CharField(max_length=100, null=True, default='')
    mrt_default_value = models.CharField(max_length=100,null=True, default='')
    mrt_updated_at = models.DateTimeField(null=True, auto_now=True)
    mrt_updated_by = models.ForeignKey(MyUser, on_delete=models.PROTECT, null=True,
                                     related_name='mrt_updated_by', db_column='mrt_updated_by')
    mrt_status=models.ForeignKey(status_Info,on_delete=models.PROTECT,null=True,blank=True,default=1)
    def __str__(self):
        return str(self.mrt_parameter) if self.p_id is not None else ""

    class Meta:
        ordering = ["-mrt_parameter_ref"]