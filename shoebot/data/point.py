class Point(object):
    '''
    Taken from Nodebox and modified
    '''
    def __init__(self, *args):
        self.cmd = args[0]
        if len(args) == 3:
            self.x, self.y, self.z = args
        if len(args) == 2:
            self.x, self.y = args
        elif len(args) == 1:
            self.x, self.y = args[0]
        elif len(args) == 0:
            self.x = self.y = 0.0
        else:
            raise ValueError, _("Wrong initializer for Point object")

    def __repr__(self):
        return (self.x, self.y)
    def __str__(self):
        return "Point(%.3f, %.3f)" % (self.x, self.y)
    def __getitem__(self,key):
        return (float(self.x), float(self.y))[key]
    def __eq__(self, other):
        if other is None: return False
        return self.x == other.x and self.y == other.y
    def __ne__(self, other):
        return not self.__eq__(other)

