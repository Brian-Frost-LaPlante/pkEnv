import random
import math
from Stage2Mult import stage2Mult

def damageCalc(Attacker,Defender,moveNumber,typeInfo):
    
    attMod = stage2Mult(Attacker.modifiers[0])
    defMod = stage2Mult(Defender.modifiers[1])
    attspecMod = stage2Mult(Attacker.modifiers[2])
    defspecMod = stage2Mult(Defender.modifiers[2])
    isCritMod =Attacker.modifiers[6]
    move = Attacker.moveset[moveNumber]
    status = Attacker.status
    wall = Defender.wall
    level = Attacker.level

    power = move["power"]
    moveType = move["type"]

    if move["name"] == "Seismic Toss":
        damage = level
    elif move["name"] == "Night Shade":
        damage = level
    elif move["name"] == "Dragon Rage":
        damage = 40
    elif move["name"] == "Sonic Boom":
        damage = 20
    elif move["name"] == "Super Fang":
        damage = math.ceil(Defender.HP/2)
    elif move["name"] == "Psywave":
        damage = random.randint(1,math.floor(1.5*level))

    else: #if not a fixed damage move
        # Compute crit chance
        baseSpeed = Attacker.poke["base stats"][4]
        critMoves = ["Crabhammer","Karate Chop","Slash","Razor Leaf"]
        if move["name"] not in critMoves:
            if isCritMod:
                critThresh = math.floor(baseSpeed/8)
            else:
                critThresh = math.floor(baseSpeed/2)
        else:
            if isCritMod:
                critThresh = 4*math.floor(baseSpeed/4)
            else:
                critThresh = min(8*math.floor(baseSpeed/2),255)
        critThresh = min(255,critThresh)
        critRoll = random.randint(0,255)
        isCrit = critRoll<critThresh
        
        if isCrit:
            level = 2*Attacker.level   
            print("A critical hit!")

        wallGain = 1
        damageClass = typeInfo[moveType]["damageClass"]

        if not isCrit: # not a crit
            if damageClass == "physical":
                if "reflect" in wall:
                    wallGain = 2
                attStat = Attacker.attack
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(Defender.defense/2)*wallGain
                else:
                    defStat = math.floor(Defender.defense)*wallGain
            else:
                attStat = Attacker.special
                if "light screen" in wall:
                    wallGain = 2
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(Defender.special/2)*wallGain
                else:
                    defStat = Defender.special*wallGain
        else: # is a crit
            if damageClass == "physical":
                attStat = Attacker.outOfBattleStats[1]
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(Defender.outOfBattleStats[2]/2)
                else:
                    defStat = Defender.outOfBattleStats[2]
            else:
                attStat = Attacker.outOfBattleStats[3]
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(Defender.outOfBattleStats[3]/2)
                else:
                    defStat = Defender.outOfBattleStats[3]

        if (attStat > 255) or (defStat > 255):
            attStat = math.floor(attStat / 4) % 256
            defStat = math.floor(defStat / 4) % 256

        multiplier = 1
        defenderTypes = Defender.poke["types"]
        for type in defenderTypes:
            if moveType in typeInfo[type]["weakTo"]:
                multiplier = multiplier*2
            elif moveType in typeInfo[type]["resistantTo"]:
                multiplier = multiplier/2
            elif moveType in typeInfo[type]["nullTo"]:
                multiplier = 0
        roll = random.randint(217,255)

        STAB = 1
        if moveType.casefold() in Attacker.poke["types"]:
            STAB = 1.5

        baseDamage = math.floor(math.floor((math.floor((2*level)/5 + 2)*max(1,attStat)*power)/max(1,defStat))/50)
        threshDamage = min(baseDamage,997)+2
        STABDamage = math.floor(threshDamage*STAB)
        typeDamage = math.floor(STABDamage*multiplier)
        damage = math.floor(typeDamage*roll/255)
        damage = max(damage,1)

    return damage