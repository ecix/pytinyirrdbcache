from collections import namedtuple


# Update wrapper
Update = namedtuple('Update', 'action,serial,record')

# Record types
Macro = namedtuple('Macro', 'name,members')
Route = namedtuple('Route', 'route,origin')
Route6 = namedtuple('Route6', 'route6,origin')
Unrecognised = namedtuple('Unrecognised', 'key')

# Action types
ADD = namedtuple('Add', '')()
DEL = namedtuple('Del', '')()
