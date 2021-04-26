import os
import shutil
import argparse
import subprocess


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

    tempdir = "tmp_export/"
    tempfilename = "tmp_export/" + args.script.split("/")[-1].replace(".bot", ".png")
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)
    result = subprocess.call(
        f"sbot {args.script} --repeat {args.framenumber} --outputfile {tempfilename}",
        shell=True,
    )
    subprocess.call(
        f"ffmpeg -loglevel 8 -r 30 -f image2 -pattern_type glob -i 'tmp_export/*.png' -c:v libx264 -crf 20 -movflags faststart -c:a aac -pix_fmt yuv420p {outfile}",
        shell=True,
    )
    shutil.rmtree(tempdir)


if __name__ == "__main__":
    main()
