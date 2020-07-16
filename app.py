from flask import Flask, Response
import requests
import json
import os

app = Flask(__name__)
apiKey = os.getenv("API_TOKEN") or "9de8f3b1-1701-4229-8ebc-346914043f4a"


def get_trains_approaching(station_id):
    return requests.get(
        f"https://mnorthstg.prod.acquia-sites.com/wse/Mymnr/v5/api/trains/{station_id}/{apiKey}/"
    )


def get_all_stations():
    return requests.get(
        f"https://mnorthstg.prod.acquia-sites.com/wse/Mymnr/v5/api/stations/{apiKey}/"
    )


def get_train_info(train_number, station_id):
    all_info = requests.get(
        f"https://mnorthstg.prod.acquia-sites.com/wse/Mymnr/v5/api/train/{train_number}/{station_id}/{apiKey}/"
    ).json()
    train_info = []
    train_info.append(all_info["details"]["summary"])
    train_info.append(all_info["consist"]["Cars"])
    return train_info

@app.route("/")
def default():
    return "Default"


@app.route("/trains-approaching/<station_id>/")
def show_trains_approaching_station(station_id):
    train_info = get_trains_approaching(station_id)
    # add carinfo for each one of the trains
    # iterate through and get "TRAINS": [
    #   "SCHED":
    #   "TRAIN_ID"
    trains_list = train_info.json()["TRAINS"]

    return Response(train_info.text, mimetype="application/json")


# "Branch": "Waterbury",
# "Code": "168",
# "Name": "Ansonia",
# "Latitude": 41.34415,
# "Longitude": -73.0799255,
# "Type": "S",
# "Branch_Id": 6,
# "Location_Index": 162,
# "Location_Id": 168


@app.route("/all-stations/")
def show_all_stations():
    all_trains = get_all_stations()
    station_names = []
    for listitem in all_trains.json():
        station_item = {
            "name": listitem["Name"],
            "lat": listitem["Latitude"],
            "long": listitem["Longitude"],
            "station_id": listitem["Location_Id"],
        }
        station_names.append(station_item)
    return Response(json.dumps(station_names), mimetype="application/json")


@app.route("/current-train-info/<train_number>/<station_id>/")
def show_train_info(train_number, station_id):
    return Response(json.dumps(get_train_info(train_number, station_id)), mimetype="application/json")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

"""
{
  "LOC": "37",
  "TIME": "07/15/2020 23:13:56",
  "TRAINS": [
    {
      "SCHED": "7/15/2020 11:40:00 PM",
      "TRAIN_ID": "8876",
      "DEST": "33",
      "STOPS": null,
      "DIR": "I",
      "TRACK": "2",
      "ETA": "7/15/2020 11:40:00 PM",
      "CD": 1563,
      "SERVICE_STATUS": "Delayed"
    },
    {
      "SCHED": "7/15/2020 11:47:00 PM",
      "TRAIN_ID": "8867",
      "DEST": "51",
      "STOPS": null,
      "DIR": "O",
      "TRACK": "1",
      "ETA": "7/15/2020 11:47:00 PM",
      "CD": 1983,
      "SERVICE_STATUS": "On Time"
    },
    {
      "SCHED": "7/16/2020 12:34:00 AM",
      "TRAIN_ID": "8898",
      "DEST": "33",
      "STOPS": null,
      "DIR": "I",
      "TRACK": "2",
      "ETA": "7/16/2020 12:34:00 AM",
      "CD": 4803,
      "SERVICE_STATUS": "On Time"
    }
  ]
}
"""
