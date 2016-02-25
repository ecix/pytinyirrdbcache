
import os, string

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WHOIS_UPSTREAMS = {
    'RADB': {
        "name": "RADB",
        "dump_uri": "ftp://ftp.radb.net/radb/dbase/radb.db.gz",
        "serial_uri": "ftp://ftp.radb.net/radb/dbase/RADB.CURRENTSERIAL",
        "telnet": ("whois.radb.net", 43),
    },
    'RIPE': {
        "name": "RIPE",
        "dump_uri": "ftp://ftp.ripe.net/ripe/dbase/ripe.db.gz",
        "serial_uri": "ftp://ftp.ripe.net/ripe/dbase/RIPE.CURRENTSERIAL",
        "telnet": ("nrtm.db.ripe.net", 4444),
    },
    'LEVEL3': {
        'name': "LEVEL3",
        'serial_uri': 'ftp://ftp.radb.net/radb/dbase/LEVEL3.CURRENTSERIAL',
        'dump_uri': 'ftp://ftp.radb.net/radb/dbase/level3.db.gz',
        'telnet': ('rr.ntt.net', 43),
    },
    'ARIN': {
        "name": "ARIN",
        'serial_uri': 'ftp://ftp.arin.net/pub/rr/ARIN.CURRENTSERIAL',
        'dump_uri': 'ftp://ftp.arin.net/pub/rr/arin.db',
        'telnet': ('rr.arin.net', 4444),
    },
    'ALTDB': {
        'name': "ALTDB",
        'serial_uri': 'ftp://ftp.radb.net/radb/dbase/ALTDB.CURRENTSERIAL',
        'dump_uri': 'ftp://ftp.radb.net/radb/dbase/altdb.db.gz',
        'telnet': ('rr.ntt.net', 43),
    },
}


# Path to the cache data directory. Must exist.
CACHE_DATA_DIRECTORY = os.path.join(BASE_DIR, 'data')


# Seconds between WHOIS update query
WHOIS_UPDATE_INTERVAL = 60

HTTP_ENDPOINT = ('0.0.0.0', 8087)

# Read server version 
try:
    version_file = open(os.path.join(BASE_DIR, 'VERSION'), 'r')
    VERSION = string.strip(version_file.read())
    version_file.close()
except:
    VERSION = 'unknown'



