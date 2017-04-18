
import os, string

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WHOIS_UPSTREAMS = {
    'RIPE': {
        "name": "RIPE",
        "dump_uri": "ftp://ftp.ripe.net/ripe/dbase/ripe.db.gz",
        "serial_uri": "ftp://ftp.ripe.net/ripe/dbase/RIPE.CURRENTSERIAL",
        "telnet": ("localhost", 4444),
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



