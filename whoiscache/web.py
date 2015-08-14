import flask


class WhoisCacheApp(flask.Flask):
    def __init__(self, name, db_names):
        super(WhoisCacheApp, self).__init__(name)
        self.db_name = db_names
