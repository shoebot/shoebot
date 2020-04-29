import re
import sys
import unittest

from pathlib import Path
from textwrap import dedent
from unittest.mock import patch, Mock

from tests.unittests.helpers import ShoebotTestCase

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Regex from semver.org to recognize if text is a semantic version.
SEMVER_REGEX = "^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"


class TestSetup(unittest.TestCase):
    def test_version(self):
        """
        Mock setuptools.setup and find the version parameter passed to it.

        Verify that the version is in semantic version format.
        """
        with patch("setuptools.setup", Mock()) as _setup:
            import setup

            args, kwargs = setup.setup.call_args_list[0]

            version = kwargs.get("version")
            match = re.match(SEMVER_REGEX, version).groups()

            self.assertIn("version", kwargs)
            self.assertIsNotNone(match)
            self.assertRegex(version, SEMVER_REGEX)


if __name__ == "__main__":
    unittest.main()
