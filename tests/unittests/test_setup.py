import re
import sys
import unittest
from importlib import reload
from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock
from unittest.mock import mock_open
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Regex from semver.org to recognize if text is a semantic version.
SEMVER_REGEX = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"


class TestSetup(unittest.TestCase):
    @patch("setuptools.setup", Mock())
    def test_version(self):
        """Mock setuptools.setup and find the version parameter passed to it.

        Verify that the version is in semantic version format.
        """
        import setup

        setup = reload(setup)

        args, kwargs = setup.setup.call_args_list[0]

        version = kwargs.get("version")
        match = re.match(SEMVER_REGEX, version).groups()

        self.assertIn("version", kwargs)
        self.assertIsNotNone(match)
        self.assertRegex(version, SEMVER_REGEX)

    @patch("setuptools.setup", Mock())
    def test_setup_parses_version_from_version_file(self):
        """Test that setup loads and parses the version from the file VERSION,
        deliberately uses a version that is not the real version.

        Mocks open, to do an end to end test using mock data.
        """
        expected_version = "1.2.1"
        example_versionfile_content = dedent(
            """\
            name            Shoebot
            desc            vector graphics scripting application
            version         1.2.1
            url             http://shoebot.net
            packager        Ricardo Lafuente <r@manufacturaindependente.org>
            """,
        )

        with patch("builtins.open", mock_open(read_data=example_versionfile_content)):
            import setup

            setup = reload(setup)

            args, kwargs = setup.setup.call_args_list[0]

            actual_version = kwargs.get("version")

            self.assertEqual(actual_version, expected_version)


if __name__ == "__main__":
    unittest.main()
