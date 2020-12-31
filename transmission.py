import requests
import logging
import configuration

def send_metrics(metric_type,external_data,unit,external_source):
    data = 'air_monitoring,external_source=' +external_source + ',measuretype='+metric_type+',unit='+unit+' value='+str(external_data)
    res = requests.post(url=configuration.influxdb_url,data=data)
    if res.status_code != 204:
        print("request not successful",configuration.influxdb_url)
        return
    logging.info("sending: {} {}".format(external_source,metric_type))

def send_future_metrics(metric_type,external_data,unit,external_source,timestamp):
    data = 'air_monitoring,external_source=' +external_source + ',measuretype='+metric_type+',unit='+unit+' value='+str(external_data) + " " + timestamp
    res = requests.post(url=configuration.influxdb_url,data=data)
    if res.status_code != 204:
        print("request not successful",configuration.influxdb_url)
        return
    logging.info("sending: {} {}".format(external_source,metric_type))
