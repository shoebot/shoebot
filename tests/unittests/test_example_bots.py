import unittest

from pathlib import Path
from parameterized import parameterized, parameterized_class

from tests.unittests.helpers import ShoebotTestCase


@parameterized_class([{"windowed": False}, {"windowed": True}])
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
        Check non animated example bots against their expected output.
        """
        actual_output = self.output_dir / f"{output_prefix}-actual.png"
        expected_output = self.output_dir / f"{output_prefix}-expected.png"

        self.run_filename(filename, outputfile=actual_output, windowed=self.windowed)

        self.assertOutputFile(actual_output)
        self.assertOutputFilesEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main(buffer=False)
