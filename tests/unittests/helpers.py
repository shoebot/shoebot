import filecmp
import math
import shutil
import sys
from os import environ
from pathlib import Path
from random import seed
from unittest import TestCase
from unittest.mock import Mock

from PIL import Image
from PIL import ImageChops
from wrapt import decorator

from shoebot import create_bot

TEST_DIR = Path(__file__).parent.absolute()
TEST_INPUT_DIR = TEST_DIR / "input/tests"
TEST_OUTPUT_DIR = TEST_DIR / "output/tests"
EXAMPLE_INPUT_DIR = TEST_DIR / "input/examples"
EXAMPLE_OUTPUT_DIR = TEST_DIR / "output/examples"

RUNNING_IN_CI = "CI" in environ


def stub_sideeffect():
    # Stubs are here to give IDEs something to import without complaining.
    NotImplementedError("This dummy stub should not be used directly.")


command_stubs = Mock(side_effect=stub_sideeffect)


def shoebot_named_testfunction(func, num, param):
    """
    The following code:

    @parameterized.expand(
        ["png", "ps", "pdf", "svg"], name_func=shoebot_named_testfunction
    )
    def test_output_formats(self, file_format):
    ....

    Will name tests based on the first parameter:
     test_output_formats_png
     test_output_formats_ps
     test_output_formats_pdf
     test_output_formats_svg
    """
    return f"{func.__name__}_{'_'.join(param[0])}"


def shoebot_named_testclass(cls, num, params_dict):
    """
    parameterized helper to name class based whether 'windowed' is set to True or not.

    The following code:

    @parameterized_class(
        [{"windowed": False}, {"windowed": True}], class_name_func=shoebot_named_testclass
    )
    class TestOutputFormats(ShoebotTestCase):
    ...

    Will name the expanded test classes:
     TestOutputFormatsHeadless
     TestOutputFormatsWindowed
    """
    suffix = "Windowed" if params_dict["windowed"] else "Headless"
    return f"{cls.__name__}{suffix}"


def test_as_bot(outputfile=None, windowed=None, verbose=True):
    @decorator
    def wrapper(wrapped, instance, args, kwargs):
        """
        Decorator that runs code in a method as a shoebot bot.

        This is adapted from ShoebotTestCase.run_code with extra code to
        inject the bot namespace.
        """
        bot = create_bot(
            window=any([instance.windowed, windowed]), outputfile=outputfile
        )

        # Inject the test into the namespace.
        test_name = f"{wrapped.__func__.__name__}"
        bot._namespace[test_name] = wrapped
        bot._namespace["args"] = args
        bot._namespace["kwargs"] = kwargs
        # Inject the bot globals into the test method namespace
        bot._load_namespace(wrapped.__globals__)
        # Inject outputfile as it may be need for image assertions.
        wrapped.__globals__["outputfile"] = outputfile
        # Hack!  Create a function to allow flushing the output file.
        wrapped.__globals__["flush_outputfile"] = lambda: bot._canvas.flush(bot._frame)

        seed(0)
        bot.run(f"{test_name}(*args, **kwargs)", verbose=verbose)

        # cleanup.
        del wrapped.__globals__["outputfile"]

    return wrapper


class ShoebotTestCase(TestCase):
    paths = [
        TEST_INPUT_DIR,
        ".",
        "../..",
    ]  # When specifying a filename these paths will be searched.
    windowed = False  # default is headless.

    _created_directories = set()
    _copied_files = set()

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        """
        Create output directories and copy input images to them so that
        users can view input and output images in using a file manager.
        """
        for input_path, output_path in [
            (TEST_INPUT_DIR, TEST_OUTPUT_DIR),
            (EXAMPLE_INPUT_DIR, EXAMPLE_OUTPUT_DIR),
        ]:
            if output_path in ShoebotTestCase._created_directories:
                continue
            try:
                output_path.mkdir(parents=True)
            except FileExistsError:
                # Directory already existing is expected.
                pass
            else:
                ShoebotTestCase._created_directories.add(output_path)

            if not RUNNING_IN_CI:
                for input_file in input_path.glob("*"):
                    if input_file in ShoebotTestCase._copied_files:
                        continue

                    ShoebotTestCase._copied_files.add(input_file)
                    output_file = output_path / input_file.name
                    try:
                        shutil.copy(input_file, output_file)
                    except FileNotFoundError:
                        pass

    def assertReferenceImage(self, file1, file2):
        """
        Under Linux check the file contents match exactly,
        with assertFilesEqual.

        Under OSX use assertImagesAlmostEqual.
        """
        if sys.platform in ("darwin", "win32"):
            # Rendering on OSX and Windows is slightly different to the original Linux renders.
            self.assertImagesAlmostEqual(file1, file2)
        else:
            # So far Linux output has been identical - this will probably need to
            # change to use image comparison.
            self.assertFilesEqual(file1, file2)

    def assertImagesAlmostEqual(self, file1, file2, error=0.14):
        """
        Assert that the two images have a high level of similarity.

        Linux and OSX have render slightly fonts and lines slightly
        differently, so this can be used under OSX to check against
        reference images originally rendered in Linux.
        """
        with Image.open(file1) as img1, Image.open(file2) as img2:
            diff = ImageChops.difference(img1, img2).histogram()
            sq = (value * (i % 256) ** 2 for i, value in enumerate(diff))
            sum_squares = sum(sq)
            rms = math.sqrt(sum_squares / float(img1.size[0] * img1.size[1]))

            # Error is an arbitrary value, based on values when
            # comparing 2 rotated images & 2 different images.
            self.assertLess(rms, error)

    def assertFilesEqual(self, file1, file2):
        """
        Assert that the two passed in filenames are identical.
        """
        # TODO it would be fairly straightforward to check the contents of images if this is needed.
        self.assertTrue(filecmp.cmp(file1, file2), f"Files differ: {file1} {file2}")

    def assertFileExists(self, filename, msg=None):
        if not Path(filename).is_file():
            self.fail(msg or f"{filename} does not exist.")

    def assertFileSize(self, filename, size=0):
        """
        Assert file exists and is larger than 0 bytes.
        """
        self.assertFileExists(filename)
        self.assertNotEqual(
            size, Path(filename).stat().st_size, f"{filename} is zero bytes."
        )

    @staticmethod
    def run_code(code, outputfile, windowed=False, namespace=None, verbose=True):
        """
        Run shoebot code, sets random.seed to stabilize output.
        """
        bot = create_bot(window=windowed, outputfile=outputfile, namespace=namespace)

        seed(0)
        bot.run(code, verbose=verbose)

    def run_filename(
        self, filename, outputfile, windowed=False, namespace=None, verbose=True
    ):
        """
        Run shoebot from filename.

        Paths in ShoebotTestCase.paths will be searched for the file.

        random.seed is set, to stabilize output.

        outputfile is passed to run_code, e.g. "output.png".

        :param outputfile: File with supported shoebot supported extension, e.g. .png.
        """
        for path in self.paths:
            full_path = Path(path) / filename
            if full_path.is_file():
                with open(full_path) as f:
                    self.run_code(
                        f.read(),
                        outputfile,
                        windowed=windowed,
                        namespace=namespace,
                        verbose=verbose,
                    )
                    return
        else:
            raise ValueError(f"Could not find bot {filename} in paths {self.paths}")
