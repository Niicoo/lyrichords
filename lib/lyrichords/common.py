from enum import Enum
import logging

# Get Logger
logger = logging.getLogger(__name__)

class Notation(Enum):
    ALPHABETICAL = "Alphabetical"
    SYLLABIC = "Syllabic"
    GERMAN_ALPHABETICAL = "German Alphabetical"


class Key(Enum):
    """
    (Height, Alphabetical Notation, Syllabic Notation, German alphabetic Notation)
    """
    C = (0,  "C",  "Do",  "C")
    D = (2,  "D",  "Re",  "D")
    E = (4,  "E",  "Mi",  "E")
    F = (5,  "F",  "Fa",  "F")
    G = (7,  "G",  "Sol", "G")
    A = (9,  "A",  "La",  "A")
    B = (11, "B",  "Si",  "H")

    def getHeight(self) -> int:
        return self.value[0]

    def getAlphabeticalName(self) -> str:
        return self.value[1]
    
    def getSyllabicName(self) -> str:
        return self.value[2]

    def getGermanAlphabeticalName(self) -> str:
        return self.value[3]

    def getName(self, notation: Notation) -> str:
        if notation == Notation.ALPHABETICAL:
            return self.getAlphabeticalName()
        elif notation == Notation.SYLLABIC:
            return self.getSyllabicName()
        elif notation == Notation.GERMAN_ALPHABETICAL:
            return self.getGermanAlphabeticalName()
        else:
            raise ValueError("Invalid notation input value")

class Alter(Enum):
    NONE = (0, "")
    SHARP = (1, "#")
    FLAT = (-1, "b")

    def getName(self) -> str:
        return self.value[1]

    def getHeightAlter(self) -> int:
        return self.value[0]

class Suffix(Enum):
    MAJOR = ""
    MINOR = "m"
    AUG = "aug"
    DIM = "dim"
    SEVEN = "7"
    MINOR_SEVEN = "m7"
    MAJOR_SEVEN = "maj7"
    SIX = "6"
    MINOR_SIX = "m6"
    ADD_NINE = "add9"
    MINOR_NINE = "m9"
    NINE = "9"
    SUS_SECOND = "sus2"
    SUS_FORTH = "sus4"
    SEVEN_SUS_FORTH = "7sus4"


class Chord():
    def __init__(self, key: Key, alter: Alter, suffix: Suffix, bass_key: Key = None, bass_alter: Alter = None):
        self.key: Key = key
        self.alter: Alter = alter
        self.suffix: Suffix = suffix
        self.bass_key: Key = bass_key
        self.bass_alter: Alter = bass_alter
        height = self.key.getHeight()
        height += self.alter.getHeightAlter()
        # In order to get an height only between 0 and 11 (12 = 0 = C)
        self._height: int = height % 12
        # If it's a slashed chord
        self._bass_height: int = None
        if (self.bass_key is not None) and (self.bass_alter is not None):
            bass_height = self.bass_key.getHeight()
            bass_height += self.bass_alter.getHeightAlter()
            self._bass_height = bass_height % 12

    def __str__(self):
        name = self.key.getAlphabeticalName() + self.alter.getName() + self.suffix.value
        if self.isSlashedChord():
            name += '/' + self.bass_key.getAlphabeticalName() + self.bass_alter.getName()
        return name

    def __repr__(self):
        name = f"{self._height}"
        if self.suffix.value != "":
            name += f"-{self.suffix.value}"
        if self.isSlashedChord():
            name += f"/{self._bass_height}"
        return name

    def isSlashedChord(self):
        return self._bass_height is not None

    def getName(self, notation: Notation = Notation.ALPHABETICAL) -> str:
        name = self.key.getName(notation) + self.alter.getName() + self.suffix.value
        if self.isSlashedChord():
            name += '/' + self.bass_key.getName(notation) + self.bass_alter.getName()
        return name

    def parse(name: str) -> "Chord":
        bass_key = None
        bass_alter = None
        chordname = name
        if '/' in name:
            chordname, bass_name = name.split('/')
            bass_note = Chord.parse(bass_name)
            bass_key = bass_note.key
            bass_alter = bass_note.alter
        for key in Key:
            for notation in key.value[1:]:
                for alter in Alter:
                    for suffix in Suffix:
                        tmp_name = notation.upper() + alter.getName().upper() + suffix.value.upper()
                        if tmp_name == chordname.upper():
                            return Chord(key, alter, suffix, bass_key, bass_alter)
        raise ValueError(f"Fail to parse chord: {name}")

    def getHeight(self) -> int:
        return self._height

    def __eq__(self, other: "Chord"):
        suffix_eq = self.suffix == other.suffix
        height_eq = self.getHeight() == other.getHeight()
        bass_eq = self._bass_height == other._bass_height
        return suffix_eq and height_eq and bass_eq

    def __hash__(self):
        return hash((self.suffix, self._height, self._bass_height))
