import unittest

from parameterized import parameterized

from tests.unittests.helpers import ShoebotTestCase
from tests.unittests.helpers import test_as_bot

class TestXImportLibs(ShoebotTestCase):
    @parameterized.expand(
        [
	   ("beziereditor",),
           ("boids",),
           ("colors",),
           ("cornu",),
           ("database",),
           ("graph",),
           ("lsystem",),
           ("photobot",),
           ("sbaudio", "numpy"),
           ("sbopencv", "opencv", "numpy"),
           ("sbvideo", "opencv", "numpy"),
           ("supershape",),
           ("svg",),
           ("tuio",),
        ],
    )
    @test_as_bot()
    def test_path_commands(self, lib, *requires):
        """Attempt to ximport each of the libraries shoebot provides."""
        for required in requires:
            try:
                __import__(required)
            except ImportError as e:
                self.skipTest(f"Skipping Test, required library not found: {e}")

        ximport(lib)


if __name__ == "__main__":
    unittest.main(buffer=False)
