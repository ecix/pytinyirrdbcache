
WHOIS_UPSTREAMS = {
    'RADB': {
        "name":"RADB",
        "dump_uri": "ftp://ftp.radb.net/radb/dbase/radb.db.gz",
        "serial_uri": "ftp://ftp.radb.net/radb/dbase/RADB.CURRENTSERIAL",
        "telnet": ("whois.radb.net", 43),
    },
    'RIPE': {
        "name":"RIPE",
        "dump_uri": "ftp://ftp.ripe.net/ripe/dbase/ripe.db.gz",
        "serial_uri": "ftp://ftp.ripe.net/ripe/dbase/RIPE.CURRENTSERIAL",
        "telnet": ("nrtm.db.ripe.net", 4444),
    }
}


# Path to the cache data directory. Must exist.
CACHE_DATA_DIRECTORY = 'data'


# Seconds between WHOIS update query
WHOIS_UPDATE_INTERVAL = 60
