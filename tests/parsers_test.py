import pytest

import os.path


from StringIO import StringIO

from whoiscache.parsers import parse_dump, parse_updates
from whoiscache import parsers
from whoiscache import types as T


def _open_resource(name):
    return open(_resource_path(name))

def _resource_path(name):
    return os.path.join(os.path.dirname(__file__), 'resources', name)


def _run_parser(parser, data_filename, expected):
    """Execute parser on loaded input"""
    data = open(_resource_path(data_filename))
    result = list(parser(data))
    assert result == expected


def test_parse_radb_dump():
    """Test radb parsing"""
    expected = [
        T.Unrecognised(key='aut-num'),
        T.Route(prefix='167.96.0.0/16', origin='AS2900'),
        T.Unrecognised(key='mntner'),
        T.Macro(name='AS-LEN',
                members=['AS4222', 'AS4016', 'AS4529', 'AS6377']),
        T.Macro(name='AS-OREGON-IX-PEERAGE',
                members=['AS4201', 'AS1798', 'AS3582', 'AS4222', 'AS2914',
                         'AS6447', 'AS5650', 'AS6108', 'AS3838', 'AS1982',
                         'AS4534', 'AS5798', 'AS8028']),
        T.Route6(prefix='2001:1988::/32',
                 origin='AS16467')
    ]

    _run_parser(parse_dump, 'radb.db.sample', expected)


def test_parse_ripedb_dump():
    """Test ripedb dump parsing"""
    expected = [
        T.Unrecognised(key='as-block'),
        T.Macro(name='AS-TMPEBONECWIX',
                members=['AS3727', 'AS4445', 'AS4610', 'AS4624', 'AS4637',
                         'AS4654', 'AS4655', 'AS4656', 'AS4659', 'AS4681',
                         'AS4696', 'AS4714', 'AS4849', 'AS5089', 'AS5090',
                         'AS5532', 'AS5551', 'AS5559', 'AS5655', 'AS6081',
                         'AS6255', 'AS6292', 'AS6618', 'AS6639']),
        T.Route(prefix='193.254.30.0/24',
                origin='AS12726'), T.Route6(prefix='2001:1578:200::/40',
                                            origin='AS12817')
    ]

    _run_parser(parse_dump, 'ripe.db.sample', expected)


def test_parse_radb_updates():
    """Test telnet / update stream parsing with radb data"""
    expected = [
        ("ADD", '2393925',
         T.Macro(name='AS-HURRICANE',
                 members=['AS-LAIX', 'AS-MEMSET', 'AS-VOCUS', 'AS-TPG',
                          'AS-JAPAN-TELECOM', 'AS4', 'AS5', 'AS10', 'AS16',
                          'AS17'])),
         ("DEL", '2393926',
          T.Route(prefix='42.116.22.0/24',
                  origin='AS18403'))
    ]

    _run_parser(parse_updates, 'radb.updates.sample', expected)


def test_parse_update_headers():
    """Parse update headers"""
    expected = {
        "version": 3,
        "source": "radb",
        "serials": (2393925, 2393950),
    }
    data = open(_resource_path('radb.updates.sample'))
    result = parsers.read_header(data)
    assert result == expected

    expected = {
        "version": 1,
        "source": "LEVEL3",
        "serials": (767081, 767082),
    }
    data = open(_resource_path('l3.updates.sample'))
    result = parsers.read_header(data)
    assert result == expected

def test_level3_updates():
    """
    Level3 does not provide serials in commands like 'ADD' and
    'DEL', so we have to mitigate this issue.
    """
    expected = [
        ("ADD", "767081",
         T.Macro(name='AS-HURRICANE',
                 members=['AS-LAIX', 'AS-MEMSET', 'AS-VOCUS', 'AS-TPG',
                          'AS-JAPAN-TELECOM', 'AS4', 'AS5', 'AS10', 'AS16',
                          'AS17'])),
         ("DEL", '767082',
          T.Route(prefix='42.116.22.0/24',
                  origin='AS18403'))

    ]
    _run_parser(parse_updates, 'l3.updates.sample', expected)



def test_range_error():
    """Raise a range error"""
    try:
        raise parsers.SerialRangeError(
            "%ERROR:401: invalid range: Not within 2278326-38325450",
            52221,
            1230000)
    except parsers.SerialRangeError as e:
        assert e.first == 52221
        assert e.last == 1230000


def test_parse_headers():
    """Test header parsing"""
    arin_header = StringIO("""
% The ARIN Database is subject to Terms and Conditions.
% See http://www.arin.net/db/support/db-terms-conditions.pdf

%START Version: 3 ARIN 66038-66844 FILTERED

    """)

    arin_expected = {
        "version": 3,
        "source": "ARIN",
        "serials": (66038, 66844),
    }

    ripe_header = StringIO("""
% The RIPE Database is subject to Terms and Conditions.
% See http://www.ripe.net/db/support/db-terms-conditions.pdf

%START Version: 3 RIPE 38325160-38325288

    """)

    ripe_expected = {
        "version": 3,
        "source": "RIPE",
        "serials": (38325160, 38325288),
    }

    headers = [ripe_header, arin_header]
    expected = [ripe_expected, arin_expected]

    results = [parsers.read_header(h) for h in headers]
    assert results == expected


def test_handle_range_errors():
    """Parse headers with range errors, check result"""
    headers = [_open_resource('level3.header.rangeerror.sample'),
               _open_resource('radb.header.rangeerror.sample'),
               _open_resource('ripe.header.rangeerror.sample')]

    ranges = [(789, 765562),
              (789, 3339553),
              (2278326, 38325450)]

    for i, header in enumerate(headers):
        with pytest.raises(parsers.SerialRangeError) as excinfo:
            parsers.read_header(header)
        # Check exception
        err = excinfo.value
        expected = ranges[i]
        assert (err.first, err.last) == expected


def test_handle_outofsync_errors():
    """Like range error, but without range info"""
    header = _open_resource('ripe.header.outofsync.sample')
    with pytest.raises(parsers.OutOfSyncError):
        parsers.read_header(header)


