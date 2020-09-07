#imports used in file creation
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import MySQLdb 
import json
import re
from influxdb import InfluxDBClient
from flask import Flask
from flask_influxdb import InfluxDB
import pandas as pd
import numpy as np
import matlab
import matlab.engine
import pygal
import jinja2
from jinja2 import Environment, PackageLoader, select_autoescape

#!!INFO ON SCRIPT!! 
#Connecting an SQL and NOSQL database togeather for information
#Connecting through the use of flask to send and recieve information from matlab
#Creating an html webpage in which to display information from two databases and information from matlab
#Chartjs to show ECG data from matlab in json format
#table format to display through the use of monitors the patient information and current bpm and changes

#connection to both influc and sql databases
DatabaseName = "yourDatabaseName"
conn = MySQLdb.connect(host='hostname', user='username', password='password', database='SQLdatabasename') 
client = InfluxDBClient("hostname", "portnumber", database = DatabaseName)
eng = matlab.engine.connect_matlab('matlabname') #alternating name on share
app = Flask(__name__)
influx_db = InfluxDB(app=app)
#api = Api(app)
CORS(app)

@app.route('/matlab',methods=['GET'])     
def matlabdata():
   influxquery = ("SELECT ECGRate, PatientBPM, idM, Monitor, Location  FROM heartrate")
   pd.set_option('display.max_rows', 10000)
   dfl = pd.DataFrame(client.query(influxquery).get_points(measurement='heartrate'))
   return (str(dfl))

@app.route('/matlabcsv',methods=['GET'])  #backup creation of csv file   
def matlabcsvcreate():
   influxquery = ("SELECT Monitor, Location, ECGRate, PatientBPM FROM heartrate")
   dfl = pd.DataFrame(client.query(influxquery).get_points())
   jsoncsv = dfl.to_csv(r'')
   return (jsoncsv)

@app.route('/mdreturn', methods=['GET'])
def data():
   ecgprocessing = eng.fileprocess(1,1)
   jsondata = jsonify(ecgprocessing)
   datajson = "{\"values\":" + str(ecgprocessing) + "}"
   return(datajson)

@app.route('/',methods=['GET'])     
def Vitals():
  #read_sql through connection
  sqlquery = pd.read_sql("SELECT Firstname, Lastname, Allergies, Ward, Monitor from patient", con=conn)
  influxquery = "SELECT Monitor,PatientBPM FROM heartrate"
  pd.set_option('display.max_rows', 1)
  sq = pd.DataFrame(sqlquery) #create sql query into a dataframe
  dfl = pd.DataFrame(client.query(influxquery).get_points())  # make influx query a dataframe
  MERGE = pd.merge(sq,dfl, on="Monitor") # merge two databases on one using dataframes
  Tailend = MERGE.tail(4)

  #create a html page for the table holding a refresh rate and table design using a function 
  # to check over the table, checking the patientbpm and adding a colour on the value
  # to help identify problems such as high value on heart rate
  # using style in order to create a clean table issue due to calling css file via href use of inline was chosen

  #$(function() {{
  # }})
  #<meta http-equiv="refresh" content="10"> 
  htmldesign = '''
  <html>
    <meta charset=utf-8>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <head>
    <script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
     <!--Load the AJAX API-->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.min.js'></script> 
    <head>
       <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    </head> 
    <style> 
    table, th, td {{font-family: arial, sans-serif;border-collapse: collapse; table-layout: fixed; width: 155px;}}
    tr:hover td {{background-color: #ffff99;}}
    th, td {{border: 4px solid #dddddd; text-align: left; padding: 3px;  background-color:#D3D3D3; color: black; text-align: center;}}
    body {{background-color: #FFFFFF; padding: 14px; text-align: center;}}
    w {{width: 500px;}}
 
      .column {{
      float: left;
      width: 50%;
      padding: 3px;
      }}
      .ul {{
      list-style-type: none;
      margin: 0;
      padding: 0;
      overflow: hidden;
      text-align: center;
      float: left;
      color: white;
      }}
    
    </style>
     </head>
    <body>

    <h1 text-align: center> Patient Vitals</h1>

    <div class="column">
        <p id="ctb"></p>
        <button type="hidden" onclick="ctree()">Prediction Accuracy Class Tree</button>
        <canvas class="btn btn-light" id="container" style="width: 100%; height: 500" style="text-align:left;" ></canvas>
    </div>

    <div class="column">
        <p id="knt"></p>
        <button type="hidden" onclick="knn()">Prediction Accuracy KNN</button>
        <canvas class="btn btn-light" id="container2" style="width: 100%; height: 500"></canvas>
    </div>

      {table}

    <script>
      function ctree() {{
          $.ajax({{
             type: 'GET',
             url: "url return",
             dataType: "json",
             success: function(data){{
             var ct = data.values.cTree; 
             document.getElementById("ctb").innerHTML = ct;
            }}     
        }})
      }}
         
      function knn() {{
              $.ajax({{
             type: 'GET',
             url: "url return",
             dataType: "json",
             success: function(data){{
             var kn = data.values.KTree;
             document.getElementById("knt").innerHTML = kn;
            }}     
        }})
      }}
             $.ajax({{
             type: 'GET',
             url: "url return",
             dataType: "json",
             success: function(data){{
                console.log(data);
                var realTime = new Date();
                var datag = data.values.MonitorOne;
                var datag2 = data.values.MonitorTwo;
                var t = data.values.timeOne;
                var t2 = data.values.time2;  
                     var maxpoints = 250;
                     var maxpointscounter = 0;
                     if(maxpointscounter >= maxpoints){{
                     graph.data.labels.shift();
                     graph.data.datasets[0].data.shift();
                     graph2.data.labels.shift();
                     graph2.data.datasets[0].data.shift();
                     
                  }} else {{
                     maxpointscounter++;
                  }}   
               var ctx = document.getElementById("container").getContext('2d');
               var ctx2 = document.getElementById("container2").getContext('2d');
               var graph = new Chart(ctx, {{
                        type: 'line',
                        data:{{
                           labels:t,
                           datasets:[{{
                              label: "ECG HEART RATE Monitor One",
                              borderColor: "#0000FF",
                              borderDash: [5, 1],
                              backgroundColor: "#e755ba",
					               fill: false,
                              data: datag,
                           }}]
                        }}
                     }})
               var graph2 = new Chart(ctx2, {{
                        type: 'line',
                        data:{{
                           labels:t2,
                           datasets:[{{
                              label: "ECG HEART RATE Monitor Two",
                              borderColor: "#0000FF",
                              borderDash: [5, 1],
                              backgroundColor: "#e755ba",
					               fill: false,
                              data: datag2,
                           }}]
                        }}
                     }})
                }}     
            }})
         
      var checktable =  document.getElementById("table").getElementsByTagName("td");;
         for(i = 0; i < checktable.length; i++){{
            if(checktable[i].innerHTML >= 49 && checktable[i].innerHTML <= 55){{
               checktable[i].style.backgroundColor = "light-blue";
            }} else if(checktable[i].innerHTML >= 56 && checktable[i].innerHTML <= 61 ) {{
               checktable[i].style.backgroundColor = "blue";
            }} else if(checktable[i].innerHTML >= 62 && checktable[i].innerHTML <= 69) {{
               checktable[i].style.backgroundColor = "green";
            }} else if(checktable[i].innerHTML >= 70 && checktable[i].innerHTML <= 73) {{
               checktable[i].style.backgroundColor = "yellow";
            }} else if(checktable[i].innerHTML >= 74 && checktable[i].innerHTML <= 79) {{
               checktable[i].style.backgroundColor = "orange";
            }} else if(checktable[i].innerHTML >= 80 && checktable[i].innerHTML <= 500) {{
               checktable[i].style.backgroundColor = "red";
            }} else if(checktable[i].innerHTML <= 45) {{
               checktable[i].style.backgroundColor = "red";             
            }} 
         }}
    </script>
    <footer>
        <p style="text-align:center; color: white; background-color: black">© 2020 Nathan Kirk (Ulster University Jordanstown)</p>
    </footer>
    </body>
  </html>
  '''

  #send the merged pandas dataframe to a html page through use of to_html and display on web
  htmlframe  = htmldesign.format(table=Tailend.to_html(classes='table table-hover', escape=True, max_rows=20, table_id="table"))
  return htmlframe
#using bootstrap table creation
#<link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">
if __name__ == '__main__':
        app.run(debug=True)  