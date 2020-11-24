import argparse
from liblyrichords.Song import Song
from liblyrichords.SongDrawer import SongDrawer
from matplotlib.backends.backend_pdf import PdfPages
import pathlib


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Lyrichords')
    parser.add_argument('path', help='Path of the lyrics and chords')
    parser.add_argument('--instrument', action='store', type=str, default="ukuleleGCEA", required=False,
                        help='Instrument to use, [default: ukuleleGCEA]')
    parser.add_argument('--format', action='store', type=str, default="A4", required=False,
                        help='Format of the pages: A0, A1, A2, A3, A4, A5 or A6, [default: A4]')
    parser.add_argument('--lefthand', dest='lefthand', default=False, action='store_true', required=False,
                        help='Option to set chords for lefthand')
    parser.add_argument('--grayscale', dest='grayscale', default=False, action='store_true', required=False,
                        help='Option to draw the lyrics in black and white')
    parser.add_argument('--landscape', dest='landscape', default=False, action='store_true', required=False,
                        help='Option to draw the page in the landscape mode')
    parser.add_argument('--disabletitle', dest='disabletitle', default=False, action='store_true', required=False,
                        help='Option to remove the title')
    parser.add_argument('--background', required=False,
                        help='Path of an image to set as background')
    parser.add_argument('--background_opacity', type=float, default=0.3, required=False,
                        help='Opacity of the background, between 0 (transparent) and 1 (opaque)')
    parser.add_argument('--notation', type=str, default="Alphabetical", required=False,
                        help='Notation used for the chord: Syllabic, Alphabetical, German Alphabetical, [default: Alphabetical]')
    parser.add_argument('--output', required=False,
                        help='Path of the output pdf file, [default name: same name as input file, default path: current path]')
    args = parser.parse_args()
    
    # Load song
    sc = Song()
    sc.load(args.path)

    # Set the drawer
    drawer = SongDrawer(pageformat=args.format,
                        instrument=args.instrument,
                        notation=args.notation,
                        lefthand=args.lefthand,
                        grayscale=args.grayscale,
                        landscape=args.landscape,
                        disabletitle=args.disabletitle)
    if(args.background):
        drawer.addBackground(args.background, args.background_opacity)

    # Draw song and save the figure
    output_path = args.output if args.output else str(pathlib.Path(args.path).stem) + ".pdf"
    output_path += "" if pathlib.Path(output_path).suffix else ".pdf"
    figs = drawer.draw(sc)
    with PdfPages(output_path) as pdf:
        for fig in figs:
            pdf.savefig(fig)
