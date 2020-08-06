from difflib import SequenceMatcher
from models import *
import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_parent_rec_from_double(place_id):
    double = Double.query.filter(Double.double_place_id.like(f"%{place_id}%")).first()
    if double:
        rec = Recommendation.query.filter_by(place_id=double.place_id).first()
        return rec
    return None

def get_info_parent_rec_from_double_if_sameRec(place_id):
    rec = get_parent_rec_from_double(place_id)
    if rec:
        for double in rec.doubles:
            doubleDict = ast.literal_eval(double.double_place_id)
            if doubleDict[place_id]:
                return rec
            else:
                return None
    return None

def get_double_place_ids(place_id):
    place_ids = []
    parentRec = get_parent_rec_from_double(place_id)

    # check if place id from function is from a parent or a child location
    if parentRec:
        place_ids.append(parentRec.place_id)
        for double in parentRec.doubles:
            doubleDict = ast.literal_eval(double.double_place_id)
            for key, value in doubleDict.items():
                if key != place_id:
                    place_ids.append(key)
    else:
        parentRec = Recommendation.query.filter_by(place_id=place_id).first()
        for double in parentRec.doubles:
            doubleDict = ast.literal_eval(double.double_place_id)
            for key, value in doubleDict.items():
                if key != place_id:
                    place_ids.append(key)
    return place_ids

def get_link_info_doubles(place_ids):
    doublesInfo = []
    for place_id in place_ids:

        # google places api request for location
        res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": place_id, "fields": "name,formatted_address", "language": "nl"})

        if res.status_code == 200:
            data = res.json()
            data["result"]["place_id"] = place_id
            doublesInfo.append(data)
    return doublesInfo
