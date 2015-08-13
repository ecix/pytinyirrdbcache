import logging
import pprint
import sys
from whoiscache import types as T

"""
Parse data from WHOIS servers
"""


def parse_dump(handle):
    """
    Parse a whois dump file, yield records
    """
    while True:
        record = read_record(handle)
        if not record:
            break
        yield record


def parse_updates(handle):
    """
    Parse output from whois update stream
    """
    while True:
        act_serial = read_act_serial(handle)
        if not act_serial:
            break
        record = read_record(handle)
        yield T.Update(*(act_serial + (record,)))


def read_act_serial(handle):
    while True:
        line = handle.readline()
        if line == '':
            break
        elif line[0] in {'%', '#', '\n'}:
            if line[0] == '%':
                logging.info('recv: ' + line.strip())
            continue
        if line.startswith('ADD '):
            return (T.ADD, line[4:].strip())
        elif line.startswith('DEL '):
            return (T.DEL, line[4:].strip())
        else:
            raise ValueError("Unrecognised action: %s" % line)


def read_record(handle):
    """ Read a record from a handle """
    block = []
    while True:
        line = handle.readline()
        if line == '\n':
            if block:
                break
            continue
        if line == '':
            break
        if not line.startswith('#'):
            block.append(line[:-1])
    if block:
        try:
            return parse_record(block)
        except Exception:
            logging.error("Error parsing block:")
            pprint.pprint(block, stream=sys.stderr)
            raise


def parse_record(block):
    """ Parse a record from a block of related properties """
    key = block[0].split(':')[0].lower()
    if key == 'as-set':
        return parse_macro(block)
    elif key == 'route':
        return parse_route(block)
    elif key == 'route6':
        return parse_route6(block)
    else:
        return T.Unrecognised(key)


def parse_macro(block):
    """ Parse a macro """
    name = block_lookup(block, 'as-set')
    members = []
    for line in block_lookup_many(block, 'members'):
        items = filter(None, line.split(','))
        members.extend(i.strip() for i in items)
    return T.Macro(name, members)


def parse_route(block):
    """ Parse a route """
    return T.Route(block_lookup(block, 'route'),
                   block_lookup(block, 'origin'))


def parse_route6(block):
    """
    Parse a ipv6 route

    >>> parse_route6(['route6: abc', 'origin: wat'])
    T.Route6(route6='abc', origin='wat')
    """
    return T.Route6(block_lookup(block, 'route6'),
                    block_lookup(block, 'origin'))


def block_lookup(block, key):
    """ Lookup a value from a block by iterating the lines """
    for line in block:
        if line.startswith(key + ':'):
            return line[len(key)+1:].strip()
    raise KeyError(key)


def block_lookup_many(block, key):
    """ Lookup a multiline value from a block by iterating """
    lines = []
    lastkey = None
    for line in block:
        thiskey = lastkey
        val = line.strip()
        if val.startswith('#'):
            continue
        if ':' in val:
            (thiskey, val) = val.split(':', 1)
            lastkey = key
        if thiskey == key:
            lines.append(val)
    return lines
