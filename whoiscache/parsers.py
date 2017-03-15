import logging
import pprint
import re
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

    header = read_header(handle)

    while True:
        act_serial = read_act_serial(handle)
        if not act_serial:
            break
        record = read_record(handle)
        yield act_serial + (record,)



def parse_header(line):
    """Extract header data"""
    match = re.match(r'%START Version: (\d+) (\w+) (\d+)-(\d+)', line)
    if not match:
        return None

    header = {
        "version": int(match.group(1)),
        "source": match.group(2),
        "serials": (int(match.group(3)), int(match.group(4))),
    }
    return header


def read_header(handle):
    """Read START header for version, source and serial range"""
    handle.seek(0) # Assert we are at the beginning of the file
    while True:
        line = handle.readline()
        if line == None:
            break
        if line == '':
            continue
        if line.startswith('%START'):
            return parse_header(line)


def read_act_serial(handle):
    while True:
        line = handle.readline()
        if line == '':
            break
        elif line[0] in {'%', '#', '\n'}:
            if line[0] == '%':
                logging.info('recv: ' + line.strip())
            if 'error' in line.lower():
                raise ErrorResponse(line)
            continue
        if line.startswith('ADD '):
            return ("ADD", line[4:].strip())
        elif line.startswith('DEL '):
            return ("DEL", line[4:].strip())
        else:
            raise ParseFailure("Cannot parse: %s" % line)


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
    name = block_lookup(block, 'as-set').upper()
    members = []
    for line in block_lookup_many(block, 'members'):
        items = filter(None, line.split(','))
        members.extend(i.strip().upper() for i in items)
    return T.Macro(name, members)


def parse_route(block):
    """ Parse a route """
    return T.Route(block_lookup(block, 'route'),
                   block_lookup(block, 'origin').upper())


def parse_route6(block):
    """
    Parse a ipv6 route

    >>> parse_route6(['route6: abc', 'origin: wat'])
    T.Route6(route6='abc', origin='wat')
    """
    return T.Route6(block_lookup(block, 'route6'),
                    block_lookup(block, 'origin').upper())


re_strip_comment = re.compile('\s*#.*')


def block_lookup(block, key):
    """ Lookup a value from a block by iterating the lines """
    for line in block:
        if line.startswith(key + ':'):
            val = line[len(key)+1:].strip()
            return re_strip_comment.sub('', val)
    raise KeyError(key)


def block_lookup_many(block, key):
    """ Lookup a multiline value from a block by iterating """
    lines = []
    curkey = None
    for line in block:
        val = line.strip()
        if val.startswith('#'):
            continue
        if ':' in val:
            (curkey, val) = val.split(':', 1)
        if curkey == key:
            val = re_strip_comment.sub('', val)
            lines.append(val)
    return lines


class ParseFailure(ValueError):
    pass


class ErrorResponse(ValueError):
    pass
