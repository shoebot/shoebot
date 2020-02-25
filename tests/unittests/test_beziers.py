import unittest

from shoebot.core import CairoCanvas, CairoImageSink
from shoebot.data import BezierPath
from shoebot.grammar import NodeBot

class BezierTest(unittest.TestCase):
    # Test the bot API directly.
    def setUp(self):
        sink = CairoImageSink("output.png")
        canvas = CairoCanvas(sink)
        self.bot = NodeBot(canvas=canvas)
    
    def test_copy_path(self):
        """
        Verify BezierPath.copy returns a new path with copies of all the elements.
        """
        path = BezierPath(self.bot)
        path.lineto(4,4)
        path.lineto(10, 10)
        path.closepath()

        copied_path = path.copy()
        
        self.assertIsNot(path, copied_path)
        self.assertCountEqual(path, copied_path)

if __name__ == '__main__':
    unittest.main()
