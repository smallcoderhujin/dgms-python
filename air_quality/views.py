#coding=utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponse
from pyamf.remoting.client import RemotingService
from pyamf import AMF3
from air_quality.models import *
from air_quality import views_china
from pyquery import PyQuery as pyq
import urllib,thread,time,datetime,urllib2,cookielib,json,xml.dom.minidom
from AQMS_Python.log import *

def show_list(request):
    airMonitorList=list(AirMonitor.objects.raw('select * from aqms.t_air_monitor order by M_RecordTime DESC limit 10'))
    return render_to_response('air_quality/list.html',{'AirMonitorList':airMonitorList})

def start():
    writeInfoLogger('-----------------------------------------------------------\n')
    thread.start_new_thread(start_jiangsu,())
    thread.start_new_thread(start_shandong,())
    thread.start_new_thread(start_yunnan,())
    thread.start_new_thread(start_hunan,())
    thread.start_new_thread(start_zhejiang,())
    thread.start_new_thread(start_shanghai,())
    thread.start_new_thread(start_beijing,())
    thread.start_new_thread(views_china.start,())

#江苏
def start_jiangsu():
    writeInfoLogger('江苏空气开始监测')
    test_intenet('江苏')
    try:
        items=['SO2','NO2','PM10','PM25','CO','O3']
        gw = RemotingService('http://218.94.78.75/pm25RmServices72/Gateway.aspx')
        service = gw.getService('FlashRemotingServiceLibrary.Sample.getchartdataValue')
        regionList=Region.objects.filter(R_ProvinceId='10').order_by('R_Code')
        for i in range(len(regionList)):
            nodeList=Node.objects.filter(N_RegionId=regionList[i].R_Id).order_by('N_Code')
            for i in range(len(nodeList)):
                data={}
                for k in range(len(items)):
                    result=service(items[k],nodeList[i].N_Code)
                    data[items[k]]=result.split(';')[0].split(',')[1]

                region=Region.objects.filter(R_Id=nodeList[i].N_RegionId)[0]
                province=Province.objects.filter(P_Id=region.R_ProvinceId)[0]
                airMonitor=AirMonitor(M_ProvinceName=province.P_Name,M_RegionName=region.R_Name,M_NodeName=nodeList[i].N_Name,M_Longitude=nodeList[i].N_Longitude,
                                      M_Latitude=nodeList[i].N_Latitude,M_CO=data[items[4]],M_NO2=data[items[1]],M_O3=data[items[5]],M_PM10=data[items[2]],
                                      M_PM25=data[items[3]],M_SO2=data[items[0]],M_RecordTime=datetime.datetime.now())
                airMonitor.save()
    except Exception,e:
        writeErrorLogger('江苏'+e)
    finally:
        writeInfoLogger('江苏休眠一小时')
        time.sleep(60*60)
        start_jiangsu()

#山东
def start_shandong():
    writeInfoLogger('山东空气开始监测')
    test_intenet('山东')
    try:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0')]
        urllib2.install_opener(opener)
        req = urllib2.Request("http://58.56.98.78:8801/AirDeploy.Web/AirDeployService.svc",'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetAirDeployHours><strStCode>0</strStCode><strItem>0</strItem></GetAirDeployHours></s:Body></s:Envelope>')
        req.add_header("Referer","http://58.56.98.78:8801/airdeploy.web/ClientBin/AirDeploy.xap")
        req.add_header('Content-Type','text/xml; charset=utf-8')
        req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        req.add_header('SOAPAction','"urn:AirDeployService/GetAirDeployHours"')
        resp = urllib2.urlopen(req)
        result=resp.read()
        doc = xml.dom.minidom.parseString(result)
        regionName={}
        temp={}
        for node in doc.documentElement.getElementsByTagName("a:CM_AirDeploy"):
            if len(regionName)==0:
                regionName[0]=node.getElementsByTagName("a:strStName")[0].childNodes[0].nodeValue
                regionName[1]=node.getElementsByTagName("a:strPName")[0].childNodes[0].nodeValue
                regionName[2]=node.getElementsByTagName("a:strLongitued")[0].childNodes[0].nodeValue
                regionName[3]=node.getElementsByTagName("a:strLatitude")[0].childNodes[0].nodeValue
            if regionName[0]==node.getElementsByTagName("a:strStName")[0].childNodes[0].nodeValue and regionName[1]==node.getElementsByTagName("a:strPName")[0].childNodes[0].nodeValue:
                temp[node.getElementsByTagName("a:strItemName")[0].childNodes[0].nodeValue]= node.getElementsByTagName("a:strHourAvg")[0].childNodes[0].nodeValue
            else:
                airMonitor=AirMonitor(M_ProvinceName=u'山东',M_RegionName=regionName[0],M_NodeName=regionName[1],M_Longitude=regionName[2],M_Latitude=regionName[3],M_CO=temp[u'一氧化碳'],M_NO2=temp[u'二氧化氮'],M_O3=temp[u'臭氧'],M_PM10=temp['PM10'],M_PM25=temp['PM2.5'],M_SO2=temp[u'二氧化硫'],M_RecordTime=datetime.datetime.now())
                airMonitor.save()
                regionName={}
                regionName[0]=node.getElementsByTagName("a:strStName")[0].childNodes[0].nodeValue
                regionName[1]=node.getElementsByTagName("a:strPName")[0].childNodes[0].nodeValue
                regionName[2]=node.getElementsByTagName("a:strLongitued")[0].childNodes[0].nodeValue
                regionName[3]=node.getElementsByTagName("a:strLatitude")[0].childNodes[0].nodeValue
                temp={}
                temp[node.getElementsByTagName("a:strItemName")[0].childNodes[0].nodeValue]= node.getElementsByTagName("a:strHourAvg")[0].childNodes[0].nodeValue
    except Exception,e:
        writeErrorLogger('山东'+e)
    finally:
        writeInfoLogger('山东休眠一小时')
        time.sleep(60*60)
        start_shandong()

#云南
def start_yunnan():
    writeInfoLogger('云南空气开始监测')
    test_intenet('云南')
    try:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0')]
        urllib2.install_opener(opener)
        req = urllib2.Request("http://112.112.16.162:8888/Services/DataCenter.aspx?type=getData&mid=0.02219218574464321",urllib.urlencode({'type':'getData','mid':'0.02219218574464321'}))
        req.add_header("Referer","http://112.112.16.162:8888/Default.aspx")
        req.add_header('Accept','*/*')
        resp = urllib2.urlopen(req)
        data= json.loads(resp.read())['Head']
        lang=['102.67','102.82','102.37','102.44','102.43','102.68','102.75']
        lat=['25.04','24.90','25.00','25.11','25.04','25.07','25.01']
        for i in range(len(data)-1):
            airMonitor=AirMonitor(M_ProvinceName=u'云南',M_RegionName=u'昆明',M_NodeName=data[i]['PointName'],M_Longitude=lang[i],M_Latitude=lat[i],M_CO=data[i]['CO_1H'],M_NO2=data[i]['NO2_1H'],M_O3=data[i]['O3_1H'],M_SO2=data[i]['SO2_1H'],M_PM10=data[i]['PM10_1H'],M_PM25=data[i]['PM25_1H'],M_RecordTime=datetime.datetime.now())
            airMonitor.save()
    except Exception,e:
        writeErrorLogger('云南'+e)
    finally:
        writeInfoLogger('云南休眠一小时')
        time.sleep(60*60)
        start_yunnan()

#湖南
def start_hunan():
    writeInfoLogger('湖南空气开始监测')
    test_intenet('湖南')
    try:
        regionName=['长沙','株洲','湘潭']
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0')]
        urllib2.install_opener(opener)
        for i in range(len(regionName)):
            req = urllib2.Request("http://222.247.51.155:8025/publishwcf/EnvAQIServeice.svc",'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetAQIDataByCityName xmlns="http://tempuri.org/"><CityName>'+regionName[i]+'</CityName></GetAQIDataByCityName></s:Body></s:Envelope>')
            req.add_header("Referer","http://222.247.51.155:8025/ClientBin/ProvinceAQI.xap")
            req.add_header('Content-Type','text/xml; charset=utf-8')
            req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            req.add_header('SOAPAction','"http://tempuri.org/IEnvAQIServeice/GetAQIDataByCityName"')
            resp = urllib2.urlopen(req)
            result=resp.read()
            doc = xml.dom.minidom.parseString(result)
            for node in doc.documentElement.getElementsByTagName("a:AQIDataPublishLiveInfo"):
                nodeName=node.getElementsByTagName("a:PositionName")[0].childNodes[0].nodeValue
                latitude=node.getElementsByTagName("a:Latitude")[0].childNodes[0].nodeValue
                longitude=node.getElementsByTagName("a:Longitude")[0].childNodes[0].nodeValue
                co=node.getElementsByTagName("a:CO")[0].childNodes[0].nodeValue
                so2=node.getElementsByTagName("a:SO2")[0].childNodes[0].nodeValue
                no2=node.getElementsByTagName("a:NO2")[0].childNodes[0].nodeValue
                o3=node.getElementsByTagName("a:O3")[0].childNodes[0].nodeValue
                pm10=node.getElementsByTagName("a:PM10")[0].childNodes[0].nodeValue
                pm25=node.getElementsByTagName("a:PM2_5")[0].childNodes[0].nodeValue
                recordTime=node.getElementsByTagName("a:TimePoint")[0].childNodes[0].nodeValue
                airMonitor=AirMonitor(M_ProvinceName=u'湖南',M_RegionName=regionName[i],M_NodeName=nodeName,M_Longitude=longitude,M_Latitude=latitude,M_CO=co,M_NO2=no2,M_O3=o3,M_PM10=pm10,M_PM25=pm25,M_SO2=so2,M_RecordTime=datetime.datetime.now())
                airMonitor.save()
    except Exception,e:
        writeErrorLogger('湖南'+e)
    finally:
        writeInfoLogger('湖南休眠一小时')
        time.sleep(60*60)
        start_hunan()

#浙江
def start_zhejiang():
    writeInfoLogger('浙江空气开始监测')
    test_intenet('浙江')
    try:
        a={}
        gw = RemotingService('http://115.236.164.226:8099/messagebroker/amf',amf_version=AMF3)
        service = gw.getService('GisCommonDataUtil.getRealTimeAQIDataCollection')
        datas=service()
        for i in range(len(datas)):
            regionName= datas[i]['site']['city']['name']
            nodeName=datas[i]['site']['name']
            longitude=datas[i]['site']['longitude']
            latitude=datas[i]['site']['latitude']
            if datas[i]['iaqiDataMap']:
                pm25=datas[i]['iaqiDataMap']['121']['publishData']
                co=datas[i]['iaqiDataMap']['106']['publishData']
                no2=datas[i]['iaqiDataMap']['141']['publishData']
                so2=datas[i]['iaqiDataMap']['101']['publishData']
                o3=datas[i]['iaqiDataMap']['108']['publishData']
                pm10=datas[i]['iaqiDataMap']['107']['publishData']
            #recordTime=datas[i]['monitorTime']
            airMonitor=AirMonitor(M_ProvinceName=u'浙江',M_RegionName=regionName,M_NodeName=nodeName,M_Longitude=longitude,M_Latitude=latitude,M_CO=co,M_NO2=no2,M_O3=o3,M_PM10=pm10,M_PM25=pm25,M_SO2=so2,M_RecordTime=datetime.datetime.now())
            airMonitor.save()
    except Exception,e:
        writeErrorLogger('浙江'+e)
    finally:
        writeInfoLogger('浙江休眠一小时')
        time.sleep(60*60)
        start_zhejiang()

#上海
def start_shanghai():
    writeInfoLogger('上海空气开始监测')
    test_intenet('上海')
    try:
        gw = RemotingService('http://www.semc.gov.cn/aqi/Gateway.aspx',amf_version=AMF3)
        service=gw.getService('ServiceLibrary.Sample.getSiteValueData')
        result= service(None)
        lang=['121.39','121.52','121.46','120.97','121.47','121.44','121.41','121.69','121.61','121.54']
        lat=['31.25','31.26','31.22','31.11','31.30','31.23','30.16','31.19','31.21','31.22']
        for i in range(len(result)-1):
            airMonitor=AirMonitor(M_ProvinceName='上海市',M_RegionName=result[i]['sitename'],M_NodeName=result[i]['sitename'],M_Longitude=lang[i],M_Latitude=lat[i],M_CO=result[i]['co'],M_NO2=result[i]['no2'],M_O3=result[i]['o3'],M_PM10=result[i]['pm101'],M_PM25=result[i]['pm251'],M_SO2=result[i]['so2'],M_RecordTime=datetime.datetime.now())
            airMonitor.save()
    except Exception,e:
        writeErrorLogger('上海'+e)
    finally:
        writeInfoLogger('上海休眠一小时')
        time.sleep(60*60)
        start_shanghai()

#北京
def start_beijing():
    writeInfoLogger('北京空气开始监测')
    test_intenet('北京')
    try:
        nodeList=Node.objects.filter(N_RegionId='601').order_by('N_Code')
        lang=['116.40','116.46','116.39','117.19','116.35','116.18','116.34','116.41','116.39','116.36','116.22','116.33','116.84','116.95',   '117.11','115.97','116.63','116.14','116.23','116.20','116.31','116.79','116.41','116.39','116.03','116.35','116.65','116.10','116.65','116.48','117.11','116.28','116.16','116.48','116.00']
        lat=['39.90','39.93','39.90','40.13','39.85','39.91','39.73','39.88','39.98','39.93','40.29','39.85','40.37','40.49',  '40.14','40.46','40.32','39.75','40.22','40.00','39.51','39.71','39.92','39.87','39.61','39.94','39.91','39.94','40.13','39.91','40.10','39.86','39.81','39.80','40.36']
        for i in range(len(nodeList)):

            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0')]
            urllib2.install_opener(opener)
            req = urllib2.Request("http://zx.bjmemc.com.cn/ashx/Data.ashx?Action=GetIAQIAll_ByStation",urllib.urlencode({'StationName':nodeList[i].N_Name.encode('utf-8')}))

            req.add_header("Referer","http://zx.bjmemc.com.cn/")
            req.add_header('Content-Type','application/x-www-form-urlencoded')
            req.add_header('Accept','text/html, */*; q=0.01')
            resp = urllib2.urlopen(req)
            doc= pyq(resp.read().decode('utf-8'))
            spanValue=doc('span')
            regionName=(pyq(spanValue[0]).text())[0:pyq(spanValue[0]).text().find('(')]
            pm10=pyq(spanValue[18]).text()
            pm25=pyq(spanValue[19]).text()
            so2=pyq(spanValue[20]).text()
            co=pyq(spanValue[21]).text()
            no2=pyq(spanValue[22]).text()
            o3=pyq(spanValue[23]).text()
            airMonitor=AirMonitor(M_ProvinceName='北京市',M_RegionName=regionName,M_NodeName=regionName,M_Longitude=lang[i],M_Latitude=lat[i],M_CO=co,M_NO2=no2,M_O3=o3,M_PM10=pm10,M_PM25=pm25,M_SO2=so2,M_RecordTime=datetime.datetime.now())
            airMonitor.save()
    except Exception,e:
        writeErrorLogger('北京'+e)
    finally:
        writeInfoLogger('北京休眠一小时')
        time.sleep(60*60)
        start_beijing()

import xlwt,os
def export(request):
    try:
        if request.method=='GET':
            startDate=datetime.datetime.strptime(request.GET.get('start'),'%Y-%m-%d')
            endDate=datetime.datetime.strptime(request.GET.get('end'),'%Y-%m-%d')
            exportDate=str(datetime.datetime.today().year)+str(datetime.datetime.today().month)+str(datetime.datetime.today().day)
            if startDate and endDate:
                workbook = xlwt.Workbook(encoding = 'utf-8')
                t=0
                airMonitorList=AirMonitor.objects.filter(M_RecordTime__lte=endDate).filter(M_RecordTime__gte=startDate).order_by('M_RecordTime')
                for k in range(len(airMonitorList)):
                    if k%10000==0:
                        t+=1
                        worksheet = workbook.add_sheet(str(t))
                        worksheet.write(0, 3, label = u'空气质量监测数据')
                        worksheet.write(1, 0, label = u'省份名称')
                        worksheet.write(1, 1, label = u'地区名称')
                        worksheet.write(1, 2, label = u'节点名称')
                        worksheet.write(1, 3, label = u'经度')
                        worksheet.write(1, 4, label = u'纬度')
                        worksheet.write(1, 5, label = u'CO')
                        worksheet.write(1, 6, label = u'NO2')
                        worksheet.write(1, 7, label = u'O3')
                        worksheet.write(1, 8, label = u'PM10')
                        worksheet.write(1, 9, label = u'PM2.5')
                        worksheet.write(1,10, label = u'SO2')
                        worksheet.write(1, 11, label = u'记录时间')
                        if len(airMonitorList)-k<10000:
                            m=len(airMonitorList)-k
                        else:m=10000

                        for i in range(m):
                            worksheet.write(i+2, 0, label = airMonitorList[k+i].M_ProvinceName)
                            worksheet.write(i+2, 1, label = airMonitorList[k+i].M_RegionName)
                            worksheet.write(i+2, 2, label =airMonitorList[k+i].M_NodeName)
                            worksheet.write(i+2, 3, label = airMonitorList[k+i].M_Longitude)
                            worksheet.write(i+2, 4, label = airMonitorList[k+i].M_Latitude)
                            worksheet.write(i+2, 5, label =airMonitorList[k+i].M_CO)
                            worksheet.write(i+2, 6, label = airMonitorList[k+i].M_NO2)
                            worksheet.write(i+2, 7, label = airMonitorList[k+i].M_O3)
                            worksheet.write(i+2, 8, label = airMonitorList[k+i].M_PM10)
                            worksheet.write(i+2, 9, label = airMonitorList[k+i].M_PM25)
                            worksheet.write(i+2, 10, label = airMonitorList[k+i].M_SO2)
                            worksheet.write(i+2, 11, label = str(airMonitorList[k+i].M_RecordTime))
                        workbook.save(os.path.dirname(os.path.dirname(__file__))+'\static\export\AirMonitor'+exportDate+'.xls')
                return HttpResponse('/static/export/AirMonitor'+exportDate+'.xls')
            return HttpResponse('fail')
    except Exception,e:
        writeErrorLogger('空气导出'+e)
        return HttpResponse('fail')

def test_intenet(name):
    try:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0')]
        urllib2.install_opener(opener)
        req = urllib2.Request("http://www.baidu.com")
        req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        resp = urllib2.urlopen(req)
        resp.read()
        writeInfoLogger(name+':网络连接正常')
    except Exception,e:
        writeErrorLogger(name+':网络连接断开。。。。')
