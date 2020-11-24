from .common import mm2inch, textRectangled, Chord
from .StringChordDrawer import UkuleleGCEA
import matplotlib.pyplot as plt
import numpy as np
import warnings
import matplotlib.font_manager as fm
import pathlib
fontpath = pathlib.Path(__file__).parent.absolute().joinpath("fonts")
titlefontprop = fm.FontProperties(fname=str(fontpath.joinpath("DancingScript-Regular.ttf")))
lyricsfontprop = fm.FontProperties(fname=str(fontpath.joinpath("Kurale-Regular.ttf")))


PAGE_FORMATS = {
    "A0": (1189, 841),
    "A1": (841, 594),
    "A2": (594, 420),
    "A3": (420, 297),
    "A4": (297, 210),
    "A5": (210, 148),
    "A6": (148, 105)
}


### Enumerate list of chords and associate them a color ###
# Color list from: https://sashamaps.net/docs/tools/20-colors/
DISTINCT_COLORS = [
    (230, 25, 75), (60, 180, 75), (255, 225, 25), (0, 130, 200), (245, 130, 48),
    (145, 30, 180), (70, 240, 240), (240, 50, 230), (210, 245, 60), (250, 190, 190),
    (0, 128, 128), (230, 190, 255), (170, 110, 40), (255, 250, 200), (128, 0, 0),
    (170, 255, 195), (128, 128, 0), (255, 215, 180), (0, 0, 128), (128, 128, 128)
]


class SongDrawer:
    def __init__(self,
                    pageformat="A4",
                    instrument="UkuleleGCEA",
                    notation="Alphabetical",
                    lefthand=False,
                    grayscale=False,
                    landscape=False,
                    disabletitle=False):
        self.background = None
        self.background_opacity = None
        self.grayscale = grayscale
        self.notation = notation
        self.titledisabled = disabletitle
        self.figsize = PAGE_FORMATS[pageformat]
        if(not landscape):
            self.figsize = self.figsize[::-1]
        if(instrument.upper() == "UKULELEGCEA"):
            self.chord_drawer = UkuleleGCEA(lefthand)
        else:
            raise NotImplementedError("The instrument '%s' is not compatible" % instrument)
        self.figs = []
        self.axes = []
        ### CUSTOMIZABLE PARAMETERS ###
        # Title parameters
        self.title_size_height = 25
        self.ptitle = { "x": self.figsize[0] / 2.0, "y": self.title_size_height / 2.0, "fontproperties": titlefontprop,
                        "fontsize": 30, "horizontalalignment": 'center', "verticalalignment": 'center'}
        self.pcomposer = {  "x": self.figsize[0] / 2.0, "y": self.title_size_height * 4.0 / 5.0 , "fontproperties": titlefontprop,
                            "fontsize": 9, "horizontalalignment": 'center', "verticalalignment": 'center'}
        # Width reserved for lyrics and chords
        self.lyrics_proportion = 70 / 100. # [%] width reserved for the lyrics
        # Lyrics parameters
        self.lyrics_padding = {"top": 10, "bottom": 10, "right": 0, "left": 10}
        self.plyrics = {"fontproperties": lyricsfontprop, "fontsize": 14, "verticalalignment": 'center', "horizontalalignment": 'center'}
        self.linespacing = 10 # Space between each line of the lyrics
        self.partspacing = 15 # Space between each couplet
        # Chords parameters
        self.chords_padding = {"top": 40, "bottom": 10, "right": 10, "left": 10}
        self.chordspacingheight = 5 # Height space reserved between chords representations
        self.chordspacingwidth = 5 # Width space reserved between chords representations
        ### CUSTOMIZABLE PARAMETERS (END) ###

    def addBackground(self, imgpath, opacity=0.3):
        self.background = plt.imread(imgpath)[::-1,:,:]
        self.background_opacity = opacity
        if(self.grayscale):
            self.background = np.dot(self.background[...,:3], [0.2989, 0.5870, 0.1140])

    def addPage(self):
        self.figs.append(plt.figure(figsize=mm2inch(np.array(self.figsize))))
        self.axes.append(self.figs[-1].add_subplot(111))
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.axes[-1].set_xlim([0, self.figsize[0]])
        self.axes[-1].set_ylim([0, self.figsize[1]])
        plt.gca().invert_yaxis()
        # Transform from pixel to data coordinates
        self.rendered = self.figs[-1].canvas.get_renderer()
        self.invtransform = self.axes[-1].transData.inverted()
        if not (self.background is None):
            gsopts = {"cmap": 'gray', "vmin": 0, "vmax": 255.} if self.grayscale else {}
            self.axes[-1].imshow(self.background, extent=[0, self.figsize[0], 0, self.figsize[1]], alpha=self.background_opacity, **gsopts)
        self.updateRegions()

    def updateRegions(self):
        self.lyrics_region = {  "x": self.lyrics_padding["left"],
                                "y": self.lyrics_padding["top"],
                                "width": self.lyrics_proportion * self.figsize[0] - self.lyrics_padding["left"] - self.lyrics_padding["right"],
                                "height": self.figsize[1] - self.lyrics_padding["top"] - self.lyrics_padding["bottom"]}
        
        self.chords_region = {  "x": self.lyrics_proportion * self.figsize[0] + self.chords_padding["left"],
                                "y": self.chords_padding["top"],
                                "width": (1 - self.lyrics_proportion) * self.figsize[0] - self.chords_padding["left"] - self.chords_padding["right"],
                                "height": self.figsize[1] - self.chords_padding["top"] - self.chords_padding["bottom"]}
        if((len(self.figs) == 1) and not self.titledisabled):
            self.lyrics_region["y"] += self.title_size_height
            self.lyrics_region["height"] -= self.title_size_height
            self.chords_region["y"] += self.title_size_height
            self.chords_region["height"] -= self.title_size_height

    def drawTitle(self, song):
        self.axes[0].text(s=song.title + " - " + song.artist, **self.ptitle)
        if(song.isComposerSet()):
            self.axes[0].text(s="Composed by: " + song.composer, **self.pcomposer)

    def splitVerseIfTooLong(self, verse):
        ind_max = len(verse.text) - 1
        while(True):
            linetext = self.axes[-1].text(x=self.lyrics_region["x"], y=self.y_lyrics, s=verse.text[:ind_max + 1], **self.plyrics)
            bb = linetext.get_window_extent(renderer=self.rendered)
            linetext_width, _ = self.invtransform.transform((bb.width,  bb.height))
            linetext.remove()
            if(linetext_width <= self.lyrics_region["width"]):
                break
            else:
                ind_max -= 1
        verses = []
        if(ind_max != (len(verse.text) -1)):
            verse1, verse2 = verse.split(ind_max)
            verses.append(verse1)
            verses += self.splitVerseIfTooLong(verse2)
        else:
            verses.append(verse)
        return verses

    def drawVerse(self, brutverse):
        verse_list = self.splitVerseIfTooLong(brutverse)
        x_text = self.lyrics_region["x"]
        if("horizontalalignment" in self.plyrics):
            if(self.plyrics["horizontalalignment"] == "center"):
                 x_text += self.lyrics_region["width"] / 2.0
        for k_verse, verse in enumerate(verse_list):
            linetext = self.axes[-1].text(x=x_text, y=self.y_lyrics+3, s=verse.text, **self.plyrics)
            bb = linetext.get_window_extent(renderer=self.rendered)
            linetext_width, _ = self.invtransform.transform((bb.width,  bb.height))
            if(verse.chords):
                for chord in verse.chords:
                    # I have to temporary plot a text to estimate its width rendered in the axes
                    # in order to print the chord name to the right place whatever the font chosen
                    # This method won't work if I want to center horizontally the text
                    ind = chord["index"]
                    if(ind < len(verse.text)):
                        temp_text = verse.text[:ind]
                    else:
                        temp_text = verse.text + "x" * (ind - len(verse.text))
                    textplt = self.axes[-1].text(x=self.lyrics_region["x"], y=self.y_lyrics, s=temp_text, **self.plyrics)
                    bb = textplt.get_window_extent(renderer=self.rendered)
                    width, height = self.invtransform.transform((bb.width,  bb.height))
                    rect_width = 5
                    x_chord = self.lyrics_region["x"] + width + rect_width / 2
                    color = None if self.grayscale else self.chordcolors[chord["chord"].getName()]
                    if("horizontalalignment" in self.plyrics):
                        if(self.plyrics["horizontalalignment"] == "center"):
                            x_chord = self.lyrics_region["x"] + self.lyrics_region["width"] / 2.0
                            x_chord -= linetext_width / 2.0
                            x_chord += width + rect_width / 2
                    chordname = chord["chord"].getName(self.notation)
                    textRectangled(self.axes[-1], x_chord, self.y_lyrics, chordname, 8, color, rect_width, fontweight="bold")
                    textplt.remove()
            if(k_verse != (len(verse_list) -1)):
                self.increaseY(self.linespacing)

    def drawChords(self):
        if(len(self.current_page_chords) == 0):
            return
        chord_width, chord_height = self.chord_drawer.getSize(nb_frets=self.nb_visible_frets)
        max_chords_height = max(1, int(self.chords_region["height"] / (self.chordspacingheight + chord_height)))
        max_chords_width = int(self.chords_region["width"] / (self.chordspacingwidth + chord_width))
        if (max_chords_width + 1) * (self.chordspacingwidth + chord_width) - self.chordspacingwidth <= self.chords_region["width"]:
            max_chords_width += 1
        max_chords = max_chords_height * max_chords_width
        if(len(self.current_page_chords) > max_chords):
            warnings.warn("Too much chords to plot on the page, %d to plot, %d only will be plotted" % (len(self.current_page_chords), max_chords))
        num_chord = 0
        for p in range(0, max_chords_height):
            y_coor = self.chords_region["y"] + p * (chord_height + self.chordspacingheight)
            for k in range(0, max_chords_width):
                x_coor = self.chords_region["x"] + k * (chord_width + self.chordspacingwidth)
                color =  None if self.grayscale else self.chordcolors[self.current_page_chords[num_chord]]
                self.chord_drawer.draw(Chord(self.current_page_chords[num_chord]), self.axes[-1], x_coor, y_coor, self.notation, color=color, nb_visible_fret=self.nb_visible_frets)
                num_chord += 1
                if(num_chord >= len(self.current_page_chords)):
                    return

    def addChordsToList(self, verse):
        temp_chords = verse.getChordList()
        for chordname in temp_chords:
            if not (chordname in self.current_page_chords):
                self.current_page_chords.append(chordname)

    def associateChordColors(self, song):
        chordlist = song.getChordsUsed()
        chordlist = sorted(chordlist.items() , reverse=True, key=lambda x: x[1])
        self.chordcolors = {}
        for k, chord in enumerate(chordlist):
            self.chordcolors[chord[0]] = tuple(np.array(DISTINCT_COLORS[k % len(DISTINCT_COLORS)]) / 255.0)

    def increaseY(self, value):
        self.y_lyrics += value
        if(self.y_lyrics >= (self.lyrics_region["y"] + self.lyrics_region["height"])):
            self.drawChords()
            self.addPage()
            self.current_page_chords = []
            self.y_lyrics = self.lyrics_region["y"]

    def draw(self, song):
        # Closing and clearing any previous figure
        for fig in self.figs:
            fig.close()
        self.figs.clear()
        self.axes.clear()
        # For each chord used in this song, associate a color
        self.associateChordColors(song)
        self.nb_visible_frets = self.chord_drawer.getMaxFretUsed(song.getChordsUsed())
        # Create the first page and print the title on it
        self.addPage()
        if(not self.titledisabled):
            self.drawTitle(song)
        # Y position of the cursor to print the lyrics
        self.y_lyrics = self.lyrics_region["y"]
        # Chords used in the current page
        self.current_page_chords = []
        for k, verse in enumerate(song.lyrics):
            if(k > 0):
                if(song.lyrics[k-1].isEmptyLine()):
                    self.increaseY(self.partspacing)
                elif(not verse.isEmptyLine()):
                    self.increaseY(self.linespacing)
            if(verse.isEmptyLine()):
                continue
            self.drawVerse(verse)
            self.addChordsToList(verse)
        self.drawChords()
        return self.figs


########################################
# TO DO: Using different subplots for each parts (lyrics, chords, title, etc..)

# import matplotlib.gridspec as gridspec

# fig_size = PAGE_FORMATS["A6"][::-1]

# fig = plt.figure(figsize=mm2inch(np.array(fig_size)))
# plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
# gs = gridspec.GridSpec(2, 2, width_ratios=[3, 1])

# ax_background = fig.add_subplot(111)
# ax_title = fig.add_subplot(211)
# ax_lyrics = fig.add_subplot(gs[2])
# ax_chords = fig.add_subplot(gs[3])


# bbax_title = ax_title.get_position()
# bbax_lyrics = ax_lyrics.get_position()
# bbax_chords = ax_chords.get_position()
# bbax_background = ax_background.get_position()

# for ax in [ax_title, ax_lyrics, ax_chords, ax_background]:
#     ax.set_facecolor("none")
#     bb = ax.get_position()
#     width = (bb.get_points()[1][0] - bb.get_points()[0][0]) * fig_size[0]
#     height = (bb.get_points()[1][1] - bb.get_points()[0][1]) * fig_size[1]
#     ax.set_xlim([0, width])
#     ax.set_ylim([0, height])

# plt.gca().invert_yaxis()

# img = plt.imread("/home/ndejax/Downloads/background.jpg")
# ax_background.imshow(img, extent=[0, fig_size[0], 0, fig_size[1]], alpha=1)
# ax_background.patch.set_alpha(0.5)

# ax_title.text(5, 10, "salut ca va")
