import random
import math

def DamageCalc(Attacker,Defender,moveNumber,typeInfo,modifiers):
    
    # modifiers is 5-element list attack, defense, attacker special, defender special, crit chance
    attMod = modifiers[0]
    defMod = modifiers[1]
    attspecMod = modifiers[2]
    defspecMod = modifiers[3]
    isCritMod = modifiers[4]
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

        burnLoss = 1    
        wallGain = 1
        damageClass = typeInfo[moveType]["damageClass"]

        if not isCrit: # not a crit
            if damageClass == "physical":
                if status == "burn":
                    burnLoss = 2
                if "reflect" in wall:
                    wallGain = 2
                attStat = math.floor(math.floor(Attacker.Attack*attMod)/burnLoss)
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(math.floor(Defender.Defense*defMod)/2)*wallGain
                else:
                    defStat = math.floor(Defender.Defense*defMod)*wallGain
            else:
                attStat = Attacker.Special*attspecMod
                if "light screen" in wall:
                    wallGain = 2
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(math.floor(Defender.Special*defspecMod)/2)*wallGain
                else:
                    defStat = math.floor(Defender.Special*defspecMod)*wallGain
        else: # is a crit
            if damageClass == "physical":
                attStat = Attacker.Attack
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(Defender.Defense/2)
                else:
                    defStat = Defender.Defense
            else:
                attStat = Attacker.Special
                if move["name"] in ["Explosion","SelfDestruct"]:
                    defStat = math.floor(Defender.Special/2)
                else:
                    defStat = Defender.Special

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

        baseDamage = math.floor(math.floor(math.floor(math.floor(math.floor(math.floor((2*level/5))*attStat*power/defStat)/50)*STAB)*multiplier)*roll/255)
        baseDamage = math.floor(math.floor((math.floor((2*level)/5 + 2)*max(1,attStat)*power)/max(1,defStat))/50)
        threshDamage = min(baseDamage,997)+2
        STABDamage = math.floor(threshDamage*STAB)
        typeDamage = math.floor(STABDamage*multiplier)
        damage = math.floor(typeDamage*roll/255)

    return damage