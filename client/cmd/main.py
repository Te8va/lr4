import json

from flask import Flask, request, jsonify
import requests, datetime
import dateutil.parser as datetime_parser
from geopy.geocoders import Nominatim
from os import getenv

import grpc

import opis_pb2, opis_pb2_grpc
import opis_pb2_grpc

from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

geolocation = Nominatim(user_agent="Teva")


@app.route("/v1/forecast/")
def get_forecast():
    if request.args.get("dt") is None:
        return "Invalid parameter: Datetime parameter is empty"
     
    try:
        dt = datetime_parser.parse(request.args.get("dt"))
    except datetime_parser._parser.ParserError:
        return "Invalid parameter: Datetime parameter format is incorrerct. Try something like 2023-03-17T11"

    city = request.args.get("city")
    if city is None:
        return "Invalid parameter: City parameter is empty"

    coord = geolocation.geocode(city)
    if coord is None:
        return "Invalid parameter: City parameter does not represent city name"

    get_param ={
        "latitude": coord.latitude,
        "longitude": coord.longitude,
        "start_date": dt.date(),
        "end_date": dt.date(),
        "hourly": "temperature_2m"
    }
    
    if check_username():
       response = requests.get(getenv("API"), params=get_param, timeout=30)
       if response.status_code != 200:
            return "Invalid request: Something went wrong while getting response from weather API"
       
       json_response = response.json()
       
       return jsonify({"city": city, "unit": "celsius", "temperature": json_response["hourly"]["temperature_2m"][dt.hour]})

    return "Invalid username: User not found in table", 403

@app.route("/v1/current/")
def get_current_temperature():
    city = request.args.get("city")
    if city is None:
        return "Invalid parameter: City parameter is empty"

    coord = geolocation.geocode(city)
    if coord is None:
        return "Invalid parameter:City parameter does not represent city name"
    get_param ={
        "latitude": coord.latitude,
        "longitude": coord.longitude,
        "current_weather": "true"
    }

    if check_username():
        response = requests.get(getenv("API"), params=get_param, timeout=30)
        if response.status_code != 200:
            return "Invalid request: Something went wrong while getting response from weather API"

        json_response = response.json()

        return jsonify({"city": city, "unit": "celsius", "temperature": json_response["current_weather"]["temperature"]})
    
    return "Invalid username: User not found in table", 403

def check_username():
    if "Own-Auth-UserName" in request.headers:
        if request.headers["Own-Auth-UserName"] is None:
            return "Invalid header: Username header is empty"

        with grpc.insecure_channel('localhost:9000') as channel:
            stub = opis_pb2_grpc.AuthStub(channel)

            response = stub.CheckAuth(opis_pb2.AuthRequest(username=request.headers["Own-Auth-UserName"]))

            if response.exists:
                return True
    return False


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True, port=getenv("PORT"))