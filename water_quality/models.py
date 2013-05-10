from django.db import models

class WaterMonitor(models.Model):
    W_Id=models.AutoField(primary_key=True)
    W_AreaName=models.CharField(max_length=100)
    W_RiverName=models.CharField(max_length=100)
    W_PH=models.CharField(max_length=100,null=True)
    W_DO=models.CharField(max_length=100,null=True)
    W_NH3N=models.CharField(max_length=100,null=True)
    W_COD=models.CharField(max_length=100,null=True)
    W_TOC=models.CharField(max_length=100,null=True)
    W_RecordTime=models.DateTimeField()
    class Meta:
        app_label = 'water_quality'
        db_table ='t_water_monitor'






