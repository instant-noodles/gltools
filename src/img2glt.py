import argparse
import os

def img2glt(image_file):

    # everything happens where the image is saved
    os.chdir(os.path.dirname(image_file.name))
    base_filename = os.path.splitext(os.path.basename(image_file.name))[0]

    original_file = open(base_filename + ".tex", "rb")
    if not original_file:
        print(f"Original file {original_file.name} not found!")
        return False

    # read original klei file header from original texture file
    original_magic = original_file.read(4)
    klei_file_header = ""
    if original_magic == b"KTEX":
        klei_file_header = original_magic + original_file.read(5)
    original_file.close()

    # backup original file in case something goes wrong (if it doesn't exit yet)
    backup_filename = base_filename + ".original.tex"
    if not os.path.isfile(backup_filename):
        os.rename(original_file.name, backup_filename)

    # use imagemagick to convert png to dds
    os.system(f"magick -define dds:compression=dxt5 {base_filename}.png {base_filename}.dds")

    # create final tex file by adding original klei header
    dds_file = open(base_filename + ".dds", "rb")
    tex_file = open(base_filename + ".tex", "wb")

    tex_file.write(klei_file_header + dds_file.read())
    dds_file.close()
    os.remove(dds_file.name)

    tex_file.close()

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "########################################################################\n"
        "# Griftlands Image to Klei Texture Converter\n"
        "# by Fymir27 - inspired by https://github.com/instant-noodles/gltools\n"
        "# (requires imagemagick to be installed and added to PATH)\n"
        "########################################################################")
    parser.add_argument("-ver", "--version", action="version", version="%(prog)s 1.0")
    parser.add_argument("input", help="image file with same name as original .tex file")
    args = parser.parse_args()
    path_input = None

    if not os.path.isfile(args.input):
        print(f"-- {args.input} is not a valid file")

    if img2glt(open(args.input)):
        print("Success! Now copy the .tex file into the Griftlands data archive!")
