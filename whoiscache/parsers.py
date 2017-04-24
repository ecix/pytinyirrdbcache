import logging
import pprint
import re
import sys
from whoiscache import types as T

"""
Parse data from WHOIS servers
"""

class ParseFailure(ValueError):
    pass

class SerialRangeError(Exception):
    """The requested update is out of range"""
    def __init__(self, message, first, last):
        self.first = first
        self.last = last

        super(SerialRangeError, self).__init__(message)

class OutOfSyncError(Exception):
    """Like serial error, but without serial range information"""
    pass


class ErrorResponse(ValueError):
    pass


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
    if not header:
        logging.info("Recevied no update header; skipping updates.")
        return

    current_serial = header['serials'][0]

    while True:
        act_serial = read_act_serial(handle, current_serial)
        if not act_serial:
            break
        record = read_record(handle)
        yield act_serial + (record,)
        current_serial += 1


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



def handle_range_exception(error):
    """
    Parse exception message:

    check if we are out of sync (e.g. too old)
    or not within a desired range
    """
    # Match range " xxxx - yyyy "
    match = re.match(r'.*?(\d+)\W?-\W?(\d+).*', error)
    if not match:
        raise OutOfSyncError(error) # Nothing we could do here
    start = int(match.group(1))
    end = int(match.group(2))
    raise SerialRangeError(error, start, end)



def match_invalid_range_error(line):
    if re.match(r'.*ERROR.*(I|i)nvalid range.*', line):
        handle_range_exception(line)
    if re.match(r'.*ERROR.*serials.*don.t exist.*', line):
        handle_range_exception(line)


def handle_error(line):
    """Handle errors in response"""
    tokens = line.split(':', 3)
    if len(tokens) < 2:
        raise ErrorResponse("General Error")
    try:
        code = int(tokens[1])
        if code == 401:
            handle_range_exception(line)
    except ValueError:
        pass # We could not parse the error code,
             # coming up next: Regex matching.

    match_invalid_range_error(line)

    # Otherwise this is just an error response
    raise ErrorResponse(line)


def read_header(handle):
    """Read START header for version, source and serial range"""
    watchdog = 6 # The header must occur in the first couple of lines
    while True:
        line = handle.readline()
        watchdog -= 1
        if watchdog == 0:
            break
        if line == None:
            continue
        if line == '':
            continue
        if line.startswith('%END'):
            break
        if line.startswith('%START'):
            return parse_header(line)
        if line.startswith('% ERROR') or line.startswith('%ERROR'):
            handle_error(line)


def parse_act_serial(line, fallback_serial=None):
    """Extract serial from action line"""
    serial = line[4:].strip()
    if not serial and fallback_serial:
        serial = str(fallback_serial)
    return serial


def read_act_serial(handle, fallback_serial=None):
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
        if line.startswith('ADD'):
            return ("ADD", parse_act_serial(line, fallback_serial))
        elif line.startswith('DEL'):
            return ("DEL", parse_act_serial(line, fallback_serial))
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


