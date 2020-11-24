from .common import COMPATIBLE_CHORDNAMES, Chord

class Verse:
    def __init__(self, text_line="", chord_line=""):
        self.text = text_line.strip()
        self.chords = []
        k = 0
        list_of_chords = chord_line.split()
        for chordname in list_of_chords:
            index = chord_line[k:].find(chordname)
            self.chords.append({"chord": Chord(chordname), "index": k + index})
            k = k + index + len(chordname)

    def setText(self, text):
        self.text = text

    def addChord(self, chord, index):
        if (type(chord) is str):
            in_chord = Chord(chord)
        else:
            in_chord = chord
        self.chords.append({"chord": in_chord, "index": index})

    def isEmptyLine(self):
        return not self.text

    def getChordList(self):
        return [chord["chord"].getName() for chord in self.chords]

    def split(self, ind_split):
        if(ind_split > (len(self.text) - 1)):
            raise ValueError("Index cannot be superior to the text length")
        text1 = ""
        text2 = ""
        next_ind = 0
        for k, word in enumerate(self.text.split(" ")):
            next_ind += 0 if (next_ind == 0) else 1
            next_ind = len(word) + next_ind
            if(next_ind <= ind_split):
                text1 += " " if text1 else ""
                text1 += word
            else:
                text2 += " " if text2 else ""
                text2 += word
        verse1 = Verse(text1)
        verse2 = Verse(text2)
        for chord in self.chords:
            if(chord["index"] < len(text1)):
                verse1.addChord(chord["chord"], chord["index"])
            else:
                verse2.addChord(chord["chord"], chord["index"] - len(text1))
        return verse1, verse2


class Song:
    def __init__(self, lyrics_first=False):
        self.title = ""
        self.artist = ""
        self.composer = ""
        self.lyrics_first = lyrics_first
        self.capo = 0
        self.lyrics = []

    def load(self, path):
        # Read the file
        with open(path, "r") as f:
            lines = f.readlines()
        # Remove the last empty lines
        for k in range(len(lines)-1, -1, -1):
            if(not lines[k].strip()):
                lines.pop(k)
            else:
                break
        # Read the lines
        previous_line = ""
        nextlinemustbelyrics = True
        lyricsStarted = False
        self.lyrics = []
        for k, line in enumerate(lines):
            if(len(line) > 5):
                if(line[0:5].upper() == "CAPO:"):
                    self.capo = int(line[5:].strip())
                    continue
            if(len(line) > 6):
                if(line[0:6].upper() == "TITLE:"):
                    self.title = line[6:].strip()
                    continue
            if(len(line) > 7):
                if(line[0:7].upper() == "ARTIST:"):
                    self.artist = line[7:].strip()
                    continue
            if(len(line) > 9):
                if(line[0:9].upper() == "COMPOSER:"):
                    self.composer = line[9:].strip()
                    continue
            
            # Empty line
            if not line.strip():
                if lyricsStarted:
                    if len(self.lyrics) > 0:
                        if not self.lyrics[-1].isEmptyLine():
                            self.lyrics.append(Verse())
                continue
            
            lyricsStarted = True
            if(self.isChordLine(line)):
                if(self.lyrics_first):
                    # Lyrics First - (previous)None -> Chords
                    if not previous_line:
                        raise ValueError("Expecting a previous lyrics line")
                    # Lyrics First - (previous)Chords -> Chords
                    elif self.isChordLine(previous_line):
                        raise ValueError("Expecting a previous lyrics line")
                    # Lyrics First - (previous)Lyrics -> Chords
                    else:
                        self.lyrics.append(Verse(text_line=previous_line, chord_line=line))
                        previous_line = ""
                else:
                    # Chords First - (previous)None -> Chords
                    if not previous_line:
                        previous_line = line
                    # Chords First - (previous)Chords -> Chords
                    elif self.isChordLine(previous_line):
                        raise ValueError("Expecting a lyrics line: Got 2 consecutives chords lines")
                    # Chords First - (previous)Lyrics -> Chords
                    else:
                        raise ValueError("Well this error should never happened")
            else:
                if(self.lyrics_first):
                    # Lyrics First - (previous)None -> Lyrics
                    if not previous_line:
                        previous_line = line
                    # Lyrics First - (previous)Chords -> Lyrics
                    elif self.isChordLine(previous_line):
                        raise ValueError("Wrong file format: Got Lyrics line after a Chords line.")
                    # Lyrics First - (previous)Lyrics -> Lyrics
                    else:
                        self.lyrics.append(Verse(text_line=previous_line))
                        previous_line = line
                else:
                    # Chords First - (previous)None -> Lyrics
                    if not previous_line:
                        self.lyrics.append(Verse(text_line=line))
                    # Chords First - (previous)Chords -> Lyrics
                    elif self.isChordLine(previous_line):
                        self.lyrics.append(Verse(text_line=line, chord_line=previous_line))
                        previous_line = ""
                    # Chords First - (previous)Lyrics -> Lyrics
                    else:
                        raise ValueError("Well this error should never happened either")
        if(previous_line):
            if self.isChordLine(previous_line):
                raise ValueError("Got chords at the end... weird")
            self.lyrics.append(Verse(text_line=previous_line))

    def isChordLine(self, line):
        for word in line.split():
            if not (word.upper() in COMPATIBLE_CHORDNAMES):
                return False
        return True

    def isComposerSet(self):
        return len(self.composer) > 0

    def getChordsUsed(self, ind_line_start=0, line_stop=None):
        chordlist = {}
        for line in self.lyrics[ind_line_start:line_stop]:
            chordsline = line.getChordList()
            for name in chordsline:
                if not (name in chordlist):
                    chordlist[name] = 1
                else:
                    chordlist[name] += 1
        return chordlist
