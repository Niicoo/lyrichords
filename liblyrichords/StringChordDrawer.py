from abc import ABC
import matplotlib.patches as mpatches
from .common import textRectangled, font2mm


class StringChordDrawer(ABC):
    def __init__(self, lefthand=False):
        # Drawing parameters
        self.fret_width = 6
        self.string_width = 5
        self.title_font = 12
        self.circle_radius = 1.5
        self.lefthand = lefthand

    def getNumberOfString(self):
        return len(self.frets["C"])

    def getTitleHeight(self):
        return font2mm(self.title_font) + 2

    def getMaxFretUsed(self, chordlist):
        max_fret = 0
        for key in chordlist:
            values = self.getFrets(key)
            if(max(values) > max_fret):
                max_fret = max(values)
        return max_fret

    def getFrets(self, chord):
        chordname = chord if type(chord) is str else chord.getName(notation="Alphabetical")
        chordname = chordname.replace("Cb", "B").replace("Db", "C#").replace("D#", "Eb") \
                                .replace("E#", "F").replace("Fb", "E").replace("Gb", "F#") \
                                .replace("G#", "Ab").replace("A#", "Bb").replace("B#", "C")
        return self.frets[chordname]

    def getSize(self, nb_frets):
        title_height = self.getTitleHeight()
        height = title_height + nb_frets * self.fret_width
        width = (self.getNumberOfString() - 1) * self.string_width
        return width, height

    def getMaxFret(self):
        max_fret = 0
        for key, values in self.frets.items():
            if(max(values) > max_fret):
                max_fret = max(values)
        return max_fret

    def drawFretsAndStrings(self, ax, nb_frets, x_offset, y_offset):
        y_start = y_offset + self.getTitleHeight()
        nb_strings = self.getNumberOfString()
        for k in range(0, nb_frets + 1):
            x = [x_offset, x_offset + (nb_strings-1) * self.string_width]
            y = [y_start + k * self.fret_width, y_start + k * self.fret_width]
            if(k == 0):
                linew = 3
            else:
                linew = 1
            ax.plot(x, y, color='gray', linewidth=linew, zorder=-1)
        for k in range(0, nb_strings):
            x = [x_offset + k * self.string_width, x_offset + k * self.string_width]
            y = [y_start, y_start + nb_frets * self.fret_width]
            ax.plot(x, y, color='gray', zorder=-1)

    def drawChordName(self, ax, chord, x_offset, y_offset, notation, color=None):
        chordname = chord.getName(notation)
        nb_strings = self.getNumberOfString()
        x = x_offset + ((nb_strings-1) * self.string_width) / 2.0
        y = y_offset + self.getTitleHeight() / 2.0
        textRectangled(ax, x, y, chordname, self.title_font, color)

    def drawFingers(self, ax, chord, x_offset, y_offset):
        positions = self.getFrets(chord)
        if(self.lefthand):
            positions = positions[::-1]
        for num_string, position in enumerate(positions):
            if(position <= 0):
                continue
            x = x_offset + num_string * self.string_width
            y = y_offset + self.getTitleHeight() + position * self.fret_width - (self.fret_width / 2.0)
            circle = mpatches.Circle((x, y), self.circle_radius, color="dimgray", zorder=1)
            ax.add_artist(circle)

    def draw(   self,
                chord,
                ax,
                x_offset,
                y_offset,
                notation,
                color = None,
                nb_visible_fret=None):
        if(nb_visible_fret):
            nb_frets = nb_visible_fret
        else:
            nb_frets = self.getMaxFret()
        self.drawChordName(ax, chord, x_offset, y_offset, notation, color)
        self.drawFretsAndStrings(ax, nb_frets, x_offset, y_offset)
        self.drawFingers(ax, chord, x_offset, y_offset)


# http://ukulelear.blogspot.com/p/chord-chart.html
# To keep it simple, the notation of the chords must be Alphabetical (C, D, E, F, G, A, B)
class UkuleleGCEA(StringChordDrawer):
    def __init__(self, lefthand=False):
        self.frets = {
            # C
            "C":       [0, 0, 0, 3], "C7":      [0, 0, 0, 1], "Cm":      [3, 3, 3, 0], 
            "Cm7":     [3, 3, 3, 3], "Cdim":    [2, 3, 2, 3], "Caug":    [1, 0, 0, 3], 
            "C6":      [0, 0, 0, 0], "Cmaj7":   [0, 0, 0, 2], "C9":      [0, 2, 0, 1], 
            # C#
            "C#":      [1, 1, 1, 4], "C#7":     [1, 1, 1, 2], "C#m":     [1, 1, 0, 3], 
            "C#m7":    [4, 4, 4, 4], "C#dim":   [0, 1, 0, 1], "C#aug":   [2, 1, 1, 0], 
            "C#6":     [1, 1, 1, 1], "C#maj7":  [1, 1, 1, 3], "C#9":     [1, 3, 1, 2], 
            # D
            "D":       [2, 2, 2, 5], "D7":      [2, 2, 2, 3], "Dm":      [2, 2, 1, 0], 
            "Dm7":     [2, 2, 1, 3], "Ddim":    [1, 2, 1, 2], "Daug":    [3, 2, 2, 1], 
            "D6":      [2, 2, 2, 2], "Dmaj7":   [2, 2, 2, 4], "D9":      [2, 4, 2, 3], 
            # Eb
            "Eb":      [3, 3, 3, 1], "Eb7":     [3, 3, 3, 4], "Ebm":     [3, 3, 2, 1], 
            "Ebm7":    [3, 3, 2, 4], "Ebdim":   [2, 3, 2, 3], "Ebaug":   [2, 1, 1, 4], 
            "Eb6":     [3, 3, 3, 3], "Ebmaj7":  [3, 3, 3, 0], "Eb9":     [0, 1, 1, 1], 
            # E
            "E":       [4, 4, 4, 2], "E7":      [1, 2, 0, 2], "Em":      [0, 4, 3, 2], 
            "Em7":     [0, 2, 0, 2], "Edim":    [0, 1, 0, 1], "Eaug":    [1, 0, 0, 3], 
            "E6":      [1, 0, 2, 0], "Emaj7":   [1, 3, 0, 2], "E9":      [1, 2, 2, 2], 
            # F
            "F":       [2, 0, 1, 0], "F7":      [2, 3, 1, 0], "Fm":      [1, 0, 1, 3], 
            "Fm7":     [1, 3, 1, 3], "Fdim":    [1, 2, 1, 2], "Faug":    [2, 1, 1, 0], 
            "F6":      [2, 2, 1, 3], "Fmaj7":   [2, 4, 1, 3], "F9":      [2, 3, 3, 3], 
            # F#
            "F#":      [3, 1, 2, 1], "F#7":     [3, 4, 2, 4], "F#m":     [2, 1, 2, 0], 
            "F#m7":    [2, 4, 2, 4], "F#dim":   [2, 3, 2, 3], "F#aug":   [4, 3, 2, 2], 
            "F#6":     [3, 3, 2, 4], "F#maj7":  [0, 1, 1, 1], "F#9":     [1, 1, 0, 1], 
            # G
            "G":       [0, 2, 3, 2], "G7":      [0, 2, 1, 2], "Gm":      [0, 2, 3, 1], 
            "Gm7":     [0, 2, 1, 1], "Gdim":    [0, 1, 0, 1], "Gaug":    [4, 3, 3, 2], 
            "G6":      [0, 2, 0, 2], "Gmaj7":   [0, 2, 2, 2], "G9":      [2, 2, 1, 2], 
            # Ab
            "Ab":      [5, 3, 4, 3], "Ab7":     [1, 3, 2, 3], "Abm":     [1, 3, 2, 3], 
            "Abm7":    [0, 3, 2, 2], "Abdim":   [1, 2, 1, 2], "Abaug":   [1, 0, 0, 0], 
            "Ab6":     [1, 3, 1, 3], "Abmaj7":  [1, 3, 3, 3], "Ab9":     [3, 3, 2, 3], 
            # A
            "A":       [2, 1, 0, 0], "A7":      [0, 1, 0, 0], "Am":      [2, 0, 0, 0], 
            "Am7":     [0, 4, 3, 3], "Adim":    [2, 3, 2, 3], "Aaug":    [2, 1, 1, 1], 
            "A6":      [2, 4, 2, 4], "Amaj7":   [1, 1, 0, 0], "A9":      [0, 1, 0, 2], 
            # Bb
            "Bb":      [3, 2, 1, 1], "Bb7":     [1, 2, 1, 1], "Bbm":     [3, 1, 1, 1], 
            "Bbm7":    [1, 1, 1, 1], "Bbdim":   [0, 1, 0, 1], "Bbaug":   [3, 2, 2, 1], 
            "Bb6":     [0, 2, 1, 1], "Bbmaj7":  [3, 2, 1, 0], "Bb9":     [1, 2, 1, 3], 
            # B
            "B":       [4, 3, 2, 2], "B7":      [2, 3, 2, 2], "Bm":      [4, 2, 2, 2], 
            "Bm7":     [2, 2, 2, 2], "Bdim":    [1, 2, 1, 2], "Baug":    [4, 3, 3, 2], 
            "B6":      [1, 3, 2, 2], "Bmaj7":   [3, 3, 2, 2], "B9":      [2, 3, 2, 4], 
        }
        super(UkuleleGCEA, self).__init__(lefthand)


# Example how to automatically generate pre formatted python code for guitar chord from https://github.com/tombatossals/chords-db/tree/master/lib
# import json
# jschords = json.loads(open("guitar.json").read())

# with open("temp.txt", "w") as fout:
#     for key in ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]:
#         fout.write("\n# %s\n" % key)
#         for suffix in ["", "7", "m", "m7", "dim", "aug", "6", "maj7", "9"]:
#             if((suffix == "m7") or (suffix == "6")):
#                 fout.write("\n")
#             complete_key = key + suffix
#             jsonsuffix = suffix
#             if suffix == "m":
#                 jsonsuffix = "minor"
#             for k_chord, chord in enumerate(jschords["chords"][key.replace("#", "sharp")]):
#                 if(chord["suffix"] == jsonsuffix):
#                     ind = k_chord
#                     break
#             frets = jschords["chords"][key.replace("#", "sharp")][k_chord]["positions"][0]["frets"]
#             if "capo" in jschords["chords"][key.replace("#", "sharp")][k_chord]["positions"][0]:
#                 print("oh nonnn %s\n" % complete_key)
#             fout.write("{0:<10} [{1:>2}, {2:>2}, {3:>2}, {4:>2}, {5:>2}, {6:>2}]".format("\"" + complete_key + "\":", frets[0], frets[1], frets[2], frets[3], frets[4], frets[5]))
#             fout.write(", ")