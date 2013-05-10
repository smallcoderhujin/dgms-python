from django.db import models

class Province(models.Model):
    P_Id=models.AutoField(primary_key=True)
    P_Code=models.CharField(max_length=100,unique=True)
    P_Name=models.CharField(max_length=100)
    class Meta:
        app_label = 'AQMS_Python'
        db_table ='t_province'

class Region(models.Model):
    R_Id=models.AutoField(primary_key=True)
    R_ProvinceId=models.CharField(max_length=100)
    R_Code=models.CharField(max_length=100,unique=True)
    R_Name=models.CharField(max_length=100)
    class Meta:
        app_label = 'AQMS_Python'
        db_table ='t_region'

class Node(models.Model):
    N_Id=models.AutoField(primary_key=True)
    N_Longitude=models.CharField(max_length=50,null=True)
    N_Latitude=models.CharField(max_length=50,null=True)
    N_Code=models.CharField(max_length=50,unique=True)
    N_Name=models.CharField(max_length=50)
    N_RegionId=models.CharField(max_length=50)
    class Meta:
        app_label = 'air_quality'
        db_table ='t_node'

class AirMonitor(models.Model):
    M_Id=models.AutoField(primary_key=True)
    M_ProvinceName=models.CharField(max_length=100)
    M_RegionName=models.CharField(max_length=100)
    M_NodeName=models.CharField(max_length=100,null=True)
    M_Longitude=models.CharField(max_length=50,null=True)
    M_Latitude=models.CharField(max_length=50,null=True)
    M_CO=models.CharField(max_length=100,null=True)
    M_NO2=models.CharField(max_length=100,null=True)
    M_O3=models.CharField(max_length=100,null=True)
    M_PM10=models.CharField(max_length=100,null=True)
    M_PM25=models.CharField(max_length=100,null=True)
    M_SO2=models.CharField(max_length=100,null=True)
    M_RecordTime=models.DateTimeField()
    class Meta:
        app_label = 'air_quality'
        db_table ='t_air_monitor'






