import datetime
from datetime import timezone
from pickle import TRUE
import Validation as v
from typing import overload
import firebase_admin , json
from flask import Flask, jsonify, request
from firebase_admin import credentials
from firebase_admin import firestore
from flask_cors import CORS , cross_origin

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

db= firestore.client()
app = Flask(__name__)
CORS(app)

@app.route('/addParts', methods=['POST','GET'])
@cross_origin
def addParts():
    if request.method=='POST':
        data= request.get_json()
        ct = datetime.datetime.now(datetime.timezone.utc)
        print(type(data))
        data['created_at']= ct
        list1=db.collection('parts').get()
        str1=v.nextId(list1)
        db.collection('parts').document(str1).set(data)
        db.collection('parts').document(str1).update({'updated_at': firestore.ArrayUnion([ct])})

        return jsonify({'Response':'part added successfully'})

    if request.method=='GET':
        result= db.collection('parts').get()
        data=[]
        for r in result:
            data.append(r.to_dict())
            print(r.id)
        
        return jsonify(data)
@app.route('/parts/<string:id>', methods=['PUT','DELETE','GET'])
def parts(id):
    if request.method=='GET':
        result=(db.collection('parts').document(id).get()).to_dict()
        return jsonify(result)
    
    if request.method=='PUT':
        data=request.get_json()
        db.collection('parts').document(id).update(data)
        return jsonify({'Response':'updated successfully'})
    
    if request.method=='DELETE':
        db.collection('parts').document(id).delete()
        return jsonify({'Response':'Deleted successfully'})

@app.route('/service/<string:id>', methods=['PUT','DELETE','GET'])
def service(id):
    if request.method=='GET':
        result=(db.collection('services').document(id).get()).to_dict()
        return jsonify(result)
    
    if request.method=='PUT':
        data=request.get_json()
        db.collection('service').document(id).update(data)
        return jsonify({'Response':'updated successfully'})
    
    if request.method=='DELETE':
        db.collection('service').document(id).delete()
        return jsonify({'Response':'Deleted successfully'})

@app.route('/addService', methods=['POST','GET'])        
def addService():
    if request.method=='POST':
        data= request.get_json()
        ct = datetime.datetime.now(datetime.timezone.utc)
        data['created_at']= ct
        list1=db.collection('services').get()
        str1=v.nextId(list1)
        db.collection('services').document(str1).set(data)
        return jsonify({'Response':'service added successfully'})

    if request.method=='GET':
        result= db.collection('services').get()
        data=[]
        for r in result:
            data.append(r.to_dict())
            print(r.id)
        
        return jsonify(data)
@app.route('/addEmployee', methods=['POST','GET'])
def addEmployee():
    if request.method=='POST':
        data= request.get_json()
        ct = datetime.datetime.now(datetime.timezone.utc)
        print(type(data))
        data['created_at']= ct
        db.collection('employee').document(data['phone']).set(data)
        return jsonify({'Response':'employee added sucessfully'})
    
    if request.method=='GET':
        result= db.collection('employee').get()
        data=[]
        for r in result:
            data.append(r.to_dict())
            print(r.id)
        
        return jsonify(data)

@app.route('/appointments', methods=['GET'])
def appointments():
    if request.method=='GET':
        data= getData("appointments")
        return jsonify(data)

@app.route('/unassigned', methods=['GET'])
def unassigned():
    if request.method=='GET':
        data= seeUnAssignedJobs()
        return jsonify(data)

@app.route('/pending', methods=['GET'])
def pending():
    if request.method=='GET':
        data= seeAllPendingJobs()
        return jsonify(data)

@app.route('/in_progress', methods=['GET'])
def in_progress():
    if request.method=='GET':
        data= seeAllInProgressJobs()
        return jsonify(data)

@app.route('/sales', methods=['GET'])
def sales():
    if request.method=='GET':
        data= seeAllCompletedJobs()

        return jsonify(data)

@app.route('/freeEmployee/<string:id>', methods=['GET'])
def freeEmployee(id):
    if request.method=='GET':
        emp= db.collection('employee').get()
        emp_list=[]
        for p in emp:
            emp_list.append(p.id)
        appoint=(db.collection('appointments').document(id).get()).to_dict()
        appoint_time= appoint['appoint_time']
        docs = db.collection(u'appointments').where('appoint_time' ,'==', appoint_time ).get()
        if docs:
            for doc in docs:
                t1=doc.to_dict()
                for i in range(len(emp_list)):
                    if int(t1['employee_id']) == int(emp_list[i]):
                        print(len(emp_list))
                        print(emp_list[i])
                        emp_list.remove(emp_list[i])
                        print(emp_list)
                        print('removed' )
                        break
            emp_list2=[]
            for index in range(len(emp_list)):
                result= (db.collection('employee').document(emp_list[index]).get()).to_dict()
                emp_list2.append(result)
            return jsonify(emp_list2)
        else:
            return jsonify({'result':'NULL'})

@app.route('/assignEmployee/<string:id>', methods=['PUT'])
def assignEmployee(id):
    if request.method=='PUT':
        data= request.get_json()
        ct = datetime.datetime.now(datetime.timezone.utc)
        data['status.assigned']=ct
        db.collection('appointments').document(id).update(data)
        return jsonify({'Response':'employee assigned successfully'})


#this function will receive table name whose data you wish to use
def getData(tableName): #this will return the desired Data in array from where the appoints data can be accessed
    data = db.collection(str(tableName)).get()
    list = []
    for d in data:
        a = d.to_dict()
        list.append(a)

    return list

#To view data in sequence wise, apply loop
'''---------------------------------------------------------------------------------'''


#This function will return a list (array) which contains all those appointments which are un-assigned along with all corresponding appointment details
def seeUnAssignedJobs():
    temp = []
    appointmentTable = getData("appointments")

    for data in appointmentTable:
        try:
            a = data['status']['assigned']
        except KeyError:
            temp.append(data)

    return temp

#assigned = True and no in-progress
#Will give list whihc contains all the pending jobs along details
def seeAllPendingJobs():
    temp = []
    appointmentTable = getData("appointments")

    for data in appointmentTable:
        try:
            a = data['status']['assigned']

            try:
                b = data['status']['in_progress']
            except KeyError:
                temp.append(data)

        except KeyError:
            pass

    return temp

#when complete is empty and in-progress exists then it is in progresss
def seeAllInProgressJobs():
    temp = []
    appointmentTable = getData("appointments")

    for data in appointmentTable:
        try:
            a = data['status']['in_progress']

            try:
                b = data['status']['completed']
            except KeyError:
                temp.append(data)

        except KeyError:
            pass

    return temp

#when complete exists
def seeAllCompletedJobs():
    temp = []
    appointmentTable = getData("appointments")

    for data in appointmentTable:
        try:
            a = data['status']['completed']
            temp.append(data)

        except KeyError:
            pass

    return temp

if __name__=='__main__':
    app.run(debug=TRUE)