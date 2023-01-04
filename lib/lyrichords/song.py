from .common import Chord
import re
import bisect 
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

    def getIndexLastLetter(self) -> int:
        return self.index + len(self.name) - 1

@dataclass
class WordLocation():
    word: str
    index: int

    def getIndexLastLetter(self) -> int:
        return self.index + len(self.word) - 1

class Verse():
    def __init__(self, text_line: str = "", chord_line: str = ""):
        self.words: List[WordLocation] = []
        self.chords: List[ChordLocation] = []
        # Detecting words positions
        index = 0
        for word in text_line.split(' '):
            if word == "":
                index += 1
            else:
                self.addWord(word, index)
                index += len(word) + 1
        # Detecting chords positions
        index = 0
        for chordname in chord_line.split(' '):
            if chordname == "":
                index += 1
            else:
                self.addChord(chordname, index)
                index += len(chordname) + 1
        # Ensure the first index is 0
        self.resetIndex()

    def resetIndex(self):
        mini = 9999
        if len(self.words) > 0:
            mini = self.words[0].index
        if len(self.chords) > 0:
            mini = min(mini, self.chords[0].index)
        if mini != 9999:
            for k in range(0, len(self.words)):
                self.words[k].index -= mini
            for k in range(0, len(self.chords)):
                self.chords[k].index -= mini

    def __str__(self):
        if self.isEmpty():
            return "Empty Line Verse"
        _text = self.getTextLine()
        _chords = self.getChordsLine()
        text =   f"Text: ->{_text}<-"
        chords = f"Chords: ->{_chords}<-"
        return text + "   " + chords

    def __repr__(self):
        return self.__str__()

    def emptyText(self) -> bool:
        return len(self.words) == 0

    def getMinMaxIndex(self) -> Tuple[int, int]:
        mini = None
        maxi = None
        for word in self.words + self.chords:
            if mini is None:
                mini = word.index
            if maxi is None:
                maxi = word.getIndexLastLetter()
            if word.index < mini:
                mini = word.index
            if word.getIndexLastLetter() > maxi:
                maxi = word.getIndexLastLetter()
        return(mini, maxi)

    def getTextLine(self) -> str:
        _text = ""
        for word in self.words:
            _text += (word.index - len(_text)) * " " + word.word
        return(_text)

    def getChordsLine(self) -> str:
        _chords = ""
        for chord in self.chords:
            _chords += (chord.index - len(_chords)) * " " + chord.name
        return(_chords)

    def getWords(self) -> List[ChordLocation]:
        return(self.words)

    def getChords(self) -> List[ChordLocation]:
        return(self.chords)

    def addChord(self, chordname: str, index: int):
        self.chords.append(ChordLocation(chordname, index))

    def addWord(self, word: str, index: int):
        self.words.append(WordLocation(word, index))

    def isEmpty(self) -> bool:
        return (len(self.words) == 0) and (len(self.chords) == 0)

    def getChordList(self) -> List[str]:
        return [chord.name for chord in self.chords]

    def splitByIndex(self, index: int) -> Tuple["Verse", "Verse"]:
        """
            Index where to cut the verse
        """
        verse1 = Verse()
        verse2 = Verse()
        for word in self.words:
            if word.getIndexLastLetter() <= index:
                verse1.addWord(word.word, word.index)
            else:
                verse2.addWord(word.word, word.index)
        for chord in self.chords:
            chord_index = chord.index
            if chord_index <= index:
                for word in self.words:
                    if (chord.index >= word.index) and (chord.index <= word.getIndexLastLetter()):
                        chord_index = word.getIndexLastLetter()
            if chord_index <= index:
                verse1.addChord(chord.name, chord.index)
            else:
                verse2.addChord(chord.name, chord.index)
        verse1.resetIndex()
        verse2.resetIndex()
        return verse1, verse2

    def getPossibleCutIndexes(self) -> List[int]:
        indexes = []
        for ind_word, word in enumerate(self.words):
            last_letter_index = word.getIndexLastLetter()
            if ind_word < (len(self.words) - 1):
                indexes.append(last_letter_index)
            else:
                for chord in self.chords:
                    if chord.index > last_letter_index:
                        indexes.append(last_letter_index)
                        break
        for chord in self.chords:
            chord_index = chord.index
            for word in self.words:
                if (chord.index >= word.index) and (chord.index <= word.getIndexLastLetter()):
                    chord_index = word.getIndexLastLetter()
            if chord_index not in indexes:
                bisect.insort(indexes, chord_index)
        return indexes


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
        if verse.isEmpty():
            if len(self.verses) == 0:
                logger.debug("Empty line ignored")
                return
            elif self.verses[-1].isEmpty():
                logger.debug("Empty line ignored")
                return
        logger.debug(f"Adding Verse: {verse}")
        self.verses.append(verse)

    def setVerses(self, verses: List[Verse]):
        for verse in verses:
            self.addVerse(verse)

    def getVerses(self) -> List[Verse]:
        return self.verses

    def isChordsLine(line: str) -> bool:
        # Here I should remove all character such as: , - _
        for word in line.split():
            try:
                Chord.parse(word)
            except ValueError as e:
                return False
        return True

    def fromFile(path: str, lyrics_first: bool = False) -> "Song":
        logger.info(f"Parsing File: {path}")
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
            if(len(line) >= 5):
                if(line[0:5].upper() == "CAPO:"):
                    capo_str = line[5:].strip()
                    if capo_str == '': continue
                    song.setCapo(int(capo_str))
                    continue
            if(len(line) >= 6):
                if(line[0:6].upper() == "TITLE:"):
                    song.setTitle(line[6:].strip())
                    continue
            if(len(line) >= 7):
                if(line[0:7].upper() == "ARTIST:"):
                    song.setArtist(line[7:].strip())
                    continue
            if(len(line) >= 9):
                if(line[0:9].upper() == "COMPOSER:"):
                    song.setComposer(line[9:].strip())
                    continue
            is_empty_line = not line.strip()
            is_chords_line = Song.isChordsLine(line)
            if(lyrics_first):
                if is_empty_line:
                    # Empty Line
                    if previous_line:
                        song.addVerse(Verse(text_line=previous_line))
                    song.addVerse(Verse())
                    previous_line = ""
                elif is_chords_line:
                    # Chords Line
                    if not previous_line:
                        # Lyrics First - (previous)None -> Chords
                        # => Chord line without lyrics
                        song.addVerse(Verse(text_line="", chord_line=line))
                    else:
                        # Lyrics First - (previous)Lyrics -> Chords
                        song.addVerse(Verse(text_line=previous_line, chord_line=line))
                        previous_line = ""
                else:
                    # Lyrics Line
                    if not previous_line:
                        # Lyrics First - (previous)None -> Lyrics
                        previous_line = line
                    else:
                        # Lyrics First - (previous)Lyrics -> Lyrics
                        song.addVerse(Verse(text_line=previous_line))
                        previous_line = line
            else:
                if is_empty_line:
                    # Empty Line
                    if previous_line:
                        song.addVerse(Verse(text_line="", chord_line=previous_line))
                    song.addVerse(Verse())
                    previous_line = ""
                elif is_chords_line:
                    if not previous_line:
                        # Chords First - (previous)None -> Chords
                        previous_line = line
                    else:
                        # Chords First - (previous)Chords -> Chords
                        # => Chord line without lyrics
                        song.addVerse(Verse(text_line="", chord_line=previous_line))
                        previous_line = line
                else:
                    if not previous_line:
                        # Chords First - (previous)None -> Lyrics
                        song.addVerse(Verse(text_line=line))
                    else:
                        # Chords First - (previous)Chords -> Lyrics
                        song.addVerse(Verse(text_line=line, chord_line=previous_line))
                        previous_line = ""
        if(previous_line):
            if Song.isChordsLine(previous_line):
                song.addVerse(Verse(chord_line=previous_line))
            else:
                song.addVerse(Verse(text_line=previous_line))

        return song

    def isComposerSet(self) -> bool:
        return len(self.composer) > 0

    def getChordsUsed(self, ind_line_start: int = 0, ind_line_stop: int = None) -> Dict[str, int]:
        chords = []
        for line in self.verses[ind_line_start : ind_line_stop]:
            chords += line.getChordList()
        return dict(Counter(chords))
