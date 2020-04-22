import sys
import unittest

from pathlib import Path
from parameterized import parameterized, parameterized_class

from tests.unittests.helpers import ShoebotTestCase, shoebot_named_testclass


@parameterized_class(
    [{"windowed": False}, {"windowed": True}], class_name_func=shoebot_named_testclass
)
class TestExampleOutput(ShoebotTestCase):
    windowed = False  # False for headless, True for GUI

    @parameterized.expand(
        [
            ("examples/basic/primitives.bot", "basic--primitives"),
            ("examples/libraries/graph/shortest_path.bot", "graph--shortest_path"),
        ]
    )
    def test_static_example_bots(self, filename, output_prefix):
        """
        Check non animated example bots render matches the reference images.
        """
        actual_output = self.example_output_dir / f"{output_prefix}-actual.png"
        expected_output = self.example_input_dir / f"{output_prefix}-expected.png"

        self.run_filename(filename, outputfile=actual_output, windowed=self.windowed)

        self.assertFileSize(actual_output)
        self.assertReferenceImage(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main(buffer=False)
