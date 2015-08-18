import unittest

from whoiscache.state import WhoisCacheState, CacheStateCombiner
from whoiscache import types as T


class TestWhoisState(unittest.TestCase):
    def test_macros(self):
        state = WhoisCacheState()
        add1 = (T.ADD, '2', T.Macro(name='A', members=['a', 'b']))
        add2 = (T.ADD, '3', T.Macro(name='B', members=['b', 'c']))
        state.apply_update(add1)
        state.apply_update(add2)
        self.assertEqual({
            'A': set("ab"),
            'B': set("bc"),
        }, state.macros)
        self.assertEqual('3', state.serial)
        state.apply_update((T.DEL, '4', T.Macro(name='B', members=[])))
        self.assertEqual({'A': set("ab")}, state.macros)
        self.assertEqual('4', state.serial)

    def test_prefix4(self):
        state = WhoisCacheState()
        state.apply_update((T.ADD, '1', T.Route(prefix='abc', origin='asn1')))
        state.apply_update((T.ADD, '2', T.Route(prefix='bcd', origin='asn2')))
        state.apply_update((T.ADD, '3', T.Route(prefix='def', origin='asn1')))
        state.apply_update((T.DEL, '4', T.Route(prefix='abc', origin='asn1')))
        self.assertEqual({
            'asn1': set(['def']),
            'asn2': set(['bcd']),
        }, state.prefix4)
        state.apply_update((T.DEL, '5', T.Route(prefix='bcd', origin='asn2')))
        self.assertEqual({'asn1': set(['def'])}, state.prefix4)

    def test_prefix6(self):
        state = WhoisCacheState()
        state.apply_update((T.ADD, '1', T.Route6(prefix='abc', origin='asn1')))
        state.apply_update((T.ADD, '2', T.Route6(prefix='bcd', origin='asn2')))
        state.apply_update((T.ADD, '3', T.Route6(prefix='def', origin='asn1')))
        state.apply_update((T.DEL, '4', T.Route6(prefix='abc', origin='asn1')))
        self.assertEqual({
            'asn1': set(['def']),
            'asn2': set(['bcd']),
        }, state.prefix6)
        state.apply_update((T.DEL, '5', T.Route6(prefix='bcd', origin='asn2')))
        self.assertEqual({'asn1': set(['def'])}, state.prefix6)
