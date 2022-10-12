import unittest

from parameterized import parameterized
from parameterized import parameterized_class
from tests.unittests.helpers import (
    EXAMPLE_INPUT_DIR,
    shoebot_example_render_testfunction,
)
from tests.unittests.helpers import EXAMPLE_OUTPUT_DIR
from tests.unittests.helpers import shoebot_named_testclass
from tests.unittests.helpers import ShoebotTestCase


@parameterized_class(
    [{"windowed": False}, {"windowed": True}], class_name_func=shoebot_named_testclass
)
class TestExampleOutput(ShoebotTestCase):
    windowed = False  # False for headless, True for GUI

    """
    Tests that run examples.

    Where we are lacking bots to test features, running an existing example
    can work to excersize an API.

    Be mindful this can be expensive (in CPU, Memory and time), before adding
    examples.
    """

    @parameterized.expand(
        [
            ("examples/basic/primitives.bot", "basic--primitives"),
            (
                "examples/libraries/lsystem/growing_plant.bot",
                "lsystem--growing_plant",
                {"FRAME": 60},
            ),
        ]
    )
    def test_static_example_bots(self, filename, output_prefix, namespace=None):
        """Check non animated example bots render matches the reference
        images."""
        self.skipTest("FIXME - update these images, once runs-3-times is merged")
        actual_output = f"{EXAMPLE_OUTPUT_DIR}/{output_prefix}-actual.png"
        expected_output = f"{EXAMPLE_INPUT_DIR}/{output_prefix}-expected.png"

        # Always run the script, even if the reference image is not present:
        # this catches more errors and means the output can still be visually inspected.
        self.run_filename(
            filename,
            outputfile=actual_output,
            windowed=self.windowed,
            namespace=namespace,
        )

        self.assertFileExists(
            expected_output, f"Missing example output image: {expected_output}."
        )
        self.assertFileSize(actual_output)
        self.assertReferenceImage(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main(buffer=False)
