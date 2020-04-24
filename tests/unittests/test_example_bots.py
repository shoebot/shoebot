import unittest

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
            ("examples/libraries/lsystem/growing_plant.bot", "lsystem--growing_plant", {"FRAME": 60}),
        ]
    )
    def test_static_example_bots(self, filename, output_prefix, namespace=None):
        """
        Check non animated example bots render matches the reference images.
        """
        actual_output = self.example_output_dir / f"{output_prefix}-actual.png"
        expected_output = self.example_input_dir / f"{output_prefix}-expected.png"

        # Always run the script, even if the reference image is not present:
        # this catches more errors and means the output can still be visually inspected.
        self.run_filename(filename,
                          outputfile=actual_output, windowed=self.windowed, namespace=namespace)

        self.assertFileExists(expected_output, f"Missing example output image: {expected_output}.")
        self.assertFileSize(actual_output)
        self.assertReferenceImage(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main(buffer=False)
