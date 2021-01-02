import requests
import logging
import configuration

def send_metrics(metric_type,external_data,unit,external_source):
    data = 'air_monitoring,external_source=' +external_source + ',measuretype='+metric_type+',unit='+unit+' value='+str(external_data)
    result = requests.post(url=configuration.influx_config.write_url,data=data)
    if result.status_code != 204:
        logging.error("request not successful: {}:{} {}".format(configuration.influx_config.write_url,result.status_code,result.content))
        return
    logging.info("sending: {} {}".format(external_source,data))

def send_future_metrics(metric_type,external_data,unit,external_source,timestamp):
    data = 'air_monitoring,external_source=' +external_source + ',measuretype='+metric_type+',unit='+unit+' value='+str(external_data) + " " + timestamp
    result = requests.post(url=configuration.influx_config.write_url,data=data)
    if result.status_code != 204:
        logging.error("request not successful: {}:{} {}".format(configuration.influx_config.write_url,result.status_code,result.content))
        return
    logging.info("sending: {} {}".format(external_source,data))

def get_last_timestamp(external_source,measuretype):

    query="q=SELECT value FROM air_monitoring where external_source='" + external_source + "' and measuretype='" + measuretype + "' GROUP BY * ORDER BY DESC LIMIT 1"
    result = requests.get(url=configuration.influx_config.query_url + "&" +query + "&epoch=ns" )
    if result.status_code != 200:
        logging.error("request not successful: {}:{} {}".format(configuration.influx_config.write_url,result.status_code,result.content))
        return
    logging.info("received timestamp for: {}".format(external_source))
    return result.content
