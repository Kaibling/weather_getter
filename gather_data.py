import requests
import json
import logging
from transmission import send_metrics,send_future_metrics

units = dict()
units["temperature"] = "Celsius"
units["humidity"] = "%"
units["feelslike"] = "Celsius"

def save_btc():
    external_source = "kraken-btc"
    url = "https://api.kraken.com/0/public/Depth?pair=xbteur&count=1"
    logging.info("Start gathering: {}".format(external_source))
    result = requests.get(url)
    market = json.loads(result.content)["result"]["XXBTZEUR"]["asks"][0]
    send_future_metrics("btc",str(market[0]),"EUR",external_source,str(market[2])+"000000000")
    logging.info("Finished: {}".format(external_source))


def save_gold_price():
    external_source = "forex-gold"
    url = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/EUR"
    logging.info("Start gathering: {}".format(external_source))
    result = requests.get(url)
    market = json.loads(result.content)[0]

    timestamp = ""
    price = -1
    for market_type in market["spreadProfilePrices"]:
        if market_type["spreadProfile"] == "Standard":
            timestamp = str(market["ts"])
            price = market_type["bid"]  
    send_future_metrics("gold",price,"EUR",external_source,timestamp+"000000")
    logging.info("Finished: {}".format(external_source))

def gather_weatherstack_data(city,apikey):
    weatherstack_url = "http://api.weatherstack.com/current?access_key="+apikey+"&query="+ city
    external_source = "weatherstack"
    logging.info("Start gathering: {}".format(external_source))

    result = requests.get(weatherstack_url)
    if result.status_code != 200:
        print("request not successful",weatherstack_url)
        return

    current_weather = json.loads(result.content)
    temperature = current_weather["current"]["temperature"]
    humidity = current_weather["current"]["humidity"]
    feels_like = current_weather["current"]["feelslike"]

    send_metrics("temperature",temperature,units["temperature"],external_source)
    send_metrics("humidity",humidity,units["humidity"],external_source)
    send_metrics("feelslike",feels_like,units["feelslike"],external_source)
    logging.info("Finished: {}".format(external_source))

def gather_openweathermap_data(city,apikey):
    external_source = "openweathermap"
    url = "http://api.openweathermap.org/data/2.5/weather?q="+ city + "&appid=" + apikey + "&units=metric"
    logging.info("Start gathering: {}".format(external_source))
    
    result = requests.get(url)
    if result.status_code != 200:
        print("request not successful",url)
        print(result.content)
        return
    
    current_weather = json.loads(result.content)
    temperature = current_weather["main"]["temp"]
    humidity = current_weather["main"]["humidity"]
    feels_like = current_weather["main"]["feels_like"]

    send_metrics("temperature",temperature,units["temperature"],external_source)
    send_metrics("humidity",humidity,units["humidity"],external_source)
    send_metrics("feelslike",feels_like,units["feelslike"],external_source)
    logging.info("Finished: {}".format(external_source))

def forecast(city,apikey):
    external_source = "openweathermap_forcast"
    lat=47.0708678
    lon=15.4382786
    url = "http://api.openweathermap.org/data/2.5/onecall?lat="+str(lat)+"&lon="+str(lon)+"&appid="+ apikey + "&units=metric&exclude=minutely,daily"
    logging.info("Start gathering: {}".format(external_source))
    
    result = requests.get(url)
    if result.status_code != 200:
        print("request not successful",url)
        print(result.content)
        return

    weatherdata = json.loads(result.content)
    for day in weatherdata["hourly"]:
        timestamp = str(day["dt"])+"000000000"
        temperature = day["temp"]
        humidity = day["humidity"]
        feels_like = day["feels_like"]
            
        send_future_metrics("temperature",temperature,units["temperature"],external_source,timestamp)
        send_future_metrics("humidity",humidity,units["humidity"],external_source,timestamp)
        send_future_metrics("feelslike",feels_like,units["feelslike"],external_source,timestamp)
    logging.info("Finished: {}".format(external_source))
