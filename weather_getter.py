import json
import requests
import os
import logging

def send_metrics(metric_type,external_data,unit,external_source):
    data = 'air_monitoring,external_source=' +external_source + ',measuretype='+metric_type+',unit='+unit+' value='+str(external_data)
    res = requests.post(url=influxdb_url,data=data)
    if res.status_code != 204:
        print("request not successful",influxdb_url)
        return
    logging.info("sending: {} {}".format(external_source,metric_type))



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
    weatherstack_url = "http://api.openweathermap.org/data/2.5/weather?q="+ city + "&appid=" + apikey + "&units=metric"
    logging.info("Start gathering: {}".format(external_source))
    
    result = requests.get(weatherstack_url)
    if result.status_code != 200:
        print("request not successful",weatherstack_url)
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


units = dict()
units["temperature"] = "Celsius"
units["humidity"] = "%"
units["feelslike"] = "Celsius"

influxdb_url = ""

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',level=logging.INFO)
    logging.info('Application start..')
    influxdb_url = 'http://'+os.environ['INFLUXDB_HOST']+':8086/write?db=temp_test'
    gather_weatherstack_data(os.environ['WEATHER_GETTER_CITY'],os.environ['WEATHERSTACK_APIKEY'])
    gather_openweathermap_data(os.environ['WEATHER_GETTER_CITY'],os.environ['OPENWEATHERMAP_APIKEY'])
    logging.info('Application finished')
