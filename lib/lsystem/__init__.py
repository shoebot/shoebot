### CREDITS ##########################################################################################

# Copyright (c) 2007 Frederik De Bleser.
# See LICENSE.txt for details.

__author__    = "Frederik De Bleser, Mark Meyer, Tom De Smedt"
__version__   = "1.9.3"
__copyright__ = "Copyright (c) 2007 Frederik De Bleser"
__license__   = "MIT"

### L-SYSTEM #########################################################################################

from shoebot.data import CORNER, CENTER
from sys import maxint

class LSystem(object):
    
    def __init__(self):
        
        self.angle = 20
        self.segmentlength = 40
        self.decrease = 0.7
        self.threshold = 3.0
        
        # The system's growth pattern.
        # Each rule can contain command symbols 
        # or a character referring to another rule.
        # This default ruleset draws a nice geometric tree.
        self.rules = {
        	"1" : "FFF[--2][-2][+2][++2]",
        	"2" : "FFF[--3][-3][+4][++4]",
        	"3" : "FFF[--5][-5][+5][++5]",
        	"4" : "FFF[--5][-5][+5][++5]",
        	"5" : "FFFFF[--5][++5]"   
        }
        self.root = "1"
        
        # You also define your own command symbols.
        self.commands = {}
        
        self._segments = 0
        self._duration = 0
        self._timed = False
        self.cost = 0.25
        
    def _get_d(self): return self.segmentlength
    def _set_d(self, v): self.segmentlength = v
    d = property(_get_d, _set_d)
		
    def _reset(self):
    	
		""" Resets the number of drawn segments and the duration.

		To calculate the number of segments or the total time needed,
		we need to recurse through LSystem._grow().
		Before that, the draw(), segments() and duration() command
		will reset both tally variables.    	
    	
		"""

		self._segments = 0
		self._duration = 0

    def _grow(self, generation, rule, angle, length, time=maxint, draw=True):

        """ Recurse through the system.
        
        When a segment is drawn, the LSsytem.segment() method will be called.
        You can customize this method to create your own visualizations.
        It takes an optional time parameter. 
        
        If you divide this parameter by LSsytem.duration() you get 
        a number between 0.0 and 1.0 you can use as an alpha value for example.
        
        The method also has an id parameter which is a unique number 
        between 0 and LSystem.segments.
        
        """

        if generation == 0: 
        	# We are at the bottom of the system so now we now the total time needed.
        	self._duration = 1 + maxint-time
        
        if length <= self.threshold: 
        	# Segment length has fallen below the threshold, stop recursing.
        	self._duration = 1 + maxint-time
        	return

        if rule in self.commands: 
        	# Custom command symbols:
        	# If the rule is a key in the LSsytem.commands dictionary,
        	# execute its value which is a function taking 6 parameters:
        	# lsystem, generation, rule, angle, length and time.
            self.commands[rule](self, generation, rule, angle, length, time)
        
        if draw:
            # Standard command symbols:
            # f signifies a move,
            # + and - rotate either left or right, | rotates 180 degrees,
            # [ and ] are for push() and pop(), e.g. offshoot branches,
            # < and > decrease or increases the segment length,
            # ( and ) decrease or increases the rotation angle.
	        if   rule == "f": _ctx.translate(0, -min(length, length*time))
	        elif rule == "-": _ctx.rotate(max(-angle, -angle*time))
	        elif rule == "+": _ctx.rotate(min(+angle, +angle*time))
	        elif rule == "|": _ctx.rotate(180)
	        elif rule == "[": _ctx.push()
	        elif rule == "]": _ctx.pop()

        if rule in self.rules \
        and generation > 0 \
        and time > 0:
        	# Recursion:
        	# Occurs when there is enough "life" (i.e. generation or time).
        	# Generation is decreased and segment length scaled down.
        	# Also, F symbols in the rule have a cost that depletes time.
            for cmd in self.rules[rule]:
            	# Modification command symbols:
                if   cmd == "F": time -= self.cost
                elif cmd == "!": angle = -angle
                elif cmd == "(": angle *= 1.1
                elif cmd == ")": angle *= 0.9
                elif cmd == "<": length *= 0.9
                elif cmd == ">": length *= 1.1
                self._grow(
                    generation-1,
                    cmd, 
                    angle, 
                    length*self.decrease, 
                    time,
                    draw
                )
        
        elif rule == "F" \
        or (rule in self.rules and self.rules[rule] == ""):
        	# Draw segment:
        	# If the rule is an F symbol or empty (e.g. in Penrose tiles).
        	# Segment length grows to its full size as time progresses.
            self._segments += 1
            if draw and time > 0:
            	length = min(length, length*time)
            	if self._timed:
            	    self.segment(length, generation, time, id=self._segments)
                else:
                    self.segment(length, generation, None, id=self._segments)
            	_ctx.translate(0, -length)
        
    def segment(self, length, generation, time=None, id=None):
    	_ctx.push()
    	_ctx.line(0, 0, 0, -length)
    	_ctx.scale(0.65)
    	_ctx.rect(-length/2, -length*3/2, length, length)
    	_ctx.pop()
       
    def draw(self, x, y, generation, time=None, ease=None):
    	
    	""" Draws a number of generations at the given position.
    	
    	The time parameter can be used to progress the system in an animatiom.
    	As time nears LSystem.duration(generation), more segments will be drawn.
    	
    	The ease parameter can be used to gradually increase the branching angle
    	as more segments are drawn.
    	
    	"""
        
        angle = self.angle
        if time is not None and ease:
        	angle = min(self.angle, self.angle * time / ease)

    	self._timed = True
    	if not time:
    		self._timed = False
    		time = maxint        

    	mode = _ctx.transform()
        _ctx.transform(CORNER)
        _ctx.push()
        _ctx.translate(x, y)
        self._reset()
        self._grow(generation, self.root, angle, self.d, time, draw=True)
        _ctx.pop()
        _ctx.transform(mode)
        
    def segments(self, generation, time=None):
    	
    	""" Returns the number of segments drawn for a number of generations.
    	
    	The number of segments that are drawn to the screen
    	depends of the number of generations and the amount of time.
    	Each F command has a cost that depletes time.
    	Segments will stop being drawn if generation reaches 0,
    	when there is no time left 
    	or when the segment length falls below LSystem.threshold.
    	
    	"""
    	
    	if not time: 
    		time = maxint
    	_ctx.push()
        self._reset()
        self._grow(generation, self.root, self.angle, self.d, time, draw=False)
        _ctx.pop()
        return self._segments

    def duration(self, generation):
    	
    	""" Returns the total draw time needed based on the current cost.
    	
    	In an animation, the system will expand as time progresses.
    	Each F command that draws a segment has a cost that depletes time.
    	To calculate the total amount of time for a number of generations,
    	we need to recurse through the system.
    	Time does not flow through the system linearly, 
    	it "branches" from generation to generation.
    	
    	"""
    	_ctx.push()
        self._reset()
        self._grow(generation, self.root, self.angle, self.d, draw=False)
        _ctx.pop()
        return max(self._duration, 0.1)

def lsystem(angle=20, segmentlength=40, rules={}, root=None):
	
	s = LSystem()
	s.angle = angle
	s.segmentlength = segmentlength
	if len(rules) > 0: 
		s.rules = rules
	if root: 
		s.root = root
	return s
	
create = lsystem

### TREE RULESETS ####################################################################################

def oak(angle=20, segmentlength=40):
	rules = {
  		"1" : "FF[++FF[2][+FF2]][-FF3]",
		"2" : "F-F-F+[2]F+F+F+F+([2]",
		"3" : "F+F+F-[2]F-F-F-F-([2]"
	}
	return lsystem(angle, segmentlength, rules) 
	
def beech(angle=15, segmentlength=40):
	rules = {
		"1" : "FF[-2][3][+3]",
		"2" : "FF+F-F-F[FFF3][+3]-F-F3",
		"3" : "FF-F+F+F[2][-2]+F+F2"
	}
	return lsystem(angle, segmentlength, rules)  

def yew(angle=20, segmentlength=40):
    rules = {
        "1" : "F-F+F[++2][F+2][F-2][--2]",
		"2" : "F+FF-F[++3][+3][-4][--4]",
		"3" : "-[4]F-FF-FF-FF-F[4]",
		"4" : "+[3]F+FF+FF+FF+F[3]"
    }
    return lsystem(angle, segmentlength, rules) 

def elm(angle=20, segmentlength=40):
    rules = {
        "1" : "F-F+F+F[(+2]-FF-F[(-2](2",
		"2" : "F+F-FF[(+1]-FFF[(-1](1",
    }
    return lsystem(angle, segmentlength, rules) 

def hawthorn(angle=20, segmentlength=40):
	rules = {
        "1" : "F-F+2",
		"2" : "F-[[-F-F+F+FF2]+FF2]+F[+F+F+FF2]-FF+F-F2"        
    }
	return lsystem(angle, segmentlength, rules) 

def eucalyptus(angle=23, segmentlength=40):
	rules = {
		"1" : "FFF+[2]F+(>[---1]",
		"2" : "FFF[1]+[1]+[1]+[1]"
    }
	return lsystem(angle, segmentlength, rules) 

def acacia(angle=25, segmentlength=40):
	
	rules = {
    	"1" : "FFF-[-F+F[2]-[1]]+[+F+F[1]-[1]]",
		"2" : "FF-[-F+F]+[+F+F2]"        
    }
	return lsystem(angle, segmentlength, rules) 

gnarled = oak
tall    = beech
great   = yew 
old     = elm
crooked = hawthorn  
slender = eucalyptus
strong  = acacia

trees = [gnarled, tall, great, old, crooked, slender, strong]

######################################################################################################

#stroke(0)
#tree = strong()
#tree.draw(250, 500, 6)
