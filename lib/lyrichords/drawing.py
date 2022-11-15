from .instruments import StringInstrument
from .common import Notation, Chord
from .song import Song, Verse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.transforms import Bbox
from dataclasses import dataclass
from enum import Enum
import logging
import matplotlib.font_manager as fm
import pathlib
import os
FONT_PATH = pathlib.Path(__file__).parent.absolute().joinpath("fonts")
# Typing
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.text import Text
from matplotlib.gridspec import SubplotSpec
from matplotlib.artist import Artist
from typing import List, Dict, Tuple

# Get Logger
logger = logging.getLogger(__name__)


def reload_fonts() -> None:
    # Add the fonts from local path
    existing_fonts = []
    for font in fm.fontManager.ttflist:
        existing_fonts.append(font.fname)
    for root, _, files in os.walk(FONT_PATH):
        for filename in files:
            # Filepath
            p = pathlib.Path(root, filename)
            ext = p.suffix.lower()
            if (ext in [".ttf", ".otf"]) and (str(p) not in existing_fonts):
                fm.fontManager.addfont(str(p))
                font_name = fm.FontProperties(fname=str(p)).get_name()
                logger.info(f"Adding Font: {font_name}")


# Page formats in mm
class PAGE_FORMATS(Enum):
    A0 = (1189, 841)
    A1 = (841, 594)
    A2 = (594, 420)
    A3 = (420, 297)
    A4 = (297, 210)
    A5 = (210, 148)
    A6 = (148, 105)


def mm2inch(value):
    return value / 25.4


def font2mm(fontsize):
    return fontsize * 0.3527777778

def mm2font(size):
    return size / 0.3527777778


def get_bboxs_union(ax: Axes, artists: List[Artist]) -> Bbox:
    renderer = ax.figure.canvas.get_renderer()
    bboxs = []
    for artist in artists:
        disp_bb = artist.get_tightbbox(renderer)
        bb = disp_bb.transformed(ax.transData.inverted())
        bboxs.append(bb)
    bb = Bbox.union(bboxs)
    return bb

def get_artists_dimension(ax: Axes, artists: List[Artist]) -> Tuple[float, float]:
    """
    Returns (Width, Height)
    """
    bb = get_bboxs_union(ax, artists)
    return((bb.x1 - bb.x0), (bb.y1 - bb.y0))

def center_ax(ax: Axes):
    if len(ax._children) == 0:
        return
    bb = get_bboxs_union(ax, ax._children)
    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()
    xmiddle = x1 + ((x2 - x1) / 2)
    ymiddle = y1 + ((y2 - y1) / 2)
    xmiddle_new = bb.x0 + ((bb.x1 - bb.x0) / 2)
    ymiddle_new = bb.y0 + ((bb.y1 - bb.y0) / 2)
    x_offset = xmiddle_new - xmiddle
    y_offset = ymiddle_new - ymiddle
    ax.set_xlim([x1 + x_offset, x2 + x_offset])
    ax.set_ylim([y1 + y_offset, y2 + y_offset])



# Generating using: https://mokole.com/palette.html
DISTINCT_COLORS = {
    # 2 colors: lime, blue
    2: ("#00ff00", "#0000ff"),
    # 3 colors: red, lime, blue
    3: ("#ff0000", "#00ff00", "#0000ff"),
    # 4 colors: red, lime, blue, lightskyblue
    4: ("#ff0000", "#00ff00", "#0000ff", "#87cefa"),
    # 5 colors: orange, springgreen, deepskyblue, blue, deeppink
    5: ("#ffa500", "#00ff7f", "#00bfff", "#0000ff", "#ff1493"),
    # 6 colors: mediumaquamarine, orange, lime, blue, dodgerblue, deeppink
    6: ("#66cdaa", "#ffa500", "#00ff00", "#0000ff", "#1e90ff", "#ff1493"),
    # 7 colors: olive, orangered, mediumvioletred, lime, aqua, blue, dodgerblue
    7: ("#808000", "#ff4500", "#c71585", "#00ff00", "#00ffff", "#0000ff", "#1e90ff"),
    # 8 colors: darkgreen, red, gold, mediumvioletred, lime, aqua, blue, dodgerblue
    8: ("#006400", "#ff0000", "#ffd700", "#c71585", "#00ff00", "#00ffff", "#0000ff", "#1e90ff"),
    # 9 colors: darkgreen, rosybrown, red, gold, mediumblue, lime, aqua, dodgerblue, deeppink
    9: ("#006400", "#bc8f8f", "#ff0000", "#ffd700", "#0000cd", "#00ff00", "#00ffff", "#1e90ff", "#ff1493"),
    # 10 colors: darkgreen, darkblue, maroon3, orangered, yellow, burlywood, lime, aqua, fuchsia, cornflower
    10: ("#006400", "#00008b", "#b03060", "#ff4500", "#ffff00", "#deb887", "#00ff00", "#00ffff", "#ff00ff", "#6495ed"),
    # 11 colors: saddlebrown, forestgreen, steelblue, indigo, red, yellow, lime, aqua, blue, deeppink
    #            bisque
    11: ("#8b4513", "#228b22", "#4682b4", "#4b0082", "#ff0000", "#ffff00", "#00ff00", "#00ffff", "#0000ff", "#ff1493",
         "#ffe4c4"),
    # 12 colors: darkslategray, saddlebrown, forestgreen, darkblue, red, yellow, lime, aqua, fuchsia, dodgerblue
    #            wheat, hotpink
    12: ("#2f4f4f", "#8b4513", "#228b22", "#00008b", "#ff0000", "#ffff00", "#00ff00", "#00ffff", "#ff00ff", "#1e90ff",
         "#f5deb3", "#ff69b4"),
    # 13 colors: darkslategray, saddlebrown, green, indigo, red, gold, lime, aqua, blue, fuchsia
    #            cornflower, navajowhite, hotpink
    13: ("#2f4f4f", "#8b4513", "#008000", "#4b0082", "#ff0000", "#ffd700", "#00ff00", "#00ffff", "#0000ff", "#ff00ff",
         "#6495ed", "#ffdead", "#ff69b4"),
    # 14 colors: darkslategray, maroon2, midnightblue, green, tan, darkorange, mediumblue, lime, deepskyblue, fuchsia
    #            laserlemon, plum, deeppink, aquamarine
    14: ("#2f4f4f", "#7f0000", "#191970", "#008000", "#d2b48c", "#ff8c00", "#0000cd", "#00ff00", "#00bfff", "#ff00ff",
         "#ffff54", "#dda0dd", "#ff1493", "#7fffd4"),
    # 15 colors: darkslategray, saddlebrown, darkgreen, navy, red, darkturquoise, orange, yellow, mediumvioletred, lime
    #            blue, fuchsia, dodgerblue, palegreen, lightpink
    15: ("#2f4f4f", "#8b4513", "#006400", "#000080", "#ff0000", "#00ced1", "#ffa500", "#ffff00", "#c71585", "#00ff00",
         "#0000ff", "#ff00ff", "#1e90ff", "#98fb98", "#ffb6c1"),
    # 16 colors: darkslategray, maroon2, darkgreen, navy, red, darkturquoise, orange, yellow, lime, mediumspringgreen
    #            blue, fuchsia, khaki, cornflower, deeppink, pink
    16: ("#2f4f4f", "#7f0000", "#006400", "#000080", "#ff0000", "#00ced1", "#ffa500", "#ffff00", "#00ff00", "#00fa9a",
         "#0000ff", "#ff00ff", "#f0e68c", "#6495ed", "#ff1493", "#ffc0cb"),
    # 17 colors: darkslategray, saddlebrown, darkgreen, darkblue, maroon3, orangered, darkturquoise, orange, yellow, chartreuse
    #            mediumspringgreen, blue, thistle, fuchsia, dodgerblue, khaki, violet
    17: ("#2f4f4f", "#8b4513", "#006400", "#00008b", "#b03060", "#ff4500", "#00ced1", "#ffa500", "#ffff00", "#7fff00",
         "#00fa9a", "#0000ff", "#d8bfd8", "#ff00ff", "#1e90ff", "#f0e68c", "#ee82ee"),
    # 18 colors: darkslategray, darkred, green, purple2, darkseagreen, red, orange, lime, mediumspringgreen, royalblue
    #            darksalmon, aqua, deepskyblue, blue, fuchsia, laserlemon, plum, deeppink
    18: ("#2f4f4f", "#8b0000", "#008000", "#7f007f", "#8fbc8f", "#ff0000", "#ffa500", "#00ff00", "#00fa9a", "#4169e1",
         "#e9967a", "#00ffff", "#00bfff", "#0000ff", "#ff00ff", "#ffff54", "#dda0dd", "#ff1493"),
    # 19 colors: gainsboro, darkslategray, seagreen, maroon, olive, purple, red, orange, mediumblue, chartreuse
    #            mediumspringgreen, royalblue, darksalmon, aqua, deepskyblue, fuchsia, laserlemon, plum, deeppink
    19: ("#dcdcdc", "#2f4f4f", "#2e8b57", "#800000", "#808000", "#800080", "#ff0000", "#ffa500", "#0000cd", "#7fff00",
         "#00fa9a", "#4169e1", "#e9967a", "#00ffff", "#00bfff", "#ff00ff", "#ffff54", "#dda0dd", "#ff1493"),
    # 20 colors: darkslategray, darkgreen, firebrick, yellowgreen, darkblue, darkseagreen, red, darkorange, gold, lime
    #            mediumspringgreen, royalblue, darksalmon, aqua, deepskyblue, blue, thistle, fuchsia, deeppink, violet
    20: ("#2f4f4f", "#006400", "#b22222", "#9acd32", "#00008b", "#8fbc8f", "#ff0000", "#ff8c00", "#ffd700", "#00ff00",
         "#00fa9a", "#4169e1", "#e9967a", "#00ffff", "#00bfff", "#0000ff", "#d8bfd8", "#ff00ff", "#ff1493", "#ee82ee")
}


@dataclass(eq=False, unsafe_hash=True, )
class SongDrawer:
    instrument: StringInstrument
    page_format: PAGE_FORMATS = PAGE_FORMATS.A4
    notation: Notation = None
    lefthand: bool = False
    grayscale: bool = False
    landscape: bool = False
    design_vertical: bool = False
    chords_all_pages: bool = False
    background_opacity: float = 0.3 # (0: transparent, 1: opaque)
    title_height: float = 25 # mm
    title_fontfamily: str = "Dancing Script"
    title_fontsize: float = 30
    composer_fontfamily: str = "Dancing Script"
    composer_fontsize: float = 10
    chords_fontsize: float = 8
    chords_fret_spacing: float = 3.5 # mm
    chords_string_spacing: float = 3.5 # mm
    chords_first_fret_height: float = 1.5 # mm
    chords_fret_height: float = 0.5 # mm
    chords_string_width: float = 0.5 # mm
    chords_finger_radius: float = 1.0 # mm
    chords_margin: float = 4 # mm
    lyrics_line_spacing: float = 10 # mm
    lyrics_chords_fontsize: float = 6
    lyrics_fontfamily: str = "Kurale"
    lyrics_fontsize: float = 10
    lyrics_ha: str = "center",
    lyrics_nb_cols: int = 0

    def __post_init__(self):
        # Intermediary attributes
        self.plyrics = {"fontfamily": self.lyrics_fontfamily, "fontsize": self.lyrics_fontsize, "horizontalalignment": self.lyrics_ha, "verticalalignment": "top"}
        self.ptitle = {"fontfamily": self.title_fontfamily, "fontsize": self.title_fontsize, "horizontalalignment": "center", "verticalalignment": "center"}
        self.pcomposer = {"fontfamily": self.composer_fontfamily, "fontsize": self.composer_fontsize, "horizontalalignment": "center", "verticalalignment": "center"}
        self.figsize = self.page_format.value
        if(not self.landscape):
            self.figsize = self.figsize[::-1]
        # Temporary attributes
        self.figs: List[Figure] = []
        self.ax_title: Axes = None
        self.ax_chords: Axes = None
        self.ax_lyrics: Axes = None
        self.chords_colors: Dict[Chord, str] = {}
        self.gs_lyrics: SubplotSpec = None
        reload_fonts()

    def _scaleAxis(self, ax: Axes, invert_yaxis: bool = True):
        ax.set_facecolor("none")
        ax.set_axis_off()
        bb = ax.get_position()
        width = (bb.get_points()[1][0] - bb.get_points()[0][0]) * self.figsize[0]
        height = (bb.get_points()[1][1] - bb.get_points()[0][1]) * self.figsize[1]
        ax.set_xlim([0, width])
        ax.set_ylim([0, height])
        if invert_yaxis:
            ax.invert_yaxis()

    def _getChordTitleHeight(self) -> float:
        return font2mm(self.chords_fontsize)

    def _getChordDimension(self, with_margin: bool = False) -> Tuple[float, float]:
        """
        !!! The dimensions must match the one used during drawing.
        """
        nb_frets = self.instrument.getMaxFretsRange()
        width = (self.instrument.getNbStrings() - 1) * self.chords_string_spacing + self.chords_string_width
        title_height = self._getChordTitleHeight()
        mute_strings_height = self.chords_fret_spacing
        height = nb_frets * self.chords_fret_spacing + self.chords_first_fret_height + mute_strings_height + title_height
        if with_margin:
            width += 2 * self.chords_margin
            height += 2 * self.chords_margin
        return(width, height)

    def _getNbColumnRowChords(self, with_title: bool = True):
        chord_width, chord_height = self._getChordDimension(with_margin=True)
        nb_chords = len(self.chords_colors)
        if self.design_vertical:
            height = self.figsize[1]
            if with_title:
                height -= self.title_height
            nb_rows = int(height / chord_height)
            nb_columns = int(np.ceil(nb_chords / nb_rows))
        else:
            width = self.figsize[0]
            nb_columns = int(width / chord_width)
            nb_rows = int(np.ceil(nb_chords / nb_columns))
        return(nb_rows, nb_columns)

    def _addBackground(self, fig: Figure, background: str):
        ax_background = fig.add_subplot(111)
        self._scaleAxis(ax_background, invert_yaxis=True)
        # Add the background
        bg_img = plt.imread(background)[::-1, :, :]
        gsopts = {}
        if(self.grayscale):
            bg_img = np.dot(bg_img[..., :3], [0.2989, 0.5870, 0.1140])
            gsopts = {"cmap": 'gray', "vmin": 0, "vmax": 255.}
        ax_background.imshow(bg_img, extent=[0, self.figsize[0], 0, self.figsize[1]], alpha=self.background_opacity, **gsopts)

    def _drawTitle(self, song: Song):
        self.ax_title.text(
            x=self.figsize[0] / 2.0,
            y=self.title_height / 2.0,
            s=f"{song.getTitle()} - {song.getArtist()}",
            **self.ptitle
        )
        if(song.isComposerSet()):
            self.ax_title.text(
                x=self.figsize[0] / 2.0,
                y=self.title_height * 4.0 / 5.0,
                s=f"Composed by: {song.getComposer()}",
                **self.pcomposer)

    def _drawChordBox(self, ax, x, y, chordname, fontsize) -> Text:
        if self.notation is not None:
            chordname = Chord.parse(chordname).getName(self.notation)
        color = self.chords_colors[chordname]
        return ax.text(x, y, chordname, size=fontsize, ha="center", va="center",
            bbox=dict(
                    boxstyle="round",
                    ec=mcolors.to_rgb(color),
                    fc=mcolors.to_rgb(color) + (0.5, ),
                    )
        )

    def _drawChords(self, song: Song, with_title: bool = True):
        chord_width, chord_height = self._getChordDimension(with_margin=False)
        nb_rows, nb_columns = self._getNbColumnRowChords(with_title)
        chords = song.getChordsUsed()
        if (nb_rows * nb_columns) < len(chords):
            raise ValueError("Not enough space to draw all the chords")
        chords_indexes = list(np.ndindex((nb_rows, nb_columns)))
        xmin, ymin = np.inf, np.inf
        xmax, ymax = -np.inf, -np.inf
        for ind_chord, chordname in enumerate(chords.keys()):
            ind_row, ind_col = chords_indexes[ind_chord]
            # X and Y where to draw the chord
            x_offset = ind_col * (chord_width + 2 * self.chords_margin)
            y_offset = ind_row * (chord_height + 2 * self.chords_margin)
            if x_offset < xmin: xmin = x_offset
            if y_offset < ymin: ymin = y_offset
            if x_offset + chord_width > xmax: xmax = x_offset + chord_width
            if y_offset + chord_height > ymax: ymax = y_offset + chord_height
            # Draw Frets and Strings
            title_height = self._getChordTitleHeight()
            y_offset_chord = y_offset + title_height + self.chords_fret_spacing
            nb_strings = self.instrument.getNbStrings()
            nb_frets = self.instrument.getMaxFretsRange()
            full_width = (self.instrument.getNbStrings() - 1) * self.chords_string_spacing + self.chords_string_width
            self.ax_chords.add_patch(mpatches.Rectangle((x_offset, y_offset_chord), full_width, self.chords_first_fret_height, color="gray", linewidth=0))
            y_offset_chord += self.chords_first_fret_height - (self.chords_fret_height / 2)
            for k in range(1, nb_frets + 1):
                y_temp = y_offset_chord + self.chords_fret_spacing * k - (self.chords_fret_height / 2)
                self.ax_chords.add_patch(mpatches.Rectangle((x_offset, y_temp), full_width, self.chords_fret_height, color="gray", linewidth=0))
            for k in range(0, nb_strings):
                x_temp = x_offset + self.chords_string_spacing * k
                self.ax_chords.add_patch(mpatches.Rectangle((x_temp, y_offset_chord), self.chords_string_width, nb_frets * self.chords_fret_spacing, color="gray", linewidth=0))
            # Draw Chordname
            self._drawChordBox(self.ax_chords, x_offset + chord_width / 2, y_offset, chordname, self.chords_fontsize)
            # Draw Fingers
            frets =  self.instrument.getFrets(chordname)[0]
            if(self.lefthand):
                frets = frets[::-1]
            y_fret_zero = y_offset + title_height + self.chords_fret_spacing + self.chords_first_fret_height - (self.chords_fret_height / 2) + self.chords_fret_spacing / 2
            x_string_zero = x_offset + self.chords_string_width / 2
            offset = max(0, max([int(f) for f in frets if f.upper() != 'X']) - nb_frets)
            if offset > 0:
                self.ax_chords.text(x_string_zero - self.chords_string_spacing / 2, y_fret_zero, str(offset + 1), size=self.chords_fontsize, ha="center", va="center")
            for num_string, position in enumerate(frets):
                xtemp = x_string_zero + num_string * self.chords_string_spacing
                if(position.upper() in ["X", "0", "O"]):
                    # Draw the muted strings
                    y_offset_muted = y_offset + title_height + self.chords_fret_spacing / 2
                    text = "o" if (position.lower() in ["0", "o"]) else position.lower()
                    self.ax_chords.text(xtemp, y_offset_muted, text, size=mm2font(self.chords_string_spacing), ha="center", va="center", color="gray")
                    continue
                ytemp = y_fret_zero + (int(position) - 1 - offset) * self.chords_fret_spacing
                self.ax_chords.add_artist(mpatches.Circle((xtemp, ytemp), self.chords_finger_radius, color="dimgray", zorder=1))
        # Center the chords to the middle of the ax
        center_ax(self.ax_chords)

    def _drawVerse(self, x: float, y: float, verse: Verse, with_chords: bool = True) -> Tuple[Text, List[Text], float]:
        verse_text = verse.getText()
        ltext = self.ax_lyrics.text(x, y, s=verse_text, **self.plyrics)
        lwidth, _ = get_artists_dimension(self.ax_lyrics, [ltext])
        ctexts = []
        if with_chords:
            y_chord = y - self.lyrics_line_spacing / 4
            for chord in verse.getChords():
                # I have to temporary plot the lyrics until the position of the chord to get
                # its width rendered in the axes in order to print the chord name to the right
                # place whatever the font chosen
                ind = chord.index
                if(ind < len(verse_text)):
                    temp_text = verse_text[:ind]
                else:
                    temp_text = verse_text + "x" * (ind - len(verse_text))
                textplt = self.ax_lyrics.text(x, y, temp_text, **self.plyrics)
                cwidth, _ = get_artists_dimension(self.ax_lyrics, [textplt])
                x_chord = x + cwidth
                if("horizontalalignment" in self.plyrics):
                    if(self.plyrics["horizontalalignment"] == "center"):
                        x_chord = x + cwidth - (lwidth / 2.0)
                    elif(self.plyrics["horizontalalignment"] == "right"):
                        x_chord = x - lwidth + cwidth
                ctext = self._drawChordBox(self.ax_lyrics, x_chord, y_chord, chord.name, self.lyrics_chords_fontsize)
                ctexts.append(ctext)
                textplt.remove()
        lwidth, _ = get_artists_dimension(self.ax_lyrics, [ltext] + ctexts)
        return(ltext, ctexts, lwidth)
    
    def _drawVerseAutoWrapping(self,
            x: float,
            y: float,
            verse: Verse,
            width_available: float,
            height_available: float,
            texts: List[Text] = None,
            nb_wraps: int = 0,
            max_width: float = 0) -> Tuple[List[Text], int, float]:
        if texts is None: texts = []
        nb_words_removed = 0
        ltext, ctexts, width = self._drawVerse(x, y, verse)
        verse_2 = None
        while(width > width_available):
            ltext.remove()
            for ctext in ctexts:
                ctext.remove()
            nb_words_removed += 1
            verse_1, verse_2 = verse.splitByWords(nb_words_removed, from_end=True)
            ltext, ctexts, width = self._drawVerse(x, y, verse_1)
        if width > max_width:
            max_width = width
        texts.append(ltext)
        texts += ctexts
        height = (nb_wraps + 1) * self.lyrics_line_spacing
        if height > height_available:
            for text in texts:
                text.remove()
            return ([], 0, 0)
        if verse_2 is not None:
            nb_wraps += 1
            return self._drawVerseAutoWrapping(x, y + self.lyrics_line_spacing, verse_2, width_available, height_available, texts, nb_wraps, max_width)
        return(texts, nb_wraps, max_width)

    def _drawLyricsAx(self, song: Song, ax: Axes, nb_verses_done: int) -> Tuple[int, int]:
        margin = 3 # mm
        full_width = ax.get_xlim()[1]
        full_height = ax.get_ylim()[0]
        x = 0 # if self.plyrics["horizontalalignment"] == "left" else full_width / 2
        y = 0
        max_width = 0
        nb_verses_written = 0
        nb_wraps_total = 0
        for verse in song[nb_verses_done:]:
            if verse.isEmpty():
                nb_verses_written += 1
                y += self.lyrics_line_spacing / 2
                continue
            texts, nb_wraps, lwidth = self._drawVerseAutoWrapping(x, y, verse, full_width - margin * 2, full_height - margin * 2 - y)
            if lwidth > max_width:
                max_width = lwidth
            if texts == []:
                break
            nb_verses_written += 1
            nb_wraps_total += nb_wraps
            y += (nb_wraps + 1) * self.lyrics_line_spacing
        # Center the lyrics to the middle of the ax
        center_ax(ax)
        return(nb_verses_written, nb_wraps_total)

    def _drawLyrics(self, song: Song) -> bool:
        nb_verses_total = len(song.getVerses())
        nb_cols = 1 if (self.lyrics_nb_cols <= 0) else self.lyrics_nb_cols
        nb_verses_written_past = 0
        axs_past = []
        while True:
            nb_verses_written = 0
            nb_wraps_total = 0
            axs = []
            subgs = gridspec.GridSpecFromSubplotSpec(1, nb_cols, subplot_spec=self.gs_lyrics)
            for ind_col in range(0, nb_cols):
                ax = self.figs[-1].add_subplot(subgs[ind_col])
                self._scaleAxis(ax, invert_yaxis=True)
                self.ax_lyrics = ax
                _nb_verses_ax, _nb_wraps = self._drawLyricsAx(song, ax, self.nb_verses_already_draw + nb_verses_written)
                nb_verses_written += _nb_verses_ax
                nb_wraps_total += _nb_wraps
                axs.append(ax)
                if self.nb_verses_already_draw + nb_verses_written >= nb_verses_total:
                    break
            if(self.lyrics_nb_cols > 0):
                # Clear the previous config and keep this current config
                if len(axs_past) > 0:
                    for ax in axs_past: ax.remove()
                break
            if(nb_wraps_total / nb_verses_written) > 0.2:
                # Clear this config and Keep the previous one except if nb_cols == 1
                if(nb_cols > 1):
                    for ax in axs: ax.remove()
                    nb_verses_written = nb_verses_written_past
                break
            if (self.nb_verses_already_draw + nb_verses_written >= nb_verses_total):
                # Clear the previous config and keep this current config
                if len(axs_past) > 0:
                    for ax in axs_past: ax.remove()
                break
            if nb_verses_written <= nb_verses_written_past:
                # Keep the previous config and clear this current one
                for ax in axs: ax.remove()
                nb_verses_written = nb_verses_written_past
                break
            nb_cols += 1
            if len(axs_past) > 0:
                for ax in axs_past: ax.remove()
            axs_past = axs.copy()
            nb_verses_written_past = nb_verses_written
            
        self.nb_verses_already_draw += nb_verses_written
        if self.nb_verses_already_draw >= nb_verses_total:
            self.nb_verses_already_draw = 0
            return True
        return False

    def draw(self, song: Song, background: str = None):
        self.nb_verses_already_draw = 0
        # Closing and clearing any previous figure
        for fig in self.figs:
            plt.close(fig)
        self.figs.clear()
        chords = song.getChordsUsed()
        self.chords_colors = {chordname: DISTINCT_COLORS[len(chords)][ind_chord] for ind_chord, chordname in enumerate(chords.keys())}
        chord_width, chord_height = self._getChordDimension(with_margin=True)
        finished = False
        while(not finished):
            is_first_page = len(self.figs) == 0
            fig = plt.figure(figsize=mm2inch(np.array(self.figsize)))
            self.figs.append(fig)
            fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
            if is_first_page or self.chords_all_pages:
                nb_rows, nb_columns = self._getNbColumnRowChords(with_title=is_first_page)
                if self.design_vertical:
                    chords_width = nb_columns * chord_width
                    lyrics_height = self.figsize[1] - self.title_height
                    height_ratios = [self.title_height, lyrics_height] if is_first_page else [0, 1]
                    lyrics_width = self.figsize[0] - chords_width
                    gs = gridspec.GridSpec(2, 2, width_ratios=[lyrics_width, chords_width], height_ratios=height_ratios)
                    self.gs_lyrics = gs[1:, 0]
                    self.ax_chords = fig.add_subplot(gs[1:, 1])
                else:
                    chords_height = nb_rows * chord_height
                    lyrics_height = self.figsize[1] - chords_height
                    height_ratios = [0, chords_height, lyrics_height]
                    if is_first_page:
                        lyrics_height -= self.title_height
                        height_ratios = [self.title_height, chords_height, lyrics_height]
                    gs = gridspec.GridSpec(3, 1, height_ratios=height_ratios)
                    self.gs_lyrics = gs[2, :]
                    self.ax_chords = fig.add_subplot(gs[1, :])
                self._scaleAxis(self.ax_chords, invert_yaxis=True)
                self._drawChords(song, with_title=is_first_page)
                if is_first_page:
                    self.ax_title = fig.add_subplot(gs[0, :])
                    self._scaleAxis(self.ax_title, invert_yaxis=True)
                    self._drawTitle(song)
            else:
                gs = gridspec.GridSpec(1, 1)
                self.gs_lyrics = gs[:, :]
            finished = self._drawLyrics(song)
            if background is not None:
                self._addBackground(fig, background)
        return self.figs
