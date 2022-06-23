import json
import random
import math
from PokemonClass import Pokemon
from DamageCalculation import DamageCalc
from TrainerClass import Trainer
from BattleClass import Battle

with open("gen1data/moveInfo_gen1.json") as jsonFile:
    moveList = json.load(jsonFile)
    jsonFile.close()
with open("gen1data/pkmnInfo_gen1.json") as jsonFile:
    pokemonList = json.load(jsonFile)
    jsonFile.close()
with open("gen1data/typeInfo_gen1.json") as jsonFile:
    typeList = json.load(jsonFile)
    jsonFile.close()

name = "Alakazam"
stats = [313,198,188,368,338]
level = 100
moves = ["psychic","wrap","earthquake","hydro pump"]
pk1 = Pokemon(name,level,stats,moves,pokemonList,moveList)
pk1.status="burn"

name = "Abra"
stats = [253,138,128,308,278]
level = 100
moves = ["thunder wave","psychic","seismic toss","counter"]
pk2 = Pokemon(name,level,stats,moves,pokemonList,moveList)
pk2.wall = ["reflect"]

#damage = []
#for i in range(1000):
#    damage.append(DamageCalc(pk1,pk2,0,typeList,[1,1,1,1,0]))

#print(max(damage))
#print(min(damage))

player = Trainer("brian",[pk1,pk2],["another","more","some others"])
enemy = Trainer("kevin",[pk2,pk2,pk1],["briantime XP"])
battle = Battle(player,enemy)
playerOptions = battle.options(player)
enemyOptions = battle.options(enemy)
battle.turn(["attack",1],["attack",2])
print(battle.player.team[1].poke["name"])