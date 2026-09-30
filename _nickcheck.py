from pathlib import Path

text = Path(r"D:\Programming\python\PokeRead\Gen 1.py").read_text(encoding="utf-8")
text = text.replace(
    'gameSave(r"D:\\Emulation\\Games\\Gameboy (all of them)\\Pokemon - Red Version (USA, Europe).sav")',
    "pass",
)
ns = {}
exec(compile(text, "Gen1", "exec"), ns)
CHAR = ns["POKERED_CHARMAP"]
POKEMON = ns["POKEMON"]

data = Path(
    r"D:\Emulation\Games\Gameboy (all of them)\Pokemon - Red Version (USA, Europe).sav"
).read_bytes()


def decode(raw):
    name = ""
    for b in raw:
        if b == 0x50:
            break
        name += CHAR[b]
    return name


party = 0x2F2C
count = data[party]
print("=== PARTY ===")
for i in range(count):
    mon = data[party + 8 + i * 44]
    nick = decode(data[party + 0x152 + i * 11 : party + 0x152 + (i + 1) * 11])
    print(f"{i+1}: nick={nick!r} speciesName={POKEMON.get(mon)!r} index={mon:02X}")

print("\n=== BOX 1 ===")
bc = data[0x4000]
for i in range(bc):
    sp = data[0x4016 + i * 33]
    nick = decode(data[0x4000 + 0x386 + i * 11 : 0x4000 + 0x386 + (i + 1) * 11])
    species = POKEMON.get(sp, f"?{sp:02X}")
    print(f"{i:02d} idx={sp:02X} species={species!r:16} nick={nick!r}")
