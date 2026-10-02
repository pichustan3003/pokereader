import json
import Gen1
from Gen1 import attributedDictionary
from typing import overload

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
            self.TMPocket = 0x23E6
            self.itemPocket = 0x241F
            self.keyPocket = 0x2449
            self.ballPocket = 0x2464
            self.pcPocket = 0x247E
            self.boxNames = 0x2727
            self.party = 0x288A
        else:
            self.gameCoins = 0x23E3
            self.money = 0x23DC
            self.johtoBadges = 0x23E5
            self.kantoBadges = 0x23E6
            self.TMPocket = 0x23E7
            self.itemPocket = 0x2420
            self.keyPocket = 0x244A
            self.ballPocket = 0x2465
            self.pcPocket = 0x247F
            self.boxNames = 0x2703
            self.party = 0x2865

class pocket:
    def __init__(self):
        self.store : list[item] = []
        self.descriptiveStore : dict[str, item] = {}

    @overload
    def __getitem__(self, key : int) -> item: # type: ignore
        return self.store[key]

    @overload
    def __getitem__(self, key : str) -> item:
        return self.descriptiveStore[key]

    def __setitem__(self, key : str, value : item):
        self.descriptiveStore[key] = value
        self.store.append(value)
    
    def __str__(self) -> str:
        return "\n".join([str(im) for im in self.store])

class bag:
    def __init__(self):
        self.TMHM = pocket()
        self.item = pocket()
        self.ball = pocket()
        self.key = pocket()
        self.pc = pocket()

class item:
    def __init__(self, index : int, count : int) -> None:
        self.index = index
        self.count = count
        self.name : str = GEN2_ITEMS[index]

    def __str__(self) -> str:
        return f"{self.name}({self.index}): {self.count}"

class pokemon:
    def __init__(self, raw : bytes):
        self.index = raw[0x0]
        self.speciesName = DEX[self.index - 1]
        self.heldIndex = raw[0x1]
        self.heldItem = GEN2_ITEMS[self.heldIndex]
        self.move1 = raw[0x02]
        self.move2 = raw[0x03]
        self.move3 = raw[0x04]
        self.move4 = raw[0x05]
        self.OTId = int.from_bytes(raw[0x06:0x08])
        self.eXP = int.from_bytes(raw[0x08:0x0B])
        self.HPEV = int.from_bytes(raw[0x0B:0x0D])
        self.atkEV = int.from_bytes(raw[0x0D:0x0F])
        self.defEV = int.from_bytes(raw[0x0F:0x11])
        self.spdEV = int.from_bytes(raw[0x11:0x13])
        self.spcEV = int.from_bytes(raw[0x13:0x15])
        print(self.HPEV, self.atkEV, self.defEV, self.spdEV, self.spcEV)
        IVdat = int.from_bytes(raw[0x15:0x17])
        self.atkIV = IVdat & 0x0f
        self.defIV = (IVdat & 0xF0 >> 4)
        self.spdIV = (IVdat & 0x0F00 >> 8)
        self.spcIV = IVdat >> 12
        self.hpIV = (
            ((self.atkIV & 1) << 3) |
            ((self.defIV & 1) << 2) |
            ((self.spdIV & 1) << 1) |
            (self.spcIV & 1)
        )

        self.move1pp = raw[0x17] & 0b111111
        self.move1ppups = raw[0x17] >> 6

        self.move2pp = raw[0x18] & 0b111111
        self.move2ppups = raw[0x18] >> 6

        self.move3pp = raw[0x19] & 0b111111
        self.move3ppups = raw[0x19] >> 6

        self.move4pp = raw[0x1A] & 0b111111
        self.move4ppups = raw[0x1A] >> 6

        self.friendship = raw[0x1B]

        self.pokerus = True if raw[0x1C] == 1 else False

        match raw[0x1D] >> 6:
            case 1:
                self.caughtTime = "morning"
            case 2:
                self.caughtTime = "afternoon"
            case 3:
                self.caughtTime = "night"
            case _:
                raise ValueError("Bad caught time")
        self.caughtLevel = raw[0x1D] & 0b111111
        self.otGender = "male" if raw[0x1E] >> 7 == 0 else "female"
        self.location = GEN2_LOCATIONS[raw[0x1E] & 0b1111111]

        self.level = raw[0x1F]
        assert 0 < self.level <= 100


class box:
    def __init__(self, holds : list[pokemon], boxNam : str):
        self.pokemon = holds
        self.boxName = boxNam
    def __getitem__(self, key : int):
        return self.pokemon[key]

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

            # read items (TM/HM Pocket)
            self.bag = bag()
            startIndex = 190
            sav.seek(locations.TMPocket)
            for tm in sav.read(57):
                assert 0 < tm < 100
                startIndex += 1
                if tm == 0:
                    continue
                self.bag.TMHM[GEN2_ITEMS[startIndex]] = item(startIndex, tm)

            # item pocket

            sav.seek(locations.itemPocket)
            count = sav.read(1)[0]
            assert 0 < count < 21
            for i in range(count):
                indx = sav.read(1)[0]
                itemcount = sav.read(1)[0]
                assert 0 < itemcount < 100
                self.bag.item[GEN2_ITEMS[indx]] = item(indx, itemcount)

            # key pocket

            sav.seek(locations.keyPocket)
            count = sav.read(1)[0]
            assert 0 < count < 26
            for i in range(count):
                indx = sav.read(1)[0]
                self.bag.key[GEN2_ITEMS[indx]] = item(indx, 1)


            # ball pocket

            sav.seek(locations.ballPocket)
            count = sav.read(1)[0]
            assert 0 < count < 13
            for i in range(count):
                indx = sav.read(1)[0]
                itemcount = sav.read(1)[0]
                assert 0 < itemcount < 100
                self.bag.ball[GEN2_ITEMS[indx]] = item(indx, itemcount)

            # pc pocket

            sav.seek(locations.pcPocket)
            count = sav.read(1)[0]
            assert 0 < count < 51
            for i in range(count):
                indx = sav.read(1)[0]
                itemcount = sav.read(1)[0]
                assert 0 < itemcount < 100
                self.bag.ball[GEN2_ITEMS[indx]] = item(indx, itemcount)

            # box names
            sav.seek(locations.boxNames)
            self.boxNames : list[str] = []
            for i in range(14):
                bits = sav.read(9)
                name = ""
                for bit in bits:
                    if bit == 0x50: break
                    name += GEN2_CHARMAP[bit]
                self.boxNames.append(name)

            # party

            sav.seek(locations.party)
            count = sav.read(1)[0]
            sav.read(7)
            parttemp : list[pokemon] = []
            for i in range(count):
                parttemp.append(pokemon(sav.read(48)))
            self.party = box(parttemp, "party")

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

BADGES = ["Zephyr", "Insect", "Plain", "Fog", "Storm", "Mineral", "Glacier", "Rising"]
with open("GEN2_CHARMAP.json", "r") as f:
    GEN2_CHARMAP_STR : dict[str,str]= json.load(f)
    GEN2_CHARMAP : dict[int,str] = {}
    for key, val in GEN2_CHARMAP_STR.items():
        GEN2_CHARMAP[int(key)] = val
with open("GEN2_ITEMS.json", "r") as f:
        GEN2_ITEMS_STR : dict[str,str]= json.load(f)
        GEN2_ITEMS : dict[int,str] = {}
        for key, val in GEN2_ITEMS_STR.items():
            GEN2_ITEMS[int(key)] = val
with open("moves.json", "r") as f:
    MOVES : list[str] = json.load(f)
with open("dexnational.json") as f:
    DEX : list[str] = json.load(f)
with open("Locations2.json", "r") as f:
    GEN2_LOCATIONS : list[str] = json.load(f)

game = gameSave(r"D:\Emulation\Games\Gameboy (all of them)\Pokémon - Crystal Version.sav")
for i in game.party:
    print(i.speciesName)