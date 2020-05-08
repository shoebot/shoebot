import unittest

from tests.unittests.helpers import ShoebotTestCase
from textwrap import dedent

class TestLifecycle(ShoebotTestCase):
    def test_lifecycle(self):
        """
        Test that loading an svg image doesn't raise an exception (this was a bug).
        """
        code = dedent(
            f"""\
        print("Run frame:", FRAME)
        """
        )

        self.run_code(code, outputfile="/tmp/blah.png", windowed=True, 
        kwargs={"run_forever": True}
        )

        # TODO:  assert output was   "Run frame: 1"

        # TODO: Need  a better way of generating output we don't use.
        self.fail("TODO - complete this test + make useful")

if __name__ == "__main__":
    unittest.main()
