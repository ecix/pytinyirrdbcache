#!/usr/bin/env python

"""
Whoiscache
----------

Check if the whoiscache is up and running and the whoisdata is
up to date.
"""

import requests
import sys

from datetime import timedelta, datetime

# === CONFIG ===

WHOISCACHE='http://whoiscache.ecix.net:8087'

CACHE_MAX_AGE=timedelta(hours=24)

# === END CONFIG ===

class WhoiscacheDown(Exception):
    pass

class WhoiscacheServerError(Exception):
    pass

class WhoiscacheStatusError(Exception):
    pass


def _fetch_status(whoiscache_url):
    """
    Get whoiscache status
    """
    try:
        res = requests.get(whoiscache_url + '/cache/ALL/status')
        status = res.json()
    except:
        raise WhoiscacheDown()

    if status.get('status') != '200 OK' or status.get('data') == None:
        raise WhoiscacheServerError({
            'text': res.reason,
            'code': res.status_code,
            'status': status.get('status'),
        })

    return status.get('data')


def _status_caches(status):
    """
    Get parsed serial and update time for all caches.
    """
    try:
        serials = dict([cache.split(':') for cache in status.get('serial').split(',')])
    except Exception as e:
        raise WhoiscacheStatusError("Could not parse serials: %s"%str(e))

    try:
        updates = dict([(c[0], datetime.strptime(c[1], '%Y-%m-%d %H:%M:%S.%f'))
                        for c in [cache.split(':', 1) for cache in status.get(
                            'updated_at').split(',')]])
    except Exception as e:
        raise WhoiscacheStatusError("Could not parse update timestamps: %s" %
                                    str(e))

    cache_status = {}
    for cache, serial in serials.iteritems():
        cache_status[cache] = {
            'serial': serial
        }

    for cache, ts in updates.iteritems():
        cache_status[cache]['updated_at'] = ts

    return cache_status


def _status_check_cache_fill(caches):
    """
    Check if serials are present in caches
    """
    for cache, status in caches.iteritems():
        if status.get('serial') <= 0:
            raise WhoiscacheStatusError("Cache %s is empty." % cache)



def _status_check_cache_age(caches, max_age):
    """
    Check whoiscache stats for cache ages
    """
    for cache, status in caches.iteritems():
        update_ts = status.get('updated_at')
        if (datetime.now() - update_ts) > max_age:
            raise WhoiscacheStatusError("Cache %s is outdated. Updated at: %s"
                                        % (cache, str(update_ts)))


def main():
    """
    Run checks on whoiscache
    """
    try:
        status = _fetch_status(WHOISCACHE)
    except WhoiscacheDown:
        print("Could not reach whoiscache server.")
        sys.exit(-1)
    except WhoiscacheServerError as e:
        print("Could not get whoiscache status: %s (%d), status: %s" %
              (e['text'], e['code'], e['status']))
        sys.exit(-1)
    except:
        print("General error while fetching status from whoiscache.")
        sys.exit(-1)


    # Run checks
    try:
        caches = _status_caches(status)
        _status_check_cache_fill(caches)
        _status_check_cache_age(caches, CACHE_MAX_AGE)
    except WhoiscacheStatusError as e:
        print(e)
        sys.exit(-1)

    # Everything is fine
    sys.exit(0)


if __name__ == '__main__':
    main()
