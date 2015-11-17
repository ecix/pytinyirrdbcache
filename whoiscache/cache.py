import cPickle as pickle
import copy
import gevent
import logging
import os
import os.path
import socket
import subprocess
import time

from whoiscache import parsers, settings, state


class WhoisCache(object):
    """
    Top level manager of a whois cache of an upstream.
    Should manage all aspects of cache including persistance,
    synchronisation, and making data available.
    """
    def __init__(self, config):
        self.config = config
        self.state = state.WhoisCacheState()
        self.logger = logging.root
        self.cache_path = os.path.join(settings.CACHE_DATA_DIRECTORY,
                                       "%s.cache" % self.config['name'])

    @property
    def name(self):
        return self.config['name']

    def update(self):
        """
        All in one functon to restore and/or update and/or download state.
        """
        in_sync = False

        if not self.state.serial:
            if os.path.exists(self.cache_path):
                self.logger.info("Restoring state from %s", self.cache_path)
                self.state = pickle.load(open(self.cache_path))

        if self.state.serial:
            try:
                self.update_telnet()
                in_sync = True
            except parsers.ErrorResponse as e:
                self.logger.warning("Error in realtime update: %s" % e)

        if not in_sync:
            os.path.exists(self.cache_path) and os.unlink(self.cache_path)
            clone = copy.copy(self)
            clone.state = state.WhoisCacheState()
            clone.update_dump()
            self.state = clone.state

        self.logger.info("Loaded state@%s", self.state.serial)

    def save(self):
        self.logger.info("Saving state@%s to %s", self.state.serial,
                         self.cache_path)
        pickle.dump(self.state, open(self.cache_path, 'w'))

    def update_dump(self):
        """ Update state from dump """
        serial, dump_path = self.download_dump()
        if serial != self.state.serial:
            self.load_dump(serial, dump_path)

    def load_dump(self, serial, dump_path):
        """ Build the cache from a dump """
        self.logger.info("Loading dump at %s" % dump_path)
        # Use zcat in separate process for speedup
        if dump_path.endswith('gz'):
            zcat = subprocess.Popen(['zcat', dump_path], -1,
                                    stdout=subprocess.PIPE)
            fh = zcat.stdout
        else:
            fh = open(dump_path)
        for record in long_thing("Loading dump", parsers.parse_dump(fh)):
            update = ("ADD", serial, record)
            self.state.apply_update(update)
        self.save()

    def download_dump(self):
        """ Download latest data dump and serial from upstream """
        dump_dir = os.path.join(settings.CACHE_DATA_DIRECTORY,
                                "dump_%s" % self.config['name'])
        os.path.exists(dump_dir) or os.mkdir(dump_dir)
        serial_path = os.path.join(dump_dir,
                                   os.path.basename(self.config['serial_uri']))
        dump_path = os.path.join(dump_dir,
                                 os.path.basename(self.config['dump_uri']))
        existing_serial = None
        have_serial, have_dump = map(os.path.exists, [serial_path, dump_path])
        if have_serial and have_dump:
            existing_dump_serial = open(serial_path).read().strip()
        self.logger.info("Downloading %s", self.config['serial_uri'])
        download_file(serial_path, self.config['serial_uri'])
        new_serial = open(serial_path).read().strip()
        if new_serial != existing_serial:
            self.logger.info("Downloading %s", self.config['dump_uri'])
            download_file(dump_path, self.config['dump_uri'])
        return (new_serial, dump_path)

    def update_telnet(self):
        """ Get latest updates from upstream telnet """
        sock = socket.socket()
        self.logger.info("Connecting to %s", self.config['telnet'])
        sock.connect(self.config['telnet'])
        req = "-g %s:3:%s-LAST\n" % (self.config['name'],
                                     int(self.state.serial)+1)
        self.logger.info("Sending %s", req.strip())
        sock.send(req)
        fh = sock.makefile()
        saw_updates = 0
        for update in long_thing("Process updates",
                                 parsers.parse_updates(fh)):
            saw_updates = 1
            self.state.apply_update(update)
        if saw_updates:
            self.save()
        else:
            self.logger.info("No new updates")


def download_file(dest, uri):
    """ Download a file using CURL """
    os.path.exists(dest) and os.unlink(dest)
    tmp = dest + '.part'
    cmd = 'curl -s -o "%s" "%s"' % (tmp, uri)
    logging.info('+ ' + cmd)
    rc = os.system(cmd)
    if rc != 0:
        raise IOError("Command exited with %s: %s" % (rc, cmd))
    os.rename(tmp, dest)


def long_thing(name, iter, notify=100000):
    """ Wrapper to log progress of a long operation """
    logging.info("Starting %s", name)
    start_t = time.time()
    for i, item in enumerate(iter):
        yield item
        if i % 100 == 0:
            gevent.sleep(0)  # yield to other threads
        if i and i % notify == 0:
            logging.info(str(i))
    logging.info("Finished %s in %.2f seconds", name, time.time() - start_t)
