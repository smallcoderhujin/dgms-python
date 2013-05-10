#coding=utf-8
from pyquery import PyQuery as pyq
import datetime
import time,cookielib,urllib2,json
from air_quality.models import *
from AQMS_Python.log import *

address=[
         '太原,山西',
         '天津,天津市',
         '重庆,重庆市',
         '大连,辽宁','沈阳,辽宁',
         '郑州,河南',
         '保定,河北','沧州,河北','邯郸,河北','衡水,河北','廊坊,河北','秦皇岛,河北','张家口,河北','石家庄,河北','唐山,河北','邢台,河北',
         '呼和浩特,内蒙古',
         '南宁,广西',
         '西安,陕西',
         '长春,吉林',
         '成都,四川',
         '哈尔滨,黑龙江',
         '东莞,广东','佛山,广东','广州,广东','惠州,广东','江门,广东','珠海,广东','中山,广东','肇庆,广东','深圳,广东',
         '福州,福建','厦门,福建',
         '贵阳,贵州',
         '合肥,安徽',
         '海口,海南',
         '南昌,江西',
         '武汉,湖北',
         '兰州,甘肃',
         '乌鲁木齐,新疆',
         '拉萨,西藏',
         '银川,宁夏',
         '西宁,青海',
         ]

def start():
    GetDynamicData()
    #GetHistoryData()

def GetDynamicData():
    writeInfoLogger('全国空气开始监测')
    testIntenet('全国')
    try:
        for i in range(len(address)):
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0')]
            urllib2.install_opener(opener)
            print address[i].split(',')[0]
            req = urllib2.Request('http://pm25.in/api/querys/aqi_details.json?city='+address[i].split(',')[0]+'&token=EyqVR1FaZFprK6QDFszY')
            req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            result =json.loads(urllib2.urlopen(req).read())
            print result
            for j in range(len(result)):
                print result[j]['area'],result[j]['position_name'],result[j]['co']
                airMonitor=AirMonitor(M_ProvinceName=address[i].split(',')[1], M_RegionName=result[j]['area'],M_NodeName=result[j]['position_name'],M_CO=result[j]['co'],M_NO2=result[j]['no2'],M_O3=result[j]['o3'],M_PM10=result[j]['pm10'],M_PM25=result[j]['pm2_5'],M_SO2=result[j]['so2'],M_RecordTime=datetime.datetime.strptime(result[j]['time_point'],'%Y-%m-%dT%H:%M:%SZ'))
                airMonitor.save()
    except Exception,e:
        print e
        writeErrorLogger('全国:'+e)
    finally:
        writeInfoLogger('全国休眠一小时')
        time.sleep(60*60)
        GetDynamicData()

def GetHistoryData():
    try:
        for i in range(len(address)):
            try:
                strUrl='http://www.pm2d5.com/city/%s.html' %address[i]
                doc=pyq(url=strUrl)
            except Exception,e:
                continue
            cts=doc('script')
            for i in cts:
                text=pyq(i).text()
                if text.find('flashvalue')!=-1:
                    cityName=text[text.find('=')+3:text.find(u'最')]
                    datas= str(text[text.find('*/')+2:text.find('myChart')-10].encode('gbk')).strip().replace('flashvalue','').replace('+=','').replace('=','').replace('"','').replace('<','').replace('/>','').split(';')

                    for j in range(len(datas)):
                        if len(datas[j])>1:
                            dataValue=datas[j][datas[j].find('value')+6:datas[j].find('color')-2]
                            dataDate=datas[j][datas[j].find('name')+9:datas[j].find('value')-4]
                            airMonitor=AirMonitor(M_NodeName=cityName,M_PM25=dataValue,M_RecordTime=datetime.date(2013,3,int(dataDate)))
                            airMonitor.save()
    except Exception,e:
        print e
    finally:
        time.sleep(6)
        GetHistoryData()

def testIntenet(name):
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