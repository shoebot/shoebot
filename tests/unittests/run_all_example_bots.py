"""This uses the test infrastructure but is NOT intended to run every time
tests are run as it would be very inefficient."""
import os
import sys
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

from parameterized import parameterized
from tests.unittests.helpers import ShoebotTestCase, TEST_DIR, shoebot_example_render_testfunction

PROJECT_DIR = Path(__file__).absolute().parent.parent.parent
EXAMPLES_DIR = PROJECT_DIR / "examples"

LIBRARY_EXAMPLES_DIR = EXAMPLES_DIR / "libraries"


def get_bot_relpath(bot_path):
    return bot_path.relative_to(EXAMPLES_DIR)


def get_bot_prefix(rel_bot_path):
    if str(rel_bot_path).startswith("libraries"):
        return str(rel_bot_path.parent.relative_to(LIBRARY_EXAMPLES_DIR)).replace(
            os.sep, "--",
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
    # TODO: Photobot is currently broken
    ("libraries/photobot/blur.bot",),
    ("libraries/photobot/crossfade.bot",),
    # Audio bots cause issues as the audio thread stays open
    ("libraries/audio/audio-circles2.bot",),
    ("libraries/audio/70s_wallpaper.bot",),
    ("libraries/audio/reactive_cells.bot",),
    ("libraries/audio/tunnel_graph.bot",),
    # gradients have not been ported to cairo yet (expected failure)
    ("libraries/color/shading_example_1.bot",),
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
    """Abusing the testing infrastructure to generate images of every bot."""
    EXAMPLE_BOT_FILTER = []

    __unittest_skip__ = os.getenv("RUN_EXAMPLE_BOTS", "N").lower() not in (*"yt1", "yes", "true")
    __unittest_skip_why__ = "Generating example images should only be run manually."

    # Customise the output directory
    image_output_dir = TEST_DIR / "run_all_bots"
    # Do not copy expected output to the output directory
    copy_expected_output = False

    @parameterized.expand(EXAMPLE_BOTS, name_func=shoebot_example_render_testfunction)
    def test_run_examples_and_generate_images(self, bot_path):
        """Render image from non animated example bot."""
        rel_bot_path = str(get_bot_relpath(bot_path))
        if self.EXAMPLE_BOT_FILTER and rel_bot_path in self.EXAMPLE_BOT_FILTER:
            self.skipTest("Bot not included in filter.")

        if (rel_bot_path,) in EXCLUDE_EXAMPLE_BOTS:
            self.skipTest(f"Excluded example {rel_bot_path}")

        namespace = EXAMPLE_BOT_OVERRIDES.get(rel_bot_path, {})

        output_prefix = get_bot_prefix(bot_path)
        output_filename = str(
            Path(self.image_output_dir).absolute()
            / f"{output_prefix}-{bot_path.stem}.png",
        )
        log_output_filename = str(
            Path(self.image_output_dir).absolute()
            / f"{output_prefix}-{bot_path.stem}.log",
        )
        error_output_filename = str(
            Path(self.image_output_dir).absolute()
            / f"{output_prefix}-{bot_path.stem}-error.log",
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
            with open(log_output_filename, 'w+') as f:
                f.write(output.getvalue())
            self.assertFalse(f"{rel_bot_path} raised exception {e}")
        else:
            with open(error_output_filename, 'w+') as f:
                f.write(output.getvalue())
        finally:
            os.chdir(cwd)
        self.assertFileExists(
            output_filename,
            f"{rel_bot_path} failed to generate example output image at: {output_filename}.",
        )
        self.assertFileSize(output_filename)


if __name__ == "__main__":
    import sys

    example_bot_filter = sys.argv[1:]
    sys.argv = sys.argv[0:1]

    # Enable running this manually:
    RunAllExampleBots.__unittest_skip__ = False
    if example_bot_filter:
        RunAllExampleBots.EXAMPLE_BOT_FILTER = example_bot_filter

    unittest.main(buffer=False, argv=sys.argv, verbosity=4)
