import pytest

from whoiscache.state import WhoisCacheState
from whoiscache import types as T


def test_macros():
    """Test macro state updates"""
    state = WhoisCacheState()
    add1 = ("ADD", '2', T.Macro(name='A', members=['a', 'b']))
    add2 = ("ADD", '3', T.Macro(name='B', members=['b', 'c']))
    state.apply_update(add1)
    state.apply_update(add2)

    expected = {
        'A': set('ab'),
        'B': set('bc'),
    }
    assert state.macros == expected
    assert state.serial == '3'

    # Update
    state.apply_update(("DEL", '4', T.Macro(name='B', members=[])))

    # Check results
    expected = {
        'A': set('ab'),
    }
    assert state.macros == expected
    assert state.serial == '4'


def test_prefix4():
    """Test IPv4 prefixes updates"""
    state = WhoisCacheState()
    state.apply_update(("ADD", '1', T.Route(prefix='abc', origin='asn1')))
    state.apply_update(("ADD", '2', T.Route(prefix='bcd', origin='asn2')))
    state.apply_update(("ADD", '3', T.Route(prefix='def', origin='asn1')))
    state.apply_update(("DEL", '4', T.Route(prefix='abc', origin='asn1')))

    expected = {
        'asn1': set(['def']),
        'asn2': set(['bcd']),
    }
    assert state.prefix4 == expected

    # Apply update
    state.apply_update(("DEL", '5', T.Route(prefix='bcd', origin='asn2')))
    expected = {
        'asn1': set(['def']),
    }
    assert state.prefix4 == expected


def test_prefix6():
    """Test IPv6 prefixes updates"""
    state = WhoisCacheState()
    state.apply_update(("ADD", '1', T.Route6(prefix='abc', origin='asn1')))
    state.apply_update(("ADD", '2', T.Route6(prefix='bcd', origin='asn2')))
    state.apply_update(("ADD", '3', T.Route6(prefix='def', origin='asn1')))
    state.apply_update(("DEL", '4', T.Route6(prefix='abc', origin='asn1')))

    expected = {
        'asn1': set(['def']),
        'asn2': set(['bcd']),
    }
    assert state.prefix6 == expected

    # Apply update
    state.apply_update(("DEL", '5', T.Route6(prefix='bcd', origin='asn2')))
    expected = {
        'asn1': set(['def']),
    }
    assert state.prefix6 == expected

