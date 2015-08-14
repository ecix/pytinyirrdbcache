import flask
import json


def add_routes(app):

    @app.route('/', methods=('GET',))
    def index():
        return "hi"

    @app.route('/cache/<string:cache>/macros/lookup/<string:macro>')
    @app.uses_cache
    def lookup_macro(cache, macro):
        try:
            return json200(list(cache.macros[macro]))
        except KeyError:
            return json404

    @app.route('/cache/<string:cache>/macros/list')
    @app.uses_cache
    def macro_names(cache):
        return json200(cache.macros.keys())


def json200(data):
        data = {"status": "200 OK",
                "data": data}
        return flask.Response(json.dumps(data), status=200,
                              content_type="application/json")

json404 = flask.Response(json.dumps({"status": "404 NOT FOUND"}), status=404,
                         content_type="application/json")

