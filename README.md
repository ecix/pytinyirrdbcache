
# pytinyirrdcache

This service chaches whois data in an optimised way


## Setup

Initialize your development environment by running

```bash
./bin/venv_init
```

This will setup your virtualenv and will install all required
libraries (as specified in `requirements.txt`).

# Running the server

```bash
./bin/run_server
```

# Adding new modules

Please note that there is a module whitelist within `src/inc/__init__.py`
called MODULES. You have to update this list when adding new modules so that
they are loaded.
