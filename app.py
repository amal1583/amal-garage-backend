# from crypt import methods
# import datetime
# from datetime import *
from genericpath import exists
import time
from datetime import datetime, timezone
from pickle import TRUE
import Validation as v
from typing import overload
import firebase_admin, json
from flask import Flask, jsonify, request
from firebase_admin import credentials
from firebase_admin import firestore , auth
from flask_cors import CORS , cross_origin
from flask import Response
from partsSalePrediction import previousPartSale, futurePartSale
from servicesSalePrediction import previousServicesSale, futureServicesSale

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
au=auth._auth_client
db = firestore.client()
app = Flask(__name__)
CORS(app)


# ---------------------- signin api -----------------
@app.route('/signin', methods=['GET'])
def signin():
    if request.method == 'GET':
        phone = request.args.get('phone')
        password = request.args.get('password')
        user = (db.collection('users').document(phone).get()).to_dict()
        if user is not None:
            if user['password'] == password:
                token = datetime.now().strftime('%d%m%y%H%M%S%f')
                admin_permissions = {
                    "employees": True,
                    "parts": True,
                    "services": True,
                    "appointments": True,
                    "dashboard": True,
                    "partsPrediction": True,
                    "servicesPrediction": True,
                }
                customer_permissions = {
                    "customer_appointments": True,
                }
                data = dict()
                data['token'] = token
                data['usertype'] = user['user_type']
                data['userid'] = user['phone']
                if user['user_type'] == "admin":
                    data["permissions"] = admin_permissions
                elif user['user_type'] == "customer":
                    data["permissions"] = customer_permissions
                return jsonify(data)
            else:
                message = {'detail': 'incorrect password'}
                return jsonify(message), 400
        else:
            message = {'detail': 'user not found'}
            return jsonify(message), 400


# ----------------------  Employee Apis ------------------------------
@app.route('/employees', methods=['GET', 'POST', 'PUT', 'DELETE'])
def employee():
    if request.method == 'GET':
        id = request.args.get('id')
        if id is not None:
            result = (db.collection('employee').document(id).get()).to_dict()
            return jsonify(result)
        else:
            result = db.collection('employee').get()
            data = []
            for r in result:
                data.append(r.to_dict())
            return jsonify(data)

    elif request.method == 'POST':
        data = request.get_json()
        ct = datetime.now(timezone.utc)
        data['created_at'] = ct
        db.collection('employee').document(data['phone']).set(data)
        return jsonify({'Response': 'employee added sucessfully'})

    elif request.method == 'PUT':
        data = request.get_json()
        db.collection('employee').document(data['phone']).update(data)
        return jsonify({'Response': 'updated successfully'})

    elif request.method == 'DELETE':
        id = request.args.get('id')
        db.collection('employee').document(id).delete()
        return jsonify({'Response': 'Deleted successfully'})

# -------------------------- Services APIS -----------------------------------

@app.route('/services', methods=['GET', 'POST', 'PUT', 'DELETE'])
def service():
    if request.method == 'GET':
        id = request.args.get('id')
        if id is not None:
            result = (db.collection('services').document(id).get()).to_dict()
            result['id'] = id
            return jsonify(result)
        else:
            result = db.collection('services').get()
            data = []
            for r in result:
                res = r.to_dict()
                res['id'] = r.id
                data.append(res)
            return jsonify(data)

    elif request.method == 'POST':
        data = request.get_json()
        ct = datetime.now(timezone.utc)
        data['created_at'] = ct
        list1 = db.collection('services').get()
        str1 = v.nextId(list1)
        data['id']=str1
        data['price']=int(data['price'])
        data['service_avail']=0
        db.collection('services').document(str1).set(data)
        return jsonify({'Response': 'service added successfully'})

    if request.method == 'PUT':
        data = request.get_json()
        data.pop("service_avail", None)
        db.collection('services').document(data['id']).update(data)
        return jsonify({'Response': 'updated successfully'})

    if request.method == 'DELETE':
        id = request.args.get('id')
        db.collection('services').document(id).delete()
        return jsonify({'Response': 'Deleted successfully'})


# ----------------------------  Parts APIS -------------------------------------

@app.route('/parts', methods=['GET', 'POST', 'PUT', 'DELETE'])
def parts():
    if request.method == 'GET':
        id = request.args.get('id')
        if id is not None:
            result = (db.collection('parts').document(id).get()).to_dict()
            result['id'] = id
            return jsonify(result)
        else:
            result = db.collection('parts').get()
            data = []
            for r in result:
                res = r.to_dict()
                res['id'] = r.id
                data.append(res)
            return jsonify(data)

    elif request.method == 'POST':
        data = request.get_json()
        ct = datetime.now(timezone.utc)
        data['created_at'] = ct
        list1 = db.collection('parts').get()
        str1 = v.nextId(list1)
        data['id']=str1
        data['price']=int(data['price'])
        data['quantity']=int(data['quantity'])
        data['part_sold']=0
        db.collection('parts').document(str1).set(data)
        db.collection('parts').document(str1).update({'updated_at': firestore.ArrayUnion([ct])})
        return jsonify({'Response': 'part added successfully'})

    elif request.method == 'PUT':
        data = request.get_json()
        data.pop("part_sold", None)
        db.collection('parts').document(data['id']).update(data)
        return jsonify({'Response': 'updated successfully'})

    if request.method == 'DELETE':
        id = request.args.get('id')
        db.collection('parts').document(id).delete()
        return jsonify({'Response': 'Deleted successfully'})

# ------------------------ create new Appointments ------------------------
@app.route('/new_appointment', methods=['GET','POST'])
def new_appointment():
    # if request.method == 'GET':
    #     data = seeAllInProgressJobs()
    #     return jsonify(data)
    if request.method =='POST':
        data = request.get_json()
        ct = datetime.now(timezone.utc)
        data['created_at'] = ct
        

#  ------------------------ Appointments -------------------------------
@app.route('/appointments', methods=['GET'])
def appointments():
    if request.method == 'GET':
        data = getData("appointments")
        return jsonify(data)


# ----------------------- Un Assigned Appointments -----------------
@app.route('/unassigned', methods=['GET'])
def unassigned():
    if request.method == 'GET':
        data = seeUnAssignedJobs()
        return jsonify(data)

# ----------------------- Pending Appointments -----------------
@app.route('/pending', methods=['GET'])
def pending():
    if request.method == 'GET':
        data = seeAllPendingJobs()
        return jsonify(data)


# ------------------------ In Progress Appointments ------------------------
@app.route('/in_progress', methods=['GET'])
def in_progress():
    if request.method == 'GET':
        data = seeAllInProgressJobs()
        return jsonify(data)


# -------------------------- Completed Appointments -------------------------
@app.route('/sales', methods=['GET'])
def sales():
    if request.method == 'GET':
        data = completedJobsWithNames()
        return jsonify(data)

# ---------------------- Get Free employees -------------------------
@app.route('/freeEmployees', methods=['GET'])
def freeEmployee():
    if request.method == 'GET':
        appointment_id = request.args.get('appointment_id')
        employees = db.collection('employee').get()
        employee_list = []
        for employee in employees:
            employee_list.append(employee.id)
        requested_appointment = (db.collection('appointments').document(appointment_id).get()).to_dict()
        all_appointments = db.collection(u'appointments').where('appoint_time', '==', requested_appointment['appoint_time']).get()

        if all_appointments:
            for appointment in all_appointments:
                appointment = appointment.to_dict()
                if 'employee_id' in appointment.keys():
                    if appointment['employee_id'] is not None and appointment['employee_id'] != "":
                        employee_list.remove(appointment['employee_id'])
            final_employees = []
            free_employees = db.collection(u'employee').where('phone', 'in', employee_list).get()
            for final in free_employees:
                final_employees.append(final.to_dict())
            return jsonify(final_employees)
        else:
            return jsonify([])

# ------------------------- Assign employee to job -----------------------
@app.route('/assignEmployee', methods=['PUT'])
def assignEmployee():
    if request.method == 'PUT':
        data = request.get_json()
        appointment_id = data.pop("appointment_id", None)
        ct = datetime.now(timezone.utc)
        data['status.assigned'] = ct
        db.collection('appointments').document(appointment_id).update(data)
        return jsonify({'Response': 'employee assigned successfully'})


# ---------------- Jobs of specific employee -----------------------
@app.route('/employeeJobs', methods=['GET'])
def employeeJobs():
    if request.method == 'GET':
        id = request.args.get('id')
        result = db.collection('appointments').where('employee_id', '==', id).get()
        data = []
        for r in result:
            temp = r.to_dict()
            if 'location' in temp:
                temp.pop('location')
            data.append(temp)
        return jsonify(data)


# -------------------------------- total parts sale  -----------------------------
@app.route('/partRevenue', methods=['GET'])
def totalPartsRevenue():
    if request.method == 'GET':
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        start_date = time.mktime(datetime.strptime(start_date, "%Y-%m-%d").timetuple())
        end_date = time.mktime(datetime.strptime(end_date, "%Y-%m-%d").timetuple())

        final_data = []
        appointments = completedinframe(start_date, end_date)

        for appointment in appointments:
            appointment_date = appointment['appoint_time']
            appointment_date = str(appointment_date.date())
            total_parts_price = 0
            part_ids = appointment['pr_id']
            for part in part_ids:
                temp_id = part
                db_part = db.collection('parts').document(temp_id).get().to_dict()
                total_parts_price += int(db_part['price'])

            if len(final_data) > 0:
                is_exist = False
                for final in final_data:
                    if final['date'] == appointment_date:
                        print()
                        final['sale'] += total_parts_price
                        is_exist = True
                        break
                if not is_exist:
                    final_data.append({'date': appointment_date, 'sale': total_parts_price})
            else:
                final_data.append({'date': appointment_date, 'sale': total_parts_price})

        return jsonify(final_data)


# -------------------------------- total services sale  -----------------------------
@app.route('/serviceRevenue', methods=['GET'])
def totalServiceRevenue():
    if request.method == 'GET':
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        start_date = time.mktime(datetime.strptime(start_date, "%Y-%m-%d").timetuple())
        end_date = time.mktime(datetime.strptime(end_date, "%Y-%m-%d").timetuple())

        final_data = []
        appointments = completedinframe(start_date, end_date)

        for appointment in appointments:
            appointment_date = appointment['appoint_time']
            appointment_date = str(appointment_date.date())
            total_service_price = 0
            service_id = appointment['sr_id']
            service_id = service_id 
            db_service = db.collection('services').document(service_id).get().to_dict()
            if db_service is not None:
                total_service_price += int(db_service['price'])

                if len(final_data) > 0:
                    is_exist = False
                    for final in final_data:
                        if final['date'] == appointment_date:
                            final['sale'] += total_service_price
                            is_exist = True
                            break
                    if not is_exist:
                        final_data.append({'date': appointment_date, 'sale': total_service_price})
                else:
                    final_data.append({'date': appointment_date, 'sale': total_service_price})

        return jsonify(final_data)


# -------------------------------- Top Selling Data  -----------------------------
@app.route('/topSelling', methods=['GET'])
def topSellingData():
    if request.method == 'GET':
        parts_data = []
        services_data = []
        parts = db.collection('parts').order_by("part_sold",direction=firestore.Query.DESCENDING).limit(3).get()
        for part in parts:
            parts_data.append(part.to_dict())

        services = db.collection('services').order_by("service_avail",direction=firestore.Query.DESCENDING).limit(3).get()
        for service in services:
            services_data.append(service.to_dict())

        dic = {
            "parts": parts_data,
            "services": services_data
        }
        return jsonify(dic)

# -------------------------- Customer APIS -----------------------------------
@app.route('/customer', methods=['GET', 'POST', 'PUT', 'DELETE'])
def customer():    
    if request.method == 'POST':
        data = request.get_json()
        users={}
        ct = datetime.now(timezone.utc)
        data['created_at'] = ct
        db.collection('customer').document(data['phone']).set(data)
        users['name']=data['name']
        users['password']=data['password']
        users['phone']=data['phone']
        users['user_type']='customer'
        db.collection('users').document(users['phone']).set(users)
        return jsonify({'Response': 'customer added sucessfully'})

    elif request.method == 'PUT':
        data = request.get_json()
        db.collection('customer').document(data['phone']).update(data)
        return jsonify({'Response': 'updated successfully'})

# ------------------- customer History---------------------------
@app.route('/customerCompletedAppointments', methods=['GET'])
def customerCompletedAppointments():
    if request.method == 'GET':
        id = request.args.get('id')
        results = db.collection('sales').where('customer_id','==',id).order_by("appoint_time",direction=firestore.Query.DESCENDING).get()
        data = []
        for result in results:
            temp = result.to_dict()
            temp.pop('location', None)
            if "status" in temp.keys():
                all_status = temp['status']
                if "completed" in all_status.keys():
                    data.append(temp)
        return jsonify(data)

# ------------------------- customer live appointments---------------------------
@app.route('/customerPendingAppointments', methods=['GET'])
def customerPendingAppointments():
    if request.method == 'GET':
        id = request.args.get('id')
        results = db.collection('appointments').where('customer_id','==',id).order_by("appoint_time",direction=firestore.Query.DESCENDING).get()
        data = []
        for result in results:
            temp = result.to_dict()
            temp.pop('location', None)
            if "status" in temp.keys():
                all_status = temp['status']
                if "completed" not in all_status.keys():
                    data.append(temp)
            else:
                data.append(temp)
        return jsonify(data)


# @app.route('/customerJobs/<string:id>', methods=['GET'])
# def customerJobs(id):
#     if request.method == 'GET':
#         result = db.collection('sales').where('customer_id','==',id).order_by("appoint_time",direction=firestore.Query.DESCENDING).get()
#         data = []
#         for r in result:
#             temp = r.to_dict()
#             temp.pop('location')
#             data.append(temp)
#         return jsonify(data)


#this function will receive table name whose data you wish to use
def getData(tableName): #this will return the desired Data in array from where the appoints data can be accessed
    data = db.collection(str(tableName)).get()
    list = []
    for d in data:
        a = d.to_dict()
        a['id'] = d.id
        try:
            a.pop('location')
        except KeyError:
            pass

        list.append(a)
    return list



#To view data in sequence wise, apply loop
'''---------------------------------------------------------------------------------'''


#This function will return a list (array) which contains all those appointments which are un-assigned along with all corresponding appointment details
def seeUnAssignedJobs():
    temp = []
    appointment_data = getData("appointments")
    for data in appointment_data:
        try:
            a = data['status']['assigned']
        except KeyError:
            temp.append(data)
    return temp

#assigned = True and no in-progress
#Will give list whihc contains all the pending jobs along details
def seeAllPendingJobs():
    temp = []
    appointment_table = getData("appointments")
    for data in appointment_table:
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

def completedinframe(start,end):
    start_date = datetime.fromtimestamp(start)
    end_date = datetime.fromtimestamp(end)
    ab = db.collection('appointments').where('appoint_time','>',start_date).where('appoint_time','<=',end_date).get()
    l2 = []
    for a in ab:
        res = a.to_dict()
        if 'status' in res.keys():
            statuses = res['status']
            if 'completed' in statuses.keys():
                if statuses['completed'] != "" and statuses['completed'] is not None:
                    res.pop('location')
                    l2.append(res)

    return l2


def completedJobsWithNames():
    completedjobs = seeAllCompletedJobs()
    pr_id=''
    temp = []

    for job in completedjobs:
        cusID = job['customer_id']
        empID = job['employee_id']
        sr_id = job['sr_id']
        pr_id = job['pr_id'] #this will sometimes return array of having multiple ids for different parts
        count=1

        for i in range(len(pr_id)):
            temp_id = pr_id[i]
            

            parts = db.collection('parts').document(temp_id).get().to_dict()

            job['part '+str(count)+'_name'] = parts['name']
            job['part '+str(count)+'_price'] = parts['price']
            count+=1

        temp_id = sr_id 

        services = db.collection('services').document(temp_id).get().to_dict()
        if services is not None:
            job['service_name'] = services['name']
            job['service_price'] = services['price']

        customer = db.collection('customer').document(cusID.strip()).get().to_dict()
        if customer is not None:
            job['customer_name'] = customer['name']
        else:
            job['customer_name'] = ""

        employee = db.collection('employee').document(empID.strip()).get().to_dict()
        if employee is not None:
            job['employee_name'] = employee['name']
        else:
            job['employee_name'] = ""
        temp.append(job)

    return temp



@app.route('/historicPartSale', methods=['GET'])
def historicPartsSale():
    if request.method == 'GET':
        response = previousPartSale()
        return jsonify(response)


@app.route('/futurePartSale', methods=['GET'])
def futurePartsSale():
    if request.method == 'GET':
        response = futurePartSale()
        return jsonify(response)


@app.route('/historicServicesSale', methods=['GET'])
def historicServiceSale():
    if request.method == 'GET':
        response = previousServicesSale()
        return jsonify(response)


@app.route('/futureServicesSale', methods=['GET'])
def futureServiceSale():
    if request.method == 'GET':
        response = futureServicesSale()
        return jsonify(response)

@app.route('/serviceDonutChart',methods=["GET"])
def serviceDonutChart(): 
    home , garage= v.serv_category()
    data = {'labels': ['Home', 'Garage'],'datasets': [{'label': 'Services','data': [home, garage],'backgroundColor': ['rgba(255, 99, 132)','rgba(54, 162, 235)'],'borderWidth': 1}]} 
    if request.method == 'GET':
        response = data
        return jsonify(response)
    else:
        return jsonify({'message':request.method +"is not allowed on this route"})

if __name__=='__main__':
    app.run(debug=TRUE)