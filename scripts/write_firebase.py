from lxml import html
import requests
from twilio.rest import Client
from time import sleep
import sys
from threading import Timer
from datetime import datetime
import os
import interval_timer 
import requests as rs
import json
from firebase_connect import read_from_firebase,write_to_firebase,upsert_to_firebase
import time

def get_nordic_accounts():
    # print('Get nordic devices') 
    # NORDIC_API_KEY
    accounts_keys = []
    try:
        accounts_list = read_from_firebase('jupiter-flutter','api_keys')
        for snapshot in accounts_list:
            # print(snapshot.to_dict())
            account_dict = snapshot.to_dict()
            accounts_keys.append(account_dict['api_key'])
        # print(accounts_list)
        return accounts_keys
    except Exception as error:
        print(error)

def get_nordic_devices():
    # print('Get nordic devices') 
    # NORDIC_API_KEY

    try:
        nordic_accounts = get_nordic_accounts()
        nordic_account_list = []
        for item in  nordic_accounts:   
            url = 'https://api.nrfcloud.com/v1' #base URL
            path = '/devices' #get method for API
            headers ={'Authorization':'Bearer '+item}
            # os.environ['NORDIC_API_KEY']
            # print(url+path)
            r = rs.get(url+path,headers=headers)
            json_data =  json.loads(r.content)
            device_data_dict = {'api_key':item,'data':json_data}
            nordic_account_list.append(device_data_dict)
        # print(r.content) #display the reponse from Api call 
        return nordic_account_list
    except Exception as error:
        print(error)


def get_nordic_device_status(deviceId, api_key):
    # print('Get nordic devices') 
    # NORDIC_API_KEY
    try:
        
        url = 'https://api.nrfcloud.com/v1' #base URL
        path = '/devices/'+deviceId #get method for API
        headers ={'Authorization':'Bearer '+api_key}
        # print(url+path)
        r = rs.get(url+path,headers=headers)
        data = json.loads(r.content)
        print(data['state']['reported']['connection']['status']) #display the reponse from Api call 
        return data['state']['reported']['connection']['status']
    except Exception as error:
        print(error)

#Get the last 2 known locations for the device
def get_nordic_device_last_location(deviceId,api_key):
    
    # NORDIC_API_KEY
    try:
        
        url = 'https://api.nrfcloud.com/v1' #base URL
        path = '/location/history' #get method for API
        headers ={'Authorization':'Bearer '+api_key}
        values = {'deviceIdentifier':deviceId,'pageLimit':99}
        # print(url+path)
        r = rs.get(url+path,headers=headers,params=values)
        # print(r.content) #display the reponse from Api call 
        return json.loads(r.content)
    except Exception as error:
        print(error)

def get_nordic_device_APP_data(deviceId,api_key):
    
    # NORDIC_API_KEY
    try:
        
        url = 'https://api.nrfcloud.com/v1' #base URL
        path = '/messages' #get method for API
        headers ={'Authorization':'Bearer '+api_key}
        values = {'deviceIdentifier':deviceId,'pageLimit':99}
        # print(url+path)
        r = rs.get(url+path,headers=headers,params=values)
        # print(r.content) #display the reponse from Api call 
        return json.loads(r.content)
    except Exception as error:
        print(error)

def save_device_APP_data_firebase(deviceId,api_key):
    try:
        device_data = get_nordic_device_APP_data(deviceId,api_key)
        device_data_dict = {"GPS":{"data":""},
                            "FLIP":{"data":""},
                            "TEMP":{"data":""},
                            "HUMID":{"data":""},
                            "AIR_PRESS":{"data":""},
                            }
    
        gps_data_filled = 0
        temp_data_filled = 0
        flip_data_filled = 0
        humid_data_filled= 0
        pressure_data_filled = 0
        filled_val = 0
        if device_data['total'] > 0:
            for i in range(99):
                
                # print('filled_val',filled_val)
                gps_data = device_data_dict['GPS']
            
                # print('GPS Data : ',i,'filled_val',filled_val, 'APP:' ,device_data['items'][i]['message']['appId'])
                app_data = device_data['items'][i]['message']['appId']
                app_message = device_data['items'][i]['message']
                if app_data =='GPS' and gps_data_filled == 0:
                    try:
                        # print('Update gps')
                        app_message = device_data['items'][i]['message']
                        gps_data.update(app_message)
                        
                        gps_data_filled = gps_data_filled +1
                        filled_val = filled_val + 1
                    except Exception as error:
                        print(error)
                
                flip_data = device_data_dict['FLIP']
                if app_data == 'FLIP' and flip_data_filled == 0:
                    # print('Update flip')
                    flip_data.update(app_message)
                    filled_val = filled_val +1
                    flip_data_filled= flip_data_filled + 1

                temp_data = device_data_dict['TEMP']
                # app_message = device_data['items'][i]['message']
                if app_data == 'TEMP' and temp_data_filled == 0:
                    # print('Update temp')
                    temp_data.update(app_message)
                    filled_val = filled_val +1
                    temp_data_filled =  temp_data_filled +1

                humid_data = device_data_dict['HUMID']
                if app_data == 'HUMID'and humid_data_filled == 0:
                    # print('Update humid')
                    humid_data.update(app_message)
                    filled_val = filled_val +1
                    humid_data_filled = humid_data_filled +1

                pressure_data = device_data_dict['AIR_PRESS']
                if app_data == 'AIR_PRESS'and pressure_data_filled == 0:
                    # print('Update AIR pressure')
                    pressure_data.update(app_message)
                    filled_val = filled_val +1
                    pressure_data_filled = pressure_data_filled + 1
            print('Device : ',deviceId,device_data_dict)
            # print(device_data['total'])
            timestamp = time.time()
            upload_data = { 'data':device_data_dict,
                            'device': deviceId,
                            'ts':timestamp}
            doc_id = deviceId+'_'+str(int(timestamp))
            write_to_firebase('jupiter-flutter','device_monitor',upload_data,doc_id)  
    except Exception as ex:
        print(ex)

def save_devices_firebase():
    
    device_data = get_nordic_devices()
    try:
        # print(device_data['total'])
        if device_data['total'] > 0:
            for i in range(device_data['total']):
                print(device_data['items'][i]['type'],device_data['items'][i]['id'],device_data['items'][i]['name'],device_data['items'][i]['tags'])
                if device_data['items'][i]['type'] == 'Generic':       
                    print(device_data['items'][i]['$meta']['createdAt'],device_data['items'][i]['$meta']['updatedAt'],device_data['items'][i]['$meta']['version'])
                else:
                    print(device_data['items'][i]['$meta']['createdAt'],device_data['items'][i]['$meta']['version'])
    except Exception as ex:
        print(ex)

def save_device_status_firebase(deviceId,api_key,active):
    try:
        # print('GPS Location entries:',device_data['total'])
        timestamp = time.time()
        if active:
            upload_data = { 'active':active,
                        'device': deviceId,
                        'last_active':timestamp,
                        'ts':timestamp}
        else:
            upload_data = { 'active':active,
                        'device': deviceId,
                        'ts':timestamp}
        doc_id = deviceId
        upsert_to_firebase('jupiter-flutter','device_activity',upload_data,doc_id)            
        # print (timestamp)
    except Exception as ex:
        print(ex)

def send_sms():
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        message = client.messages.create(
         body='Course open again \n https://ce.harpercollege.edu/public/category/programArea.do?method=load&selectedProgramAreaId=29362',
         from_=os.environ['TWILIO_FROM_NUMBER'],
         to=os.environ['TWILIO_TO_NUMBER1'])
        message = client.messages.create(
         body='Course open again \n https://ce.harpercollege.edu/public/category/programArea.do?method=load&selectedProgramAreaId=29362',
         from_=os.environ['TWILIO_FROM_NUMBER'],
         to=os.environ['TWILIO_TO_NUMBER2'])
        print(message.sid)
    except Exception as ex:
        print(ex)

#TODO: Add wrapper to call all methods from one method
def get_all_device_data():
    device_data_list = get_nordic_devices()
    try:
        #TODO: Use another thread to save all the devices in firebase
        # print (device_data)
        for device_item in device_data_list:
            # print('--------------')
            device_data = device_item['data']
            device_api_key = device_item['api_key']
            # print(device_data['total'],device_api_key)
            if device_data['total'] > 0:
                for i in range(device_data['total']):
                    # print(device_data['items'][i]['type'],device_data['items'][i]['id'],device_data['items'][i]['name'],device_data['items'][i]['tags'])
                    if device_data['items'][i]['type'] == 'Generic':       
                        device_id = (device_data['items'][i]['id'])
                        # print(device_id)
                        device_status = get_nordic_device_status(device_id,device_api_key)
                        if(device_status == 'connected'):
                            save_device_status_firebase(device_id,device_api_key,True)
                        else:
                            save_device_status_firebase(device_id,device_api_key,False)
    except Exception as ex:
        print(ex)




def request_validation_in_intervals():
    global rt
    rt = interval_timer.RepeatedTimer(int(os.environ['REFRESH_RATE_IN_SECONDS']), get_all_device_data) # it auto-starts, no need of rt.start()
    
    try:
        sleep(10000) # your long-running job goes here...
    finally:
        rt.stop() # better in a try/finally block to make sure the program ends!


request_validation_in_intervals()
