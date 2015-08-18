from collections import namedtuple


# Update wrapper
Update = namedtuple('Update', 'action,serial,record')

# Record types
Macro = namedtuple('Macro', 'name,members')
Route = namedtuple('Route', 'prefix,origin')
Route6 = namedtuple('Route6', 'prefix,origin')
Unrecognised = namedtuple('Unrecognised', 'key')

# Action types
ADD = namedtuple('ADD', '')
DEL = namedtuple('DEL', '')

# Cache data
WhoisCacheData = namedtuple('WhoisCacheData', 'serial,macros,prefix4,prefix6')
