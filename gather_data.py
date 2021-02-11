#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import logging
from transmission import send_metrics,send_future_metrics,get_last_timestamp,send_custom_metrics
import time
import csv
import urllib3
from io import StringIO


units = dict()
units["temperature"] = "Celsius"
units["humidity"] = "%"
units["feelslike"] = "Celsius"

def save_corona_data():
    external_source = "covid19-dashboard"
    url = "https://covid19-dashboard.ages.at/data/CovidFaelle_Altersgruppe.csv"
    logging.info("Start gathering: {}".format(external_source))
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    try:
        requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    except AttributeError as err:
        logging.error(err)

    result = requests.get(url)
    if result.status_code != 200:
        logging.error("request not successful: {}:{} {}".format(url,result.status_code,result.content))
        return
    #content = str(result.content)
    #print(content)
    f = StringIO(result.content.decode("utf-8") )
    csv_reader = csv.reader(f, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            Altersgruppe = row[1]
            Bundesland =  row[2]
            AnzEinwohner = row[4]
            Geschlecht =  row[5]
            Anzahl =  row[6]
            data = "corona_stats_austria,agerange='"+ str(Altersgruppe) +"',country='"+Bundesland+"',inhabitants="+str(AnzEinwohner)+",sex='"+Geschlecht+"',amount="+str(Anzahl)
            #print(data)
            send_custom_metrics(data)
            line_count += 1
    print(f'Processed {line_count} lines.')
    exit()
    #try:
    #    
    #    market = json.loads(result.content)["result"]["XXBTZEUR"]["asks"][0]
    #    send_future_metrics("btc",str(market[0]),"EUR",external_source,str(market[2])+"000000000")
    #    logging.info("Finished: {}".format(external_source))
    #except Exception as err:
    #    logging.exception("{} {}".format(external_source,err))

def save_btc():
    external_source = "kraken-btc"
    url = "https://api.kraken.com/0/public/Depth?pair=xbteur&count=1"
    logging.info("Start gathering: {}".format(external_source))
    try:
        result = requests.get(url)
        if result.status_code != 200:
            logging.error("request not successful: {}:{} {}".format(url,result.status_code,result.content))
            return
    except Exception as err:
        logging.exception("{} {}".format(external_source,err))
    
    try:
        market = json.loads(result.content)["result"]["XXBTZEUR"]["asks"][0]
        send_future_metrics("btc",str(market[0]),"EUR",external_source,str(market[2])+"000000000")
        logging.info("Finished: {}".format(external_source))
    except Exception as err:
        logging.exception("{} {}".format(external_source,err))


def save_gold_price():
    external_source = "forex-gold"
    url = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/EUR"
    logging.info("Start gathering: {}".format(external_source))
    try:
        result = requests.get(url)
        if result.status_code != 200:
            logging.error("request not successful: {}:{} {}".format(url,result.status_code,result.content))
            return
        market = json.loads(result.content)[0]
        timestamp = ""
        price = -1
        for market_type in market["spreadProfilePrices"]:
            if market_type["spreadProfile"] == "Standard":
                timestamp = str(market["ts"])
                price = market_type["bid"]  
        send_future_metrics("gold",price,"EUR",external_source,timestamp+"000000")
        logging.info("Finished: {}".format(external_source))
    except Exception as err:
        logging.exception("{} {}".format(external_source,err))


def gather_weatherstack_data(city,apikey):
    weatherstack_url = "http://api.weatherstack.com/current?access_key="+apikey+"&query="+ city
    external_source = "weatherstack"
    logging.info("Start gathering: {}".format(external_source))


    try:
        result = requests.get(weatherstack_url)
        if result.status_code != 200:
            logging.error("request not successful: {}:{} {}".format(weatherstack_url,result.status_code,result.content))
            return
        current_weather = json.loads(result.content)
        temperature = current_weather["current"]["temperature"]
        humidity = current_weather["current"]["humidity"]
        feels_like = current_weather["current"]["feelslike"]

        send_metrics("temperature",temperature,units["temperature"],external_source)
        send_metrics("humidity",humidity,units["humidity"],external_source)
        send_metrics("feelslike",feels_like,units["feelslike"],external_source)
        logging.info("Finished: {}".format(external_source))
    except Exception as err:
        logging.exception("{} {}".format(external_source,err))

def gather_openweathermap_data(city,apikey):
    external_source = "openweathermap"
    url = "http://api.openweathermap.org/data/2.5/weather?q="+ city + "&appid=" + apikey + "&units=metric"
    logging.info("Start gathering: {}".format(external_source))
    

    try:
        result = requests.get(url)
        if result.status_code != 200:
            logging.error("request not successful: {}:{} {}".format(url,result.status_code,result.content))
            return
        current_weather = json.loads(result.content)
        temperature = current_weather["main"]["temp"]
        humidity = current_weather["main"]["humidity"]
        feels_like = current_weather["main"]["feels_like"]

        send_metrics("temperature",temperature,units["temperature"],external_source)
        send_metrics("humidity",humidity,units["humidity"],external_source)
        send_metrics("feelslike",feels_like,units["feelslike"],external_source)
        logging.info("Finished: {}".format(external_source))
    except Exception as err:
        logging.exception("{} {}".format(external_source,err))

def forecast(city,apikey):
    external_source = "openweathermap_forcast"
    lat=47.0708678
    lon=15.4382786
    url = "http://api.openweathermap.org/data/2.5/onecall?lat="+str(lat)+"&lon="+str(lon)+"&appid="+ apikey + "&units=metric&exclude=minutely,daily"

    try:
        result = get_last_timestamp(external_source,"temperature")
        result_json = json.loads(result)
        last_entry = result_json['results'][0]['series'][0]['values'][0][0]
        current_time = time.time_ns()
        onehour_ns_time = current_time + (3600 * 1000000000)
        if onehour_ns_time < last_entry:
            return
    except Exception as err:
        logging.exception("{} {}".format(external_source,err))
  
    logging.info("Start gathering: {}".format(external_source))
    


    try:
        result = requests.get(url)
        if result.status_code != 200:
            logging.error("request not successful: {}:{} {}".format(url,result.status_code,result.content))
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
    except Exception as err:
        logging.exception("{} {}".format(external_source,err))
