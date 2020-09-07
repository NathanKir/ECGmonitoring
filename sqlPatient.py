from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import MySQLdb 
import json
import re
#!!INFO ON SCRIPT!! 
#Connection to sql database in order to inserting, delete, retrieving and update patient information.
#This database is strictly for paitent information!
#Through the use of flask the creation of url links allows for methods of POST and GET method of sending and retrieving.
#All information is escaped to remove the use of sql injection making sure that information is secure and protected.

conn = MySQLdb.connect(host='hostname', user='username', password='password', database='yourSQLdbname') 
app = Flask(__name__)
#api = Api(app)
CORS(app)

@app.route('/')
def defaultResponse():
       return "Working" 


@app.route('/insertPatient', methods = ['POST'])
def insertPatientRoutine():

       for entry in request.json:  
              cursor = conn.cursor()
              #!!Unsecure method!!
              #sql2 = "INSERT INTO patient (Firstname, LastName, PatientNumber, Birthday, Allergies, PhoneNumber, Ward, Monitor) 
              # VALUES ('" + entry["FirstName"] +"', '"+ entry["LastName"] +"',
              #  "+ entry["PatientNumber"] +", '"+ entry["Birthday"] +"', '"+ entry["Allergies"] +"', 
              # '"+ entry["PhoneNumber"] +"', '"+ entry["Ward"] +"', '"+ entry["Monitor"]+"')"
              
              #!!Secure method!!
              sql2 = "INSERT INTO patient (Firstname, LastName, PatientNumber, Birthday, Allergies, PhoneNumber, Ward , Monitor) VALUES (%(Firstname)s, %(LastName)s, %(PatientNumber)s, %(Birthday)s, %(Allergies)s, %(PhoneNumber)s, %(Ward)s, %(Monitor)s)"
              cursor.execute(sql2
              
              , {
            'Firstname': entry["FirstName"],
            'LastName': entry["LastName"],
            'PatientNumber': entry["PatientNumber"],
            'Birthday': entry["Birthday"],
            'Allergies': entry["Allergies"],
            'PhoneNumber': entry["PhoneNumber"],
            'Ward': entry["Ward"],
            'Monitor': entry["Monitor"]

              })
            
              conn.commit()

       return "Done"


@app.route('/dataPatient', methods = ['GET'])
def selectall():
    cursor = conn.cursor() # connect to database
    cursor.execute("SELECT * from patient;") # This line performs query and returns json result
    retunall = cursor.fetchall()
    return (str(retunall))
        


@app.route('/deletePatient', methods = ['POST'])
def delete():
       for entry in request.json: 
              cursor = conn.cursor()
              #!!Unsecure method!!
              #sql = "DELETE FROM patient WHERE PatientNumber = " + entry["PatientNumber"] + "" # unsafe sql injection
              
              #!!Secure method!!
              sql = "DELETE FROM patient WHERE PatientNumber = %(PatientNumber)s"
              cursor.execute(sql
                 , {
            'PatientNumber': entry["PatientNumber"]
                 })
              conn.commit()
       return "Done"      


@app.route('/updatePatient',methods=['POST'])
def update():
      
       for entry in request.json: 
              cursor = conn.cursor()
              #!!Unsecure method!!
              #sql2 = "UPDATE patient SET Firstname= '" + entry["Firstname"] + "' LastName= '" + entry["LastName"] + "' PatientNumber= " + entry["PatientNumber"] + " Birthday= '" + entry["Birthday"] + "' Allergies= '" + entry["Allergies"] + "' PhoneNumber= '" + entry["PhoneNumber"] + "' Ward= '" + entry["Ward"] + "' Monitor= '" + entry["Monitor"] + "'"
              
              #!!Secure method!!
              sql2 = "UPDATE patient SET Firstname = %(Firstname)s, LastName= %(LastName)s, PatientNumber = %(PatientNumber)s, Birthday =%(Birthday)s, Allergies =%(Allergies)s, PhoneNumber =%(PhoneNumber)s, Ward =%(Ward)s, Monitor = %(Monitor)s WHERE idpatient = %(idpatient)s"
              cursor.execute(sql2  
              , {
            'idpatient': str(entry["idpatient"]),
            'Firstname': entry["FirstName"],
            'LastName': entry["LastName"],
            'PatientNumber': entry["PatientNumber"],
            'Birthday': entry["Birthday"],
            'Allergies': entry["Allergies"],
            'PhoneNumber': entry["PhoneNumber"],
            'Ward': entry["Ward"],
            'Monitor': entry["Monitor"]
            
              })
              conn.commit()
       return "Done"

if __name__ == "__main__":
    app.run(debug=True)
