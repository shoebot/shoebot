#!/usr/bin/env python

import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))


def gedit_install():
    version = None
    try:
        version = subprocess.check_output(["gedit", "--version"]).strip()
    except OSError:
        print("gedit not found")
        return
    v_str = version.rpartition(b" ")[-1]
    major, minor, patch = map(int, v_str.split(b"."))

    if major == 2:
        subprocess.call([sys.executable, f"{here}/gedit2-plugin/install.py"])
    elif major == 3:
        if minor < 12:
            subprocess.call([sys.executable, f"{here}/gedit3-plugin/install.py"])
        else:
            os.path.join(here, "gedit3.12-plugin")
            subprocess.call([sys.executable, f"{here}/gedit3.12-plugin/install.py"])
    else:
        print(f"Unknown gedit version {version}")


if __name__ == "__main__":
    print("Install gedit plugin")
    gedit_install()
