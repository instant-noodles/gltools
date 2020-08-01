import argparse

from gltex import main
from pathlib import Path

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Griftlands Tex to PNG Converter (by Instant-Noodles)")
    parser.add_argument("-ver", "--version", action="version", version="%(prog)s 1.1")
    parser.add_argument("input", help="file/folder containing Griftlands .tex files")
    args=parser.parse_args()
    uInput=args.input
    path_input=None

    try:
        path_input=Path(uInput).absolute() if Path(uInput).absolute().is_file() or Path(uInput).absolute().is_dir() else Path().absolute()/uInput
    except:
        print(f"-- {uInput} is not a valid path")
        
    if path_input!=None:
        main(path_input)
