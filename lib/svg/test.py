# This script tests if the SVG library works correctly.
import unittest

svg = ximport("__init__")
reload(svg)

BLACK = Color()
WHITE = Color(1)
RED = Color(1, 0, 0)

class SVGTest(unittest.TestCase):

    def test_import(self):
        paths = svg.parse(open('blocktest.svg').read())
        # Blocktest contains 9 paths:
        # first row: 0: black fill | 1: black stroke | 2: black thick stroke
        # second row: 3: white fill | 4: white stroke | 5: white thick stroke
        # third row: 6: red fill | 7: red stroke | 8: red thick stroke
        self.assertEqual(9, len(paths))
        # First row
        # Path 0: black fill
        self.assertFill(paths[0], BLACK)
        self.assertNoStroke(paths[0])
        self.assertStrokewidth(paths[0], 1)
        # Path 1: black stroke
        self.assertNoFill(paths[1])
        self.assertStroke(paths[1], BLACK)
        self.assertStrokewidth(paths[1], 1)
        # Path 2: black thick stroke
        self.assertNoFill(paths[2])
        self.assertStroke(paths[2], BLACK)
        self.assertStrokewidth(paths[2], 10)
        # Second row
        # Path 3: white fill
        self.assertFill(paths[3], WHITE)
        self.assertNoStroke(paths[3])
        self.assertStrokewidth(paths[3], 1)
        # Path 4: white stroke
        self.assertNoFill(paths[4])
        self.assertStroke(paths[4], WHITE)
        self.assertStrokewidth(paths[4], 1)
        # Path 5: white thick stroke
        self.assertNoFill(paths[5])
        self.assertStroke(paths[5], WHITE)
        self.assertStrokewidth(paths[5], 10)
        # Third row
        # Path 6: red fill
        self.assertFill(paths[6], RED)
        self.assertNoStroke(paths[6])
        self.assertStrokewidth(paths[6], 1)
        # Path 7: red stroke
        self.assertNoFill(paths[7])
        self.assertStroke(paths[7], RED)
        self.assertStrokewidth(paths[7], 1)
        # Path 8: red thick stroke
        self.assertNoFill(paths[8])
        self.assertStroke(paths[8], RED)
        self.assertStrokewidth(paths[8], 10) 
        
    def assertFill(self, path, c):
        self.assertColorEquals(c, path.fill)        
        
    def assertNoFill(self, path):
        self.assertColorEquals(Color(0, 0), path.fill)

    def assertStroke(self, path, c):
        self.assertColorEquals(c, path.stroke)

    def assertNoStroke(self, path):
        self.assertColorEquals(Color(0, 0), path.stroke)
        
    def assertStrokewidth(self, path, width):
        self.assertEqual(width, path.strokewidth)
        
    def assertColorEquals(self, c1, c2):
        self.assertEquals(c1.red, c1.red)
        self.assertEquals(c1.green, c1.green)
        self.assertEquals(c1.blue, c1.blue)
        self.assertEquals(c1.alpha, c1.alpha)
        
suite = unittest.TestLoader().loadTestsFromTestCase(SVGTest)
suite.debug()
print "All tests passed."