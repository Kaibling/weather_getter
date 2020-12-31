import os
import logging
import schedule
import time
import configuration
import gather_data
import sys

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',level=logging.INFO)
    logging.info('Application start..')
    configuration.influxdb_url = 'http://'+os.environ['INFLUXDB_HOST']+':8086/write?db=temp_test'
    schedule.every().hour.at(':00').do(gather_data.gather_weatherstack_data,os.environ['WEATHER_GETTER_CITY'],os.environ['WEATHERSTACK_APIKEY'])
    schedule.every().hour.at(':00').do(gather_data.gather_openweathermap_data,os.environ['WEATHER_GETTER_CITY'],os.environ['OPENWEATHERMAP_APIKEY'])
    schedule.every().hour.at(':00').do(gather_data.save_gold_price)
    schedule.every().hour.at(':00').do(gather_data.save_btc)
    schedule.every(2).day.do(gather_data.forecast,os.environ['WEATHER_GETTER_CITY'],os.environ['OPENWEATHERMAP_APIKEY'])

    while 1:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping")
            sys.exit(0)
