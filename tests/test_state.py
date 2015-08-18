import unittest

from whoiscache.state import WhoisCacheState, CacheStateCombiner, \
    CombinerDict
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


class TestCacheStateCombiner(unittest.TestCase):
    def setUp(self):
        self.z = WhoisCacheState()
        self.y = WhoisCacheState()
        self.x = WhoisCacheState()
        self.states = {'z': self.z, 'y': self.y, 'x': self.x}
        for name in self.states:
            self.states[name].serial = ord(name)
        self.combined = CacheStateCombiner(self.states)

    def test_combiner_dicts(self):
        for prop in ['macros', 'prefix4', 'prefix6']:
            ids = [id(getattr(l, prop)) for l in [self.x, self.y, self.z]]
            self.assertEqual(ids, map(id, getattr(self.combined, prop).sources))

    def test_combiner_serial(self):
        self.assertEqual('x:120,y:121,z:122', self.combined.serial)


class TestCombinerDict(unittest.TestCase):
    def setUp(self):
        self.sources = [{'A': 10}, {'A': 2, 'B': 3}]
        self.combined = CombinerDict(iter(self.sources),
                                     reducer=lambda x, y: x*y+1)

    def test_construction(self):
        self.assertEqual(self.sources, self.combined.sources)

    def test_getitem(self):
        self.assertEqual(21, self.combined['A'])
        self.assertEqual(3, self.combined['B'])
        with self.assertRaises(KeyError):
            self.combined['C']

    def test_get(self):
        self.assertEqual(21, self.combined.get('A'))
        self.assertEqual(3, self.combined.get('C', 3))

    def test_keys(self):
        self.assertEqual(set("AB"), set(self.combined.keys()))

    def test_items(self):
        self.assertEqual(set([('A', 21), ('B', 3)]),
                         set(self.combined.items()))

