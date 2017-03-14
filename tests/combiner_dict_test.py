
import pytest

from whoiscache.state import CombinerDict


def _make_combiner_dict():
    sources = [{'A': 10}, {'A': 2, 'B': 3}]
    combined = CombinerDict(iter(sources),
                            reducer=lambda x, y: x*y+1)
    return (sources, combined)


def test_constructor():
    sources, combined = _make_combiner_dict()
    assert sources == combined.sources

def test_getitem():
    _, combined = _make_combiner_dict()
    assert combined['A'] == 21 # x*y+1
    assert combined['B'] == 3
    with pytest.raises(KeyError):
        combined['C']

def test_get():
    _, combined = _make_combiner_dict()
    assert combined.get('A') == 21
    assert combined.get('B') == 3
    assert combined.get('C', 42) == 42

def test_keys():
    _, combined = _make_combiner_dict()
    assert set(combined.keys()) == {'A', 'B'}

def test_items():
    _, combined = _make_combiner_dict()
    items = {('A', 21), ('B', 3)}
    assert set(combined.items()) == items
