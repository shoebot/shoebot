from objects import *

class TuioProfile(object):
    """An abstract profile as defined in the TUIO protocol"""

    # the OSC address that is used for the messages of this profile
    address = None

    # the name that is used to populate a convenient variable to access objs()
    list_label = None

    def __init__(self):
        self.objects = {}
        self.sessions = []

    def set(self, client, message):
        """
        The state of each alive (but unchanged) fiducial is periodically
        resent with 'set' messages.
        """
        raise NotImplementedError

    def alive(self, client, message):
        """
        The 'alive' message contains the session ids of all alive fiducials
        known to reacTIVision.
        """
        raise NotImplementedError

    def fseq(self, client, message):
        """
        fseq messages associate a unique frame id with a set of set
        and alive messages
        """
        client.last_frame = client.current_frame
        client.current_frame = message[3]

    def objs(self):
        """
        Returns a generator list of tracked objects which are recognized with
        this profile and are in the current session.
        """
        for obj in self.objects.itervalues():
            if obj.sessionid in self.sessions:
                yield obj

class Tuio2DcurProfile(TuioProfile):
    """A profile for a 2D cursor, e.g. a finger."""
    address = "/tuio/2Dcur"
    list_label = "cursors"

    def __init__(self):
        super(Tuio2DcurProfile, self).__init__()

    def set(self, client, message):
        sessionid = message[3]
        if sessionid not in self.objects:
            self.objects[sessionid] = Tuio2DCursor(sessionid)
        self.objects[sessionid].update(sessionid, message[4:])

    def alive(self, client, message):
        if client.refreshed():
            self.sessions = message[3:]
            for obj in self.objects.keys():
                if obj not in self.sessions:
                    del self.objects[obj]

class Tuio2DobjProfile(TuioProfile):
    """A profile for a 2D tracking object, e.g. a fiducial."""
    address = "/tuio/2Dobj"
    list_label = "objects"

    def __init__(self):
        super(Tuio2DobjProfile, self).__init__()

    def set(self, client, message):
        sessionid, objectid = message[3:5]
        if objectid not in self.objects:
            self.objects[objectid] = Tuio2DObject(objectid, sessionid)
        self.objects[objectid].update(sessionid, message[5:])

    def alive(self, client, message):
        if client.refreshed():
            self.sessions = message[3:]
