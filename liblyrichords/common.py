import matplotlib.patches as mpatches


NOTATIONS = {   "Syllabic": ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si"],
                "Alphabetical": ["C", "D", "E", "F", "G", "A", "B"],
                "German Alphabetical": ["C", "D", "E", "F", "G", "A", "H"]}
ALTERATIONS = {"", "b", "#"}
QUALITIES = {"", "7", "m", "m7", "dim", "aug", "6", "maj7", "9"}


COMPATIBLE_CHORDNAMES = {}
for notation in NOTATIONS:
    for note in NOTATIONS[notation]:
        for alter in ALTERATIONS:
            for quality in QUALITIES:
                COMPATIBLE_CHORDNAMES[(note + alter + quality).upper()] = {"note": note, "alter": alter, "quality": quality}


class Chord:
    def __init__(self, chordname):
        name = chordname.upper()
        if not (name in COMPATIBLE_CHORDNAMES):
            raise ValueError("Invalid input Chord: '%s'" % chordname)
        self.note = COMPATIBLE_CHORDNAMES[name]["note"]
        self.alter = COMPATIBLE_CHORDNAMES[name]["alter"]
        self.quality = COMPATIBLE_CHORDNAMES[name]["quality"]

    def getNote(self, notation=None):
        if(notation is None):
            return self.note
        for key, notes in NOTATIONS.items():
            if(self.note in notes):
                ind_note = notes.index(self.note)
                return NOTATIONS[notation][ind_note]
        raise ValueError("Woaah, This error should never been raised, unless you modified 'COMPATIBLE_CHORDNAMES' ...") 
    
    def getAlter(self):
        return self.alter
    
    def getQuality(self):
        return self.quality
    
    def getName(self, notation=None):
        return self.getNote(notation) + self.alter + self.quality


def mm2inch(value):
    return value / 25.4


def font2mm(fontsize):
    return fontsize * 0.3527777778


def textRectangled(ax, x, y, text, font_size, color=None, rect_width=8, fontweight="bold"):
    """
        x,y: center of the text location
    """
    t = ax.text(x, y, text,
        fontsize=font_size,
        fontweight=fontweight,
        horizontalalignment='center',
        verticalalignment='center')
    h = 0.05 * font2mm(font_size)
    x_rect = x - rect_width / 2.0
    y_rect = y - font2mm(font_size) / 2 + 0.4 * font2mm(font_size)
    ecolor = color if color else "gray"
    fcolor = color if color else "none"
    rect = mpatches.FancyBboxPatch((x_rect, y_rect), width=rect_width, height=h, alpha=0.4, facecolor=fcolor, edgecolor=ecolor, boxstyle='round,pad=1.5')
    ax.add_artist(rect)
