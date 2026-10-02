import requests
import json

def readPokedex(idNumber : int | str, fname : str):

    data = requests.get(f"https://pokeapi.co/api/v2/pokedex/{idNumber}").json()
    dex : list[str] = []
    for i in range(len(data["pokemon_entries"])): # type: ignore
        dex.append( data["pokemon_entries"][i]["pokemon_species"]["name"])
    with open(f"dex{fname}.json", "w") as out:
        json.dump(dex, out)

def getMoves():

    data : list[dict[str,str]] = requests.get(f"https://pokeapi.co/api/v2/move?limit=2000").json()["results"]
    moves = {}
    for key in range(len(data)):
        moves[key + 1] = data[key]["name"]
    with open("moves.json", "w") as f:
        json.dump(moves,f, indent=4)

def flatten(fpath : str):
    with open(fpath, "r") as f:
        out = list(json.load(f).values())
    with open(fpath, "w") as f:
        json.dump(out,f)
flatten("moves.json")