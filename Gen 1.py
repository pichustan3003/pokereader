import json

from math import isqrt

class location:
    def __init__(self):
        self.playerName = 0x2598
        self.mainData = 0x25A3
        self.bag = 0x25C9
        self.money = 0x25F3
        self.rivalName = 0x25F6
        self.badges = 0x2602
        self.id = 0x2605
        self.pikachuFriendship = 0x271C
        self.itemBox = 0x27E6
        self.selectedBox = 0x284C
        self.elite4Wins = 0x284E
        self.slotCoins = 0x2850
        self.rivalStarter = 0x29C1
        self.starter = 0x29C3
        self.clock = 0x2CED 
        self.party = 0x2F2C
        self.box1 = 0x4000
        self.box7 = 0x6000
        self.daycare = 0x2CF4


        self.tilesetType = 0x3522 # for checksum testing

class attributedDictionary:
    def __init__(self) -> None:
        pass

class pokemon:
    def __str__(self) -> str:
        moves = [
            MOVES.get(self.move1, f"Unknown ({self.move1:02X})"),
            MOVES.get(self.move2, f"Unknown ({self.move2:02X})"),
            MOVES.get(self.move3, f"Unknown ({self.move3:02X})"),
            MOVES.get(self.move4, f"Unknown ({self.move4:02X}")
        ]
        return (
            f"{self.index}\n"
            f"{self.nickname} ({self.speciesName})\n"
            f"Level: {self.lvl}\n"
            f"HP: {self.remainingHP}/{self.HP}\n"
            f"Attack: {self.attack}\n"
            f"Defense: {self.defense}\n"
            f"Speed: {self.speed}\n"
            f"Special: {self.special}\n"
            f"EXP: {self.eXP}\n"
            f"Moves: {', '.join(moves)}\n"
            f"OT: {self.OTName}\n"
            f"Trainer ID: {self.tID}"
        )
    def __init__(self, data: bytes, inbox : bool) -> None:

        self.OTName = ""
        self.index = data[0]
        self.speciesName = POKEMON[self.index]
        self.nickname = self.speciesName
        self.remainingHP = int.from_bytes(data[0x01:0x03], "big")
        self.status = data[4]
        self.type1 = data[5]
        self.type2 = data[6]
        self.catchRate = data[7]
        self.move1 = data[8]
        self.move2 = data[9]
        self.move3 = data[10]
        self.move4 = data[11]
        self.tID = int.from_bytes(data[0x0C:0x0E], "big")
        self.eXP = int.from_bytes(data[0x0E:0x11], "big")

        self.HPEV = int.from_bytes(data[0x11:0x13], "big")
        self.atkEV = int.from_bytes(data[0x13:0x15], "big")
        self.defEV = int.from_bytes(data[0x15:0x17], "big")
        self.spdEV = int.from_bytes(data[0x17:0x19], "big")
        self.spcEV = int.from_bytes(data[0x19:0x1B], "big")

        self.atkIV = data[0x1B] >> 4
        self.defIV = data[0x1B] & 0x0F
        self.spdIV = data[0x1C] >> 4
        self.spcIV = data[0x1C] & 0x0F

        self.hpIV = (
            ((self.atkIV & 1) << 3) |
            ((self.defIV & 1) << 2) |
            ((self.spdIV & 1) << 1) |
            (self.spcIV & 1)
        )

        self.lvl = data[0x21] if not inbox else data[3]

        dex_number = POKEDEX_NUMBER[self.index] # type: ignore
        base = BASE_STATS[self.index]

        # Party mons store the stats the game currently uses (not recalc'd on EV gain).
        if not inbox:
            self.HP = int.from_bytes(data[0x22:0x24], "big")
            self.attack = int.from_bytes(data[0x24:0x26], "big")
            self.defense = int.from_bytes(data[0x26:0x28], "big")
            self.speed = int.from_bytes(data[0x28:0x2A], "big")
            self.special = int.from_bytes(data[0x2A:0x2C], "big")
        else:
            self.HP = self.calculate_stat( # type: ignore
                base["HP"], self.hpIV, self.HPEV, hp=True
            )

            self.attack = self.calculate_stat(
                base["Attack"], self.atkIV, self.atkEV
            )

            self.defense = self.calculate_stat(
                base["Defense"], self.defIV, self.defEV
            )

            self.speed = self.calculate_stat(
                base["Speed"], self.spdIV, self.spdEV
            )

            self.special = self.calculate_stat(
                base["Special"], self.spcIV, self.spcEV
            )

    def setOTName(self, OTName:str):
        self.OTName = OTName
    
    def setNick(self, nickname : str):
        self.nickname = nickname

    def calculate_stat(
        self,
        base: int,
        iv: int,
        ev: int,
        hp: bool = False
    ) -> int:

        ev_bonus = isqrt(ev) // 4

        stat = (
            ((base + iv) * 2 + ev_bonus)
            * self.lvl
        ) // 100

        if hp:
            result = stat + self.lvl + 10
        else:
            result = stat + 5
        return result

    

class gameSave:
    def __init__(self, fileName : str):
        with open(fileName, "rb") as sav:
            self.dump = sav.read()
            # read player's name
            sav.seek(locations.playerName)
            bytes = sav.read(11)
            self.name = ""
            for i in bytes:
                if i  == 0x50: break
                self.name += POKERED_CHARMAP[i] 

            print(self.name)

            # read main data section

            sav.seek(locations.mainData)

            # read dex caught

            caught = sav.read(0x13)
            self.caught = attributedDictionary()
            for mon in range(151):
                if caught[mon // 8] & (1 << (mon % 8)):
                    self.caught.__setattr__(pokemonDexOrder[mon], True)
                else:
                    self.caught.__setattr__(pokemonDexOrder[mon], False)

            # read dex seen

            seen = sav.read(0x13)
            self.seen = attributedDictionary()
            for mon in range(151):
                if seen[mon // 8] & (1 << (mon % 8)):
                    self.seen.__setattr__(pokemonDexOrder[mon], True)
                else:
                    self.seen.__setattr__(pokemonDexOrder[mon], False)
            sav.seek(locations.bag)
            self.bag : dict[str, int] = {}
            # read bag
            self.itemcount = sav.read(1)[0]
            for i in range(self.itemcount):
                entry = sav.read(2)
                if entry[0] not in ITEMS: continue
                self.bag[ITEMS[entry[0]]] = entry[1]

            # read money

            sav.seek(locations.money)

            self.money = int(sav.read(3).hex())

            # read rivals's name
            sav.seek(locations.rivalName)
            bytes = sav.read(11)
            self.rivalName = ""
            for i in bytes:
                if i  == 0x50: break
                self.rivalName += POKERED_CHARMAP[i]

            # get obtained badges

            sav.seek(locations.badges)

            self.badges = attributedDictionary()

            binaryBadgeReg = bin(sav.read(1)[0])[2:]
            for i in range(len(binaryBadgeReg)):
                if binaryBadgeReg[i] == "1":
                    self.badges.__setattr__(BADGES[i], True)
                else:
                    self.badges.__setattr__(BADGES[i], False)

            # read player id
            sav.seek(locations.id)
            self.id = int.from_bytes(sav.read(2))

            # read pikachu friendship

            sav.seek(locations.pikachuFriendship)
            self.pikachuFriendship = sav.read(1)[0]

            # if this value is 0 and your game is pokemon yellow god help you

            # read items in your box (Old pokemon games are weird man)

            sav.seek(locations.itemBox)
            self.itemBoxCount = sav.read(1)[0]
            self.itemBox : dict[str, int]= {}
            for i in range(self.itemBoxCount):
                entry = sav.read(2)
                if entry[0] not in ITEMS: continue
                self.itemBox[ITEMS[entry[0]]] = entry[1]

            # get current box number

            sav.seek(locations.selectedBox)
            bx = sav.read(1)[0]
            self.selectedBox = int(bin(bx)[3:],2) if bx else 0

            # get elite 4 win count

            sav.seek(locations.elite4Wins)
            self.hallOfFameEntries = sav.read(1)

            # get gambling ammo

            sav.seek(locations.slotCoins)
            self.slotCoins = int(sav.read(1).hex())

            # get rival starter

            sav.seek(locations.rivalStarter)
            self.starter = sav.read(1)[0]

            # get starter
            sav.seek(locations.starter)
            self.starter = sav.read(1)[0]

            # determine game type RB/Y

            if self.starter:
                self.version = "Y" if self.starter == 0x54 else "RB"
            else:
                self.version = "Y" if self.pikachuFriendship != 0 else "RB"

            # get time in seconds

            sav.seek(locations.clock)
            self.time = sav.read(2)[0]*3600
            self.time += sav.read(1)[0]*60
            self.time += sav.read(1)[0]
            self.daycare = None
            sav.seek(locations.daycare)
            truthofcare = sav.read(1)[0]
            if truthofcare:
                bytes = sav.read(11)
                daycarename = ""
                for i in bytes:
                    if i  == 0x50: break
                    daycarename += POKERED_CHARMAP[i] 
                
                bytes = sav.read(11)
                daycareot = ""
                for i in bytes:
                    if i  == 0x50: break
                    daycareot += POKERED_CHARMAP[i]

                self.daycare = pokemon(sav.read(33), True)
                self.daycare.setNick(daycarename)
                self.daycare.setOTName(daycareot)


            # Party data (woo)

            sav.seek(locations.party)
            self.partyCount = sav.read(1)[0]
            self.party : list[pokemon] = []
            sav.seek(locations.party+0x8)
            for i in range(self.partyCount):
                self.party.append(pokemon(sav.read(44), False))
            sav.seek(locations.party+0x110)

            for i in range(self.partyCount):
                bytes = sav.read(11)
                name = ""
                for b in bytes:
                    if b  == 0x50: break
                    name += POKERED_CHARMAP[b] 
                self.party[i].setOTName(name)

            sav.seek(locations.party+0x152)
            
            for i in range(self.partyCount):
                bytes = sav.read(11)
                name = ""
                for b in bytes:
                    if b  == 0x50: break
                    name += POKERED_CHARMAP[b] 
                self.party[i].setNick(name)

            # read box data
            self.boxes: list[list[pokemon]] = [[] for _ in range(12)]
            for c in range(6):
                sav.seek(locations.box1 + 0x462 * c)
                boxCount = sav.read(1)[0]
                sav.seek(locations.box1+0x16 + 0x462 * c)
                print(boxCount)
                if boxCount > 20:
                    continue
                for i in range(boxCount):
                    self.boxes[c].append(pokemon(sav.read(33), True))
                sav.seek(locations.box1+0x2AA + 0x462 * c)

                for i in range(boxCount):
                    data = sav.read(11)

                    name = ""
                    for b in data:
                        if b == 0x50:
                            break

                        if b not in POKERED_CHARMAP:
                            print(
                                f"Bad character: {b:02X} "
                                f"at 0x{sav.tell() - len(data):04X}, "
                                f"slot {i}"
                            )
                            print("Raw:", data.hex(" "))
                            break

                        name += POKERED_CHARMAP[b]

                    self.boxes[c][i].setOTName(name)

                sav.seek(locations.box1+0x386 + 0x462 * c)
                
                for i in range(boxCount):
                    bytes = sav.read(11)
                    name = ""
                    for b in bytes:
                        if b  == 0x50: break
                        name += POKERED_CHARMAP[b] 
                    self.boxes[c][i].setNick(name)

            for c in range(6,12):
                sav.seek(locations.box7 + 0x462 * (c-6))
                boxCount = sav.read(1)[0]
                sav.seek(locations.box7+0x16 + 0x462 * (c-6))
                if boxCount > 20:
                    continue
                for i in range(boxCount):
                    self.boxes[c].append(pokemon(sav.read(33), True))
                sav.seek(locations.box7+0x2AA + 0x462 * (c-6))

                for i in range(boxCount):
                    data = sav.read(11)

                    name = ""
                    for b in data:
                        if b == 0x50:
                            break

                        if b not in POKERED_CHARMAP:
                            print(
                                f"Bad character: {b:02X} "
                                f"at 0x{sav.tell() - len(data):04X}, "
                                f"slot {i}"
                            )
                            print("Raw:", data.hex(" "))
                            break

                        name += POKERED_CHARMAP[b]

                    self.boxes[c][i].setOTName(name)

                sav.seek(locations.box7+0x386 + 0x462 * (c-6))
                
                for i in range(boxCount):
                    bytes = sav.read(11)
                    name = ""
                    for b in bytes:
                        if b  == 0x50: break
                        name += POKERED_CHARMAP[b] 
                    self.boxes[c][i].setNick(name)
            print(self.daycare)
    def generateChkSum(self, startingOffset : int, endingOffset : int):
        return (~sum(self.dump[startingOffset:endingOffset])) & 0xFF

with open("dex2.json", encoding="utf-8") as f: pokemonDexOrder = json.load(f)
POKEDEX_NUMBER = { # type: ignore
    0x01: 112,  # Rhydon
    0x02: 115,  # Kangaskhan
    0x03: 32,  # Nidoran♂
    0x04: 35,  # Clefairy
    0x05: 21,  # Spearow
    0x06: 100,  # Voltorb
    0x07: 34,  # Nidoking
    0x08: 80,  # Slowbro
    0x09: 2,  # Ivysaur
    0x0A: 103,  # Exeggutor
    0x0B: 108,  # Lickitung
    0x0C: 102,  # Exeggcute
    0x0D: 88,  # Grimer
    0x0E: 94,  # Gengar
    0x0F: 29,  # Nidoran♀
    0x10: 31,  # Nidoqueen
    0x11: 104,  # Cubone
    0x12: 111,  # Rhyhorn
    0x13: 131,  # Lapras
    0x14: 59,  # Arcanine
    0x15: 151,  # Mew
    0x16: 130,  # Gyarados
    0x17: 90,  # Shellder
    0x18: 72,  # Tentacool
    0x19: 92,  # Gastly
    0x1A: 123,  # Scyther
    0x1B: 120,  # Staryu
    0x1C: 9,  # Blastoise
    0x1D: 127,  # Pinsir
    0x1E: 114,  # Tangela

    0x21: 58,  # Growlithe
    0x22: 95,  # Onix
    0x23: 22,  # Fearow
    0x24: 16,  # Pidgey
    0x25: 79,  # Slowpoke
    0x26: 64,  # Kadabra
    0x27: 75,  # Graveler
    0x28: 113,  # Chansey
    0x29: 67,  # Machoke
    0x2A: 122,  # Mr. Mime
    0x2B: 106,  # Hitmonlee
    0x2C: 107,  # Hitmonchan
    0x2D: 24,  # Arbok
    0x2E: 47,  # Parasect
    0x2F: 54,  # Psyduck
    0x30: 96,  # Drowzee
    0x31: 76,  # Golem
    0x33: 126,  # Magmar
    0x35: 125,  # Electabuzz
    0x36: 82,  # Magneton
    0x37: 109,  # Koffing
    0x39: 56,  # Mankey
    0x3A: 86,  # Seel
    0x3B: 50,  # Diglett
    0x3C: 128,  # Tauros

    0x40: 83,  # Farfetch'd
    0x41: 48,  # Venonat
    0x42: 149,  # Dragonite
    0x46: 84,  # Doduo
    0x47: 60,  # Poliwag
    0x48: 124,  # Jynx
    0x49: 146,  # Moltres
    0x4A: 144,  # Articuno
    0x4B: 145,  # Zapdos
    0x4C: 132,  # Ditto
    0x4D: 52,  # Meowth
    0x4E: 98,  # Krabby

    0x52: 37,  # Vulpix
    0x53: 38,  # Ninetales
    0x54: 25,  # Pikachu
    0x55: 26,  # Raichu
    0x58: 147,  # Dratini
    0x59: 148,  # Dragonair
    0x5A: 140,  # Kabuto
    0x5B: 141,  # Kabutops
    0x5C: 116,  # Horsea
    0x5D: 117,  # Seadra

    0x60: 27,  # Sandshrew
    0x61: 28,  # Sandslash
    0x62: 138,  # Omanyte
    0x63: 139,  # Omastar
    0x64: 39,  # Jigglypuff
    0x65: 40,  # Wigglytuff
    0x66: 133,  # Eevee
    0x67: 136,  # Flareon
    0x68: 135,  # Jolteon
    0x69: 134,  # Vaporeon
    0x6A: 66,  # Machop
    0x6B: 41,  # Zubat
    0x6C: 23,  # Ekans
    0x6D: 46,  # Paras
    0x6E: 61,  # Poliwhirl
    0x6F: 62,  # Poliwrath
    0x70: 13,  # Weedle
    0x71: 14,  # Kakuna
    0x72: 15,  # Beedrill

    0x74: 85,  # Dodrio
    0x75: 57,  # Primeape
    0x76: 51,  # Dugtrio
    0x77: 49,  # Venomoth
    0x78: 87,  # Dewgong

    0x7B: 10,  # Caterpie
    0x7C: 11,  # Metapod
    0x7D: 12,  # Butterfree
    0x7E: 68,  # Machamp

    0x80: 55,  # Golduck
    0x81: 97,  # Hypno
    0x82: 42,  # Golbat
    0x83: 150,  # Mewtwo
    0x84: 143,  # Snorlax
    0x85: 129,  # Magikarp
    0x88: 89,  # Muk
    0x8A: 99,  # Kingler
    0x8B: 91,  # Cloyster
    0x8D: 101,  # Electrode
    0x8E: 36,  # Clefable
    0x8F: 110,  # Weezing
    0x90: 53,  # Persian
    0x91: 105,  # Marowak

    0x93: 93,  # Haunter
    0x94: 63,  # Abra
    0x95: 65,  # Alakazam
    0x96: 17,  # Pidgeotto
    0x97: 18,  # Pidgeot
    0x98: 121,  # Starmie
    0x99: 1,  # Bulbasaur
    0x9A: 3,  # Venusaur
    0x9B: 73,  # Tentacruel
    0x9D: 118,  # Goldeen
    0x9E: 119,  # Seaking

    0xA3: 77,  # Ponyta
    0xA4: 78,  # Rapidash
    0xA5: 19,  # Rattata
    0xA6: 20,  # Raticate
    0xA7: 33,  # Nidorino
    0xA8: 30,  # Nidorina
    0xA9: 74,  # Geodude
    0xAA: 137,  # Porygon
    0xAB: 142,  # Aerodactyl
    0xAD: 81,  # Magnemite

    0xB0: 4,  # Charmander
    0xB1: 7,  # Squirtle
    0xB2: 5,  # Charmeleon
    0xB3: 8,  # Wartortle
    0xB4: 6,  # Charizard

    0xB9: 43,  # Oddish
    0xBA: 44,  # Gloom
    0xBB: 45,  # Vileplume
    0xBC: 69,  # Bellsprout
    0xBD: 70,  # Weepinbell
    0xBE: 71,  # Victreebel
}
POKEMON = {
    0x00: "MissingNo.",
    0x01: "Rhydon",
    0x02: "Kangaskhan",
    0x03: "Nidoran♂",
    0x04: "Clefairy",
    0x05: "Spearow",
    0x06: "Voltorb",
    0x07: "Nidoking",
    0x08: "Slowbro",
    0x09: "Ivysaur",
    0x0A: "Exeggutor",
    0x0B: "Lickitung",
    0x0C: "Exeggcute",
    0x0D: "Grimer",
    0x0E: "Gengar",
    0x0F: "Nidoran♀",
    0x10: "Nidoqueen",
    0x11: "Cubone",
    0x12: "Rhyhorn",
    0x13: "Lapras",
    0x14: "Arcanine",
    0x15: "Mew",
    0x16: "Gyarados",
    0x17: "Shellder",
    0x18: "Tentacool",
    0x19: "Gastly",
    0x1A: "Scyther",
    0x1B: "Staryu",
    0x1C: "Blastoise",
    0x1D: "Pinsir",
    0x1E: "Tangela",
    0x1F: "MissingNo.",
    0x20: "MissingNo.",
    0x21: "Growlithe",
    0x22: "Onix",
    0x23: "Fearow",
    0x24: "Pidgey",
    0x25: "Slowpoke",
    0x26: "Kadabra",
    0x27: "Graveler",
    0x28: "Chansey",
    0x29: "Machoke",
    0x2A: "Mr. Mime",
    0x2B: "Hitmonlee",
    0x2C: "Hitmonchan",
    0x2D: "Arbok",
    0x2E: "Parasect",
    0x2F: "Psyduck",
    0x30: "Drowzee",
    0x31: "Golem",
    0x32: "MissingNo.",
    0x33: "Magmar",
    0x34: "MissingNo.",
    0x35: "Electabuzz",
    0x36: "Magneton",
    0x37: "Koffing",
    0x38: "MissingNo.",
    0x39: "Mankey",
    0x3A: "Seel",
    0x3B: "Diglett",
    0x3C: "Tauros",
    0x3D: "MissingNo.",
    0x3E: "MissingNo.",
    0x3F: "MissingNo.",
    0x40: "Farfetch'd",
    0x41: "Venonat",
    0x42: "Dragonite",
    0x43: "MissingNo.",
    0x44: "MissingNo.",
    0x45: "MissingNo.",
    0x46: "Doduo",
    0x47: "Poliwag",
    0x48: "Jynx",
    0x49: "Moltres",
    0x4A: "Articuno",
    0x4B: "Zapdos",
    0x4C: "Ditto",
    0x4D: "Meowth",
    0x4E: "Krabby",
    0x4F: "MissingNo.",
    0x50: "MissingNo.",
    0x51: "MissingNo.",
    0x52: "Vulpix",
    0x53: "Ninetales",
    0x54: "Pikachu",
    0x55: "Raichu",
    0x56: "MissingNo.",
    0x57: "MissingNo.",
    0x58: "Dratini",
    0x59: "Dragonair",
    0x5A: "Kabuto",
    0x5B: "Kabutops",
    0x5C: "Horsea",
    0x5D: "Seadra",
    0x5E: "MissingNo.",
    0x5F: "MissingNo.",
    0x60: "Sandshrew",
    0x61: "Sandslash",
    0x62: "Omanyte",
    0x63: "Omastar",
    0x64: "Jigglypuff",
    0x65: "Wigglytuff",
    0x66: "Eevee",
    0x67: "Flareon",
    0x68: "Jolteon",
    0x69: "Vaporeon",
    0x6A: "Machop",
    0x6B: "Zubat",
    0x6C: "Ekans",
    0x6D: "Paras",
    0x6E: "Poliwhirl",
    0x6F: "Poliwrath",
    0x70: "Weedle",
    0x71: "Kakuna",
    0x72: "Beedrill",
    0x73: "MissingNo.",
    0x74: "Dodrio",
    0x75: "Primeape",
    0x76: "Dugtrio",
    0x77: "Venomoth",
    0x78: "Dewgong",
    0x79: "MissingNo.",
    0x7A: "MissingNo.",
    0x7B: "Caterpie",
    0x7C: "Metapod",
    0x7D: "Butterfree",
    0x7E: "Machamp",
    0x7F: "MissingNo.",
    0x80: "Golduck",
    0x81: "Hypno",
    0x82: "Golbat",
    0x83: "Mewtwo",
    0x84: "Snorlax",
    0x85: "Magikarp",
    0x86: "MissingNo.",
    0x87: "MissingNo.",
    0x88: "Muk",
    0x89: "MissingNo.",
    0x8A: "Kingler",
    0x8B: "Cloyster",
    0x8C: "MissingNo.",
    0x8D: "Electrode",
    0x8E: "Clefable",
    0x8F: "Weezing",
    0x90: "Persian",
    0x91: "Marowak",
    0x92: "MissingNo.",
    0x93: "Haunter",
    0x94: "Abra",
    0x95: "Alakazam",
    0x96: "Pidgeotto",
    0x97: "Pidgeot",
    0x98: "Starmie",
    0x99: "Bulbasaur",
    0x9A: "Venusaur",
    0x9B: "Tentacruel",
    0x9C: "MissingNo.",
    0x9D: "Goldeen",
    0x9E: "Seaking",
    0x9F: "MissingNo.",
    0xA0: "MissingNo.",
    0xA1: "MissingNo.",
    0xA2: "MissingNo.",
    0xA3: "Ponyta",
    0xA4: "Rapidash",
    0xA5: "Rattata",
    0xA6: "Raticate",
    0xA7: "Nidorino",
    0xA8: "Nidorina",
    0xA9: "Geodude",
    0xAA: "Porygon",
    0xAB: "Aerodactyl",
    0xAC: "MissingNo.",
    0xAD: "Magnemite",
    0xAE: "MissingNo.",
    0xAF: "MissingNo.",
    0xB0: "Charmander",
    0xB1: "Squirtle",
    0xB2: "Charmeleon",
    0xB3: "Wartortle",
    0xB4: "Charizard",
    0xB5: "MissingNo.",
    0xB6: "Kabutops Fossil",
    0xB7: "Aerodactyl Fossil",
    0xB8: "Ghost",
    0xB9: "Oddish",
    0xBA: "Gloom",
    0xBB: "Vileplume",
    0xBC: "Bellsprout",
    0xBD: "Weepinbell",
    0xBE: "Victreebel",
}
BASE_STATS = {
    # index: {"HP": ..., "Attack": ..., "Defense": ..., "Speed": ..., "Special": ...}

    0x01: {"HP": 80,  "Attack": 85,  "Defense": 95,  "Speed": 25,  "Special": 30},   # Rhydon
    0x02: {"HP": 105, "Attack": 95,  "Defense": 80,  "Speed": 90,  "Special": 40},   # Kangaskhan
    0x03: {"HP": 46,  "Attack": 57,  "Defense": 40,  "Speed": 50,  "Special": 40},   # Nidoran♂
    0x04: {"HP": 70,  "Attack": 45,  "Defense": 48,  "Speed": 35,  "Special": 60},   # Clefairy
    0x05: {"HP": 40,  "Attack": 60,  "Defense": 30,  "Speed": 70,  "Special": 31},   # Spearow
    0x06: {"HP": 40,  "Attack": 30,  "Defense": 50,  "Speed": 100, "Special": 55},   # Voltorb
    0x07: {"HP": 81,  "Attack": 92,  "Defense": 77,  "Speed": 85,  "Special": 75},   # Nidoking
    0x08: {"HP": 95,  "Attack": 75,  "Defense": 110, "Speed": 30,  "Special": 80},   # Slowbro
    0x09: {"HP": 60,  "Attack": 62,  "Defense": 63,  "Speed": 60,  "Special": 80},   # Ivysaur
    0x0A: {"HP": 95,  "Attack": 95,  "Defense": 85,  "Speed": 55,  "Special": 125},  # Exeggutor
    0x0B: {"HP": 90,  "Attack": 55,  "Defense": 75,  "Speed": 30,  "Special": 60},   # Lickitung
    0x0C: {"HP": 60,  "Attack": 40,  "Defense": 80,  "Speed": 40,  "Special": 60},   # Exeggcute
    0x0D: {"HP": 80,  "Attack": 80,  "Defense": 50,  "Speed": 25,  "Special": 40},   # Grimer
    0x0E: {"HP": 60,  "Attack": 65,  "Defense": 60,  "Speed": 110, "Special": 130},  # Gengar
    0x0F: {"HP": 55,  "Attack": 47,  "Defense": 52,  "Speed": 41,  "Special": 40},   # Nidoran♀
    0x10: {"HP": 90,  "Attack": 82,  "Defense": 87,  "Speed": 76,  "Special": 75},   # Nidoqueen
    0x11: {"HP": 50,  "Attack": 50,  "Defense": 95,  "Speed": 35,  "Special": 40},   # Cubone
    0x12: {"HP": 80,  "Attack": 85,  "Defense": 95,  "Speed": 25,  "Special": 30},   # Rhyhorn
    0x13: {"HP": 130, "Attack": 85,  "Defense": 80,  "Speed": 60,  "Special": 95},   # Lapras
    0x14: {"HP": 90,  "Attack": 110, "Defense": 80, "Speed": 95, "Special": 80},      # Arcanine
    0x15: {"HP": 100, "Attack": 100, "Defense": 100, "Speed": 100, "Special": 100},   # Mew

    0x16: {"HP": 95,  "Attack": 125, "Defense": 79, "Speed": 81, "Special": 100},     # Gyarados
    0x17: {"HP": 30,  "Attack": 65, "Defense": 100, "Speed": 40, "Special": 45},      # Shellder
    0x18: {"HP": 40,  "Attack": 40, "Defense": 35, "Speed": 70, "Special": 100},      # Tentacool
    0x19: {"HP": 30,  "Attack": 35, "Defense": 30, "Speed": 80, "Special": 100},      # Gastly
    0x1A: {"HP": 70,  "Attack": 110, "Defense": 80, "Speed": 105, "Special": 55},     # Scyther
    0x1B: {"HP": 30,  "Attack": 45, "Defense": 55, "Speed": 85, "Special": 70},      # Staryu
    0x1C: {"HP": 79,  "Attack": 83, "Defense": 100, "Speed": 78, "Special": 85},      # Blastoise
    0x1D: {"HP": 65,  "Attack": 125, "Defense": 100, "Speed": 85, "Special": 55},     # Pinsir
    0x1E: {"HP": 65,  "Attack": 55, "Defense": 115, "Speed": 60, "Special": 100},     # Tangela

    0x21: {"HP": 55,  "Attack": 70, "Defense": 45, "Speed": 60, "Special": 50},       # Growlithe
    0x22: {"HP": 35,  "Attack": 45, "Defense": 160, "Speed": 70, "Special": 30},      # Onix
    0x23: {"HP": 65,  "Attack": 90, "Defense": 65, "Speed": 100, "Special": 61},      # Fearow
    0x24: {"HP": 40,  "Attack": 45, "Defense": 40, "Speed": 56, "Special": 35},       # Pidgey
    0x25: {"HP": 90,  "Attack": 65, "Defense": 65, "Speed": 15, "Special": 40},       # Slowpoke
    0x26: {"HP": 40,  "Attack": 35, "Defense": 30, "Speed": 105, "Special": 120},      # Kadabra
    0x27: {"HP": 55,  "Attack": 95, "Defense": 115, "Speed": 35, "Special": 45},      # Graveler
    0x28: {"HP": 250, "Attack": 5, "Defense": 5, "Speed": 50, "Special": 105},         # Chansey
    0x29: {"HP": 80,  "Attack": 100, "Defense": 70, "Speed": 45, "Special": 50},       # Machoke
    0x2A: {"HP": 40,  "Attack": 45, "Defense": 65, "Speed": 90, "Special": 100},       # Mr. Mime
    0x2B: {"HP": 50,  "Attack": 120, "Defense": 53, "Speed": 87, "Special": 35},       # Hitmonlee
    0x2C: {"HP": 50,  "Attack": 105, "Defense": 79, "Speed": 76, "Special": 35},       # Hitmonchan
    0x2D: {"HP": 60,  "Attack": 85, "Defense": 69, "Speed": 80, "Special": 65},       # Arbok
    0x2E: {"HP": 60,  "Attack": 95, "Defense": 80, "Speed": 30, "Special": 80},        # Parasect
    0x2F: {"HP": 50,  "Attack": 52, "Defense": 48, "Speed": 55, "Special": 50},       # Psyduck
    0x30: {"HP": 60,  "Attack": 48, "Defense": 45, "Speed": 42, "Special": 90},       # Drowzee
    0x31: {"HP": 80,  "Attack": 110, "Defense": 130, "Speed": 45, "Special": 55},     # Golem

    0x33: {"HP": 65,  "Attack": 95, "Defense": 57, "Speed": 93, "Special": 85},       # Magmar
    0x35: {"HP": 65,  "Attack": 83, "Defense": 57, "Speed": 105, "Special": 85},      # Electabuzz
    0x36: {"HP": 50,  "Attack": 60, "Defense": 95, "Speed": 70, "Special": 120},      # Magneton
    0x37: {"HP": 40,  "Attack": 65, "Defense": 95, "Speed": 35, "Special": 60},       # Koffing

    0x39: {"HP": 40,  "Attack": 80, "Defense": 35, "Speed": 70, "Special": 35},       # Mankey
    0x3A: {"HP": 65,  "Attack": 45, "Defense": 55, "Speed": 45, "Special": 70},       # Seel
    0x3B: {"HP": 10,  "Attack": 55, "Defense": 25, "Speed": 95, "Special": 45},        # Diglett
    0x3C: {"HP": 75,  "Attack": 100, "Defense": 95, "Speed": 110, "Special": 70},      # Tauros

    0x40: {"HP": 52,  "Attack": 65, "Defense": 55, "Speed": 60, "Special": 58},       # Farfetch'd
    0x41: {"HP": 60,  "Attack": 55, "Defense": 50, "Speed": 45, "Special": 40},       # Venonat
    0x42: {"HP": 91,  "Attack": 134, "Defense": 95, "Speed": 80, "Special": 100},      # Dragonite

    0x46: {"HP": 35,  "Attack": 85, "Defense": 45, "Speed": 75, "Special": 35},       # Doduo
    0x47: {"HP": 40,  "Attack": 50, "Defense": 40, "Speed": 90, "Special": 40},       # Poliwag
    0x48: {"HP": 65,  "Attack": 50, "Defense": 35, "Speed": 95, "Special": 95},       # Jynx
    0x49: {"HP": 90,  "Attack": 100, "Defense": 90, "Speed": 90, "Special": 125},      # Moltres
    0x4A: {"HP": 90,  "Attack": 85, "Defense": 100, "Speed": 85, "Special": 125},      # Articuno
    0x4B: {"HP": 90,  "Attack": 90, "Defense": 85, "Speed": 100, "Special": 125},      # Zapdos
    0x4C: {"HP": 48,  "Attack": 48, "Defense": 48, "Speed": 48, "Special": 48},         # Ditto
    0x4D: {"HP": 40,  "Attack": 45, "Defense": 35, "Speed": 90, "Special": 40},        # Meowth
    0x4E: {"HP": 30,  "Attack": 105, "Defense": 90, "Speed": 50, "Special": 25},       # Krabby

    0x52: {"HP": 38,  "Attack": 41, "Defense": 40, "Speed": 65, "Special": 65},        # Vulpix
    0x53: {"HP": 73,  "Attack": 76, "Defense": 75, "Speed": 100, "Special": 100},      # Ninetales
    0x54: {"HP": 35,  "Attack": 55, "Defense": 30, "Speed": 90, "Special": 50},        # Pikachu
    0x55: {"HP": 60,  "Attack": 90, "Defense": 55, "Speed": 100, "Special": 90},        # Raichu

    0x58: {"HP": 41, "Attack": 64, "Defense": 45, "Speed": 50, "Special": 50},          # Dratini
    0x59: {"HP": 61, "Attack": 84, "Defense": 65, "Speed": 70, "Special": 70},          # Dragonair
    0x5A: {"HP": 30, "Attack": 80, "Defense": 90, "Speed": 55, "Special": 45},          # Kabuto
    0x5B: {"HP": 60, "Attack": 115, "Defense": 105, "Speed": 80, "Special": 70},         # Kabutops
    0x5C: {"HP": 30, "Attack": 40, "Defense": 70, "Speed": 60, "Special": 70},           # Horsea
    0x5D: {"HP": 55, "Attack": 65, "Defense": 95, "Speed": 85, "Special": 95},           # Seadra

    0x60: {"HP": 50, "Attack": 75, "Defense": 85, "Speed": 40, "Special": 30},           # Sandshrew
    0x61: {"HP": 75, "Attack": 100, "Defense": 110, "Speed": 65, "Special": 55},         # Sandslash
    0x62: {"HP": 35, "Attack": 40, "Defense": 100, "Speed": 35, "Special": 90},          # Omanyte
    0x63: {"HP": 70, "Attack": 60, "Defense": 125, "Speed": 55, "Special": 115},         # Omastar
    0x64: {"HP": 115, "Attack": 45, "Defense": 20, "Speed": 20, "Special": 25},          # Jigglypuff
    0x65: {"HP": 140, "Attack": 70, "Defense": 45, "Speed": 45, "Special": 50},          # Wigglytuff
    0x66: {"HP": 55, "Attack": 55, "Defense": 50, "Speed": 55, "Special": 65},           # Eevee
    0x67: {"HP": 65, "Attack": 130, "Defense": 60, "Speed": 65, "Special": 110},         # Flareon
    0x68: {"HP": 65, "Attack": 65, "Defense": 60, "Speed": 130, "Special": 110},         # Jolteon
    0x69: {"HP": 130, "Attack": 65, "Defense": 60, "Speed": 65, "Special": 110},         # Vaporeon
    0x6A: {"HP": 70, "Attack": 80, "Defense": 50, "Speed": 35, "Special": 35},            # Machop
    0x6B: {"HP": 40, "Attack": 45, "Defense": 35, "Speed": 55, "Special": 40},            # Zubat
    0x6C: {"HP": 35, "Attack": 60, "Defense": 44, "Speed": 55, "Special": 40},            # Ekans
    0x6D: {"HP": 35, "Attack": 70, "Defense": 55, "Speed": 25, "Special": 55},            # Paras
    0x6E: {"HP": 65, "Attack": 65, "Defense": 65, "Speed": 90, "Special": 50},            # Poliwhirl
    0x6F: {"HP": 90, "Attack": 85, "Defense": 95, "Speed": 70, "Special": 70},            # Poliwrath
    0x70: {"HP": 40, "Attack": 35, "Defense": 30, "Speed": 50, "Special": 20},            # Weedle
    0x71: {"HP": 45, "Attack": 25, "Defense": 50, "Speed": 35, "Special": 25},            # Kakuna
    0x72: {"HP": 65, "Attack": 80, "Defense": 40, "Speed": 75, "Special": 45},            # Beedrill
    0x74: {"HP": 60, "Attack": 110, "Defense": 70, "Speed": 100, "Special": 60},           # Dodrio
    0x75: {"HP": 65, "Attack": 105, "Defense": 60, "Speed": 95, "Special": 60},            # Primeape
    0x76: {"HP": 35, "Attack": 80, "Defense": 50, "Speed": 120, "Special": 70},            # Dugtrio
    0x77: {"HP": 70, "Attack": 65, "Defense": 60, "Speed": 90, "Special": 90},             # Venomoth
    0x78: {"HP": 90, "Attack": 70, "Defense": 80, "Speed": 70, "Special": 95},             # Dewgong

    0x7B: {"HP": 45, "Attack": 30, "Defense": 35, "Speed": 45, "Special": 20},             # Caterpie
    0x7C: {"HP": 50, "Attack": 20, "Defense": 55, "Speed": 30, "Special": 25},             # Metapod
    0x7D: {"HP": 60, "Attack": 45, "Defense": 50, "Speed": 70, "Special": 80},             # Butterfree
    0x7E: {"HP": 90, "Attack": 130, "Defense": 80, "Speed": 55, "Special": 65},            # Machamp

    0x80: {"HP": 80, "Attack": 82, "Defense": 78, "Speed": 85, "Special": 80},             # Golduck
    0x81: {"HP": 85, "Attack": 73, "Defense": 70, "Speed": 67, "Special": 115},             # Hypno
    0x82: {"HP": 75, "Attack": 80, "Defense": 70, "Speed": 90, "Special": 75},               # Golbat
    0x83: {"HP": 106, "Attack": 110, "Defense": 90, "Speed": 130, "Special": 154},           # Mewtwo
    0x84: {"HP": 160, "Attack": 110, "Defense": 65, "Speed": 30, "Special": 65},             # Snorlax
    0x85: {"HP": 20, "Attack": 10, "Defense": 55, "Speed": 80, "Special": 20},               # Magikarp
    0x88: {"HP": 105, "Attack": 105, "Defense": 75, "Speed": 50, "Special": 65},             # Muk
    0x8A: {"HP": 55, "Attack": 130, "Defense": 115, "Speed": 75, "Special": 50},             # Kingler
    0x8B: {"HP": 50, "Attack": 95, "Defense": 180, "Speed": 70, "Special": 85},              # Cloyster
    0x8D: {"HP": 60, "Attack": 50, "Defense": 70, "Speed": 140, "Special": 80},              # Electrode
    0x8E: {"HP": 95, "Attack": 70, "Defense": 73, "Speed": 60, "Special": 85},               # Clefable
    0x8F: {"HP": 65, "Attack": 90, "Defense": 120, "Speed": 60, "Special": 85},              # Weezing
    0x90: {"HP": 65, "Attack": 70, "Defense": 60, "Speed": 115, "Special": 65},              # Persian
    0x91: {"HP": 60, "Attack": 80, "Defense": 110, "Speed": 45, "Special": 50},              # Marowak
    0x93: {"HP": 45, "Attack": 50, "Defense": 45, "Speed": 95, "Special": 115},              # Haunter
    0x94: {"HP": 25, "Attack": 20, "Defense": 15, "Speed": 90, "Special": 105},              # Abra
    0x95: {"HP": 55, "Attack": 50, "Defense": 45, "Speed": 120, "Special": 135},              # Alakazam
    0x96: {"HP": 63, "Attack": 60, "Defense": 55, "Speed": 71, "Special": 50},               # Pidgeotto
    0x97: {"HP": 83, "Attack": 80, "Defense": 75, "Speed": 91, "Special": 70},                # Pidgeot
    0x98: {"HP": 60, "Attack": 75, "Defense": 85, "Speed": 115, "Special": 100},              # Starmie
    0x99: {"HP": 45, "Attack": 49, "Defense": 49, "Speed": 45, "Special": 65},                # Bulbasaur
    0x9A: {"HP": 80, "Attack": 82, "Defense": 83, "Speed": 80, "Special": 100},               # Venusaur
    0x9B: {"HP": 80, "Attack": 70, "Defense": 65, "Speed": 100, "Special": 120},              # Tentacruel
    0x9D: {"HP": 45, "Attack": 67, "Defense": 60, "Speed": 63, "Special": 50},                # Goldeen
    0x9E: {"HP": 80, "Attack": 92, "Defense": 65, "Speed": 68, "Special": 80},                # Seaking

    0xA3: {"HP": 50, "Attack": 85, "Defense": 55, "Speed": 90, "Special": 65},                # Ponyta
    0xA4: {"HP": 65, "Attack": 100, "Defense": 70, "Speed": 105, "Special": 80},              # Rapidash
    0xA5: {"HP": 30, "Attack": 56, "Defense": 35, "Speed": 72, "Special": 25},                # Rattata
    0xA6: {"HP": 55, "Attack": 81, "Defense": 60, "Speed": 97, "Special": 50},                # Raticate
    0xA7: {"HP": 61, "Attack": 72, "Defense": 57, "Speed": 65, "Special": 55},                # Nidorino
    0xA8: {"HP": 70, "Attack": 62, "Defense": 67, "Speed": 56, "Special": 55},                # Nidorina
    0xA9: {"HP": 40, "Attack": 80, "Defense": 100, "Speed": 20, "Special": 30},               # Geodude
    0xAA: {"HP": 65, "Attack": 60, "Defense": 70, "Speed": 40, "Special": 75},                # Porygon
    0xAB: {"HP": 80, "Attack": 105, "Defense": 65, "Speed": 130, "Special": 60},              # Aerodactyl
    0xAD: {"HP": 25, "Attack": 35, "Defense": 70, "Speed": 45, "Special": 95},                # Magnemite

    0xB0: {"HP": 39, "Attack": 52, "Defense": 43, "Speed": 65, "Special": 50},                # Charmander
    0xB1: {"HP": 44, "Attack": 48, "Defense": 65, "Speed": 43, "Special": 50},                # Squirtle
    0xB2: {"HP": 58, "Attack": 64, "Defense": 58, "Speed": 80, "Special": 65},                # Charmeleon
    0xB3: {"HP": 59, "Attack": 63, "Defense": 80, "Speed": 58, "Special": 65},                # Wartortle
    0xB4: {"HP": 78, "Attack": 84, "Defense": 78, "Speed": 100, "Special": 85},               # Charizard
    0xB9: {"HP": 45, "Attack": 50, "Defense": 55, "Speed": 30, "Special": 75},                # Oddish
    0xBA: {"HP": 60, "Attack": 65, "Defense": 70, "Speed": 40, "Special": 85},                # Gloom
    0xBB: {"HP": 75, "Attack": 80, "Defense": 85, "Speed": 50, "Special": 100},               # Vileplume
    0xBC: {"HP": 50, "Attack": 75, "Defense": 35, "Speed": 40, "Special": 70},                # Bellsprout
    0xBD: {"HP": 65, "Attack": 90, "Defense": 50, "Speed": 55, "Special": 85},                # Weepinbell
    0xBE: {"HP": 80, "Attack": 105, "Defense": 65, "Speed": 70, "Special": 100},              # Victreebel
}
TYPES = {
    0x00: "Normal",
    0x01: "Fighting",
    0x02: "Flying",
    0x03: "Poison",
    0x04: "Ground",
    0x05: "Rock",
    0x06: "Bird",       # Unused
    0x07: "Bug",
    0x08: "Ghost",

    # Dummy types; internally named "Normal"
    0x09: "Normal",
    0x0A: "Normal",
    0x0B: "Normal",
    0x0C: "Normal",
    0x0D: "Normal",
    0x0E: "Normal",
    0x0F: "Normal",
    0x10: "Normal",
    0x11: "Normal",
    0x12: "Normal",
    0x13: "Normal",

    0x14: "Fire",
    0x15: "Water",
    0x16: "Grass",
    0x17: "Electric",
    0x18: "Psychic",
    0x19: "Ice",
    0x1A: "Dragon",

    # Values >= 0x1B don't have fixed type names.
    # Their displayed names are read from other data and therefore
    # vary depending on context.
}
BADGES = ["Boulder", "Cascade", "Thunder", "Rainbow", "Soul", "Marsh", "Volcano", "Earth"]
STATUS = {
    0x4: "Asleep",
    0x8: "Poisoned",
    0x10: "Burned",
    0x20: "Frozen",
    0x40: "Paralysed"
}
POKERED_CHARMAP = {
    # Control / special characters
    0x00: "<NULL>",
    0x49: "<PAGE>",
    0x4A: "<PKMN>",
    0x4B: "<_CONT>",
    0x4C: "<SCROLL>",
    0x4E: "<NEXT>",
    0x4F: "<LINE>",
    0x50: "@",          # String terminator
    0x51: "<PARA>",
    0x52: "<PLAYER>",
    0x53: "<RIVAL>",
    0x54: "#",          # POKé
    0x55: "<CONT>",
    0x56: "<……>",
    0x57: "<DONE>",
    0x58: "<PROMPT>",
    0x59: "<TARGET>",
    0x5A: "<USER>",
    0x5B: "<PC>",
    0x5C: "<TM>",
    0x5D: "<TRAINER>",
    0x5E: "<ROCKET>",
    0x5F: "<DEXEND>",

    # Extra font characters
    0x60: "<BOLD_A>",
    0x61: "<BOLD_B>",
    0x62: "<BOLD_C>",
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
    0x6D: "<COLON>",

    0x6E: "<LV>",
    0x6F: "ぅ",
    0x70: "‘",
    0x71: "’",
    0x72: "“",
    0x73: "”",
    0x74: "·",
    0x75: "…",
    0x76: "ぁ",
    0x77: "ぇ",
    0x78: "ぉ",

    # Box drawing / space
    0x79: "┌",
    0x7A: "─",
    0x7B: "┐",
    0x7C: "│",
    0x7D: "└",
    0x7E: "┘",
    0x7F: " ",

    # Uppercase letters
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

    # Lowercase letters
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

    # Contractions
    0xBA: "é",
    0xBB: "'d",
    0xBC: "'l",
    0xBD: "'s",
    0xBE: "'t",
    0xBF: "'v",

    # More punctuation / special characters
    0xE0: "'",
    0xE1: "<PK>",
    0xE2: "<MN>",
    0xE3: "-",
    0xE4: "'r",
    0xE5: "'m",
    0xE6: "?",
    0xE7: "!",
    0xE8: ".",
    0xE9: "ァ",
    0xEA: "ゥ",
    0xEB: "ェ",
    0xEC: "▷",
    0xED: "▶",
    0xEE: "▼",
    0xEF: "♂",
    0xF0: "¥",
    0xF1: "×",
    0xF2: "<DOT>",
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
ITEMS = {
    0x01: "Master Ball",
    0x02: "Ultra Ball",
    0x03: "Great Ball",
    0x04: "Poké Ball",
    0x05: "Town Map",
    0x06: "Bicycle",
    0x07: "?????",
    0x08: "Safari Ball",
    0x09: "PokéattributedDictionary",
    0x0A: "Moon Stone",
    0x0B: "Antidote",
    0x0C: "Burn Heal",
    0x0D: "Ice Heal",
    0x0E: "Awakening",
    0x0F: "Parlyz Heal",
    0x10: "Full Restore",
    0x11: "Max Potion",
    0x12: "Hyper Potion",
    0x13: "Super Potion",
    0x14: "Potion",
    0x15: "BoulderBadge",
    0x16: "CascadeBadge",
    0x17: "ThunderBadge",
    0x18: "RainbowBadge",
    0x19: "SoulBadge",
    0x1A: "MarshBadge",
    0x1B: "VolcanoBadge",
    0x1C: "EarthBadge",
    0x1D: "Escape Rope",
    0x1E: "Repel",
    0x1F: "Old Amber",
    0x20: "Fire Stone",
    0x21: "Thunderstone",
    0x22: "Water Stone",
    0x23: "HP Up",
    0x24: "Protein",
    0x25: "Iron",
    0x26: "Carbos",
    0x27: "Calcium",
    0x28: "Rare Candy",
    0x29: "Dome Fossil",
    0x2A: "Helix Fossil",
    0x2B: "Secret Key",
    0x2C: "?????",
    0x2D: "Bike Voucher",
    0x2E: "X Accuracy",
    0x2F: "Leaf Stone",
    0x30: "Card Key",
    0x31: "Nugget",
    0x32: "PP Up",
    0x33: "Poké Doll",
    0x34: "Full Heal",
    0x35: "Revive",
    0x36: "Max Revive",
    0x37: "Guard Spec.",
    0x38: "Super Repel",
    0x39: "Max Repel",
    0x3A: "Dire Hit",
    0x3B: "Coin",
    0x3C: "Fresh Water",
    0x3D: "Soda Pop",
    0x3E: "Lemonade",
    0x3F: "S.S. Ticket",
    0x40: "Gold Teeth",
    0x41: "X Attack",
    0x42: "X Defend",
    0x43: "X Speed",
    0x44: "X Special",
    0x45: "Coin Case",
    0x46: "Oak's Parcel",
    0x47: "Itemfinder",
    0x48: "Silph Scope",
    0x49: "Poké Flute",
    0x4A: "Lift Key",
    0x4B: "Exp.All",
    0x4C: "Old Rod",
    0x4D: "Good Rod",
    0x4E: "Super Rod",
    0x4F: "PP Up",
    0x50: "Ether",
    0x51: "Max Ether",
    0x52: "Elixer",
    0x53: "Max Elixer",

    0xC4: "HM01",
    0xC5: "HM02",
    0xC6: "HM03",
    0xC7: "HM04",
    0xC8: "HM05",

    0xC9: "TM01",
    0xCA: "TM02",
    0xCB: "TM03",
    0xCC: "TM04",
    0xCD: "TM05",
    0xCE: "TM06",
    0xCF: "TM07",
    0xD0: "TM08",
    0xD1: "TM09",
    0xD2: "TM10",
    0xD3: "TM11",
    0xD4: "TM12",
    0xD5: "TM13",
    0xD6: "TM14",
    0xD7: "TM15",
    0xD8: "TM16",
    0xD9: "TM17",
    0xDA: "TM18",
    0xDB: "TM19",
    0xDC: "TM20",
    0xDD: "TM21",
    0xDE: "TM22",
    0xDF: "TM23",
    0xE0: "TM24",
    0xE1: "TM25",
    0xE2: "TM26",
    0xE3: "TM27",
    0xE4: "TM28",
    0xE5: "TM29",
    0xE6: "TM30",
    0xE7: "TM31",
    0xE8: "TM32",
    0xE9: "TM33",
    0xEA: "TM34",
    0xEB: "TM35",
    0xEC: "TM36",
    0xED: "TM37",
    0xEE: "TM38",
    0xEF: "TM39",
    0xF0: "TM40",
    0xF1: "TM41",
    0xF2: "TM42",
    0xF3: "TM43",
    0xF4: "TM44",
    0xF5: "TM45",
    0xF6: "TM46",
    0xF7: "TM47",
    0xF8: "TM48",
    0xF9: "TM49",
    0xFA: "TM50",
    0xFB: "TM51",
    0xFC: "TM52",
    0xFD: "TM53",
    0xFE: "TM54",
    0xFF: "TM55",
}
MOVES = {
    0x00: "No Move",
    0x01: "Pound",
    0x02: "Karate Chop",
    0x03: "DoubleSlap",
    0x04: "Comet Punch",
    0x05: "Mega Punch",
    0x06: "Pay Day",
    0x07: "Fire Punch",
    0x08: "Ice Punch",
    0x09: "ThunderPunch",
    0x0A: "Scratch",
    0x0B: "ViceGrip",
    0x0C: "Guillotine",
    0x0D: "Razor Wind",
    0x0E: "Swords Dance",
    0x0F: "Cut",
    0x10: "Gust",
    0x11: "Wing Attack",
    0x12: "Whirlwind",
    0x13: "Fly",
    0x14: "Bind",
    0x15: "Slam",
    0x16: "Vine Whip",
    0x17: "Stomp",
    0x18: "Double Kick",
    0x19: "Mega Kick",
    0x1A: "Jump Kick",
    0x1B: "Rolling Kick",
    0x1C: "Sand-Attack",
    0x1D: "Headbutt",
    0x1E: "Horn Attack",
    0x1F: "Fury Attack",
    0x20: "Horn Drill",
    0x21: "Tackle",
    0x22: "Body Slam",
    0x23: "Wrap",
    0x24: "Take Down",
    0x25: "Thrash",
    0x26: "Double-Edge",
    0x27: "Tail Whip",
    0x28: "Poison Sting",
    0x29: "Twineedle",
    0x2A: "Pin Missile",
    0x2B: "Leer",
    0x2C: "Bite",
    0x2D: "Growl",
    0x2E: "Roar",
    0x2F: "Sing",
    0x30: "Supersonic",
    0x31: "SonicBoom",
    0x32: "Disable",
    0x33: "Acid",
    0x34: "Ember",
    0x35: "Flamethrower",
    0x36: "Mist",
    0x37: "Water Gun",
    0x38: "Hydro Pump",
    0x39: "Surf",
    0x3A: "Ice Beam",
    0x3B: "Blizzard",
    0x3C: "Psybeam",
    0x3D: "BubbleBeam",
    0x3E: "Aurora Beam",
    0x3F: "Hyper Beam",
    0x40: "Peck",
    0x41: "Drill Peck",
    0x42: "Submission",
    0x43: "Low Kick",
    0x44: "Counter",
    0x45: "Seismic Toss",
    0x46: "Strength",
    0x47: "Absorb",
    0x48: "Mega Drain",
    0x49: "Leech Seed",
    0x4A: "Growth",
    0x4B: "Razor Leaf",
    0x4C: "SolarBeam",
    0x4D: "PoisonPowder",
    0x4E: "Stun Spore",
    0x4F: "Sleep Powder",
    0x50: "Petal Dance",
    0x51: "String Shot",
    0x52: "Dragon Rage",
    0x53: "Fire Spin",
    0x54: "ThunderShock",
    0x55: "Thunderbolt",
    0x56: "Thunder Wave",
    0x57: "Thunder",
    0x58: "Rock Throw",
    0x59: "Earthquake",
    0x5A: "Fissure",
    0x5B: "Dig",
    0x5C: "Toxic",
    0x5D: "Confusion",
    0x5E: "Psychic",
    0x5F: "Hypnosis",
    0x60: "Meditate",
    0x61: "Agility",
    0x62: "Quick Attack",
    0x63: "Rage",
    0x64: "Teleport",
    0x65: "Night Shade",
    0x66: "Mimic",
    0x67: "Screech",
    0x68: "Double Team",
    0x69: "Recover",
    0x6A: "Harden",
    0x6B: "Minimize",
    0x6C: "Smokescreen",
    0x6D: "Confuse Ray",
    0x6E: "Withdraw",
    0x6F: "Defense Curl",
    0x70: "Barrier",
    0x71: "Light Screen",
    0x72: "Haze",
    0x73: "Reflect",
    0x74: "Focus Energy",
    0x75: "Bide",
    0x76: "Metronome",
    0x77: "Mirror Move",
    0x78: "Selfdestruct",
    0x79: "Egg Bomb",
    0x7A: "Lick",
    0x7B: "Smog",
    0x7C: "Sludge",
    0x7D: "Bone Club",
    0x7E: "Fire Blast",
    0x7F: "Waterfall",
    0x80: "Clamp",
    0x81: "Swift",
    0x82: "Skull Bash",
    0x83: "Spike Cannon",
    0x84: "Constrict",
    0x85: "Amnesia",
    0x86: "Kinesis",
    0x87: "Soft-Boiled",
    0x88: "High Jump Kick",
    0x89: "Glare",
    0x8A: "Dream Eater",
    0x8B: "Poison Gas",
    0x8C: "Barrage",
    0x8D: "Leech Life",
    0x8E: "Lovely Kiss",
    0x8F: "Sky Attack",
    0x90: "Transform",
    0x91: "Bubble",
    0x92: "Dizzy Punch",
    0x93: "Spore",
    0x94: "Flash",
    0x95: "Psywave",
    0x96: "Splash",
    0x97: "Acid Armor",
    0x98: "Crabhammer",
    0x99: "Explosion",
    0x9A: "Fury Swipes",
    0x9B: "Bonemerang",
    0x9C: "Rest",
    0x9D: "Rock Slide",
    0x9E: "Hyper Fang",
    0x9F: "Sharpen",
    0xA0: "Conversion",
    0xA1: "Tri Attack",
    0xA2: "Super Fang",
    0xA3: "Slash",
    0xA4: "Substitute",
    0xA5: "Struggle",
}

locations = location()
game = gameSave(r"D:\Emulation\Games\Gameboy (all of them)\Pokemon Yellow Version.sav")
print(game.version)