import cPickle as pickle
import operator
from datetime import datetime

from whoiscache import types as T

class WhoisCacheState(object):
    """
    Internal WhoIS cache state and query interface
    """
    def __init__(self):
        self.serial = None
        self.macros = {}
        self.prefix4 = {}
        self.prefix6 = {}
        self.updated_at = False

    def apply_update(self, (action, serial, record)):
        typename = type(record).__name__.lower()
        method = getattr(self, "_update_" + typename)
        method(action, record)
        self.serial = serial
        self.updated_at = datetime.now()

    def _update_macro(self, action, macro):
        if action == "ADD":
            self.macros[macro.name] = set(macro.members)
        elif action == "DEL" and macro.name in self.macros:
            del self.macros[macro.name]

    def _update_route(self, action, route):
        if action == "ADD":
            self.prefix4.setdefault(route.origin, set()).add(route.prefix)
        elif action == "DEL" and route.origin in self.prefix4:
            prefixes = self.prefix4[route.origin]
            prefixes.discard(route.prefix)
            if prefixes:
                self.prefix4[route.origin] = prefixes
            else:
                del self.prefix4[route.origin]

    def _update_route6(self, action, route):
        if action == "ADD":
            self.prefix6.setdefault(route.origin, set()).add(route.prefix)
        elif action == "DEL" and route.origin in self.prefix6:
            prefixes = self.prefix6[route.origin]
            prefixes.discard(route.prefix)
            if prefixes:
                self.prefix6[route.origin] = prefixes
            else:
                del self.prefix6[route.origin]

    def _update_unrecognised(self, *_):
        pass


class CacheStateCombiner(object):
    """
    Provides a combined interface to underlying caches.
    """
    def __init__(self, states_by_name):
        states = sorted(states_by_name.items(), key=lambda (k, v): k)
        self.macros = CombinerDict(st.macros for _, st in states)
        self.prefix4 = CombinerDict(st.prefix4 for _, st in states)
        self.prefix6 = CombinerDict(st.prefix6 for _, st in states)
        self.serial = ','.join("%s:%s" % (name, st.serial)
                               for (name, st) in states)


class CombinerDict(object):
    """
    Dict-like object to combine dicts of sets
    """
    def __init__(self, sources, reducer=operator.ior):
        self.sources = list(sources)
        self.reducer = reducer

    def __getitem__(self, key):
        values = []
        for source in self.sources:
            try:
                values.append(source[key])
            except KeyError:
                pass
        if len(values) == 0:
            raise KeyError(key)
        return reduce(self.reducer, values)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        keysets = [set(s.keys()) for s in self.sources]
        return list(reduce(operator.ior, keysets))

    def items(self):
        return [(k, self[k]) for k in self.keys()]
