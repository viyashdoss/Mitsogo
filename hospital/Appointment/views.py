from django.shortcuts import render
from Appointment import *
import threading
import time
from django.http import  HttpResponse
import bson
from bson.json_util import dumps, LEGACY_JSON_OPTIONS
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
import sys 

def list(request):
    return_data={}
    if request.method=="POST":
        db = get_db_connection()
        mycol = db["Doctors"]
        name= request.POST.get('name', "")
        department = request.POST.get('department', "")
        isactive=0
        count=1
        for x in mycol.find({"name":name,"department":department}):
            isactive=x['isactive']
            count=x['count']
        if isactive==0:
            Token=department+'-'+name+'-'+str(count)
            db['Doctors'].update_one(
                                        {
                                            
                                                'name': name, 
                                                'isactive': 0,
                                                'department':department
                                                                                
                                        },
                                        {
                                            "$set": {
                                                
                                                        "consulting-start-time":datetime.datetime.now(),
                                                        "isactive":1,
                                                        "current_patient":Token
                                                        
                                        },
                                            '$inc': { 'count': 1 } 
                                        }
                                    )   
            
            t = threading.Thread(target=UpdateDoctor, args=(name,department,Token,600))
            t.start()
        else:
            patients_name=department+'-'+name+'-'+str(count+1)
            today=datetime.datetime.strptime(str(datetime.datetime.now().date()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
            next=datetime.datetime.strptime(str(datetime.datetime.now().date()+ datetime.timedelta(days=1)) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
            db['Queue'].update_one(
                                        { 'date':
                                                    {   '$gte': today, 
                                                        '$lte': next
                                                    } 
                                        },
                                        {
                                            "$push": {
                                                        "queue."+department+'.'+name: patients_name
                                                    }
                                        }
                                    )   
            db['Doctors'].update_one(
                                        {
                                            
                                                'name': name, 
                                                'department':department
                                                                                
                                        },
                                        {
                                            '$inc': { 'count': 1 } 
                                        }
                                    )   
            time=GetQueue(department,name)
            time=time*10*60
            
            t = threading.Thread(target=UpdateDoctor, args=(name,department,patients_name,time))
            t.start() 
            
    else:
        db = get_db_connection()
        dep = db["Department"].find({})
        doc = db["Doctors"].find({})
        today=datetime.datetime.strptime(str(datetime.datetime.now().date()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        next=datetime.datetime.strptime(str(datetime.datetime.now().date()+ datetime.timedelta(days=1)) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        queueee=db['Queue'].aggregate([
                                    { '$match': 
                                        
                                        { 'date':
                                                {   '$gte': today, 
                                                    '$lte': next
                                                } 
                                        }
                                        
                                    }                                    
                                ])
        test_string=dumps(queueee,json_options=LEGACY_JSON_OPTIONS)
        res = json.loads(test_string)
        # To reset token generation everyday
        if len(res)==0:
            query2=([
                        {
                            '$lookup': {
                                'from': 'Doctors', 
                                'localField': 'short', 
                                'foreignField': 'department', 
                                'as': 'queue'
                            }
                        }, {
                            '$group': {
                                '_id': {
                                    'name': '$queue.name', 
                                    'department': '$short'
                                }
                            }
                        }, {
                            '$project': {
                                '_id': 1
                            }
                        }
                    ])
            dict_save=dict()
            a=db["Department"].aggregate(query2)
            for i in a:
                dict_save[i['_id']['department']]={}
                for j in i['_id']['name']:
                    dict_save[i['_id']['department']][j]=[]
            db['Doctors'].update_many({},
                            {
                            "$set": {
                                    "count":1,
                                    "isactive":0,
                                    "current_patient":""
                                    }
                            }
                        )
            mydict={
            "queue": dict_save,
            "date": datetime.datetime.now()
            }
            db['Queue'].insert_one(mydict)
        return_data['department']=json.loads(dumps(dep,json_options=LEGACY_JSON_OPTIONS))
        return_data['doctors']=json.loads(dumps(doc,json_options=LEGACY_JSON_OPTIONS))
    return render(request, 'index.html', {'data': return_data})


@csrf_exempt
def Registration(request):
    return_data={}
    if request.method=="POST":
        db = get_db_connection()
        mycol = db["Doctors"]
        department = request.POST.get('department', "")
        name = request.POST.get('name', "")
        isactive=0
        count=1
        time=600
        Token=''
        for x in mycol.find({"name":name,"department":department}):
            isactive=x['isactive']
            count=x['count']
        if isactive==0:
            db['Doctors'].update_one(
                                        {
                                            
                                                'name': name, 
                                                'isactive': 0,
                                                'department':department
                                                                                
                                        },
                                        {
                                            "$set": {
                                                
                                                        "consulting-start-time":datetime.datetime.now(),
                                                        "isactive":1
                                                        
                                        },
                                            '$inc': { 'count': 1 } 
                                        }
                                    )   
            Token=department+'-'+name+'-'+str(count)
            t = threading.Thread(target=UpdateDoctor, args=(name,department,Token,600))
            t.start()
        else:
            patients_name=department+'-'+name+'-'+str(count)
            today=datetime.datetime.strptime(str(datetime.datetime.now().date()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
            next=datetime.datetime.strptime(str(datetime.datetime.now().date()+ datetime.timedelta(days=1)) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
            db['Queue'].update_one(
                                        { 'date':
                                                    {   '$gte': today, 
                                                        '$lte': next
                                                    } 
                                        },
                                        {
                                            "$push": {
                                                        "queue."+department+'.'+name: patients_name
                                                    }
                                        }
                                    )   
            db['Doctors'].update_one(
                                        {
                                            
                                                'name': name, 
                                                'department':department
                                                                                
                                        },
                                        {
                                            "$set": {
                                                
                                                        "consulting-start-time":datetime.datetime.now(),
                                                        "isactive":1
                                                        
                                        },
                                            '$inc': { 'count': 1 } 
                                        }
                                    )   
            time=GetQueue(department,name)
            time=time*10*60
            t = threading.Thread(target=UpdateDoctor, args=(name,department,patients_name,time))
            t.start() 
        return_data['token']=Token if Token else patients_name
        return_data['time']=time
        return HttpResponse(json.dumps(return_data), content_type='application/json')
    return render(request, 'index.html', {'data': return_data})

@csrf_exempt
def Check2(request):
    return_data={}
    db = get_db_connection()
    mycol = db["Doctors"]
    department = request.POST.get('department', "")
    name = request.POST.get('name', "")
    isactive=0
    current_token=""
    count=0
    time=600
    
    for x in mycol.find({"name":name,"department":department}):
        isactive=x['isactive']
        try:
            current_token=x['current_patient']
        except:
            current_token="please update in doc"
    if isactive==0:
        return_data['status']=1
        
    else:
        today=datetime.datetime.strptime(str(datetime.datetime.now().date()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        next=datetime.datetime.strptime(str(datetime.datetime.now().date()+ datetime.timedelta(days=1)) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        catch=db['Queue'].aggregate([
                                        { '$match': 
                                            { 'date':
                                                    {   '$gte': today, 
                                                        '$lte': next
                                                    } 
                                                }
  
                                            
                                        }
                                                                      
                                    ])
        

        
        next_token=''
        queuee=0
        for i in catch:
            try:
                next_token=i['queue'][department][name][0]
            except:
                next_token="You're next"
            queuee=len(i['queue'][department][name])
            
        if queuee==0:
            queuee=600
        else:
            queuee=(queuee*10*60)+600
        
        
        return_data['status']=0
        return_data['waiting_time']=queuee
        return_data['current_token']=current_token
        return_data['next_token']=next_token

    return HttpResponse(json.dumps(return_data), content_type='application/json')


#to get queue length for the day
def GetQueue(department,name):
    db = get_db_connection()
    today=datetime.datetime.strptime(str(datetime.datetime.now().date()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    next=datetime.datetime.strptime(str(datetime.datetime.now().date()+ datetime.timedelta(days=1)) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    mycol = db["Doctors"]
    isactive=0
    
    catch=db['Queue'].aggregate([
                                    { '$match': 
                                        { '$and': [ 
                                            { 'date':
                                                {   '$gte': today, 
                                                    '$lte': next
                                                } 
                                            }
                                        ]
                                        }
                                    }                                    
                                ])
    queuee=0
    for x in mycol.find({"name":name,"department":department}):
        isactive=x['isactive']
    
    if isactive==1:
        queuee+=1
    for i in catch:
        queuee=queuee+len(i['queue'][department][name])
    return queuee

def UpdateDoctor(name,department,patients_name,Time):

    db = get_db_connection()
    today=datetime.datetime.strptime(str(datetime.datetime.now().date()) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    next=datetime.datetime.strptime(str(datetime.datetime.now().date()+ datetime.timedelta(days=1)) + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    print("thread started",patients_name)
  
    Time=Time-600
    time.sleep(Time)
    print("thread updated",patients_name)
    db['Doctors'].update_one(
        { 
         'name': name ,
         'department': department
        },
        {
        "$set": {
                "isactive":1,
                "current_patient":patients_name
                }
        }
    )
    db['Queue'].update_one(
                    { 'date':
                        {   '$gte': today, 
                            '$lte': next
                        } 
                    },
                    { '$pull': 
                        { 
                         'queue.'+department+'.'+name : patients_name 
                        } 
                    }
    )
    time.sleep(601)
    
    db['Doctors'].update_one(
            { 
            'name': name ,
            'department': department
            },
            {
            "$set": {
                    "isactive":0,
                    "current_patient":""
                    }
            }
    )
    print("thread ended/ removed patient",patients_name)

    

#
@csrf_exempt
def continous_polling(request):
    db=get_db_connection()
    return_data={}
    doc = db["Doctors"].find({})
    return_data=json.loads(dumps(doc,json_options=LEGACY_JSON_OPTIONS))
    return HttpResponse(json.dumps(return_data), content_type='application/json')