from Gen1 import attributedDictionary
import json
import gameVersions
from gameVersions import gameVersion

GEN3_SUMLEN = [3884,3968,3968,3968,3848,3968,3968,3968,3968,3968,3968,3968,3968,2000]

class location:
    def __init__(self, gameversion : gameVersion, initialSection : int):
        self.game = gameversion
        self.section0 = 0
        self.section1 = 0
        self.section2 = 0
        self.section3 = 0
        self.section4 = 0
        self.section5 = 0
        self.section6 = 0
        self.section7 = 0
        self.section8 = 0
        self.section9 = 0
        self.section10 = 0
        self.section11 = 0
        self.section12 = 0
        self.section13 = 0

        self.__setattr__(f"section{initialSection}", 0)
        for i in range(14):
            print(f"set section{(i + initialSection) % 14}")
            self.__setattr__(f"section{(i + initialSection) % 14}", 0x1000 * i)

        self.section0Offsets()
        self.section1Offsets()

    def section0Offsets(self):
        self.playerName = self.section0
        self.playerGender = self.section0 + 0x08
        self.tID = self.section0 + 0x0A
        self.time = self.section0 + 0x0E
        self.options = self.section0 + 0x13
        if self.game == gameVersions.E: self.securityCode = self.section0 + 0xAC
        elif self.game == gameVersions.FRLG: self.securityCode = self.section0 + 0x0AF8
    
    def section1Offsets(self):
        self.teamSize = self.section1 + 0x34 if self.game == gameVersions.FRLG else self.section1 + 0x234
        self.team = self.teamSize + 4
        self.money = self.team + 600
        self.coins = self.money + 4
        self.pcItems = self.coins+4
        self.itemPocket = self.section1 + 0x0560 if self.game in [gameVersions.RS, gameVersions.E] else self.section1 + 0x310
        self.keyItemPocket = self.section1 + {gameVersions.RS: 0x05B0, gameVersions.E: 0x05D8, gameVersions.FRLG: 0x03B8}[self.game]
        self.ballPocket = self.section1 + {gameVersions.RS: 0x0600, gameVersions.E: 0x0650, gameVersions.FRLG: 0x430}[self.game]
        self.tmCase = self.section1 + {gameVersions.RS: 0x0640, gameVersions.E: 0x0690, gameVersions.FRLG: 0x0464}[self.game]
        self.berryPocket = self.section1 + {gameVersions.RS: 0x0740, gameVersions.E: 0x0790, gameVersions.FRLG: 0x054C}[self.game]

    def validateChecksums(self):
        for i in range(14):
            off = getattr(self, f"section{i}")

            tot = 0

            for x in range(0, GEN3_SUMLEN[i], 4):
                word = int.from_bytes(savBytes[x+off:x+off + 4], "little")
                tot = (tot + word) & 0xFFFFFFFF

            final = ((tot >> 16) + (tot & 0xFFFF)) & 0xFFFF

            stored = int.from_bytes(savBytes[off+0xFF6:off+0xFF8], "little")

            print(
                f"SECTION {i}: "
                f"calculated={final:04X}, "
                f"stored={stored:04X}"
            )

            if final != stored:
                raise ValueError(f"Unable to validate checksum {i}")

class gameSave:

    def __init__(self, fpath : str):
        global savBytes
        with open(fpath, "rb") as sav:
            savBytes = sav.read()
            sav.seek(0)
            sects : list[int] = []
            for i in range(14):
                sav.seek(0x1000 * i)
                sav.read(0xff4)
                sects.append(int.from_bytes(sav.read(2), "little"))
            if sorted(sects) != list(range(14)): raise ValueError("Save file one is missing atleast one section")

            # determine game type
            #FRLG Test
            sav.seek(0x1000*sects.index(0) + 0xAC)
            self.game : gameVersion | None = None
            if int.from_bytes(sav.read(2), 'little') == 1: self.game = gameVersions.FRLG


            # RSE Test
            if not self.game:
                sav.seek(0x1000*sects.index(0))
                trainerName = self.readText(sav.read(7))

                sav.seek(0x1000*sects.index(0) + 0xAC)
                test = self.readText(sav.read(7))

                if trainerName == test or test == 0: self.game = gameVersions.RS
                else: self.game = gameVersions.E

            if not self.game: raise ValueError("Couldn't determine game")
            print(self.game.title)

            locations = location(self.game, sects[0])

            # player name (again I know)

            sav.seek(locations.playerName)
            print(sav.tell())
            self.name = self.readText(sav.read(7))

            # gender
            sav.seek(locations.playerGender)
            self.gender = "F" if sav.read(1)[0] == 1 else "M"

            # tID/ sID
            sav.seek(locations.tID)
            full = int.from_bytes(sav.read(4), "little")
            self.tID = full & 0xFFFF
            self.sID = full >> 16

            # time played
            sav.seek(locations.time)

            self.hours = int.from_bytes(sav.read(2), "little")
            self.minutes = sav.read(1)[0]
            self.seconds = sav.read(1)[0]
            if self.game in [gameVersions.FRLG, gameVersions.E]:
                sav.seek(locations.securityCode)
                self.secCode = int.from_bytes(sav.read(4), "little")
            else: self.secCode = 0

            print(self.name, self.gender, self.tID, self.sID, self.hours, self.minutes, self.seconds)

            # read sector 1

            # team size

            sav.seek(locations.teamSize)
            print(locations.teamSize)
            self.teamSize = int.from_bytes(sav.read(4), 'little') if self.game != gameVersions.FRLG else sav.read(1)[0]

            # read gamecoins and dosh

            sav.seek(locations.money)
            self.money = int.from_bytes(sav.read(4), 'little') ^ self.secCode

            sav.seek(locations.coins)
            self.gameCoins = int.from_bytes(sav.read(2), 'little') ^ (self.secCode >> 16)

            print(self.teamSize, self.money, self.gameCoins)

            # add item bag parsing when can be bothered

            sav.seek(locations.team)

            for i in range(self.teamSize):
                data = sav.read(100)
                print(f"slot {i}: offset={sav.tell() - 100:#x}, length={len(data)}")
                
                if len(data) != 100:
                    print("Incomplete Pokémon structure")
                    break

                temp = pokemon(data, self)
                print(temp.speciesName)


    def readText(self, bytes : bytes):
        if sum(bytes) == 0: return 0
        out = ""
        for i in bytes:
            if i == 0xFF: break
            out += GEN3_CHARMAP[i]
        return out

class pokemon:
    def __init__(self, data: bytes, parent: gameSave):
        self.personalityValue = int.from_bytes(data[0:4], "little")
        self.otID = int.from_bytes(data[4:8], "little")

        self.nick = parent.readText(data[8:18])
        print(f"OT ID: {self.otID:08X}")

        self.otName = parent.readText(data[0x14:0x1B])

        substruct = data[0x20:0x50]
        dectKey = self.otID ^ self.personalityValue

        subDectrip = b"".join(
            (int.from_bytes(substruct[x:x+4], "little") ^ dectKey).to_bytes(
                4, "little"
            )
            for x in range(0, 48, 4)
        )
        check = sum([int.from_bytes(subDectrip[i:i+2], 'little') for i in range(0,len(subDectrip), 2)]) & 0xFFFF
        if int.from_bytes(data[0x1C:0x1E], 'little') != check: raise ValueError(f"Bad checksum {check} Stored {data[0x1C:0x1E]} \n data {data}")
        subStructOrder = GEN3_SUBSTRUCTURE_ORDER[
            self.personalityValue % 24
        ]

        growth = subDectrip[
            subStructOrder.index("G") * 12:
            (subStructOrder.index("G") + 1) * 12
        ]

        self.internalSpecies = int.from_bytes(growth[0:2], "little")
        self.species = internalToNational(self.internalSpecies)
        self.speciesName = DEX[self.species-1] if self.species else None
        print(self.internalSpecies, self.speciesName)

        self.item = growth[2:4]
        self.itemName = GEN3_ITEMS[int.from_bytes(self.item, 'little')]

        self.eXP = int.from_bytes(growth[4:8], 'little')
        self.move1PPUp = growth[8] & 0b11
        self.move2PPUp = (growth[8] >> 2)& 0b11
        self.move3PPUp = (growth[8] >> 4) & 0b11
        self.move4PPUp = growth[8] >> 6
        self.friendship = growth[9]


GEN3_SUBSTRUCTURE_ORDER = {
    0:  "GAEM",
    1:  "GAME",
    2:  "GEAM",
    3:  "GEMA",
    4:  "GMAE",
    5:  "GMEA",

    6:  "AGEM",
    7:  "AGME",
    8:  "AEGM",
    9:  "AEMG",
    10: "AMGE",
    11: "AMEG",

    12: "EGAM",
    13: "EGMA",
    14: "EAGM",
    15: "EAMG",
    16: "EMGA",
    17: "EMAG",

    18: "MGAE",
    19: "MGEA",
    20: "MAGE",
    21: "MAEG",
    22: "MEGA",
    23: "MEAG",
}
GEN3_CHARMAP = {
    0x01: 'À',
    0x02: 'Á',
    0x03: 'Â',
    0x04: 'Ç',
    0x05: 'È',
    0x06: 'É',
    0x07: 'Ê',
    0x08: 'Ë',
    0x09: 'Ì',
    0x0B: 'Î',
    0x0C: 'Ï',
    0x0D: 'Ò',
    0x0E: 'Ó',
    0x0F: 'Ô',
    0x10: 'Œ',
    0x11: 'Ù',
    0x12: 'Ú',
    0x13: 'Û',
    0x14: 'Ñ',
    0x15: 'ß',
    0x16: 'à',
    0x17: 'á',
    0x19: 'ç',
    0x1A: 'è',
    0x1B: 'é',
    0x1C: 'ê',
    0x1D: 'ë',
    0x1E: 'ì',
    0x20: 'î',
    0x21: 'ï',
    0x22: 'ò',
    0x23: 'ó',
    0x24: 'ô',
    0x25: 'œ',
    0x26: 'ù',
    0x27: 'ú',
    0x28: 'û',
    0x29: 'ñ',
    0x2A: 'º',
    0x2B: 'ª',
    0x2C: 'ᵉʳ',
    0x2D: '&',
    0x2E: '+',
    0x34: 'Lv',
    0x35: '=',
    0x36: ';',
    0x50: '▯',
    0x51: '¿',
    0x52: '¡',
    0x53: 'PK',
    0x54: 'MN',
    0x5A: 'Í',
    0x5B: '%',
    0x5C: '(',
    0x5D: ')',
    0x68: 'â',
    0x6F: 'í',
    0x79: '↑',
    0x7A: '↓',
    0x7B: '←',
    0x7C: '→',
    0x7D: '*',
    0x7E: '*',
    0x7F: '*',
    0x80: '*',
    0x81: '*',
    0x82: '*',
    0x83: '*',
    0x84: 'ᵉ',
    0x85: '<',
    0x86: '>',
    0xA0: 'ʳᵉ',
    0xA1: '0',
    0xA2: '1',
    0xA3: '2',
    0xA4: '3',
    0xA5: '4',
    0xA6: '5',
    0xA7: '6',
    0xA8: '7',
    0xA9: '8',
    0xAA: '9',
    0xAB: '!',
    0xAC: '?',
    0xAD: '.',
    0xAE: '-',
    0xAF: '･',
    0xB0: '‥',
    0xB1: '“',
    0xB2: '”',
    0xB3: '‘',
    0xB4: '\'',
    0xB5: '♂',
    0xB6: '♀',
    0xB7: '$',
    0xB8: ',',
    0xB9: '×',
    0xBA: '/',
    0xBB: 'A',
    0xBC: 'B',
    0xBD: 'C',
    0xBE: 'D',
    0xBF: 'E',
    0xC0: 'F',
    0xC1: 'G',
    0xC2: 'H',
    0xC3: 'I',
    0xC4: 'J',
    0xC5: 'K',
    0xC6: 'L',
    0xC7: 'M',
    0xC8: 'N',
    0xC9: 'O',
    0xCA: 'P',
    0xCB: 'Q',
    0xCC: 'R',
    0xCD: 'S',
    0xCE: 'T',
    0xCF: 'U',
    0xD0: 'V',
    0xD1: 'W',
    0xD2: 'X',
    0xD3: 'Y',
    0xD4: 'Z',
    0xD5: 'a',
    0xD6: 'b',
    0xD7: 'c',
    0xD8: 'd',
    0xD9: 'e',
    0xDA: 'f',
    0xDB: 'g',
    0xDC: 'h',
    0xDD: 'i',
    0xDE: 'j',
    0xDF: 'k',
    0xE0: 'l',
    0xE1: 'm',
    0xE2: 'n',
    0xE3: 'o',
    0xE4: 'p',
    0xE5: 'q',
    0xE6: 'r',
    0xE7: 's',
    0xE8: 't',
    0xE9: 'u',
    0xEA: 'v',
    0xEB: 'w',
    0xEC: 'x',
    0xED: 'y',
    0xEE: 'z',
    0xEF: '►',
}
_HOENN_INTERNAL_TO_NATIONAL = [
    # 277-291: Treecko .. Wurmple-line start
    252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266,
    # 292-306: Beautifly .. Shroomish
    267, 268, 269, 270, 271, 272, 273, 274, 275, 290, 291, 292, 276, 277, 285,
    # 307-321: Breloom .. Torkoal
    286, 327, 278, 279, 283, 284, 320, 321, 300, 301, 352, 343, 344, 299, 324,
    # 322-336: Sableye .. Hariyama
    302, 339, 340, 370, 341, 342, 349, 350, 318, 319, 328, 329, 330, 296, 297,
    # 337-351: Electrike .. Spoink-1
    309, 310, 322, 323, 363, 364, 365, 331, 332, 361, 362, 337, 338, 298, 325,
    # 352-366: Grumpig .. Slaking
    326, 311, 312, 303, 307, 308, 333, 334, 360, 355, 356, 315, 287, 288, 289,
    # 367-381: Gulpin .. Relicanth
    316, 317, 357, 293, 294, 295, 366, 367, 368, 359, 353, 354, 336, 335, 369,
    # 382-396: Aron .. Shelgon
    304, 305, 306, 351, 313, 314, 345, 346, 347, 348, 280, 281, 282, 371, 372,
    # 397-411: Salamence .. Chimecho
    373, 374, 375, 376, 377, 378, 379, 382, 383, 384, 380, 381, 385, 386, 358,
]
assert len(_HOENN_INTERNAL_TO_NATIONAL) == 135

def internalToNational(idx: int) -> int:
    if 1 <= idx <= 251:
        return idx
    if 277 <= idx <= 411:
        return _HOENN_INTERNAL_TO_NATIONAL[idx - 277]
    return 0  # unused/old Unown slots, empty, invalid

with open("moves.json", "r") as f:
    MOVES : list[str] = json.load(f)
with open("items3.json", "r") as f:
        GEN3_ITEMS_STR : dict[str,str]= json.load(f)
        GEN3_ITEMS : dict[int,str] = {}
        for key, val in GEN3_ITEMS_STR.items():
            GEN3_ITEMS[int(key)] = val
with open("dexnational.json") as f:
    DEX : list[str] = json.load(f)

gameSave(r"Pokemon - Sapphire Version (USA, Europe).sav")