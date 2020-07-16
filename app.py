from flask import Flask, Response
import requests
import json
import os

from expiringdict import ExpiringDict

cache = ExpiringDict(max_len=100, max_age_seconds=60)


app = Flask(__name__)
apiKey = os.getenv("API_TOKEN")


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
    train_info = {}
    train_info["id"] = all_info["train_num"]
    train_info["summary"] = all_info["details"]["summary"]
    train_info["cars"] = all_info["consist"]["Cars"]
    return train_info


@app.route("/")
def default():
    return "Default"


@app.route("/trains-approaching/<station_id>/")
def show_trains_approaching_station(station_id):
    train_info = get_trains_approaching(station_id).json()
    # add carinfo for each one of the trains
    # iterate through and get "TRAINS": [
    #   "SCHED":
    #   "TRAIN_ID"
    trains_list = train_info["TRAINS"]
    details_list = []
    for train_obj in trains_list:
        train_id = train_obj["TRAIN_ID"]
        detail = cache.get(train_obj["TRAIN_ID"])
        if detail is None:
            detail = get_train_info(train_id, station_id)
            cache[train_id] = detail
        details_list.append(detail)
    train_info["details"] = details_list
    return Response(json.dumps(train_info), mimetype="application/json")


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
    return Response(
        json.dumps(get_train_info(train_number, station_id)),
        mimetype="application/json",
    )


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
