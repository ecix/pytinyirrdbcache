######################
# Module Autoloading #
######################
import pkgutil

# Module whitelist; only those modules are loaded!
MODULES = [
    'streamParser',
    'helper',
]

for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if module_name in MODULES:
        module = loader.find_module(module_name).load_module(module_name)
        exec('%s = module' % module_name)
