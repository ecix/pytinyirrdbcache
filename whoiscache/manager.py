import gevent
import logging
import os
import os.path
import socket
import subprocess
import time

from whoiscache import parsers, settings, state, types as T


class WhoisCacheManager(gevent.Greenlet):
    """
    Top level manager of a whois cache of an upstream.
    Should manage all aspects of cache including persistance,
    synchronisation, and making data available.
    """
    def __init__(self, config):
        self.config = config
        self.ready = False
        self.state = state.WhoisCacheState()
        self.logger = logging.root
        self.cache_path = os.path.join(settings.CACHE_DATA_DIRECTORY,
                                       "%s.cache" % self.config['name'])

    def start(self):
        """ Thread target """
        self.load()

        while True:
            self.update()
            time.sleep(settings.WHOIS_UPDATE_INTERVAL)

    def load(self):
        """
        Load the cache. Until this method returns, the cache is not ready
        to use.
        """
        if os.path.exists(self.cache_path):
            self.logger.info("Restoring state from %s", self.cache_path)
            self.state.load(open(self.cache_path))
            self.logger.info("State loaded @%s", self.state.serial)
        else:
            paths = self.download_dump()
            self.load_dump(*paths)
            self.save()
        self.update()
        self.ready = True

    def save(self):
        self.logger.info("Saving state to %s", self.cache_path)
        self.state.save(open(self.cache_path, 'w'))

    def load_dump(self, serial_path, dump_path):
        """ Build the cache from a dump """
        self.logger.info("Loading dump at %s" % dump_path)
        start_t = time.time()
        serial = open(serial_path).read().strip()
        # Use zcat in separate process for speedup
        zcat = subprocess.Popen(['zcat', dump_path], -1, stdout=subprocess.PIPE)
        for record in parsers.parse_dump(zcat.stdout):
            update = T.Update(T.ADD, serial, record)
            self.state.apply_update(update)
        self.logger.info("Loaded %s in %.2f seconds", dump_path,
                         time.time() - start_t)

    def download_dump(self):
        """ Download latest data dump and serial from upstream """
        dump_dir = os.path.join(settings.CACHE_DATA_DIRECTORY,
                                "dump_%s" % self.config['name'])
        os.path.exists(dump_dir) or os.mkdir(dump_dir)
        serial_path = os.path.join(dump_dir,
                                   os.path.basename(self.config['serial_uri']))
        dump_path = os.path.join(dump_dir,
                                 os.path.basename(self.config['dump_uri']))
        if not (os.path.exists(serial_path) and os.path.exists(dump_path)):
            self.logger.info("Downloading %s", self.config['serial_uri'])
            download_file(serial_path, self.config['serial_uri'])
            self.logger.info("Downloading %s", self.config['dump_uri'])
            download_file(dump_path, self.config['dump_uri'])
        else:
            self.logger.info("Using already downloaded dump at %s" % dump_dir)
        return (serial_path, dump_path)

    def update(self):
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
        for update in parsers.parse_updates(fh):
            saw_updates = 1
            self.state.apply_update(update)
        if saw_updates:
            self.save()
        else:
            self.logger.info("No new updates")


def download_file(dest, uri):
    tmp = dest + '.part'
    cmd = 'curl -s -o "%s" "%s"' % (tmp, uri)
    logging.info('+ ' + cmd)
    rc = os.system(cmd)
    if rc != 0:
        raise IOError("Command exited with %s: %s" % (rc, cmd))
    os.rename(tmp, dest)
