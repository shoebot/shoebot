"""
Check that lists of packages in the install script and travis match.
"""
import re
from pathlib import Path
from subprocess import run
from unittest import TestCase

import yaml

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent


class TestTravisConfiguration(TestCase):
    """
    Check that the packages in install_dependencies.sh match the ones
    in .travis.yml
    """

    @classmethod
    def setUpClass(cls):
        # load travis YAML
        with open(PROJECT_DIR / ".travis.yml") as f:
            cls.travis_conf = yaml.safe_load(f)

        cls.install_script_data = cls.read_install_script()

    @classmethod
    def read_install_script(cls):
        """
        Seach install_depdencies.sh for lines starting with
        {PLATFORM}_PACKAGES, e.g. DEB_PACKAGES, HOMEBREW_PACKAGES

        :return: a dict where the key is DEB_PACKAGES and the value is the list of packages.
        """
        package_name_re = r'([A-Z]*_PACKAGES)="(.*)"'
        script_data = {}
        with open(PROJECT_DIR / "install/install_dependencies.sh") as f:
            for line in f.readlines():
                matches = re.match(package_name_re, line)
                if matches and matches.groups():
                    script_data[matches.groups()[0]] = matches.groups(0)[
                        1
                    ].split()  # e.g. script_data["DEB_PACKAGES"] = ["package1", "package2"]
        return script_data

    def test_apt_package_list(self):
        """
        Verify APT_PACKAGES in the install script matches the apt list in travis.
        """
        travis_packages = list(*self.travis_conf["addons"]["apt"]["packages"])
        script_packages = self.install_script_data["DEB_PACKAGES"]

        self.assertListEqual(
            travis_packages,
            script_packages,
            "deb packages in .travis.yml should match DEV_PACKAGES in install script.",
        )

    def test_homebrew_package_list(self):
        """
        Verify HOMEBREW_PACKAGES in the install script matches the homebrew list in travis.
        """
        travis_packages = self.travis_conf["addons"]["homebrew"]["packages"]
        travis_packages.remove("black")
        script_packages = self.install_script_data["HOMEBREW_PACKAGES"]

        self.assertListEqual(
            travis_packages,
            script_packages,
            "homebrew packages in .travis.yml should match HOMEBREW_PACKAGES in install script.",
        )


if __name__ == "__main__":
    TestTravisConfiguration().setUpClass()
