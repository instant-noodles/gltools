import argparse

from glbin import main
from pathlib import Path

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Griftlands Bin to SCML Converter (by Instant-Noodles)")
    parser.add_argument("-ver", "--version", action="version", version="%(prog)s 1.0")
    parser.add_argument("input", help="folder containing Griftlands anim.bin, atlas0.tex, and build.bin files")
    args=parser.parse_args()
    uInput=args.input
    path_input=None

    try:
        path_input=Path(uInput).absolute() if Path(uInput).absolute().is_file() or Path(uInput).absolute().is_dir() else Path().absolute()/uInput
    except:
        print(f"-- {uInput} is not a valid path")
        
    if path_input!=None:
        main(path_input)
