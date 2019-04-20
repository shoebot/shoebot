import unittest
from shoebot.core import CairoCanvas, CairoImageSink
from shoebot.data import BezierPath
from shoebot.grammar import NodeBot


class BezierTest(unittest.TestCase):
    def setUp(self):
        sink = CairoImageSink("output.png")
        canvas = CairoCanvas(sink)
        self.bot = NodeBot(canvas=canvas)

    def test_copy_len(self):
        b1 = BezierPath(self.bot)
        b1.lineto(4, 4)
        b1.lineto(10, 10)
        b1.closepath()
        b2 = b1.copy()
        self.assertEqual(len(b1), len(b2))


if __name__ == "__main__":
    unittest.main()
