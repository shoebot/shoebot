import filecmp
import math
import shutil
import sys

from os import environ
from pathlib import Path
from PIL import Image, ImageChops
from random import seed
from unittest import TestCase

from shoebot import create_bot

TEST_DIR = Path(__file__).parent.absolute()
RUNNING_IN_CI = "CI" in environ


def shoebot_named_testfunction(func, num, param):
    return f"{func.__name__}_{'_'.join(param[0])}"


def shoebot_named_testclass(cls, num, params_dict):
    suffix = "Windowed" if params_dict["windowed"] else "Headless"
    return f"{cls.__name__}{suffix}"


class ShoebotTestCase(TestCase):
    test_input_dir = TEST_DIR / "input/tests"
    test_output_dir = TEST_DIR / "output/tests"
    example_input_dir = TEST_DIR / "input/examples"
    example_output_dir = TEST_DIR / "output/examples"
    paths = [test_input_dir, ".", "../.."]  # When specifying a filename these paths will be searched.
    windowed = False  # default is headless.

    _created_directories = set()
    _copied_files = set()

    @classmethod
    def setUpClass(cls):
        """
        Create output directories and copy input images to them so that
        users can view input and output images in using a file manager.
        """
        for input_path, output_path in [
            (cls.test_input_dir, cls.test_output_dir),
            (cls.example_input_dir, cls.example_output_dir),
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
                    shutil.copy(input_file, output_file)

    def assertReferenceImage(self, file1, file2):
        """
        Under Linux check the file contents match exactly,
        with assertFilesEqual.

        Under OSX use assertImagesAlmostEqual.
        """
        if sys.platform == "darwin":
            # Rendering on OSX is slightly different to the original Linux renders.
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

    def assertFileSize(self, filename, size=0):
        """
        Assert file exists and is larger than 0 bytes.
        """
        self.assertTrue(Path(filename).is_file(), f"{filename} does not exist.")
        self.assertNotEqual(
            size, Path(filename).stat().st_size, f"{filename} is zero bytes."
        )

    def run_code(self, code, outputfile, windowed=False):
        """
        Run shoebot code, sets random.seed to stabilize output.
        """
        bot = create_bot(window=windowed, outputfile=outputfile)

        seed(0)

        bot.run(code)

    def run_filename(self, filename, outputfile, windowed=False):
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
                    self.run_code(f.read(), outputfile, windowed=windowed)
                    return
        else:
            raise ValueError(f"Could not find bot {filename} in paths {self.paths}")
