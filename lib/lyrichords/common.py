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
    def __init__(self, key: Key, alter: Alter, suffix: Suffix):
        self.key: Key = key
        self.alter: Alter = alter
        self.suffix: Suffix = suffix
        height = self.key.getHeight()
        height += self.alter.getHeightAlter()
        # In order to get an height only between 0 and 11 (12 = 0 = C)
        self._height: int = height % 12

    def __str__(self):
        return self.key.getAlphabeticalName() + self.alter.getName() + self.suffix.value

    def __repr__(self):
        return f"{self._height}-{self.suffix.value}"

    def getName(self, notation: Notation = Notation.ALPHABETICAL) -> str:
        return self.key.getName(notation) + self.alter.getName() + self.suffix.value

    def parse(name: str) -> "Chord":
        for key in Key:
            for notation in key.value[1:]:
                for alter in Alter:
                    for suffix in Suffix:
                        tmp_name = notation.upper() + alter.getName().upper() + suffix.value.upper()
                        if tmp_name == name.upper():
                            return Chord(key, alter, suffix)
        raise ValueError(f"Fail to parse chord: {name}")

    def getHeight(self) -> int:
        return self._height

    def __eq__(self, other: "Chord"):
        suffix_eq = self.suffix == other.suffix
        height_eq = self.getHeight() == other.getHeight()
        return suffix_eq and height_eq

    def __hash__(self):
        return hash((self.suffix, self._height))
