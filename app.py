import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import timedelta
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Available API Routes for Surfs Up"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Last Year of Percipitation Data"""
    session = Session(engine)
    #find last date in database from Measurements 
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    #convert last date string to date

    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")

    #calculate date one year after last date using timedelta datetime function
    date_year_ago = last_date - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_year_ago).all()
    return jsonify(last_year_data)


@app.route("/api/v1.0/stations")
def stations():
    """List of Weather Stations"""
    session = Session(engine)

    # select station names from stations table
    stations = session.query(Station.station).all()

    # Return JSONIFY List of Stations
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Temperature Observations for Top Station for Last Year"""
    
    session = Session(engine)
    
    #find last date in database from Measurements 
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    #convert last date string to date

    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")

    #calculate date one year after last date using timedelta datetime function
    date_year_ago = last_date - timedelta(days=365)
    # List the stations and the counts in descending order.
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Create top station variable from tuple
    top_station = (active_stations[0])
    top_station = (top_station[0])
    # Using the station id from the previous query, calculate the lowest temperature recorded, 
    # highest temperature recorded, and average temperature of the most active station?
    session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.station == top_station).all()
    # Choose the station with the highest number of temperature observations.
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    highest_obs = session.query(Measurement.tobs).\
    filter(Measurement.station == top_station).filter(Measurement.date >= date_year_ago).all()
    return jsonify(highest_obs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)

    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        trip_temp = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(trip_temp))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    trip_temp = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
  
    return jsonify(trip_temp)

if __name__ == '__main__':
    app.run()