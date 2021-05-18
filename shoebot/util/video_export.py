import os
import shutil
import argparse
import subprocess
import tempfile
from pathlib import Path


def main():
    global parser
    parser = argparse.ArgumentParser("usage: sbot [options] inputfile.bot [args]")
    parser.add_argument("script", help="Shoebot script to run")

    parser.add_argument(
        "-o",
        "--outputfile",
        dest="outputfile",
        help="destination file (.mp4 only)",
        metavar="FILE",
    )
    parser.add_argument(
        "-f",
        "--frames",
        dest="framenumber",
        default=300,
        help="number of frames to export (default 300)",
    )

    args, extra = parser.parse_known_args()

    if not args.outputfile:
        outfile = args.script.replace(".bot", ".mp4")
    else:
        outfile = args.outputfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdirpath = Path(tmpdirname)
        imgbasename = args.script.split("/")[-1].replace(".bot", ".png")
        tempfilename = Path(tmpdirpath, imgbasename)
        cmd = f"sbot {args.script} --repeat {args.framenumber} --outputfile {tempfilename}"
        result = subprocess.call(cmd, shell=True)

        fileglob = tmpdirpath / "*.png"
        cmd = f"ffmpeg -loglevel 8 -r 30 -f image2 -pattern_type glob \
          -i '{fileglob}' -c:v libx264 -crf 20 -movflags faststart -c:a aac \
          -pix_fmt yuv420p {outfile}"
        subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
