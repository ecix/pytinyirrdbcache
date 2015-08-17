import cPickle as pickle
import operator

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

    def apply_update(self, update):
        typename = type(update.record).__name__.lower()
        method = getattr(self, "_update_" + typename)
        method(update)
        self.serial = update.serial

    def _update_macro(self, (action, _, macro)):
        if action == T.ADD:
            self.macros[macro.name] = set(macro.members)
        elif action == T.DEL and macro.name in self.macros:
            del self.macros[macro.name]

    def _update_route(self, (action, _, route)):
        if action == T.ADD:
            self.prefix4.setdefault(route.origin, set()).add(route.prefix)
        elif action == T.DEL and route.origin in self.prefix4:
            self.prefix4[route.origin].discard(route.prefix)

    def _update_route6(self, (action, _, route)):
        if action == T.ADD:
            self.prefix6.setdefault(route.origin, set()).add(route.prefix)
        elif action == T.DEL and route.origin in self.prefix6:
            self.prefix6[route.origin].discard(route.prefix)

    def _update_unrecognised(self, _):
        pass


class CacheStateCombiner(object):
    """
    Provides a combined interface to underlying caches.
    """
    def __init__(self, states_by_name):
        states = [states_by_name[k] for k in sorted(states_by_name)]
        self.macros = combinedsetdict(st.macros for st in states)
        self.prefix4 = combinedsetdict(st.prefix4 for st in states)
        self.prefix6 = combinedsetdict(st.prefix6 for st in states)
        self.serial = repr(tuple(st.serial for st in states))


class combinedsetdict(object):
    """
    Dict-like object to combine dicts of sets
    """
    def __init__(self, sources, reducer=operator.ior):
        self.sources = list(sources)
        self.reducer = reducer

    def __getitem__(self, key):
        default = set()
        results = [s.get(key, default) for s in self.sources]
        if all(r is default for r in results):
            raise KeyError(key)
        return reduce(self.reducer, results)

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
