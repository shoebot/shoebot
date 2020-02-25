import filecmp

from pathlib import Path
from random import seed
from unittest import TestCase

from shoebot import create_bot


class ShoebotTestCase(TestCase):
    output_dir = Path(__file__).parent.absolute() / "output"
    paths = [".", "../.."]  # When specifying a filename these paths will be searched.
    hide_gui = True

    def assertOutputFilesEqual(self, file1, file2):
        """
        Assert that the two passed in filenames are identical.
        """
        # TODO it would be fairly straightforward to check the contents of images if this is needed.
        self.assertTrue(filecmp.cmp(file1, file2), f"Files differ: {file1} {file2}")

    def assertOutputFile(self, filename):
        """
        Verify file exists and is more than 0 bytes.
        """
        self.assertTrue(Path(filename).is_file(), f"{filename} does not exist.")
        self.assertNotEqual(
            0, Path(filename).stat().st_size, f"{filename} is zero bytes."
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

        Paths in ShoebotTestCase.paths will be seatched for the file.

        random.seed is set, to stabilize output.

        outputfile is passed to run_code, e.g. "output.png".

        :param outputfile: File with supported shoebot supported extension, e.g. .png.
        """
        for path in self.paths:
            full_path = Path(path) / filename
            if full_path.is_file():
                with open(full_path) as f:
                    self.run_code(f.read(), outputfile)
                    return
        else:
            raise ValueError(f"Could not find bot {filename} in paths {self.paths}")
