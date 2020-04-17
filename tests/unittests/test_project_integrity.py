"""
Check that lists of packages in the install script and travis match.
"""
import re
import yaml

from subprocess import run
from unittest import TestCase


class TestTravisConfiguration(TestCase):
    """
    Check that the packages in install_dependencies.sh match the ones
    in .travis
    """

    @classmethod
    def setUpClass(cls):
        # TODO load travis YAML
        with open("../../.travis.yml") as f:
            cls.travis_conf = yaml.safe_load(f)

        cls.install_script_data = cls.read_install_script()

    @classmethod
    def read_install_script(cls):
        package_name_re = r'([A-Z]*_PACKAGES)="(.*)"'
        script_data = {}
        with open("../../install/install_dependencies.sh") as f:
            for line in f.readlines():
                matches = re.match(package_name_re, line)
                if matches and matches.groups():
                    script_data[matches.groups()[0]] = matches.groups(0)[
                        1
                    ].split()  # e.g. script_data["DEB_PACKAGES"] = ["package1", "package2"]
        return script_data

    def test_apt_package_list(self):
        travis_packages = self.travis_conf["addons"]["apt"]["packages"]
        script_packages = self.install_script_data["DEB_PACKAGES"]

        self.assertListEqual(
            travis_packages,
            script_packages,
            "deb packages in .travis should match DEV_PACKAGES in install script.",
        )

    def test_homebrew_package_list(self):
        travis_packages = self.travis_conf["addons"]["homebrew"]["packages"]
        script_packages = self.install_script_data["HOMEBREW_PACKAGES"]

        self.assertListEqual(
            travis_packages,
            script_packages,
            "List of homebrew packages in .travis should match HOMEBREW_PACKAGES in the install script.",
        )


if __name__ == "__main__":
    TestTravisConfiguration().setUpClass()
