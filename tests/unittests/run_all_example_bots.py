"""
This uses the test infrastructure but is NOT intended to run every time tests are run as it would be very inefficient.
"""
import os
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

from parameterized import parameterized
from tests.unittests.helpers import ShoebotTestCase, TEST_DIR

PROJECT_DIR = Path(__file__).absolute().parent.parent.parent
EXAMPLES_DIR = PROJECT_DIR / "examples"

LIBRARY_EXAMPLES_DIR = EXAMPLES_DIR / "libraries"


def get_bot_relpath(bot_path):
    return bot_path.relative_to(EXAMPLES_DIR)


def get_bot_prefix(rel_bot_path):
    if str(rel_bot_path).startswith("libraries"):
        return str(rel_bot_path.parent.relative_to(LIBRARY_EXAMPLES_DIR)).replace(
            os.sep, "--"
        )
    return str(rel_bot_path.parent.relative_to(EXAMPLES_DIR)).replace(os.sep, "--")


# Tuples containing every bot for passing to parameterized
EXAMPLE_BOTS = [(example_bot,) for example_bot in EXAMPLES_DIR.rglob("*.bot")]

# Override specific bot options:
EXAMPLE_BOT_OVERRIDES = {
    "libraries/lsystem/growing_plant.bot": {"FRAME": 60},
    "animation/parade.bot": {"FRAME": 584},
}
EXCLUDE_EXAMPLE_BOTS = [
    # Audio bots cause issues as the audio thread stays open
    ("libraries/audio/70s_wallpaper.bot",),
    ("libraries/audio/reactive_cells.bot",),
    ("libraries/audio/tunnel_graph.bot",),
    # Web examples don't work
    ("libraries/web/01-retrieve.bot",),
    ("libraries/web/05-wikipedia.bot",),
    ("libraries/web/07-kuler.bot",),
    ("libraries/web/02-parse.bot",),
    ("libraries/web/09-clear_cache.bot",),
    ("libraries/web/standalone/_web_example1.bot",),
    ("libraries/web/standalone/_web_example6.bot",),
    ("libraries/web/standalone/_web_example2.bot",),
    ("libraries/web/standalone/_web_example3.bot",),
    ("libraries/web/standalone/_web_example4.bot",),
    ("libraries/web/standalone/_web_example8.bot",),
    ("libraries/web/standalone/_web_example5.bot",),
    ("libraries/web/standalone/_web_example9.bot",),
    ("libraries/web/standalone/_web_example7.bot",),
]


class RunAllExampleBots(ShoebotTestCase):
    """
    Abusing the testing infrastructure to generate images of every bot.
    """
    __unittest_skip__ = True
    __unittest_skip_why__ = "Generating example images should only be run manually."

    # Customise the output directory
    image_output_dir = TEST_DIR / "run_all_bots"
    # Do not copy expected output to the output directory
    copy_expected_output = False

    @parameterized.expand(EXAMPLE_BOTS)
    def test_run_examples_and_generate_images(self, bot_path):
        """
        Check non animated example bots render matches the reference images.
        """
        rel_bot_path = str(get_bot_relpath(bot_path))
        if (rel_bot_path,) in EXCLUDE_EXAMPLE_BOTS:
            self.skipTest(f"Excluded example {rel_bot_path}")
        namespace = EXAMPLE_BOT_OVERRIDES.get(rel_bot_path, {})

        output_prefix = get_bot_prefix(bot_path)
        output_filename = str(
            Path(self.image_output_dir).absolute()
            / f"{output_prefix}-{bot_path.stem}.png"
        )

        output = StringIO()
        # Many examples fail if run outside their own directory.
        cwd = os.getcwd()
        try:
            os.chdir(str(bot_path.parent))
            with redirect_stdout(output):
                self.run_filename(
                    bot_path,
                    outputfile=output_filename,
                    windowed=self.windowed,
                    namespace=namespace,
                )
        except Exception as e:
            self.assertFalse(f"{rel_bot_path} raised exception {e}")
        finally:
            os.chdir(cwd)

        self.assertFileExists(
            output_filename,
            f"{bot_path} failed to generate example output image at: {output_filename}.",
        )
        self.assertFileSize(output_filename)


if __name__ == "__main__":
    # Enable running this manually:
    RunAllExampleBots.__unittest_skip__ = False
    unittest.main(buffer=False)
