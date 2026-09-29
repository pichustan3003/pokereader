import requests
import json

def readPokedex(idNumber : int | str):

    data = requests.get(f"https://pokeapi.co/api/v2/pokedex/{idNumber}").json()
    dex : list[str] = []
    for i in range(len(data["pokemon_entries"])): # type: ignore
        dex.append( data["pokemon_entries"][i]["pokemon_species"]["name"])
    with open(f"dex{idNumber}.json", "w") as out:
        json.dump(dex, out)

readPokedex(2)