# -*- coding: utf-8 -*-
import math

class UpdateError(Exception):
    pass

class TuioObject(object):
    def __init__(self, *args):
        pass
        
    def __repr__(self):
        return "<%s %s> " % (self.__class__.__name__, self.label)

    def update(self):
        """
        The method which gets executed when a new state of the object was
        received.
        """
        raise NotImplementedError

    def _label(self):
        """
        The text that should be shown in the object reprentation.
        """
        raise NotImplementedError

    label = property(_label)

class Tuio2DCursor(TuioObject):
    """
    An abstract object representing a cursor, e.g. a finger.
    """
    def __init__(self, sessionid):
        super(Tuio2DCursor, self).__init__(sessionid)
        self.sessionid = sessionid
        self.xpos = self.ypos = self.xmot = self.ymot = self.mot_accel = 0.0
    
    def update(self, sessionid, args):
        if len(args) == 5:
            self.sessionid = sessionid
            self.xpos, self.ypos, self.xmot, self.ymot, self.mot_accel = args[0:5]
        else:
            raise UpdateError

    def _label(self):
        return " "

    label = property(_label)

class Tuio2DObject(TuioObject):
    """
    An abstract object representing a fiducial.
    """
    def __init__(self, objectid, sessionid):
        super(Tuio2DObject, self).__init__(objectid, sessionid)
        self.id = objectid
        self.sessionid = sessionid
        self.xpos = self.ypos = self.angle = 0.0
        self.xmot = self.ymot = self.mot_accel = self.mot_speed = 0.0
        self.rot_speed = self.rot_accel = 0.0

    def update(self, sessionid, args):
        if len(args) == 8:
            self.sessionid = sessionid
            self.xpos, self.ypos = args[0:2]
            self.angle = (180//math.pi)*args[2]
            self.xmot, self.ymot = args[3:5]
            self.rot_vector = args[5]
            self.mot_accel = args[6]
            self.rot_accel = args[7]
        else:
            raise UpdateError
    
    def _label(self):
        return "%s, %s degrees" % (str(self.id), str(int(self.angle)))

    label = property(_label)
