import unittest

from tests.unittests.helpers import ShoebotTestCase
from textwrap import dedent


class TestLifecycle(ShoebotTestCase):
    """
    These tests don't use @test_as_bot as they need to run exactly like
    """

    # def test_lifecycle_non_dynamic_bot(self):
    #     """
    #     Test that loading an svg image doesn't raise an exception (this was a bug).
    #     """
    #     code = dedent(
    #         f"""\
    #     print("Run frame:", FRAME)
    #
    #     raise Exception()
    #     """
    #     )
    #
    #     self.run_code(
    #         code,
    #         outputfile="/tmp/blah.png",
    #         windowed=True,
    #         run_forever=True,
    #     )
    #
    #     # TODO:  assert output was   "Run frame: 1"
    #
    #     # TODO: Need  a better way of generating output we don't use.
    #     self.fail("TODO - complete this test + make useful")

    def test_lifecycle_dynamic_bot(self):
        """
        Test that loading an svg image doesn't raise an exception (this was a bug).
        """
        code = dedent(
            f"""\
        if FRAME == 2:
            raise Exception()
        
        print("Run frame: FRAME")
            
        def setup():
            print("Setup frame:", FRAME)
        
        def draw():
            print("Draw frame:", FRAME)

        raise Exception()
        """
        )

        self.run_code(
            code,
            outputfile="/tmp/blah.png",
            windowed=True,
            run_forever=True,
        )

        # TODO:  assert output was   "Run frame: 1"

        # TODO: Need  a better way of generating output we don't use.
        self.fail("TODO - complete this test + make useful")


if __name__ == "__main__":
    unittest.main()
