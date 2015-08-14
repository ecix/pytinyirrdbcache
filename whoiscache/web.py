import flask
import json

from whoiscache.service import WhoisCacheApp

app = WhoisCacheApp("WhoisCache")


@app.route('/', methods=('GET',))
def index():
    return "hi"


def lookup(path, attr):
    @app.route('/cache/<string:cache>/%s/lookup/<string:key>' % path,
               endpoint="lookup_%s" % attr)
    @app.uses_cache
    def lookup_inner(cache, key):
        try:
            items = getattr(cache, attr)
            return json200(list(items[key]))
        except KeyError:
            return json404


lookup("macros", "macros")
lookup("prefixes/4", "prefix4")
lookup("prefixes/6", "prefix6")


def listing(path, attr):
    @app.route('/cache/<string:cache>/%s/list' % path,
               endpoint="list_%s" % attr)
    @app.uses_cache
    def list_inner(cache):
        return json200(getattr(cache, attr).keys())


listing("macros", "macros")
listing("prefixes/4", "prefix4")
listing("prefixes/6", "prefix6")


def json200(data):
    data = {"status": "200 OK", "data": data}
    return flask.Response(json.dumps(data), status=200,
                          content_type="application/json")

json404 = flask.Response(json.dumps({"status": "404 NOT FOUND"}), status=404,
                         content_type="application/json")
