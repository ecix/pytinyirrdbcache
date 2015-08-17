import gevent.monkey
gevent.monkey.patch_all()

import gevent.wsgi
import logging

from whoiscache import service, settings, web


def main():
    logging.basicConfig(level=logging.INFO)
    upstreams = settings.WHOIS_UPSTREAMS.values()
    web.app.service = service.WhoisCacheService(upstreams)
    web.app.service.start()
    http_server = gevent.wsgi.WSGIServer(settings.HTTP_ENDPOINT, web.app)
    logging.info("Listening on http://%s:%s/" % settings.HTTP_ENDPOINT)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
