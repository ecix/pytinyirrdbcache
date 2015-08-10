import re
import parser

###############################################################################
# is a container for the individual whois databases
###############################################################################
class WhoisDatabaseContainer(object):
    def __init__(self):
        self.databases = {}

        import json
        configFile = open("config/whoisDatabases.json","r")
        config = json.load(configFile)
        configFile.close()

        for whoisDatabaseConfig in config:
            WhoisDB(whoisDatabaseConfig, self.databases)

    ###########################################################################
    # print Information about the databases
    ###########################################################################
    def getInfo(self):
        result = []
        for database in self.databases.values():
            result.append(database.getInfo())
        return result
    
    ###########################################################################
    # get the number of databases
    ###########################################################################
    def getDatabaseCount(self):
        return len(self.databases)

    ###########################################################################
    # get the handle for a individual database by name
    ###########################################################################
    def getDatabase(self, name):
        return self.databases[name]

    ###########################################################################
    # get statistics about the container and contained databases
    ###########################################################################
    def getStatistics(self):
        result = {}
        for database in self.databases:
            result[database] = self.databases[database].getStatistics()
        return result

    ###########################################################################
    # rebuild the whois databases from scratch
    ###########################################################################
    def rebuild(self):
        for database in self.databases:
            self.databases[database].rebuild()

    ###########################################################################
    # update the whois databases from the whois servers
    ###########################################################################
    def update(self):
        for database in self.databases:
            self.databases[database].update()


###############################################################################
# reads the input database and discard everything not starting 
###############################################################################
class WhoisDB(object):
    def __init__(self, config, storage):
        # register the database in the database storage
        name = config["name"]
        storage[name] = self

        # the information about the database
        self.__name = name
        self.__dumps = config["dumps"]
        self.__dumpSerial = config["serial"]
        self.__realtimeHost = config["realtimeHost"]
        self.__realtimePort = config["realtimePort"]

        # fill the cache with data
        try:
            self.restore()
        except:
            self.rebuild()

    def getInfo(self):
        result = {}
        result["name"] = self.__name
        result["serial"] = self.__latestSerial
        return result

    ###########################################################################
    # rebuild the database from scratch
    ###########################################################################
    def rebuild(self):
        while True:
            # the containers for the state
            self.__macros = {}
            self.__asnv6 = {}
            self.__asnv4 = {}
            self.__latestSerial = None

            serial1 = self.fetchSerial(self.__dumpSerial)
            for dump in self.__dumps:
                self.loadFile(dump)
            serial2 = self.fetchSerial(self.__dumpSerial)

            if serial1 == serial2:
                self.__latestSerial = serial1
                break
        self.backup()

    def fetchSerial(self, url):
        print(url)
        import urlparse
        parsedUrl = urlparse.urlparse(url)
        path = parsedUrl.path[1:parsedUrl.path.rfind("/")+1]
        filename = parsedUrl.path[parsedUrl.path.rfind("/")+1:]

        self.__rawNumber = ""
        def getNumber(chunk):
            print(chunk)
            self.__rawNumber = self.__rawNumber + chunk

        import ftplib
        ftp = ftplib.FTP(parsedUrl.netloc)
        ftp.login()
        ftp.cwd(path)
        ftp.retrbinary('RETR ' + filename, getNumber)
        ftp.close()

        serial = int(self.__rawNumber)
        return serial

    ###########################################################################
    # rebuild the database from the whois server
    ###########################################################################
    def update(self):
        # fail if current version is unknown
        if not self.__latestSerial:
            return

        # get the update handle from the server
        import socket as socketLib
        updateSocket = socketLib.socket(socketLib.AF_INET, socketLib.SOCK_STREAM)
        updateSocket.connect((self.__realtimeHost, self.__realtimePort))
        updateSocket.send("-g "+self.__name.upper()+":3:"+str(self.__latestSerial)+"-LAST\n")
        handle = updateSocket.makefile()

        # add the update to the database
        self.discardingRead(handle)

        # close the connection
        updateSocket.close()

    ###########################################################################
    # get statistics about this database
    ###########################################################################
    def getStatistics(self):
        #TODO: return actual statistics
        return "nothing"

    ###########################################################################
    # fetch the data like the original tinyirrdbcache does
    # it probably makes sense to split or to rename this
    ###########################################################################
    def fetch(self, macro, ipVersion):
        #create the container for storing the result
        resultContainer = {"prefixes":set(), "macros":set() }

        #select the correct ip version
        if ipVersion == "v4":
            asnBase = self.__asnv4
        else:
            asnBase = self.__asnv6
        
        #TODO: check if this is needed and maybe discard
        if macro in asnBase:
            #TODO: This is wrong
            return asnBase[macro]
        else:
            # get the result
            self.getMacroInformation(macro, asnBase, resultContainer)
            resultContainer["prefixCount"] = len(resultContainer["prefixes"])

            # get the result
            return resultContainer

    ###########################################################################
    # get the information connected to a ASN-macro
    # the information concerns prefixes and ASNs the macro resoves to 
    ###########################################################################
    def getMacroInformation(self, macro, asnBase, resultContainer):
        # check if the macro exists
        if not macro in self.__macros:
            #TODO: FAIL
            return

        # gather information or contained ASNs
        for ASN in self.__macros[macro]:
            # the cycle detection
            if ASN in resultContainer["macros"]:
                continue

            # gather information for the ASN
            prog = re.compile("^AS([0-9]+)$")
            matched = prog.match(ASN)
            if matched:
                # add prefixes for this ASN to the result
                if ASN in asnBase:
                    resultContainer["prefixes"] = resultContainer["prefixes"].union(asnBase[ASN])
                else:
                    #TODO: handle missing ASN
                    continue
            else:
                # store this macro
                resultContainer["macros"].add(ASN)
    
                # recursively gather information for this macro
                tmpResult = self.getMacroInformation(ASN, asnBase, resultContainer)

    def resolveASN(self, asn, ipVersion):
        if ipVersion == "v6":
            asnbase = self.__asnv6
        else:
            asnbase = self.__asnv4

        if asn in asnbase:
            result = list(asnbase[asn])
        else:
            result = []

        return result

    def resolveASNs(self, ipVersion):
        if ipVersion == "v6":
            asns = self.__asnv6
        else:
            asns = self.__asnv4

        return asns

    ###########################################################################
    # resolve a ASN-macro to actual ASNs
    # the Macros the Macro is resoved to are included in the result
    # example AS-CHAOS -> ["AS50472", "AS13020", "AS-IN-BERLIN", "AS29...
    ###########################################################################
    def resolveMacro(self, macro, result=None):
        if not result:
            result = {"asns":set(),"macros":set()}

        # check if the macro exists
        if not macro in self.__macros:
            # TODO: FAIL
            return result

        # gather contained ASNs
        for ASN in self.__macros[macro]:
            # the cycle detection
            if ASN in result["macros"] or ASN in result["asns"]:
                continue

            # recursively resolve macros
            prog = re.compile("^AS([0-9]+)$")
            matched = prog.match(ASN)
            if not matched:
                result["macros"].add(ASN)
                self.resolveMacro(ASN, result)
            else:
                # add the ASN
                result["asns"].add(ASN)

        # return the result
        return result

    ###########################################################################
    # loads a file with whois data into the database
    # the database is not cleared beforehand, so multiple files can be loaded
    ###########################################################################
    def loadFile(self, url):
        import urlparse
        parsedUrl = urlparse.urlparse(url)
        path = parsedUrl.path[1:parsedUrl.path.rfind("/")+1]
        filename = parsedUrl.path[parsedUrl.path.rfind("/")+1:]

        if not parsedUrl.scheme == "ftp":
            return

        fileName = "data/"+self.__name+".db.gz"

        '''
        import ftplib
        fileHandle = open(fileName, 'wb')
        ftp = ftplib.FTP(parsedUrl.netloc)
        ftp.login()
        ftp.cwd(path)
        ftp.retrbinary('RETR ' + filename, fileHandle.write)
        ftp.close()
        fileHandle.close()
        '''

        print("parse file")

        import gzip
        handle = gzip.open(fileName,"r")
        self.discardingRead(handle)
        handle.close()

    ###########################################################################
    # backup the state to an internal backup file
    ###########################################################################
    def backup(self):
        print("backup")

        # create a backup container from state
        backup = {}
        backup["latestSerial"] = self.__latestSerial
        backup["macros"] = {k: list(v) for k, v in self.__macros.items()}
        backup["asnv6"] = {k: list(v) for k, v in self.__asnv6.items()}
        backup["asnv4"] = {k: list(v) for k, v in self.__asnv4.items()}

        # write the backup container to disc
        import json
        handle = open("db/"+self.__name+"_backup.json", "w")
        json.dump(backup, handle)
        handle.close()

    ###########################################################################
    # load state from the internal backup files
    ###########################################################################
    def restore(self):
        print("restore")

        # load the backup container from disc
        import json
        handle = open("db/"+self.__name+"_backup.json", "r")
        backup = json.load(handle)
        handle.close()

        # reconstruct state from the backup container
        self.__latestSerial = backup["latestSerial"]
        self.__macros = {k: set(v) for k, v in backup["macros"].items()}
        self.__asnv6 = {k: set(v) for k, v in backup["asnv6"].items()}
        self.__asnv4 = {k: set(v) for k, v in backup["asnv4"].items()}

    ###########################################################################
    # add a stream of whois data to the database
    ###########################################################################
    def discardingRead(self, handle):
        print("started parsing")

        # set default mode, since parsing whois dumps doesn't anounce add
        mode = "ADD"

        # read the stream line for line
        counter = 0
        while True:
            # read a line
            line = handle.readline()

            # break at end of file
            if line == "":
                break

            # set the mode and version if given
            if line.startswith("ADD "):
                mode = "ADD"
                self.__latestSerial = int(line[4:].strip())
                continue
            if line.startswith("DEL "):
                mode = "DEL"
                self.__latestSerial = int(line[4:].strip())
                continue

            # handle a block if given
            if line.startswith("as-set:"):
                parser.AsSetPacketParser(handle, line, self.__macros, mode)
            elif line.startswith("route:"):
                parser.RoutePacketParser(handle, line, self.__asnv4, mode)
            elif line.startswith("route6:"):
                parser.RoutePacketParser(handle, line, self.__asnv6, mode)
            else:
                parser.PacketParser(handle, line, mode)

            # print an indication of progress
            counter += 1
            if counter % 100000 == 0:
                print(counter)
                pass
        
        # print an indication of progress
        print("finished parsing")
