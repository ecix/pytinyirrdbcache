import gevent
import logging
import time

from whoiscache import cache as C, settings


class WhoisCacheService(gevent.Greenlet):
    def __init__(self, upstreams):
        self.state = 'NASCENT'
        self.caches = {up['name']: C.WhoisCache(up)
                       for up in upstreams}
        super(WhoisCacheService, self).__init__()

    def _run(self):
        """
        Exceptions initialising the caches are fatal since without updating
        successfully here it's possible that we may serve an old state.
        """
        try:
            for cache in self.caches.values():
                cache.load()
                cache.update()
        except Exception:
            self.state = "ERROR"
            raise

        self.state = "READY"
        logging.info("Caches initialised")

        while True:
            time.sleep(settings.WHOIS_UPDATE_INTERVAL)
            for cache in self.caches.values():
                try:
                    cache.update()
                except Exception:
                    logging.exception("Error updating cache: %s", cache.name)

    def get_cache(self, name):
        if self.state == 'NASCENT':
            raise CacheNotReady()
        if self.state == 'ERROR':
            raise CacheError()
        return self.caches[name].state


class CacheNotReady(Exception):
    pass


class CacheError(Exception):
    pass
