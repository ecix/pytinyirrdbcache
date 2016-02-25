import flask
import functools
import gevent
import logging
import time

from whoiscache import cache as C, settings, state

class WhoisCacheUpdateService():
    def __init__(self, upstreams):
        self.state = C.STATE_INITIALIZING
        self.caches = {up['name']: C.WhoisCache(up)
                       for up in upstreams}

    def start(self):
        """
        Exceptions initialising the caches are fatal since without updating
        successfully here it's possible that we may serve an old state.
        """
        try:
            for cache in self.caches.values():
                cache.update()
        except Exception:
            self.state = C.STATE_ERROR
            raise

        self.state = C.STATE_READY
        logging.info("Caches initialised")

        while True:
            time.sleep(settings.WHOIS_UPDATE_INTERVAL)
            for cache in self.caches.values():
                logging.info("Updating cache: %s", cache.name)
                try:
                    cache.update()
                except Exception:
                    logging.exception("Error updating cache: %s", cache.name)



class WhoisCacheService():
    def __init__(self, upstreams):
        self.state = C.STATE_INITIALIZING
        self.caches = { up['name']: C.WhoisCache(up) for up in upstreams }

        for cache in self.caches.values():
            logging.info("Loading cache: %s", cache.name)
            try:
                cache.load()
            except C.CacheNotReady:
                logging.exception("Error loading cache: %s", cache.name)

        self.state = C.STATE_READY
        logging.info("Caches initialized")

    def update(self, name):
        cache = self.caches[name]
        logging.info("Updating cache: %s", cache.name)
        cache.load()

    def get_cache_state(self, name):
        if self.state == C.STATE_INITIALIZING:
            raise C.CacheNotReady()

        if name == 'ALL':
            states = {n: c.state for n, c in self.caches.items()}
            return state.CacheStateCombiner(states)

        if not self.caches[name].ready:
            raise C.CacheNotReady()

        cache = self.caches[name]
        if not cache.ready:
            raise C.CacheNotReady()

        return cache.state


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
            except C.CacheNotReady:
                return flask.Response("Cache Not Ready", status=503)
            except C.CacheError:
                return flask.Response("Cache Init Error", status=500)
            except KeyError:
                return flask.Response("No Such Cache", status=404)
            else:
                return view(cache, *args, **kwargs)
        return functools.wraps(view)(inner)
