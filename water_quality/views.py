#coding=utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponse
from pyquery import PyQuery as pyq
import time,datetime,urllib2,cookielib,xlwt,os
from water_quality.models import *
from AQMS_Python.log import *

rive=[u'辽河流域',u'海河流域',u'淮河流域',u'太湖流域',u'长江流域',u'黄河流域',u'珠江流域',u'松花江流域',u'西南诸河',u'东南诸河',u'滇池流域',u'巢湖流域']
address={}
address['57']=u'辽宁铁岭朱尔山,0'
address['61']=u'辽宁盘锦兴安,0'
address['70']=u'辽宁营口辽河公园,0'
address['116']=u'辽宁抚顺大伙房水库,0'
address['132']=u'辽宁辽阳汤河水库,0'
address['135']=u'辽宁丹东江桥,0'

address['53']=u'北京密云古北口,1'
address['73']=u'北京门头沟沿河城,1'
address['60']=u'天津三岔口,1'
address['54']=u'天津果河桥,1'
address['66']=u'河北张家口八号桥,1'
address['72']=u'河北石家庄岗南水,1'
address['138']=u'山东聊城秤钩湾,1'

address['154']=u'河南信阳淮滨水文,2'
address['32']=u'安徽阜南王家坝,2'
address['58']=u'安徽淮南石头埠,2'
address['109']=u'安徽蚌埠蚌埠闸,2'
address['149']=u'安徽滁州小柳巷,2'
address['19']=u'江苏盱眙淮河大桥,2'
address['120']=u'河南驻马店班台,2'
address['162']=u'河南信阳蒋集水文站,2'
address['122']=u'河南周口沈丘闸,2'
address['166']=u'安徽阜阳徐庄,2'
address['161']=u'安徽阜阳张大桥,2'
address['59']=u'安徽界首七渡口,2'
address['55']=u'河南周口鹿邑付桥闸,2'
address['157']=u'河南永城黄口,2'
address['155']=u'安徽亳州颜集,2'
address['106']=u'安徽淮北小王桥,2'
address['151']=u'安徽宿州泗县公路桥,2'
address['152']=u'江苏泗洪大屈,2'
address['159']=u'安徽宿州杨庄,2'
address['164']=u'江苏徐州李集桥,2'
address['134']=u'山东枣庄台儿庄大桥,2'
address['20']=u'江苏邳州艾山西大桥,2'
address['153']=u'江苏徐州小红圈,2'
address['147']=u'山东临沂重坊桥,2'
address['150']=u'山东临沂涝沟桥,2'
address['115']=u'山东临沂清泉寺,2'
address['156']=u'江苏连云港大兴桥,2'

address['77']=u'江苏无锡沙渚,3'
address['111']=u'江苏宜兴兰山嘴,3'
address['103']=u'江苏苏州西山,3'
address['8']=u'浙江湖州新塘港,3'
address['129']=u'上海青浦急水港,3'
address['97']=u'浙江嘉兴王江泾,3'
address['139']=u'浙江嘉兴斜路港,3'

address['74']=u'四川攀枝花龙洞,4'
address['5']=u'重庆朱沱,4'
address['75']=u'湖北宜昌南津关,4'
address['16']=u'湖南岳阳城陵矶,4'
address['76']=u'江西九江河西水厂,4'
address['56']=u'安徽安庆皖河口,4'
address['18']=u'江苏南京林山,4'
address['119']=u'四川乐山岷江大桥,4'
address['117']=u'四川宜宾凉姜沟,4'
address['118']=u'四川泸州沱江二桥,4'
address['137']=u'河南南阳陶岔,4'
address['125']=u'湖北丹江口胡家岭,4'
address['110']=u'湖南长沙新港,4'
address['107']=u'湖南岳阳岳阳楼,4'
address['65']=u'湖北武汉宗关,4'
address['123']=u'江西南昌滁槎,4'
address['114']=u'江西九江蛤蟆石,4'
address['112']=u'江苏扬州三江营,4'
address['158']=u'四川广元清风峡,4'

address['81']=u'甘肃兰州新城桥,5'
address['113']=u'宁夏中卫新墩,5'
address['121']=u'内蒙乌海海勃湾,5'
address['83']=u'内蒙包头画匠营子,5'
address['108']=u'山西忻州万家寨水库,5'
address['12']=u'河南济源小浪底,5'
address['85']=u'山东济南泺口,5'
address['84']=u'山西运城河津大桥,5'
address['141']=u'陕西渭南潼关吊桥,5'

address['127']=u'广西凭祥平而关,6'
address['80']=u'广西南宁老口,6'
address['131']=u'广西桂林阳朔,6'
address['126']=u'广西贵港石嘴,6'
address['79']=u'广西梧州界首,6'
address['64']=u'广东清远七星岗,6'
address['63']=u'广东广州长洲,6'
address['142']=u'广东中山横栏,6'

address['14']=u'黑龙江肇源,7'
address['69']=u'黑龙江同江,7'
address['67']=u'吉林长春松花江村,7'
address['68']=u'吉林白城白沙滩,7'
address['133']=u'黑龙江黑河,7'
address['143']=u'内蒙古呼伦贝尔黑山头,7'
address['144']=u'黑龙江抚远乌苏镇,7'
address['136']=u'吉林延边圈河,7'

address['140']=u'云南西双版纳橄榄坝,8'
address['146']=u'云南红河州河口,8'

address['104']=u'浙江杭州鸠坑口,9'
address['128']=u'福建福州白岩潭,9'

address['62']=u'云南昆明西苑隧道,10'
address['124']=u'云南昆明观音山,10'

address['78']=u'安徽巢湖裕溪口,11'
address['105']=u'安徽合肥湖滨,11'

def water_quality_list(request):
    waterMonitorList=WaterMonitor.objects.all().order_by('-W_RecordTime')
    if len(waterMonitorList)>=10:
        waterMonitorList=waterMonitorList[:10]
    for i in range(len(waterMonitorList)):
        waterMonitorList[i].W_RecordTime='%s' %waterMonitorList[i].W_RecordTime
    return render_to_response('water_quality/list.html',{'WaterMonitorList':waterMonitorList})

def start():
    writeInfoLogger('全国水文开始监测')
    test_intenet('水文')
    try:
        strUrl=r'http://58.68.130.147'
        doc=pyq(url=strUrl)
        cts=doc('input')
        if len(cts)>0:
            datas= pyq(cts[1]).val().split('!!')
            if len(datas)>0:
                for i in range(len(datas)):
                    data=datas[i].split('$')
                    if len(data)>0 and address.has_key(data[0]):
                        name=address[data[0]]
                        if data[2]=='-' or float(data[2])<0:
                            ph='-'
                        else:
                            ph=data[2]
                        if data[4]=='-' or float(data[4])<0:
                            do='-'
                        else:
                            do=data[4]
                        if data[6]=='-' or float(data[6])<0 or float(data[6])==9999:
                            cod='-'
                        else:
                            cod=data[6]
                        if data[8]=='-' or float(data[8])<0 or float(data[8])==9999:
                            toc='-'
                        else:
                            toc=data[8]
                        if data[10]=='-' or float(data[10])<0:
                            nh3n='-'
                        else:
                            nh3n=data[10]

                        waterMonitor=WaterMonitor(W_AreaName=rive[int(name.split(',')[1])],
                                                  W_RiverName=name.split(',')[0],W_PH=ph,
                                                  W_DO=do,W_COD=cod,W_TOC=toc,W_NH3N=nh3n,
                                                  W_RecordTime=datetime.datetime.strptime(data[12]+data[1].strip(), "%Y-%m-%d %H:%M:%S"))
                        waterMonitor.save()
    except Exception,e:
        writeErrorLogger(e.message)
    finally:
        writeInfoLogger('水文休眠4小时')
        time.sleep(60*60*4)
        start()

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

def export(request):
    try:
        if request.method=='GET':
            startDate=datetime.datetime.strptime(request.GET.get('start'),'%Y-%m-%d')
            endDate=datetime.datetime.strptime(request.GET.get('end'),'%Y-%m-%d')
            exportDate=str(datetime.datetime.today().year)+str(datetime.datetime.today().month)+str(datetime.datetime.today().day)
            if startDate and endDate:
                workbook = xlwt.Workbook(encoding = 'utf-8')
                t=0
                waterMonitorList=WaterMonitor.objects.all().order_by('W_RecordTime').filter(W_RecordTime__lte=endDate).filter(W_RecordTime__gte=startDate)
                for k in range(len(waterMonitorList)):
                    if k%10000==0:
                        t+=1
                        worksheet = workbook.add_sheet(str(t))
                        worksheet.write(0, 3, label = u'水质监测数据')
                        worksheet.write(1, 0, label = u'流域名称')
                        worksheet.write(1, 1, label = u'河流名称')
                        worksheet.write(1, 2, label = u'PH值')
                        worksheet.write(1, 3, label = u'溶解氧')
                        worksheet.write(1, 4, label = u'氨氮')
                        worksheet.write(1, 5, label = u'高锰酸盐指数')
                        worksheet.write(1, 6, label = u'总有机碳')
                        worksheet.write(1, 7, label = u'时间')
                        if len(waterMonitorList)-k<10000:
                            m=len(waterMonitorList)-k
                        else:m=10000

                        for i in range(m):
                            worksheet.write(i+2, 0, label = waterMonitorList[k+i].W_AreaName)
                            worksheet.write(i+2, 1, label = waterMonitorList[k+i].W_RiverName)
                            worksheet.write(i+2, 3, label = waterMonitorList[k+i].W_DO)
                            worksheet.write(i+2, 4, label = waterMonitorList[k+i].W_NH3N)
                            worksheet.write(i+2, 5, label =waterMonitorList[k+i].W_COD)
                            worksheet.write(i+2, 6, label = waterMonitorList[k+i].W_TOC)
                            worksheet.write(i+2, 7, label = '%s' %waterMonitorList[k+i].W_RecordTime)
                        workbook.save(os.path.dirname(os.path.dirname(__file__))+'\static\export\WaterMonitor'+exportDate+'.xls')
                return HttpResponse('/static/export/WaterMonitor'+exportDate+'.xls')
            return HttpResponse('fail')
    except Exception,e:
        writeErrorLogger('水质导出'+e)
        return HttpResponse('fail')

