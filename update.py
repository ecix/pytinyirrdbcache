
import logging
from whoiscache import service, settings

def main():
    logging.basicConfig(level=logging.INFO)
    upstreams = settings.WHOIS_UPSTREAMS.values()
    update_service = service.WhoisCacheUpdateService(upstreams)
    update_service.start()

if __name__ == '__main__':
    main()
