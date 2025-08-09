from django.db import models
class project_info(models.Model):
    p_project_id= models.CharField(max_length=100, null=True,blank=True)
    p_project_name = models.CharField(max_length=100, null=True,default='')
    p_customer_name = models.CharField(max_length=100, null=True,default='')
    p_location= models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["p_project_name"]

    def __str__(self):
        return str(self.p_project_name)