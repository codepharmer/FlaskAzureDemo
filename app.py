from flask import Flask
import requests
import json
import os

app = Flask(__name__)
apiKey = os.getenv("API_TOKEN")

def get_trains_approaching(station_id):
    return requests.get(f"https://mnorthstg.prod.acquia-sites.com/wse/Mymnr/v5/api/trains/{station_id}/{apiKey}/")

def get_all_stations():
    return requests.get(f"https://mnorthstg.prod.acquia-sites.com/wse/Mymnr/v5/api/stations/{apiKey}/")

@app.route("/")
def default():
    return "Default"

@app.route("/trains_approaching/<station_id>")
def show_trains_approaching_station(station_id):
    train_info = get_trains_approaching(station_id)
    return train_info.json()

@app.route("/all_stations/")
def show_all_stations():
    all_trains =get_all_stations()
    station_names = []
    for listitem in all_trains.json():
        station_item = {
            "name": listitem["Name"],
            "lat": listitem["Latitude"],
            "long": listitem["Longitude"],
            "station_id": listitem["Location_Id"]
        }
# "Branch": "Waterbury",
#     "Code": "168",
#     "Name": "Ansonia",
#     "Latitude": 41.34415,
#     "Longitude": -73.0799255,
#     "Type": "S",
#     "Branch_Id": 6,
#     "Location_Index": 162,
#     "Location_Id": 168
#   },
        station_names.append(station_item)
    return json.dumps(station_names)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)