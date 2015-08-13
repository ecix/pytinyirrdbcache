from collections import defaultdict
import cPickle as pickle

from whoiscache import types as T


class WhoisCacheState(object):
    """
    Internal WhoIS cache state and query interface
    """
    def __init__(self):
        self.data = T.WhoisCacheData(None,
                                     macros=defaultdict(set),
                                     prefix4=defaultdict(set),
                                     prefix6=defaultdict(set))

    @property
    def serial(self):
        return self.data.serial

    def load(self, fh):
        self.data = pickle.load(fh)

    def save(self, fh):
        pickle.dump(self.data, fh)

    def apply_update(self, update):
        typename = type(update.record).__name__.lower()
        method = getattr(self, "_update_" + typename)
        method(update)
        self.data = self.data._replace(serial=update.serial)

    def _update_macro(self, (action, _, macro)):
        if action == T.ADD:
            self.data.macros[macro.name] = set(macro.members)
        elif action == T.DEL and macro.name in self.data.macros:
            del self.data.macros[macro.name]

    def _update_route(self, (action, _, route)):
        if action == T.ADD:
            self.data.prefix4[route.origin].add(route.prefix)
        elif action == T.DEL and route.origin in self.data.prefix4:
            self.data.prefix4.discard(route.prefix)

    def _update_route6(self, (action, _, route)):
        if action == T.ADD:
            self.data.prefix6[route.origin].add(route.prefix)
        elif action == T.DEL and route.origin in self.data.prefix6:
            self.data.prefix6.discard(route.prefix)

    def _update_unrecognised(self, _):
        pass
