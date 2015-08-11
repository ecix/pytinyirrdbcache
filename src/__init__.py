#
# CSC-API Server
#

from flask import Flask

from os import environ
from os import path

# Get config file from environment
config_file = environ['PY_TINY_IRRD_CACHE_CONFIG']
if not config_file:
    print("Config file not specified in ENV: PY_TINY_IRRD_CACHE_CONFIG")
    raise

# Resolve absolute path
config_file = path.abspath(config_file)

app = Flask(__name__, static_url_path='')
app.config.from_pyfile(config_file)

app.debug_log_format = '%(levelname)s - [%(pathname)s:%(lineno)d]: %(message)s'

######################
# Module Autoloading #
######################
from csc import resources
import pkgutil

# Module whitelist; only those modules are loaded!
MODULES = [
    'inc',
    'webinterface',
]

for loader, module_name, is_pkg in pkgutil.walk_packages(resources.__path__):
    if module_name in MODULES:
        module = loader.find_module(module_name).load_module(module_name)
        app.logger.info("Registering module: %s", module_name)
        exec('%s = module' % module_name)
app.logger.info("Done registering")
