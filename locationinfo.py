# locationinfo.py for implementing a city guide webapp
#
# Maurice Kingma
#
#
# python program for retrieving location info stadsgids.mauricekingma.nl

import requests
import os
from models import Recommendation
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_location_link_information(place_id):
    details = {}
    # google places api request for location
    res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": place_id, "fields": "name,formatted_address,photo,opening_hours,price_level,rating,place_id,types", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})
    if res.status_code == 200:
        data = res.json()
        details["name"] = data["result"]["name"]
        if "rating" in data["result"]:
            details["rating"] = data["result"]["rating"]
        details["place_id"] = data["result"]["place_id"]
        if "price_level" in data["result"]:
            details["price_level"] = data["result"]["price_level"] * "€"
        details["formatted_address"] = data["result"]["formatted_address"].split(",")
        if "open_now" in data["result"]["opening_hours"]:
            if data["result"]["opening_hours"]["open_now"]:
                details["opening_hours"] = "Nu open"
            else:
                details["opening_hours"] = "Gesloten"
        else:
            details["opening_hours"] = ""

        if "photos" in data["result"]:

            # google places photo api request for thumbnail
            photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "250", "photoreference": data["result"]["photos"][0]["photo_reference"]})
            if photo.status_code == 200:
                details["photos"] = photo.url
            else:
                details["photos"] = None
        details["types"] = data["result"]["types"]
    recommendation = Recommendation.query.filter_by(place_id=place_id).first()
    if recommendation:
        details["recommended"] = True
        details["types"] = recommendation.type.replace("}", "").replace("{", "").split(",")
        details["price_level"] = recommendation.price_level * "€"
        if recommendation.visible:
            details["visible"] = True
    else:
        details["recommended"] = False

    return details

def get_photo_url(reference):
    # google places photo api request for thumbnail
    photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "125", "photoreference": reference})
    if photo.status_code == 200:
        return photo.url
    else:
        return None
