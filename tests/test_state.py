import unittest

from whoiscache.state import WhoisCacheState, CacheStateCombiner
from whoiscache import types as T


class TestWhoisState(unittest.TestCase):
    def test_macros(self):
        state = WhoisCacheState()
        add1 = T.Update(action=T.ADD, serial='2',
                        record=T.Macro(name='A', members=['a', 'b']))
        add2 = T.Update(action=T.ADD, serial='3',
                        record=T.Macro(name='B', members=['b', 'c']))
        state.apply_update(add1)
        state.apply_update(add2)
        self.assertEqual({
            'A': set("ab"),
            'B': set("bc"),
        }, state.macros)
        self.assertEqual('3', state.serial)
        state.apply_update(T.Update(action=T.DEL, serial='4',
                                    record=T.Macro(name='B', members=[])))
        self.assertEqual({'A': set("ab")}, state.macros)
        self.assertEqual('4', state.serial)
