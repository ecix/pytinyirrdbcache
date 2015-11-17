import flask
import functools
import gevent
import logging
import time

from whoiscache import cache as C, settings, state


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

    def get_cache_state(self, name):
        if self.state == 'NASCENT':
            raise CacheNotReady()
        if self.state == 'ERROR':
            pass # TODO: put back
            #raise CacheError()
        if name == 'ALL':
            states = {n: c.state for n, c in self.caches.items()}
            return state.CacheStateCombiner(states)
        return self.caches[name].state


class CacheNotReady(Exception):
    pass


class CacheError(Exception):
    pass


class WhoisCacheApp(flask.Flask):
    """
    Flask app to expose caches
    """
    def uses_cache(self, view):
        """
        Decorator to provide a queryable cache object
        """
        def inner(*args, **kwargs):
            try:
                name = kwargs.pop('cache')
                cache = self.service.get_cache_state(name)
            except CacheNotReady:
                return flask.Response("Cache Not Ready", status=503)
            except CacheError:
                return flask.Response("Cache Init Error", status=500)
            except KeyError:
                return flask.Response("No Such Cache", status=404)
            else:
                return view(cache, *args, **kwargs)
        return functools.wraps(view)(inner)
