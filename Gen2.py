import json
import Gen1
from Gen1 import attributedDictionary

class location:

    def __init__(self, gameType : str) -> None:
        self.tID = 0x2009
        self.rivalName = 0x2021
        self.timePlayed = 0x2054
        if gameType == "GS":
            self.gameCoins = 0x23E2
            self.money = 0x23DB
            self.johtoBadges = 0x23E4
            self.kantoBadges = 0x23E5
        else:
            self.gameCoins = 0x23E3
            self.money = 0x23DC
            self.johtoBadges = 0x23E5
            self.kantoBadges = 0x23E6

class gameSave:
    def __init__(self, fpath : str) -> None:
        with open(fpath, "rb") as sav:
            self.dump = sav.read()
            # get game type GS/ C / determine validity of savefile
            self.checkGameType(self.generateChecksum(0x2009,  0x2D68), self.generateChecksum(0x2009, 0x2B82))
            locations = location(self.version)

            # get trainer ID
            sav.seek(locations.tID)
            self.tID = int.from_bytes(sav.read(2))

            # get trainer name
            byte = sav.read(11)
            self.name = ""
            for i in byte:
                if i == 0x50:
                    break
                self.name += GEN2_CHARMAP[i]

            # get rival name
            sav.seek(locations.rivalName)
            byte = sav.read(11)
            self.rivalName = ""
            for i in byte:
                if i == 0x50:
                    break
                self.rivalName += GEN2_CHARMAP[i]

            # calculate timeplayed
            sav.seek(locations.timePlayed)

            self.time = sav.read(1)[0] * 3600 + sav.read(1)[0] * 60 + sav.read(1)[0]

            # get remaining game coins (Where gold silver and crystal mem addresses start differing)
            sav.seek(locations.gameCoins)
            self.gameCoins = int.from_bytes(sav.read(2))

            # read money
            sav.seek(locations.money)
            self.money = int.from_bytes(sav.read(3))

            # read kanto badges

            sav.seek(locations.kantoBadges)

            self.kantoBadges = attributedDictionary()  

            binaryBadgeReg = bin(sav.read(1)[0])[2:]
            for i in range(len(binaryBadgeReg)):
                if binaryBadgeReg[i] == "1":
                    self.kantoBadges.__setattr__(Gen1.BADGES[i], True)
                else:
                    self.kantoBadges.__setattr__(Gen1.BADGES[i], False)

            sav.seek(locations.johtoBadges)
            self.johtoBadges = attributedDictionary()

            binaryBadgeReg = bin(sav.read(1)[0])[2:]
            for i in range(len(binaryBadgeReg)):
                if binaryBadgeReg[i] == "1":
                    self.johtoBadges.__setattr__(BADGES[i], True)
                else:
                    self.johtoBadges.__setattr__(BADGES[i], False)

    def generateChecksum(self, startOffset : int, endOffset : int):
        return sum(self.dump[startOffset:endOffset]) & 0xFFFF

    def checkGameType(self, GSchecksum : int, Cchecksum : int):
        """Checksum should be checksum 1"""
        if int.from_bytes(self.dump[0x2D0D:0x2D0F], "little") == Cchecksum:
            self.version = "C"
        elif int.from_bytes(self.dump[0x2D69:0x2D6B], "little") == GSchecksum:
            self.version = "GS"
        else:
            raise NameError("Could not determine type of game")

GEN2_CHARMAP = {
    0x00: "\0",

    # Control / special characters
    0x14: "<PLAYER>",
    0x15: "<MOBILE>",
    0x16: "<CR>",
    0x1F: " ",
    0x22: "\n",
    0x24: "<POKE>",
    0x25: "<WBR>",
    0x38: "<RED>",
    0x39: "<GREEN>",
    0x3F: "<ENEMY>",
    0x49: "<MOM>",
    0x4A: "<PKMN>",
    0x4B: "<CONT>",
    0x4C: "<SCROLL>",
    0x4E: "<NEXT>",
    0x4F: "<LINE>",
    0x50: "@",
    0x51: "<PARA>",
    0x52: "<PLAYER>",
    0x53: "<RIVAL>",
    0x54: "#",
    0x55: "<CONT>",
    0x56: "……",
    0x57: "<DONE>",
    0x58: "<PROMPT>",
    0x59: "<TARGET>",
    0x5A: "<USER>",
    0x5B: "<PC>",
    0x5C: "<TM>",
    0x5D: "<TRAINER>",
    0x5E: "<ROCKET>",
    0x5F: "<DEXEND>",

    # Extra font
    0x60: "■",
    0x61: "▲",
    0x62: "☎",
    0x63: "<BOLD_D>",
    0x64: "<BOLD_E>",
    0x65: "<BOLD_F>",
    0x66: "<BOLD_G>",
    0x67: "<BOLD_H>",
    0x68: "<BOLD_I>",
    0x69: "<BOLD_V>",
    0x6A: "<BOLD_S>",
    0x6B: "<BOLD_L>",
    0x6C: "<BOLD_M>",
    0x6D: ":",
    0x6E: "′",
    0x6F: "″",
    0x70: "<PO>",
    0x71: "<KE>",
    0x72: "“",
    0x73: "”",
    0x74: "·",
    0x75: "…",
    0x76: "ぁ",
    0x77: "ぇ",
    0x78: "ぉ",
    0x79: "┌",
    0x7A: "─",
    0x7B: "┐",
    0x7C: "│",
    0x7D: "└",
    0x7E: "┘",
    0x7F: " ",

    # Uppercase
    0x80: "A",
    0x81: "B",
    0x82: "C",
    0x83: "D",
    0x84: "E",
    0x85: "F",
    0x86: "G",
    0x87: "H",
    0x88: "I",
    0x89: "J",
    0x8A: "K",
    0x8B: "L",
    0x8C: "M",
    0x8D: "N",
    0x8E: "O",
    0x8F: "P",
    0x90: "Q",
    0x91: "R",
    0x92: "S",
    0x93: "T",
    0x94: "U",
    0x95: "V",
    0x96: "W",
    0x97: "X",
    0x98: "Y",
    0x99: "Z",

    # Punctuation
    0x9A: "(",
    0x9B: ")",
    0x9C: ":",
    0x9D: ";",
    0x9E: "[",
    0x9F: "]",

    # Lowercase
    0xA0: "a",
    0xA1: "b",
    0xA2: "c",
    0xA3: "d",
    0xA4: "e",
    0xA5: "f",
    0xA6: "g",
    0xA7: "h",
    0xA8: "i",
    0xA9: "j",
    0xAA: "k",
    0xAB: "l",
    0xAC: "m",
    0xAD: "n",
    0xAE: "o",
    0xAF: "p",
    0xB0: "q",
    0xB1: "r",
    0xB2: "s",
    0xB3: "t",
    0xB4: "u",
    0xB5: "v",
    0xB6: "w",
    0xB7: "x",
    0xB8: "y",
    0xB9: "z",

    # German characters (present in Western font)
    0xC0: "Ä",
    0xC1: "Ö",
    0xC2: "Ü",
    0xC3: "ä",
    0xC4: "ö",
    0xC5: "ü",

    # Contractions
    0xD0: "'d",
    0xD1: "'l",
    0xD2: "'m",
    0xD3: "'r",
    0xD4: "'s",
    0xD5: "'t",
    0xD6: "'v",

    # Symbols / punctuation
    0xDF: "←",
    0xE0: "'",
    0xE1: "<PK>",
    0xE2: "<MN>",
    0xE3: "-",
    0xE6: "?",
    0xE7: "!",
    0xE8: ".",
    0xE9: "&",
    0xEA: "é",
    0xEB: "→",
    0xEC: "▷",
    0xED: "▶",
    0xEE: "▼",
    0xEF: "♂",
    0xF0: "¥",
    0xF1: "×",
    0xF2: ".",
    0xF3: "/",
    0xF4: ",",
    0xF5: "♀",

    # Numbers
    0xF6: "0",
    0xF7: "1",
    0xF8: "2",
    0xF9: "3",
    0xFA: "4",
    0xFB: "5",
    0xFC: "6",
    0xFD: "7",
    0xFE: "8",
    0xFF: "9",
}
BADGES = ["Zephyr", "Insect", "Plain", "Fog", "Storm", "Mineral", "Glacier", "Rising"]

game = gameSave(r"D:\Emulation\Games\Gameboy (all of them)\Pokémon - Crystal Version.sav")
print(game.johtoBadges)