import pytest

from whoiscache.state import WhoisCacheState, CacheStateCombiner

def _make_initial_states():
    """Initialize three whoiscache states"""
    states = {
        'x': WhoisCacheState(),
        'y': WhoisCacheState(),
        'z': WhoisCacheState(),
    }
    for name in states:
        serial = ord(name)
        states[name].serial = serial
    return states


def _make_state_combiner(states):
    """Initialize state cache combiner"""
    return CacheStateCombiner(state)


def test_cache_state_combiner_dicts():
    """Test state combining"""
    states = _make_initial_states()
    combined = CacheStateCombiner(states)

    for prop in ['macros', 'prefix4', 'prefix6']:
        ids = [id(getattr(l, prop))
               for l in [states['x'], states['y'], states['z']]]
        expected = map(id, getattr(combined, prop).sources)
        assert ids == expected


def test_cache_state_combiner_serial():
    """Test serial combining"""
    states = _make_initial_states()
    combined = CacheStateCombiner(states)
    assert combined.serial == 'x:120,y:121,z:122'


