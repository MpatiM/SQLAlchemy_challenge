# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage - List all available api routes.
@app.route("/")

def home():
    return (
        f"<h1>Home Page: Hawaii Weather Analysis</h1>"

        f"<h2>Available Routes:</h2>"

        f"<h3>Precipitation Analysis</h3>"
        f"/api/v1.0/precipitation<br/>"
        
        "<br/>"
        f"<h3>Stations Analysis</h3>"
        f"/api/v1.0/stations<br/>"

        "<br/>"
        f"<h3>Temperature Analysis for most active station</h3>"
        f"/api/v1.0/tobs<br/>"

        "<br/>"
        f"<h3>By Specific Start Date</h3>"
        f"/api/v1.0/yyyy-mm-dd<br/>"

        "<br/>"
        f"<h3>By Specific Start & End Date</h3>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

# Precipitation Page
@app.route("/api/v1.0/precipitation")

def precipitation():
    session

    one_year_ago = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    one_year_ago = dt.date(one_year_ago.year, one_year_ago.month, one_year_ago.day)

    query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).order_by(measurement.date).all()

    session.close()
    
    precp_dict = dict(query)

    print(f"Precipitation: {precp_dict}")
    print("Out of Precipitation section.")
    return jsonify(precp_dict) 

# Stations Page
@app.route("/api/v1.0/stations")

def stations():
    session

    stations = session.query(station).all()

    session.close()

    # Convert results to a dictionary
    stations_list = []

    for station in stations:
        station_dict = {}
        station_dict['Station'] = station.station
        station_dict['Information'] = {
            "ID":station.id,
            "Name":station.name,
            "Latitude":station.latitude,
            "Longitude":station.longitude,
            "Elevation":station.elevation
        }
        stations_list.append(station_dict)
    
    # JSONify the list
    return jsonify(stations_list)

# TOBS Page
@app.route("/api/v1.0/tobs")

def tobs():
     session
    
     tobs_query = session.query(measurement.tobs).filter(measurement.station == stations_list[0][0]).filter(measurement.date >= one_year_ago).all()

     session.close()
    
     tobs_list = []
    
     for date, tobs in tobs_query:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["TOBS"] = tobs
         tobs_list.append(tobs_dict)

     return jsonify(tobs_list)


# Start Date Page
@app.route("/api/v1.0/<start>")

def Date1(start):
    # Convert start to date format
    try:
        # If the date given by the user contains "-" between Year, Month, Day - Remove the character
        if (start.__contains__("-")):
            start = start.replace("-","")
        
        start_date = dt.datetime.strptime(start, '%Y%m%d')

        session

        # Variables for reference to temperature calculations
        temp_min = func.min(Measurement.tobs)
        temp_max = func.max(Measurement.tobs)
        temp_avg = func.avg(Measurement.tobs)

        data_request = session.query(temp_min,temp_max,temp_avg).filter(measurement.date >= start_date).all()

        session.close()

        temp_list = []
        
        for temp_min, temp_max, temp_avg in data_request:
            temp_dict = {}
            temp_dict['From_Date'] = start
            temp_dict['Temp_Calcs'] = {
                "Min Temperature" : temp_min,
                "Max Temperature" : temp_max,
                "Avg Temperature" : round(temp_avg, 2)
            }
            temp_list.append(temp_dict)

        # JSONify the temp_data list
        return jsonify(temp_list)
    
    # Exception handle if date given is in the incorrect format
    except ValueError:
        return jsonify({"error": f"The specified date '{start}' is not in the correct format.",
                        "note": f"Place a date in the format: yyyy-mm-dd or yyyymmdd"}), 404


# Start Date and End Date Page
@app.route("/api/v1.0/<start>/<end>")
        
def Date2(start,end):
    # Convert start to date format
    try:
        # If the date given by the user contains "-" between Year, Month, Day - Remove the character
        if (start.__contains__("-")) or (end.__contains__("-")):
            start = start.replace("-","")
            end = end.replace("-","")

        start_date = dt.datetime.strptime(start, '%Y%m%d')
        end_date = dt.datetime.strptime(end, '%Y%m%d')

        # Check if the end date given is greater than the start date
        if (end_date > start_date):

            session

            # Variables for reference to temperature calculations
            temp_min = func.min(Measurement.tobs)
            temp_max = func.max(Measurement.tobs)
            temp_avg = func.avg(Measurement.tobs)

            data_request = session.query(temp_min,temp_max,temp_avg).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

            session.close()

            temp_list = []
            
            for temp_min, temp_max, temp_avg in data_request:
                temp_dict = {}
                temp_dict['From_Date'] = start
                temp_dict['To_Date'] = end
                temp_dict['Temp_Calcs'] = {
                    "Min Temperature" : temp_min,
                    "Max Temperature" : temp_max,
                    "Avg Temperature" : round(temp_avg, 2)
                }
                temp_list.append(temp_dict)

            # JSONify the temp_data list
            return jsonify(temp_list)
        
        # If the end date is less than start date, return an error and prompt for dates to be changed
        else:
            return jsonify({"error":f"The end date '{end}' can not be less than the start date '{start}'. Please adjust your date values."}), 404
    
    # Exception handle if date given is in the incorrect format
    except ValueError:
        return jsonify({"error": f"One of the specified dates '{start}' or '{end}' is not in the correct format.",
                        "note": f"Alter the dates to the format: yyyy-mm-dd or yyyymmdd"}), 404


if __name__ == '__main__':
    app.run(debug=False)
