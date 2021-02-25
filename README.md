# Griftlands File Converter Tools

A set of two command line file converter tools for the [Griftlands](https://store.steampowered.com/app/601840/Griftlands/) video game created by [Klei Entertainment](https://klei.com/).

For the Usage and Examples sections below, change `python` to the appropriate command for your operating system - Windows: `py`, Linux: `python3`, Mac: `python`.

## Requirements

Export tools require [Python 3.8 (or higher)](https://www.python.org/downloads/) with the [Pillow](https://python-pillow.org/) fork of the Python Imaging Library.
Import tools additionally require [imagemagick](https://imagemagick.org/script/download.php) to be installed and added to your PATH

## Griftlands Tex to PNG Converter (glt2p.py)

This tool converts Griftlands .tex files to .png files.

#### Usage:

    $ python glt2p.py [-h] [-ver] <input-file/input-directory>
    
    -h, --help
        Displays usage information and exits
    -ver, --version
        Displays version information and exits

#### Examples:

To convert `atlas0.tex` to `atlas0.png`:

    $ python glt2p.py atlas0.tex

To convert all `*.tex` files located in a directory named `folder` to `*.png` files:

    $ python glt2p.py folder

## Griftlands Bin to SCML Converter (glb2s.py)

This tool converts Griftlands anim.bin, atlas0.tex, and build.bin files to a [BrashMonkey Spriter](https://brashmonkey.com/spriter-pro/) (.scml) file.

As Spriter does not support free-form deformations, the resultant Spriter file may not always have perfect animation fidelity to what's displayed within Griftlands.

#### Usage:

    $ python glb2s.py [-h] [-ver] <input-directory>
    
    -h, --help
        Displays usage information and exits
    -ver, --version
        Displays version information and exits

#### Example:

To convert `anim.bin`, `atlas0.tex`, and `build.bin` located in a directory named `folder` to a `.scml` file and its associated images:

    $ python glb2s.py folder

## Image to Griftlands Tex Converter (img2glt.py)

(note that this tools requires imagemagick to be installed as described in the requirements above)

This tool converts pretty much any image format (altough it should be the same size as the original texture) to a Griftlands texture.
The input file should be placed in the directory with the original .tex file, as the latter is required for the conversion (the original file will be renamed and preserved)

### Usage:

    $ python img2glt.py [-h] [-ver] <input-file>

     -h, --help
        Displays usage information and exits
    -ver, --version
        Displays version information and exits

### Example:

To convert `atlas0.png` back to `atlas0.tex` (which requires the original `atlas0.tex` to be present in the same directory):

    $ python img2glt.py atlas0.png
        
## Notice

These tools are provided by the author (Instant-Noodles) "AS IS" and WITHOUT WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
