import json
import random
import math
from PokemonClass import Pokemon
from DamageCalculation import damageCalc
from TrainerClass import Trainer
from BattleClass import Battle

import tkinter
from tkinter import *
from tkinter.messagebox import showerror
from PIL import Image

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
stats = [10000,198,188,368,1]
level = 100
moves = ["bind","body slam","counter","rage"]
pk1 = Pokemon(name,level,stats,10000,moves,[15,15,15,15],[5,5,5,5],pokemonList,moveList)
#pk1.confused = True
#pk1.turncount["confused"] = 2


name = "Pidgey"
stats = [10000,138,128,308,278]
level = 100
moves = ["hyper beam","substitute","transform" ,"bide"]
pk2 = Pokemon(name,level,stats,10000,moves,[5,5,5,5],[5,5,5,5],pokemonList,moveList)
pk2.wall = ["reflect"]

name = "Porygon"
stats = [1000,138,128,308,278]
level = 100
moves = ["psywave","rage","seismic toss","counter"]
pk3 = Pokemon(name,level,stats,stats[0],moves,[5,5,5,5],[5,5,5,5],pokemonList,moveList)

#damage = []
#for i in range(1000):
#    damage.append(damageCalc(pk1,pk2,0,typeList))

#print(max(damage))
#print(min(damage))

player = Trainer("brian",[pk1],["paralyz heal","potion","full heal"],[1,1,1,1])
enemy = Trainer("kevin",[pk2,pk3],["full restore"],[1,1,1,0])
battle = Battle(player,enemy,typeList,moveList)
#playerOptions = battle.options(player)
#enemyOptions = battle.options(enemy)
#print(battle.enemy.team[0].HP)
#battle.turn(["attack",0],["attack",2])

#print(battle.enemy.team[0].HP)
