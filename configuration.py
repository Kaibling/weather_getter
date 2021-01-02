
#influxdb_write_url = influxdb_url + "/write?db=" + influxdb_db
#influxdb_query_url = influxdb_url + "/query?db=" + influxdb_db


class _influxdb_conf:
    url = ""
    db = ""
    write_url = ""
    query_url = ""

    def __init__(self,url,db):
        self.url = url
        self.db = db
        self.write_url = self.url + "/write?db=" + self.db
        self.query_url = self.url + "/query?db=" + self.db


influx_config = _influxdb_conf("","")