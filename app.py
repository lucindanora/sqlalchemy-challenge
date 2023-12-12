# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
#####################################################

# Convert the query results from precipitation analysis to a dictionary
# using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for the last 12 months of precipitation data
    prev_year = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()

    # Create a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in prev_year}

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

########################################################

#Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
     stations_data = session.query(Station.station).all()
     out = [item for t in stations_data for item in t]
     return jsonify(out)

###########################################################

#Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station_id = 'USC00519281' 
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    most_recent_date_station = session.query(Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.station == most_active_station_id).all()
    out = [item for t in most_recent_date_station for item in t]
    
    #Return a JSON list of temperature observations for the previous year.
    
    return jsonify(out)

############################################################

@app.route("/api/v1.0/<start>")
def start(start):
    start_date = dt.datetime.strptime(start, '%Y%m%d')
    most_active_station = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()
    out = [item for t in most_active_station for item in t]
    return jsonify(out)

##############################################################

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    start_date = dt.datetime.strptime(start, '%Y%m%d')
    end_date = dt.datetime.strptime(end, '%Y%m%d')
    most_active_station = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date < end_date).all()
    out = [item for t in most_active_station for item in t]
    return jsonify(out)



if __name__ == '__main__':
    app.run(debug=True)

    session.close()