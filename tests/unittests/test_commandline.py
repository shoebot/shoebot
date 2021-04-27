import subprocess
import unittest

from parameterized import parameterized


class TestCommandLine(unittest.TestCase):
    """
    See if the commands can start successfully, by starting
    them with an option that does nothing: --version

    When dependencies are not installed these commands will
    not return an error.
    """

    def test_sbot_starts(self):
        """
        Try and run sbot --help and check return code

        This may fail if a dependency is not instaled properly.
        """
        # TODO, sbot --version would be better, but we don't have that yet.
        cmd = ["sbot", "--help"]

        result = subprocess.run(cmd, capture_output=True)

        self.assertEqual(
            result.returncode,
            0,
            f"Failed to start shoebot, output:\n{result.stderr.decode('utf-8')}",
        )

    def test_shoebot_starts(self):
        """
        Try and run shoebot --help and check return code

        This may fail if a dependency is not instaled properly.
        """
        # TODO, sbot --version would be better, but we don't have that yet.
        cmd = ["shoebot", "--help"]

        result = subprocess.run(cmd, capture_output=True)

        self.assertEqual(
            result.returncode,
            0,
            f"Failed to start shoebot, output:\n{result.stderr.decode('utf-8')}",
        )

    @parameterized.expand([("sbot", "this_will_fail()",), ("sbot", "-dt", "this_will_fail()")])
    def test_sbot_errorcode_on_invalid_code(self, *cmd):
        """
        Try and run sbot, call a function that doesn't exist and verify

        The errorcode is set as expected.
        """
        result = subprocess.run(cmd, capture_output=True)

        self.assertEqual(
            result.returncode,
            1,
            f"Failed to start shoebot, output:\n{result.stderr.decode('utf-8')}",
        )


if __name__ == "__main__":
    unittest.main()
