import random
import math
from Stage2Mult import stage2Mult
def accuracyCheck(pokeAttacker,pokeDefender,moveAddress):
    moveResult = "success"
    if pokeAttacker.turncount["bound"]!=-1:
        # so long as the binding opponent hasn't swapped out
        if pokeDefender.turncount["binding"]!=-1:
            print("The Pokemon is bound!")
            pokeAttacker.turncount["bound"] = pokeAttacker.turncount["bound"]-1
            pokeDefender.turncount["binding"] = pokeDefender.turncount["binding"]-1
            if pokeAttacker.turncount["bound"] == -1:
                print(pokeAttacker.poke["name"] + " has broken free!")
                pokeDefender.turncount["binding"] == -1
        return "fail:bind"
    if pokeAttacker.status == "sleep":
            pokeAttacker.turncount["sleep"] = pokeAttacker.turncount["sleep"]-1
            if pokeAttacker.turncount["sleep"] > 0:
                print(pokeAttacker.poke["name"]+ " is fast asleep!")
                return "fail:sleep"
            else:
                print(pokeAttacker.poke["name"]+" has woken up!")
                pokeAttacker.status = "none"
                return "fail:sleep"
    if pokeAttacker.status == "paralyze":
        paralysisRoll = random.randint(0,255)
        if paralysisRoll < 64:
            return "fail:paralyze"
    if pokeAttacker.status == "freeze":
        if pokeAttacker.moveset[moveAddress]["type"] == "fire":
            print(pokeAttacker.poke["name"] + " has thawed out!")
            pokeDefender.status = "none"
            # then move on as usual
        else:
            return "fail:freeze"
    if pokeAttacker.confused:
        pokeAttacker.turncount["confused"] = pokeAttacker.turncount["confused"]-1
        if pokeAttacker.turncount["confused"]<=0:
            print(pokeAttacker.poke["name"]+" snapped out of confusion!")
            pokeAttacker.confused = False
        else:
            print(pokeAttacker.poke["name"]+" is confused...")
            if random.randint(0,1) == 1:
                moveResult = "fail:confuse"
                return moveResult
    # otherwise
    accRoll = random.randint(0,255)
    if pokeAttacker.moveset[moveAddress]["name"] == "Swift":
        # Swift can fail due to confusion or paralysis or gen 1 miss - nothing else
        if pokeAttacker.moveset[len(pokeAttacker.moveset)-1]["name"]!="Struggle":
            pokeAttacker.PP[moveAddress]=pokeAttacker.PP[moveAddress]-1    
            if pokeAttacker.PP[moveAddress]<0:
                pokeAttacker.PP[moveAddress] = 63         
                # PP ups also applied. May have to do this later
        if accRoll==255:
            return "fail:miss"
        else:
            return "success"
    
       
    moveAcc = math.floor(pokeAttacker.moveset[moveAddress]["acc"]*255/100)
    pokeAcc = stage2Mult(pokeAttacker.modifiers[4])
    pokeEva = stage2Mult(-pokeDefender.modifiers[5])
    acc = math.floor(moveAcc*pokeAcc*pokeEva)
    

    if pokeDefender.whereIs != "field":
        moveResult =  "fail:"+pokeDefender.whereIs 
    if pokeAttacker.moveset[moveAddress]["name"] == "Rage":
        if pokeAttacker.rageAcc.casefold()!="standard":
            accRoll = 1
        if pokeAttacker.modifiers[4]-pokeDefender.modifiers[5] < 0:
            if acc <= accRoll:
                return "fail:miss"
            else:
                return "success"
        else:
            if acc <= accRoll:
                return "gen1miss_rage"
            else:
                return "success"
    elif acc<=accRoll:
        moveResult = "fail:miss"    
    if (pokeAttacker.turncount["bide"]==-1) and (pokeAttacker.turncount["thrash"]==-1) and (pokeAttacker.raging == -1):
        # bide/thrash PP only decreases on first turn
        if pokeAttacker.moveset[len(pokeAttacker.moveset)-1]["name"]!="Struggle":
            pokeAttacker.PP[moveAddress]=pokeAttacker.PP[moveAddress]-1
            if pokeAttacker.PP[moveAddress]<0:
                pokeAttacker.PP[moveAddress] = 63
                # PP Ups also applied. May have to do this later
 

    return moveResult
