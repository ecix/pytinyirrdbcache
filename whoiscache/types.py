from collections import namedtuple


# Record types
Macro = namedtuple('Macro', 'name,members')
Route = namedtuple('Route', 'prefix,origin')
Route6 = namedtuple('Route6', 'prefix,origin')
Unrecognised = namedtuple('Unrecognised', 'key')
