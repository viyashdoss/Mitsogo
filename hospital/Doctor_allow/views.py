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


def doctor_allow(name):
    print("thread started",name)
    try:
        while True:
            print("running-----")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("doc",str(exc_tb.tb_lineno), str(e))
    '''Time=Time-600
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
    print("thread ended/ removed patient",patients_name)'''


