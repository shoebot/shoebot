import random
import unittest

from parameterized import parameterized

from shoebot.core import CairoCanvas
from shoebot.core import CairoImageSink
from shoebot.graphics import BezierPath
from shoebot.graphics import CLOSE
from shoebot.graphics import LINETO
from shoebot.graphics import MOVETO
from shoebot.graphics import PathElement
from shoebot.graphics import RLINETO
from shoebot.graphics import RMOVETO
from shoebot.grammar import NodeBot


class TestBezier(unittest.TestCase):
    # Test the Bezier API directly.
    def setUp(self):
        sink = CairoImageSink("output-bezier.png")
        canvas = CairoCanvas(sink)
        self.bot = NodeBot(canvas=canvas)

    def test_copy_path(self):
        """Verify BezierPath.copy returns a new path with copies of all the
        elements."""
        path = BezierPath(self.bot)
        path.lineto(4, 4)
        path.lineto(10, 10)
        path.closepath()

        copied_path = path.copy()

        self.assertIsNot(path, copied_path)
        self.assertCountEqual(path, copied_path)


class TestPathElement(unittest.TestCase):
    # Test the Bezier API directly.
    # TODO:  Add tests for:
    #  CURVETO, RCURVETO
    #  ARC, ELLIPSE and None

    @parameterized.expand([CLOSE, MOVETO, RMOVETO])
    def test_xy_no_controlpoints(self, cmd):
        """PathElement types close, moveto, rmoveto all store an x, y
        coordinate and all other properties are set to None."""
        position = random.randint(0, 800), random.randint(0, 800)

        element = PathElement(cmd, *position)

        self.assertEqual(position, (element.x, element.y))
        self.assertIsNone(element.c1x)
        self.assertIsNone(element.c1y)
        self.assertIsNone(element.c2x)
        self.assertIsNone(element.c2y)

    @parameterized.expand([LINETO, RLINETO])
    def test_xy_and_one_controlpoints(self, cmd):
        """PathElement types lineto, rlineto store an x, y and a single control
        point.

        All other properties are set to None.
        """
        # TODO:  Not verified against Nodebox. this test
        #        reflects current Shoebot behaviour which
        #        not be correct.
        position = random.randint(0, 800), random.randint(0, 800)

        element = PathElement(cmd, *position)

        self.assertEqual(position, (element.x, element.y))
        self.assertEqual(position, (element.c1x, element.c1y))
        self.assertEqual((element.c2x, element.c2y), position)


if __name__ == "__main__":
    unittest.main()
