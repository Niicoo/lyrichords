from .common import Chord
import re
from collections import Counter
from dataclasses import dataclass, field
import logging
# Typing
from typing import List, Tuple, Dict, Iterator

# Get Logger
logger = logging.getLogger(__name__)


@dataclass
class ChordLocation():
    name: str
    index: int
    chord: Chord = field(init=False)

    def __post_init__(self):
        self.chord = Chord.parse(self.name)

class Verse():
    def __init__(self, text_line: str = "", chord_line: str = ""):
        self.text: str = text_line.strip()
        self.chords: List[ChordLocation] = []
        k = 0
        list_of_chords = chord_line.split()
        for chordname in list_of_chords:
            index = chord_line[k:].find(chordname)
            self.addChord(chordname, k + index)
            k = k + index + len(chordname)

    def __str__(self):
        if self.isEmpty():
            return "Empty Line Verse"
        text =   f"Verse : {self.text}"
        _chords = ""
        for chord in self.chords:
            _chords += (chord.index - len(_chords)) * " " + chord.name
        chords = f"Chords: {_chords}"
        return text + "\n" + chords

    def __repr__(self):
        return self.__str__()

    def setText(self, text: str):
        self.text = text

    def getText(self) -> str:
        return(self.text)

    def getChords(self) -> List[ChordLocation]:
        return(self.chords)

    def addChord(self, chordname: str, index: int):
        self.chords.append(ChordLocation(chordname, index))

    def isEmpty(self) -> bool:
        return not self.text

    def getChordList(self) -> List[str]:
        return [chord.name for chord in self.chords]

    def split(self, index: int) -> Tuple["Verse", "Verse"]:
        if(index > (len(self.text) - 1)):
            raise ValueError("Index cannot be superior to the text length")
        text1 = ""
        text2 = ""
        next_ind = 0
        for word in self.text.split(" "):
            next_ind += 0 if (next_ind == 0) else 1
            next_ind += len(word)
            if(next_ind <= index):
                text1 += " " if text1 else ""
                text1 += word
            else:
                text2 += " " if text2 else ""
                text2 += word
        verse1 = Verse(text1)
        verse2 = Verse(text2)
        for chord in self.chords:
            if(chord.index < len(text1)):
                verse1.addChord(chord.name, chord.index)
            else:
                verse2.addChord(chord.name, chord.index - len(text1) - 1)
        return verse1, verse2

    def splitByWords(self, nb_words: int, from_end: bool = True) -> Tuple["Verse", "Verse"]:
        words = self.text.split(" ")
        regex = re.compile('[^a-zA-Z]')
        words_fmt = [regex.sub('', word) for word in words]
        def count_nb_true_words(words):
            nb_words = 0
            for word in words:
                if(word != ''):
                    nb_words += 1
            return nb_words
        if count_nb_true_words(words_fmt) == nb_words:
            raise ValueError("Number of words to split exceeded")
        if from_end:
            for ind in range(len(words_fmt) - 1, -1, -1):
                nb_true_words = count_nb_true_words(words_fmt[ind:])
                if nb_true_words == nb_words:
                    break
        else:
            for ind in range(len(words_fmt), 0, -1):
                nb_true_words = count_nb_true_words(words_fmt[:ind])
                if nb_true_words == nb_words:
                    break
        return self.split(len(" ".join(words[:ind])))


class Song():
    def __init__(self, title: str = "", artist: str = "", composer: str = "", capo: int = 0, verses: List[Verse] = None):
        self.title: str = title
        self.artist: str = artist
        self.composer: str = composer
        self.capo: int = capo
        self.verses: List[Verse] = verses
        if self.verses is None:
            self.verses = []

    def __str__(self):
        text = f"Song(title={self.title}, artist={self.artist}, composer={self.composer}, capo={self.capo})"
        verses = ""
        for v in self.verses:
            verses += "\n" + v.__str__()
        return text + "\n" + verses

    def __repr__(self):
        return self.__str__()

    def __iter__(self) -> Iterator[Verse]:
        return iter(self.verses)

    def __next__(self) -> Verse:
        return next(self.verses)

    def __getitem__(self, item) -> Verse:
        return self.verses[item]

    def setTitle(self, title: str):
        self.title = title

    def setArtist(self, artist: str):
        self.artist = artist

    def setComposer(self, composer: str):
        self.composer = composer

    def setCapo(self, capo: int):
        self.capo = capo
    
    def getTitle(self) -> str:
        return(self.title)

    def getArtist(self) -> str:
        return(self.artist)

    def getComposer(self) -> str:
        return(self.composer)

    def getCapo(self) -> int:
        return(self.capo)

    def addVerse(self, verse: Verse) -> None:
        if(len(self.verses) == 0 and verse.isEmpty()):
            logger.info("Empty line ignored")
            return
        self.verses.append(verse)

    def setVerses(self, verses: List[Verse]):
        for verse in verses:
            self.addVerse(verse)

    def getVerses(self) -> List[Verse]:
        return self.verses

    def isChordsLine(line: str) -> bool:
        for word in line.split():
            try:
                Chord.parse(word)
            except ValueError as e:
                return False
        return True

    def fromFile(path: str, lyrics_first: bool = False) -> "Song":
        # Read the file
        with open(path, "r") as f:
            content = f.read()
        lines = content.split("\n")
        # Remove the last empty lines
        for k in range(len(lines)-1, -1, -1):
            if(not lines[k].strip()):
                lines.pop(k)
            else:
                break
        return Song.parse(lines, lyrics_first)

    def parse(lines: List[str], lyrics_first: bool = False) -> "Song":
        song = Song()
        # Read the lines
        previous_line = ""
        for line in lines:
            # IF Line is metadata (Capo, Title, etc...)
            if(len(line) > 5):
                if(line[0:5].upper() == "CAPO:"):
                    song.setCapo(int(line[5:].strip()))
                    continue
            if(len(line) > 6):
                if(line[0:6].upper() == "TITLE:"):
                    song.setTitle(line[6:].strip())
                    continue
            if(len(line) > 7):
                if(line[0:7].upper() == "ARTIST:"):
                    song.setArtist(line[7:].strip())
                    continue
            if(len(line) > 9):
                if(line[0:9].upper() == "COMPOSER:"):
                    song.setComposer(line[9:].strip())
                    continue
            # IF Empty line
            if not line.strip():
                song.addVerse(Verse())
                continue
            if(Song.isChordsLine(line)):
                if(lyrics_first):
                    # Lyrics First - (previous)None -> Chords
                    if not previous_line:
                        raise ValueError("Expecting a previous lyrics line")
                    # Lyrics First - (previous)Chords -> Chords
                    elif Song.isChordsLine(previous_line):
                        raise ValueError("Expecting a previous lyrics line")
                    # Lyrics First - (previous)Lyrics -> Chords
                    else:
                        song.addVerse(Verse(text_line=previous_line, chord_line=line))
                        previous_line = ""
                else:
                    # Chords First - (previous)None -> Chords
                    if not previous_line:
                        previous_line = line
                    # Chords First - (previous)Chords -> Chords
                    elif Song.isChordsLine(previous_line):
                        raise ValueError("Expecting a lyrics line: Got 2 consecutives chords lines")
                    # Chords First - (previous)Lyrics -> Chords
                    else:
                        raise ValueError("Well this error should never happened")
            else:
                if(lyrics_first):
                    # Lyrics First - (previous)None -> Lyrics
                    if not previous_line:
                        previous_line = line
                    # Lyrics First - (previous)Chords -> Lyrics
                    elif Song.isChordsLine(previous_line):
                        raise ValueError("Wrong file format: Got Lyrics line after a Chords line.")
                    # Lyrics First - (previous)Lyrics -> Lyrics
                    else:
                        song.addVerse(Verse(text_line=previous_line))
                        previous_line = line
                else:
                    # Chords First - (previous)None -> Lyrics
                    if not previous_line:
                        song.addVerse(Verse(text_line=line))
                    # Chords First - (previous)Chords -> Lyrics
                    elif Song.isChordsLine(previous_line):
                        song.addVerse(Verse(text_line=line, chord_line=previous_line))
                        previous_line = ""
                    # Chords First - (previous)Lyrics -> Lyrics
                    else:
                        raise ValueError("Well this error should never happened either")
        if(previous_line):
            if Song.isChordsLine(previous_line):
                raise ValueError("Got chords at the end... weird")
            song.addVerse(Verse(text_line=previous_line))
        return song

    def isComposerSet(self) -> bool:
        return len(self.composer) > 0

    def getChordsUsed(self, ind_line_start: int = 0, ind_line_stop: int = None) -> Dict[str, int]:
        chords = []
        for line in self.verses[ind_line_start : ind_line_stop]:
            chords += line.getChordList()
        return dict(Counter(chords))
