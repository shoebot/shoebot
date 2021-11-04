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

        image_name = tmpdirpath / Path(args.script).with_suffix(".png").name
        cmd = f"sbot {args.script} --repeat {args.framenumber} \
            --outputfile {image_name}"
        result = subprocess.call(cmd, shell=True)
        if result != 0:
            sys.exit(1)

        fileglob = tmpdirpath / "*.png"
        cmd = f"ffmpeg -y -loglevel 24 -r 30 -f image2 -pattern_type glob \
          -i '{fileglob}' -c:v libx264 -crf 20 -movflags faststart -c:a aac \
          -pix_fmt yuv420p {outfile}"
        subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
