
"""
Settings resolver. Do not add settings here!

DEVELOPERS:

If you need to override some settings, create a file called
settings_local_orca_backend.py in this folder and do the overrides there.
This file is added to the .gitignore so your local settings will not be
committed.

SYSADMINS:

If you would like to persist settings such as credentials and logins to a
different location in the system, create the settings_local_orca_backend
file and add it to the PYTHONPATH environment variable when running
the service.
"""

from whoiscache.settings_global import *

try:
    from settings_local_whoiscache import *
except ImportError:
    pass
