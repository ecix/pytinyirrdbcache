import re

###############################################################################
# reads the input database and discard everything not starting 
# server as class to inherit from
# can be used to ignore blocks
###############################################################################
class PacketParser(object):
    def __init__(self, handle, head, mode):
        # handle the information for the head
        self.handleHead(head)

        # store important parameters
        self._mode = mode

        # parse the block line by line
        while True:
            # read the line
            line = handle.readline()
            
            #handle the line
            self.handleLine(line)

            # break at end of file
            if line == "":
                break
            
            # break at end of block
            if line == "\n":
                break

        # process the information gathered for this packet
        self.processPacket()
    
    ####################################################
    # handles the line
    # serves as abstract method to be overwritten later
    # can be used to ignore blocks
    ####################################################
    def handleLine(self,line):
        pass

    ####################################################
    # handles the head of a packet
    # serves as abstract method to be overwritten later
    # can be used to ignore blocks
    ####################################################
    def handleHead(self,line):
        pass

    ####################################################
    # processes the data collected from this packet
    # serves as abstract method to be overwritten later
    # can be used to ignore blocks
    ####################################################
    def processPacket(self):
        pass

###############################################################################
# parses the as-set (defenition?) packets and stores the macros
###############################################################################
class AsSetPacketParser(PacketParser):
    def __init__(self, handle, head, macroStore, mode):
        self.__macro = None
        self.__members = set()
        self.__macroStore = macroStore

        super(AsSetPacketParser,self).__init__(handle, head, mode)
    
    ###########################################################################
    # extract the name of the macro
    ###########################################################################
    def handleHead(self,line):
        #extract the name of the macro
        tmp = re.sub('^as-set: *','',line)
        tmp = re.sub(' *\n','',tmp)
        tmp = re.sub('#.*','',tmp)
        tmp = tmp.upper()

        #TODO: validate input!

        # store the name
        self.__macro = tmp
        self.__continuedMembers = False

    ####################################################
    # gather the member contained in the body
    ####################################################
    def handleLine(self,line):
        # get the members for this line
        if self.__continuedMembers or line.startswith("members:"):
            # remove clutter
            line = line.strip()
            if not self.__continuedMembers:
                tmp = re.sub('^members: *','',line)
                tmp = re.sub(' *\n','',tmp)
                tmp = re.sub('#.*','',tmp)
            else:
                tmp = line

            # continue line if needed
            if line.endswith(","):
                self.__continuedMembers = True
            else:
                self.__continuedMembers = False

            # get members
            members = tmp.split(",")
            members = map(lambda x: x.strip(),members)
            members = map(lambda x: x.upper(),members)
            members = filter(lambda x: x.startswith("AS"),members)
            members = filter(lambda x: not x == "",members)

            #TODO: validate input!

            # store members
            self.__members = self.__members.union(members)
        else:
            self.__continuedMembers = False

    ###########################################################################
    # change the macro
    ###########################################################################
    def processPacket(self):
        # add the macro
        if self._mode == "ADD":
            if not self.__macro.startswith("AS"):
                print("???")
                print(self.__macro)
            self.__macroStore[self.__macro] = self.__members
        # remove the macro
        elif self._mode == "REMOVE":
            if self.__macro in self.__macroStore:
                del self.__macroStore[self.__macro]
            

###############################################################################
# parses the route (defenition?) packets and stores the prefix
###############################################################################
class RoutePacketParser(PacketParser):
    def __init__(self, handle, head, asnBase, mode):
        self.__prefix = None
        self.__origin = None
        self.__asnBase = asnBase

        super(RoutePacketParser,self).__init__(handle, head, mode)

    ###########################################################################
    # extracts the prefix
    ###########################################################################
    def handleHead(self,line):
        # extract the prefix
        tmp = re.sub('^route6?: *','',line)
        tmp = re.sub(' *\n','',tmp)
        tmp = re.sub('#.*','',tmp)

        #TODO: validate input!

        # store the prefix
        self.__prefix = tmp
        
    ###########################################################################
    # extracts the ASN the prefix originates from
    ###########################################################################
    def handleLine(self,line):
        # get the origin
        if line.startswith("origin:"):
            # remove clutter
            tmp = re.sub('^origin: *','',line)
            tmp = re.sub(' *\n','',tmp)
            tmp = re.sub('#.*','',tmp)
            tmp = tmp.strip()

            # postprocess the origin
            tmp = tmp.upper()

            #TODO: validate input!

            # store the origin
            self.__origin = tmp

            if not self.__origin.startswith("AS"):
                print("!!!")
                print(self.__origin)
    
    ###########################################################################
    # change the prefixes
    ###########################################################################
    def processPacket(self):
        # create the origin if neccessary
        if not self.__origin in self.__asnBase:
            self.__asnBase[self.__origin] = set()

        # add the prefix
        if self._mode == "ADD":
            self.__asnBase[self.__origin].add(self.__prefix)
        # remove the prefix
        elif self._mode == "REMOVE":
            self.__asnBase[self.__origin].difference(self.__members)
            
