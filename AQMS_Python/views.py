#coding=utf-8
from django.shortcuts import render_to_response
from air_quality import views as air_view
from water_quality import  views as water_view
import thread
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

currentUser=[]

def get_login(request):
    return render_to_response('login.html')

@csrf_exempt
def login(request):
    userName=request.POST.get('UserName','')
    password=request.POST.get('Password','')
    if userName and password:
        if userName=='admin' and password=='lvku':
            currentUser.append(userName)
            currentUser.append(password)
            return  HttpResponse('true')
    return HttpResponse('false')

def home(request):
    return render_to_response('home.html')

def start(request):
    thread.start_new_thread(air_view.start,())
    thread.start_new_thread(water_view.start,())
    return HttpResponse('开始监测')
