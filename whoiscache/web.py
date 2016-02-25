import flask
import jinja2
import json

from whoiscache.service import WhoisCacheApp
from whoiscache import settings

app = WhoisCacheApp("WhoisCache")

index_tpl = jinja2.Template("""
<h1>Whois Cache ({{version}})</h1>
<p>Loaded caches: <b>{{ caches|join(', ') }}, ALL</b> (combined logical OR)</p>
<table border=1>
    {% for route in routes %}
        <tr><td><pre>GET {{ route.path }}</pre></td>
            <td><pre>{{ route.doc }}</pre></tr>
    {% endfor %}
</table>""")

@app.route('/', methods=('GET',))
def index():
    routes = []
    for rule in app.url_map.iter_rules():
        if not str(rule).startswith('/static'):
            routes.append({
                'path': jinja2.escape(str(rule).replace('string:', '')),
                'doc': getattr(app.view_functions[rule.endpoint], '__doc__')
            })
    routes.sort(key=lambda r: r['path'])
    return index_tpl.render(routes=routes,
                            caches=app.service.caches.keys(),
                            version=settings.VERSION)
index.__doc__ = "This page"



def lookup(path, attr, doc):
    @app.route('/cache/<string:cache>/%s/lookup/<string:key>' % path,
               endpoint="lookup_%s" % attr)
    @app.uses_cache
    def lookup_inner(cache, key):
        try:
            items = getattr(cache, attr)
            return json200(list(items[key]))
        except KeyError:
            return json404
    lookup_inner.__doc__ = doc


lookup("macros", "macros", "Lookup macro by name")
lookup("prefixes/4", "prefix4", "Lookup ipv4 prefixes by ASN")
lookup("prefixes/6", "prefix6", "Lookup ipv6 prefixes by ASN")


def listing(path, attr, doc):
    @app.route('/cache/<string:cache>/%s/list' % path,
               endpoint="list_%s" % attr)
    @app.uses_cache
    def list_inner(cache):
        return json200(getattr(cache, attr).keys())
    list_inner.__doc__ = doc


listing("macros", "macros", "List macro names")
listing("prefixes/4", "prefix4", "List ASNs with ipv4 prefixes")
listing("prefixes/6", "prefix6", "List ASNs with ipv6 prefixes")


@app.route('/cache/<string:cache>/status')
@app.uses_cache
def cache_status(cache):
    return json200({'serial': cache.serial})
cache_status.__doc__ = "Return status of cache"


@app.route('/cache/<string:cache>/dump')
@app.uses_cache
def dump(cache):
    return json200({
        'serial': cache.serial,
        'macros': {k: list(v) for k, v in cache.macros.items()},
        'prefix4': {k: list(v) for k, v in cache.prefix4.items()},
        'prefix6': {k: list(v) for k, v in cache.prefix6.items()},
    })
dump.__doc__ = """Dump all data for named cache in format:
{ "serial":  $serial,
  "macros":  {$name: $members},
  "prefix4": {$asn: $prefixes},
  "prefix6": {$asn: $prefixes}}"""


def json200(data):
    data = {"status": "200 OK", "data": data}
    return flask.Response(json.dumps(data), status=200,
                          content_type="application/json")

json404 = flask.Response(json.dumps({"status": "404 NOT FOUND"}), status=404,
                         content_type="application/json")
