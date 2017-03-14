import os.path

from whoiscache.parsers import parse_dump, parse_updates
from whoiscache import types as T

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
