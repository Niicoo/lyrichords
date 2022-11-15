#!/usr/bin/env python
import argparse
import pathlib
import os
import sys
import logging
LIB_PATH = pathlib.Path(pathlib.Path(__file__).absolute().parent, "lib")
sys.path.append(LIB_PATH.as_posix())
from lyrichords.song import Song
from lyrichords.drawing import SongDrawer, PAGE_FORMATS
from lyrichords.instruments import STRING_INSTRUMENTS
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
# Typing
from matplotlib.figure import Figure
from collections.abc import Iterable
from typing import Tuple

# Get Logger
logger = logging.getLogger()

def savefig2PDF(
        figs: Iterable[Figure],
        filepath: str,
        close_figs: bool = False,
        create_out_path: bool = False) -> None:
    if create_out_path:
        out_path = pathlib.Path(filepath).parent.as_posix()
        os.makedirs(out_path, exist_ok=True)
    with PdfPages(filepath) as pdf:
        for fig in figs:
            pdf.savefig(fig)
    if close_figs:
        for fig in figs:
            plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LyricsChords",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument("path", type=str,
        help="Path of the lyrics(+chords) text file OR path of the folder containing multiple lyrics text file to process"
    )
    parser.add_argument("--output", type=str, required=False,
        help="Path of the output pdf file, [default name: same name as input file, default path: path of the input file]"
    )
    parser.add_argument("--background", type=str, required=False,
        help="Path of the image file to draw as a background"
    )
    parser.add_argument("--instrument", type=str, required=False,
        default="UKULELE_GCEA",
        help="Instrument, value can be 'UKULELE_GCEA' (soprano, concert and tenor ukuleles) or 'UKULELE_DGBE' (baritone ukulele)"
    )
    parser.add_argument("--page_format", type=str, required=False,
        default="A4",
        help="Format of the pages: A0, A1, A2, A3, A4, A5 or A6"
    )
    parser.add_argument("--notation", type=str, required=False,
        default=None,
        help="Notation used for the chord: 'Syllabic', 'Alphabetical', 'German Alphabetical'"
    )
    parser.add_argument("--lefthand", action="store_true", required=False,
        default=False,
        help="Option to print the chords for left hand players"
    )
    parser.add_argument("--grayscale", action="store_true", required=False,
        default=False,
        help="Option to draw the background in grayscale"
    )
    parser.add_argument("--landscape", action="store_true", required=False,
        default=False,
        help="Option to draw in landscape orientation"
    )
    parser.add_argument("--design_vertical", action="store_true", required=False,
        default=False,
        help="Option to draw the chords to the right side of the lyrics [default: chords on top of the lyrics]"
    )
    parser.add_argument("--chords_all_pages", action="store_true", required=False,
        default=False,
        help="Option to draw the chords on all the pages [default: only the first page]"
    )
    parser.add_argument("--background_opacity", type=float, required=False,
        default=0.3,
        help="Opcity of the background [if present], [0: transparent, 1: opaque]"
    )
    parser.add_argument("--title_height", type=float, required=False,
        default=25,
        help="Height reserved to plot the title in millimeters"
    )
    parser.add_argument("--title_fontfamily", type=str, required=False,
        default="Dancing Script",
        help="Font used for the title [you can add your own font in the ./liblyrichords/fonts folder]"
    )
    parser.add_argument("--title_fontsize", type=float, required=False,
        default=30,
        help="Size of the title font"
    )
    parser.add_argument("--composer_fontfamily", type=str, required=False,
        default="Dancing Script",
        help="Font used for the composer [you can add your own font in the ./liblyrichords/fonts folder]"
    )
    parser.add_argument("--composer_fontsize", type=float, required=False,
        default=10,
        help="Size of the composer font"
    )
    parser.add_argument("--chords_fontsize", type=float, required=False,
        default=8,
        help="Size of the chords names font"
    )
    parser.add_argument("--chords_fret_spacing", type=float, required=False,
        default=3.5,
        help="Chords design: distance between frets in millimeters"
    )
    parser.add_argument("--chords_string_spacing", type=float, required=False,
        default=3.5,
        help="Chords design: distance between strings in millimeters"
    )
    parser.add_argument("--chords_first_fret_height", type=float, required=False,
        default=1.5,
        help="Chords design: height of the first fret in millimeters"
    )
    parser.add_argument("--chords_fret_height", type=float, required=False,
        default=0.5,
        help="Chords design: height of the frets in millimeters"
    )
    parser.add_argument("--chords_string_width", type=float, required=False,
        default=0.5,
        help="Chords design: width of the strings in millimeters"
    )
    parser.add_argument("--chords_finger_radius", type=float, required=False,
        default=1.0,
        help="Chords design: radius of the finger in millimeters"
    )
    parser.add_argument("--chords_margin", type=float, required=False,
        default=4,
        help="Chords design: margin arround each chords in millimeters"
    )
    parser.add_argument("--lyrics_line_spacing", type=float, required=False,
        default=10,
        help="Lyrics design: space between each text line in millimeters"
    )
    parser.add_argument("--lyrics_chords_fontsize", type=float, required=False,
        default=6,
        help="Lyrics design: size of the font used for the inline chords names"
    )
    parser.add_argument("--lyrics_fontfamily", type=str, required=False,
        default="Kurale",
        help="Lyrics design: font to use for the lyrics [you can add your own font in the ./liblyrichords/fonts folder]"
    )
    parser.add_argument("--lyrics_fontsize", type=float, required=False,
        default=10,
        help="Lyrics design: size of the font used for the lyrics"
    )
    parser.add_argument("--lyrics_ha", type=str, required=False,
        default="center",
        help="Lyrics design: Horizontal alignement of the lyrics ['left', 'center', 'right']"
    )
    parser.add_argument("--lyrics_nb_cols", type=int, required=False,
        default=0,
        help="Option to choose manually the number of the column for the lyrics [0: automatic, 1+: fixed number of column]"
    )
    parser.add_argument('--logging_level', type=str, nargs="?", const="INFO", default="INFO",
        help="Logging level: CRITICAL, ERROR, WARNING, INFO [Default] or DEBUG"
    )

    args = parser.parse_args()
    pdesign = vars(args)
    in_path = pdesign.pop("path")
    out_path = pdesign.pop("output")
    background_path = pdesign.pop("background")
    logging_level = pdesign.pop("logging_level")

    # Set Logging Level
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    for logname in ["__main__", "lyrichords"]:
        log = logging.getLogger(logname)
        log.setLevel(logging_level)
        log.addHandler(handler)

    # Detect the files to process depending on the input path is a specific file or a folder
    filepaths: Tuple[str, str] = []
    in_path = pathlib.Path(in_path)
    out_path = None if out_path is None else pathlib.Path(out_path)
    if in_path.is_file():
        if out_path is None:
            # Get the folder and name of the input file and generate a pdf file there
            out_temp = pathlib.Path(in_path.parent, in_path.stem + ".pdf")
            filepaths.append((str(in_path), str(out_temp)))
        elif out_path.suffix.lower() == ".pdf":
            filepaths.append((str(in_path), str(out_path)))
        else:
            # Assuming the path is a folder
            out_temp = pathlib.Path(out_path, in_path.stem + ".pdf")
            filepaths.append((str(in_path), str(out_temp)))
    elif in_path.is_dir():
        # Only consider the files in the current folder (not sub directories)
        for filename in os.listdir(str(in_path)):
            p = pathlib.Path(in_path, filename)
            if p.is_file():
                ext = p.suffix.lower()
                if ext == ".txt":
                    if out_path is None:
                        # Get the folder and name of the input file and generate a pdf file there
                        out_temp = pathlib.Path(p.parent, p.stem + ".pdf")
                        filepaths.append((str(p), str(out_temp)))
                    elif out_path.suffix.lower() == ".pdf":
                        raise ValueError("If you provide a folder as an input, you must set the path of folder for the output")
                    else:
                        # Assuming the path is a folder
                        out_temp = pathlib.Path(out_path, p.stem + ".pdf")
                        filepaths.append((str(p), str(out_temp)))

    # Create an instance of the drawer
    pdesign["instrument"] = STRING_INSTRUMENTS[pdesign["instrument"]].value
    pdesign["page_format"] = PAGE_FORMATS[pdesign["page_format"]]
    drawer = SongDrawer(**pdesign)

    
    # Generate the PDF files
    for in_file, out_file in filepaths:
        song = Song.fromFile(in_file)
        figs = drawer.draw(song, background_path)
        savefig2PDF(figs, out_file, close_figs=True, create_out_path=True)
