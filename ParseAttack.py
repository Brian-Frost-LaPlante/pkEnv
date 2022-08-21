import random
import math
from DamageCalculation import damageCalc
from ConfuseCalculation import confuseCalc
from AccuracyCheck import accuracyCheck

def parseAttack(pokeAttacker,pokeDefender,moveAddress,typeInfo,attBadge,defBadge):
    move = pokeAttacker.moveset[moveAddress]
    category = move["category"]
    cats = str.split(category,':')

    # first, do an accuracy check to see if confusion, paralysis, freeze, or just plain missing stops the pokemon
    accResult = accuracyCheck(pokeAttacker,pokeDefender,moveAddress)
    if accResult == "fail:sleep":
        return ""
    elif accResult == "fail:confuse":
        print(pokeAttacker.poke["name"]+" hit itself in confusion!")
        damage = min(pokeAttacker.HP,confuseCalc(pokeAttacker,pokeDefender.wall))
        pokeAttacker.HP =pokeAttacker.HP-damage
        print(pokeAttacker.poke["name"]+" took "+str(damage)+" damage!")
        if pokeAttacker.HP == 0:
            print(pokeAttacker.poke["name"]+" has fainted!")
            return "attacker:faint"
        else:
            return ""
    elif accResult == "fail:paralyze":
        print(pokeAttacker.poke["name"]+" is paralyzed and can't move!")
        return ""
    elif accResult == "fail:freeze":
        print(pokeAttacker.poke["name"] + " is frozen and can't move!")

    # there are so many cases... the simplest first...
    # null = no effect at all, like splash
    if cats[0] == "null":
        print("That move had no effect!")

    # status move *only* paralyze/confuse/poison/burn/toxic
    # alters the pokemon's status parameter
    elif cats[0] == 'status':
        # first do an accuracy check
        if accResult == "success":
            if cats[1]!= 'confuse':
                if pokeDefender.status != "none":
                    print("The pokemon is already afflicted by a status condition!")
                else:
                    if cats[1] == 'sleep':
                        pokeDefender.turncount["sleep"] = random.randint(1,7)
                        pokeDefender.status = "sleep"
                        print(pokeDefender.poke["name"]+" has been put to sleep!")
                    elif (cats[1] == 'freeze') and ("ice" not in pokeDefender.poke["types"]):
                        pokeDefender.status = "freeze"
                        print(pokeDefender.poke["name"]+" has been frozen!")
                    elif (cats[1] == 'poison') and ("poison" not in pokeDefender.poke["types"]):
                        pokeDefender.status = "poison"
                        print(pokeDefender.poke["name"]+" has been poisoned!")
                    elif (cats[1] == 'burn') and ("fire" not in pokeDefender.poke["types"]):
                        pokeDefender.status = "burn"
                        print(pokeDefender.poke["name"]+" has been burned!")
                        pokeDefender.statUpdate("+burn",defBadge)
                    elif cats[1] == "paralyze":
                        pokeDefender.status = "paralyze"
                        print(pokeDefender.poke["name"]+" has been paralyzed!")
                        pokeDefender.statUpdate("+paralyze",defBadge)
                    elif (cats[1] == 'toxic') and ("poison" not in pokeDefender.poke["types"]):
                        pokeDefender.status = "poison"
                        print(pokeDefender.poke["name"]+" has been badly poisoned!")
                        pokeDefender.turncount["toxic"] = 1
            else:
                if pokeDefender.confused:
                    print(pokeDefender.poke["name"]+" is already confused!")
                else:
                    pokeDefender.confused = True
                    pokeDefender.turncount["confused"] = random.randint(1,4)
                    print(pokeDefender.poke["name"]+" is now confused!")
        else:
            print("The move failed!")

    # there are three walls, and they all can be active at once. 
    # Reflect and Light Screen work for 5 turns, while Mist is active until the pokemon switches out
    elif cats[0] == 'wall':
        # wall moves cant miss, but can fail from par or conf
        wallname = move["name"].casefold()
        if wallname in pokeAttacker.wall:
            print(wallname+" is already up!")
        else:
            pokeAttacker.wall.append(wallname)
            print(pokeAttacker.poke["name"]+" has put up "+wallname)
            # mist lasts until switchout, reflect + light screen last two turns
            if wallname == "reflect" or "light screen":
                pokeAttacker.turncount[wallname] = 5                    
                
    # stat moves alter the self or enemy's stats
    elif cats[0] == 'stat':
        if cats[1] == 'self':
            # self stat-ups cannot miss. They can fail due to par or conf. They also fail after +6
            # They can apply badge boost and make the defending pokemon lose att/speed due to burn/par glitch    
            enemyChange = pokeAttacker.statUpdate("mod:"+cats[2]+":"+cats[3]+":self:"+pokeDefender.status,attBadge)
            if enemyChange == "speed":
                pokeDefender.activeStats[4] = max(math.floor(pokeDefender.activeStats[4]/4),1)
                pokeDefender.setStats()
            elif enemyChange == "attack":
                pokeDefender.activeStats[1] = max(math.floor(pokeDefender.activeStats[1]/2),1)
                pokeDefender.setStats()
        elif cats[1] == 'enemy':
            # enemy stat-ups can miss, fail due to par or conf and miss due to the enemy being in the sky/underground
            if accResult == "success":
                pokeDefender.statUpdate("mod:"+cats[2]+":"+cats[3]+":enemy:"+pokeDefender.status,defBadge)
            else:
                print("The move missed!")

    # there are many kinds of damage moves. the most simple kinds don't do anything other than damage
    # then some have a chance of causing status or stat , some that cause recoil, some that heal the user,
    # multi-hit moves, two-turn charge-up moves, instakill moves, self-destructing moves
    # and very unique moves which we will handle separately
    elif cats[0] == 'damage':
        # first, check if the move lands.Every damage move can fail due to confusion, paralysis, field effects or accuracy
        # even Swift can miss due to gen 1 miss mechanic!
        
        if accResult == "success":
            # Here's a rundown
            # "damage","damage:effect","damage:sd","damage:recoil" and "damage:heal" all require the same sort of damage calculation first
            # "damage:instakill" simply checks the level and kills the enemy if it hits. cool!
            # "damage:multihit" and "damage:twohit" require slightly more intricate damage calculation
            if cats[1] == "instakill":
                damage = pokeDefender.HP
                pokeDefender.HP = 0
                #check type immunity and level
                if ((move["type"]=="normal") and ("ghost" in pokeAttacker.poke["types"])) or ((move["type"]=="ground") and ("flying" in pokeDefender.poke["types"])) or (pokeDefender.level>pokeAttacker.level):
                    print("The move has no effect!")
                    return ""
                print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                print(pokeDefender.poke["name"]+" has instantly fainted!")
                return "defender:faint"
            elif cats[1] in ["standard","enemy","heal","recoil","sd"]:
                # These are all of the moves that deal regularly calculated damage once
                damage = min(pokeDefender.HP,damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo))
                pokeDefender.HP =pokeDefender.HP-damage
                print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                # self-destructing moves can kill either the attacker or both the attacker and defender
                if cats[1] == "sd":
                    pokeAttacker.HP = 0
                    print(pokeAttacker.poke["name"]+" has fainted in noble sacrifice!")
                    if pokeDefender.HP == 0:
                        print(pokeDefender.poke["name"]+" has fainted!")
                        return "both:faint"
                    else:
                        return "attacker:faint"
                elif cats[1] == "recoil":
                    selfDamage = min(math.ceil(damage/4),pokeAttacker.HP)
                    pokeAttacker.HP = pokeAttacker.HP-selfDamage
                    print(pokeAttacker.poke["name"]+" suffered "+str(selfDamage)+" in recoil damage!")
                    if pokeDefender.HP==0:
                        print(pokeDefender.poke["name"]+" has fainted!")
                        if pokeAttacker.HP==0:
                            # Case where both died
                            print(pokeAttacker.poke["name"]+" has fainted!")
                            return "both:faint"
                        else:
                            #only defender died
                            return "defender:faint"
                    elif pokeAttacker.HP == 0:
                        #only attacker fainted
                        print(pokeAttacker.poke["name"]+ " has fainted!")
                        return "attacker:faint"
                    else:
                        return ""
                # for heal, standard and effect moves we only need to consider the enemy's chance to faint
                elif cats[1] == "heal":
                    selfHeal = min(math.ceil(damage/2),pokeAttacker.maxHP-pokeAttacker.HP)
                    pokeAttacker.HP = pokeAttacker.HP+selfHeal
                    print(pokeAttacker.poke["name"]+" healed for "+str(selfHeal)+"!")
                # check if defender fainted
                if pokeDefender.HP == 0:
                    print(pokeDefender.poke["name"]+" has fainted!")
                    return "defender:faint"
                if cats[1] == "enemy":
                    # if the enemy didn't faint, we can check for possible effects on the enemy
                    effectProb = move["effect"]
                    roll = random.randint(1,100)
                    if roll<=effectProb:
                        #the effect will occur
                        if len(cats)==3:
                            # this means the move has a chance to inflict a status
                            if cats[2] not in ['confuse','flinch']:
                                # this is a standard status condition (sleep, par, burn, poison)
                                if pokeDefender.status == "none":
                                    # only actually effects the enemy if they aren't already statused
                                    # paralysis, poison and burn last forever. sleep lasts 1-7 turns.
                                    if cats[2] == 'sleep':
                                        pokeDefender.turncount["sleep"] = random.randint(1,7)
                                        pokeDefender.status = "sleep"
                                        print(pokeDefender.poke["name"]+" has been put to sleep!")
                                    elif (cats[2] == 'freeze') and ("ice" not in pokeDefender.poke["types"]):
                                        pokeDefender.status = "freeze"
                                        print(pokeDefender.poke["name"]+" has been frozen!")
                                    elif (cats[2] == 'poison') and ("poison" not in pokeDefender.poke["types"]):
                                        pokeDefender.status = "poison"
                                        print(pokeDefender.poke["name"]+" has been poisoned!")
                                    elif (cats[2] == 'burn') and ("fire" not in pokeDefender.poke["types"]):
                                        pokeDefender.status = "burn"
                                        print(pokeDefender.poke["name"]+" has been burned!")
                                    elif cats[2] == "paralyze":
                                        pokeDefender.status = "paralyze"
                                        print(pokeDefender.poke["name"]+" has been paralyzed!")
                            elif cats[2] == 'confuse':
                                if not pokeDefender.confused:
                                    #only works if pokemon not already confused, of course
                                    pokeDefender.confused = True
                                    pokeDefender.turncount["confused"] = random.randint(1,4)
                                    print(pokeDefender.poke["name"]+" is now confused!")
                            elif cats[2] == "flinch":
                                pokeDefender.flinching = True
                        else:
                            # this means the attacks inflicts a stat change
                            stat = cats[2]
                            stage = int(cats[3])
                            # modifier index is attack, defense, special, speed, accuracy, evasion, crit chance
                            statarray = ["attack","defense","special","speed","accuracy","evasion","crit"]
                            statIndex = statarray.index(stat)
                            currentStage = pokeDefender.modifiers[statIndex]
                            if (currentStage == -6):
                                print("That stat is already too low!")
                            else:
                                pokeDefender.modifiers[statIndex] = max(-6,currentStage+stage)
                                if stage == -1:
                                    print(pokeDefender.poke["name"]+"'s "+statarray[statIndex]+" has been lowered!")
                                else:
                                    print(pokeDefender.poke["name"]+"'s "+statarray[statIndex]+" has been greatly lowered!")
                                #badge boost here
            else:
                # multihit case. a multihit move deal the same amount of damage n times
                damage = min(pokeDefender.HP,damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo))
                # the pokemon hits with the same amount of damage every time.
                if cats[1] == "twohit":
                    n = 2
                else:
                    roll = random.randint(1,8)
                    if roll in [1,2,3]:
                        n = 2
                    elif roll in [4,5,6]:
                        n = 3
                    elif roll == 7:
                        n = 4
                    else:
                        n = 5
                for i in range(n):
                    min(pokeDefender.HP,damage)
                    pokeDefender.HP =pokeDefender.HP-damage
                    print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                    # check to see if the pokemon fainted. whenever it does, end the attack
                    if pokeDefender.HP == 0:
                        print(pokeDefender.poke["name"]+" has fainted!")
                        return "defender:faint"
                if (move["name"] == "Twineedle") and ("poison" not in pokeDefender.poke["types"]) and (pokeDefender.status=="none"):
                    roll = random.randint(1,5)
                    if roll ==1:
                        print(pokeDefender.poke["name"]+" is poisoned!")
                        pokeDefender.status="poison"
                print("The attack hit "+str(n)+" times!")
            if (move["type"]=="fire") and (pokeDefender.status == "freeze"):
                print(pokeDefender.poke["name"] + " has thawed out!")
                pokeDefender.status = "none"
        else:
            print("The move missed!")
            if move["name"] in ["Jump Kick","Hi Jump Kick"]:
                # The jump kick moves do one damage to the user when they miss (yes, really, 1)
                pokeAttacker.HP = pokeAttacker.HP-1
                print(pokeAttacker.poke["name"]+" hit a wall and took 1 damage!")
                if pokeAttacker.HP == 0:
                    print(pokeAttacker.poke["name"]+" has fainted!")
                    return "attacker:faint"
    return ""
