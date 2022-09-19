import random
import math
from DamageCalculation import damageCalc
from ConfuseCalculation import confuseCalc
from AccuracyCheck import accuracyCheck

def processConfuseDamage(pokeAttacker,pokeDefender,moveAddress):
    print(pokeAttacker.poke["name"]+" hit itself in confusion!")
    damage = confuseCalc(pokeAttacker,pokeDefender.wall)
    if not pokeAttacker.subbing:
        # without substitution things are normal
        damage = min(damage,pokeAttacker.HP)
        pokeAttacker.activeStats[0] =pokeAttacker.HP-damage
        pokeAttacker.setStats()
        # interestingly, confuse damage counts as last damage done
        pokeDefender.lastDamage[0] = damage
        pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
        pokeAttacker.whereIs = "field"
        print(pokeAttacker.poke["name"]+" took "+str(damage)+" damage!")
        if pokeAttacker.HP == 0:
            print(pokeAttacker.poke["name"]+" has fainted!")
            return "attacker:faint"
        else:
            return ""
    else:
        # this is the case where the pokemon has a substitute out. it's weird
        if not pokeDefender.subbing:
            # if the enemy pokemon doesn't have a substitute up, nothing happens
            print("Huh! Nothing happened!")
        else:
            # otherwise the attacker's confuse damage is afflicted to the opponent's substitute...
            damage = min(damage,pokeDefender.subHP)
            pokeDefender.subHP = pokeDefender.subHP-damage
            print(pokeDefender.poke["name"]+"'s substitute took " + str(damage)+ " damage!")
            pokeDefender.lastDamage[0] = damage
            pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
            if pokeDefender.subHP==0:
                pokeDefender.subbing = False
                print(pokeDefender.poke["name"] + "'s substitute broke!")
        return ""

def processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo):
    if not pokeDefender.subbing:
        damage = min(pokeDefender.HP,damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo))
        pokeDefender.activeStats[0] = pokeDefender.HP-damage
        pokeDefender.setStats()
        print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
        pokeDefender.lastDamage[0] = damage
        pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
        if pokeDefender.HP == 0:
            print(pokeDefender.poke["name"]+" has fainted!")
            return "defender:faint"
        return ""
    else:
        # if the defender has a substitute up, in most situations, the sub takes the damage instead
        rawDamage = damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo)
        # damage to substitute is what impacts the sub, ofc. damage for counter is computed using raw damage
        damageWouldBe = min(pokeDefender.HP,rawDamage)
        pokeDefender.lastDamage[0] = damageWouldBe
        pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
        damage = min(pokeDefender.subHP,rawDamage)
        pokeDefender.subHP = pokeDefender.subHP-damage
        print(pokeDefender.poke["name"]+"'s substitute took " + str(damage)+ " damage!")
        if pokeDefender.subHP==0:
            pokeDefender.subbing = False
            print(pokeDefender.poke["name"] + "'s substitute broke!")
        return ""



def parseAttack(pokeAttacker,pokeDefender,moveAddress,typeInfo,moveInfo,attBadge,defBadge):
    # manages almost every move, except metronome which picks a move (in battle class) and then is managed here after
    move = pokeAttacker.moveset[moveAddress]
    category = move["category"]
    cats = str.split(category,':')

    if move["name"] == pokeAttacker.disable:
        print(pokeAttacker.poke["name"]+ "'s "+move["name"]+" is disabled!")
        pokeAttacker.turncount["disable"] = pokeAttacker.turncount["disable"]-1
        if pokeAttacker.turncount["disable"] == 0:
            print(pokeAttacker.poke["name"]+ "'s "+move["name"]+" is no longer disabled!")
            pokeAttacker.disable = ""
        return ""
            
    if cats[0] == "bide":
        # bide works in a funny way, completely dismissing most accuracy checks. on the turn it is used, it can fail.
        # sleep/freeze only pause the counter
        pokeAttacker.bideUsed = moveAddress
        accResult = accuracyCheck(pokeAttacker,pokeDefender,moveAddress)
        if accResult == "fail:sleep":
            return "sleep"
        elif accResult == "fail:bind":
            return "bind"
        elif accResult == "fail:freeze":
            print(pokeAttacker.poke["name"] + " is frozen and can't move!")
            return "freeze"
        # bide counts up the amount of damage over two to three turns
        if pokeAttacker.turncount["bide"] == -1:
            # on this turn, par/confusion matter.
            if accResult == "fail:paralyze":
                print(pokeAttacker.poke["name"]+" is paralyzed and can't move!")
                pokeAttacker.whereIs = "field"
                return ""
            if accResult == "fail:confuse":
                return processConfuseDamage(pokeAttacker,pokeDefender,moveAddress)

            print(pokeAttacker.poke["name"] + " started storing up energy!")
            pokeAttacker.turncount["bide"] = random.sample([2,3],1)[0]
            return ""
        elif pokeAttacker.turncount["bide"] == 0:
            if not pokeDefender.subbing:
                print(pokeAttacker.poke["name"] + " is unleashing its energy!")
                damage = min(pokeDefender.HP,2*pokeAttacker.bideDamage)
                pokeDefender.activeStats[0] = pokeDefender.HP-damage
                pokeDefender.setStats()
                pokeAttacker.turncount["bide"] = pokeAttacker.turncount["bide"]-1
                pokeAttacker.bideDamage = 0
                print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                if pokeDefender.HP == 0:
                    print(pokeDefender.poke["name"]+" has fainted!")
                    return "defender:faint"
            else:
                print(pokeAttacker.poke["name"] + " is unleashing its energy!")
                damage = min(pokeDefender.subHP,2*pokeAttacker.bideDamage)
                pokeDefender.subHP = pokeDefender.subHP-damage
                pokeAttacker.turncount["bide"] = pokeAttacker.turncount["bide"]-1
                pokeAttacker.bideDamage = 0
                print(pokeDefender.poke["name"]+"'s substitute took "+str(damage)+" damage!")
                if pokeDefender.subHP == 0:
                    print(pokeDefender.poke["name"]+"'s substitute broke!")
                    pokeDefender.subbing = False

        else:
            print(pokeAttacker.poke["name"] + " is storing up energy!")
            pokeAttacker.bideDamage = pokeAttacker.bideDamage + pokeAttacker.lastDamage[0]
            pokeAttacker.turncount["bide"] = pokeAttacker.turncount["bide"]-1
            return ""
        return ""

    if cats[0] == "thrashlike":
        pokeAttacker.thrashUsed = moveAddress
        # bide works in a funny way, dismissing most accuracy checks after it begins. on the turn it is used, it can fail.
        # sleep/freeze only pause the counter
        accResult = accuracyCheck(pokeAttacker,pokeDefender,moveAddress)
        if accResult == "fail:sleep":
            # pokeAttacker.turncount PAUSES
            return "sleep"
        elif accResult == "fail:bind":
            return "bind"
        elif accResult == "fail:freeze":
            print(pokeAttacker.poke["name"] + " is frozen and can't move!")
            # pokeAttacker.turncount PAUSES
            return "freeze"
        
        elif accResult == "fail:paralyze":
            print(pokeAttacker.poke["name"]+" is paralyzed and can't move!")
            pokeAttacker.whereIs = "field"
            # thrash ENDS
            pokeAttacker.turncount["thrash"] = -1
            return ""

        elif accResult == "fail:confuse":
            # thrash ENDS
            pokeAttacker.turncount["thrash"] = -1
            return processConfuseDamage(pokeAttacker,pokeDefender,moveAddress)

        # thrash attacks for 3-4 turns
        if pokeAttacker.turncount["thrash"] == -1:
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
            # on this turn, par/confusion/missing matters.
            if accResult == "fail:sky":
                print(pokeAttacker.poke["name"]+" can't hit a Pokemon in the air!")
                pokeDefender.lastDamage[0] = 0
                pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
                return ""
            elif accResult == "fail:underground":
                print(pokeAttacker.poke["name"]+" can't hit a Pokemon underground!")
                pokeDefender.lastDamage[0] = 0
                pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
                return ""
            elif accResult == "fail:miss":
                print(pokeAttacker.poke["name"]+" missed!")
                pokeDefender.lastDamage[0] = 0
                return ""
            elif (pokeAttacker.moveset[moveAddress]["type"].casefold() in ["normal","fighting"]) and ("ghost" in pokeDefender.poke["types"]):
                print("That move does not affect Ghosts!")
                pokeDefender.lastDamage[0] = 0
                return ""
            # Otherwise, it begins!
            print(pokeAttacker.poke["name"] + " started thrashing about!")
            # 3-4 turns, counting this one, so really 2-3 "more" turns
            pokeAttacker.turncount["thrash"] = random.sample([1,2],1)[0]
            return processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
        else:
            print(pokeAttacker.poke["name"] + " is thrashing about!")
            if accResult == "fail:sky":
                print(pokeAttacker.poke["name"]+" can't hit a Pokemon in the air!")
                pokeAttacker.turncount["thrash"] = pokeAttacker.turncount["thrash"]-1
                pokeDefender.lastDamage[0] = 0
                pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
            elif accResult == "fail:underground":
                print(pokeAttacker.poke["name"]+" can't hit a Pokemon underground!")
                pokeAttacker.turncount["thrash"] = pokeAttacker.turncount["thrash"]-1
                pokeDefender.lastDamage[0] = 0
                pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
            else:
                damage = min(pokeDefender.HP,damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo))
                pokeDefender.activeStats[0] = pokeDefender.HP-damage
                pokeDefender.setStats()
                print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                pokeAttacker.turncount["thrash"] = pokeAttacker.turncount["thrash"]-1
                pokeDefender.lastDamage[0] = damage
                pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
            if pokeAttacker.turncount["thrash"] == -1:
                # when thrash ends, we get confused
                print(pokeAttacker.poke["name"] + " has stopped thrashing about!")
                if not pokeAttacker.confused: # the pokemon becomes confused if not already confused
                    pokeAttacker.confused = True
                    pokeAttacker.turncount["confused"] = random.randint(1,4)
                    print(pokeAttacker.poke["name"]+" is now confused!")
            if pokeDefender.HP == 0:
                print(pokeDefender.poke["name"]+" has fainted!")
                return "defender:faint"
        return ""

    if cats[0] == "bindlike":
        pokeAttacker.bindUsed = moveAddress

        # very complicated. If the pokemon we are up against has not been bound 
        # (either because it was just switched in or just bind hasnt started), we use bind anew
        if pokeDefender.turncount["bound"] == -1:
            accResult = accuracyCheck(pokeAttacker,pokeDefender,moveAddress)
            if accResult == "fail:sleep":
                return "sleep"
            elif accResult == "fail:freeze":
                print(pokeAttacker.poke["name"] + " is frozen and can't move!")
                return "freeze"
            
            elif accResult == "fail:paralyze":
                print(pokeAttacker.poke["name"]+" is paralyzed and can't move!")
                pokeAttacker.whereIs = "field"
                return ""
            elif accResult == "fail:bind":
                return "bind"
            elif accResult == "fail:confuse":
                return processConfuseDamage(pokeAttacker,pokeDefender,moveAddress)
            elif pokeDefender.subbing:
                print("You cannot bind a substitute!")
                return ""
            # apply bind , even if PP is 0! this causes an underflow
            roll = random.randint(0,63)
            if roll < 24:
                # bind will last two turn 
                pokeDefender.turncount["bound"] = 1
                pokeAttacker.turncount["binding"] = 1
            elif roll < 48:
                pokeDefender.turncount["bound"] = 2
                pokeAttacker.turncount["binding"] = 2
            elif roll < 56:
                pokeDefender.turncount["bound"] = 3
                pokeAttacker.turncount["binding"] = 3
            elif roll < 64:
                pokeDefender.turncount["bound"] = 4
                pokeAttacker.turncount["binding"] = 4
            print(pokeAttacker.poke["name"] + " has trapped its opponent!")
            # whatever damage the move does on its firt turn, it will continue to do.
            pokeAttacker.bindDamage = damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo)
            damage = min(pokeDefender.HP,pokeAttacker.bindDamage)
            pokeDefender.activeStats[0] = pokeDefender.HP-damage
            pokeDefender.setStats()
            print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
            pokeDefender.lastDamage[0] = damage
            pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
            if pokeDefender.HP == 0:
                print(pokeDefender.poke["name"]+" has fainted!")
                # in this case, the binding period is reset
                pokeAttacker.turncount["binding"] = -1
                pokeAttacker.turncount["bound"] = -1
                return "defender:faint"
        else:
            print(pokeAttacker.poke["name"]+"'s trap continues.")
            damage = min(pokeDefender.HP,pokeAttacker.bindDamage)
            pokeDefender.activeStats[0] = pokeDefender.HP-damage
            pokeDefender.setStats()
            print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
            pokeDefender.lastDamage[0] = damage
            pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
            if pokeDefender.HP == 0:
                print(pokeDefender.poke["name"]+" has fainted!")
                # in this case, the binding period is reset
                pokeAttacker.turncount["binding"] = -1
                pokeAttacker.turncount["bound"] = -1
                return "defender:faint"
        return ""


    #now for other moves first, do an accuracy check to see if confusion, paralysis, freeze, or just plain missing stops the pokemon
    accResult = accuracyCheck(pokeAttacker,pokeDefender,moveAddress)
    if accResult == "fail:sleep":
        return "sleep"
    elif accResult == "fail:bind":
        return "bind"
    elif accResult == "fail:confuse":
        return processConfuseDamage(pokeAttacker,pokeDefender,moveAddress)
    elif accResult == "fail:paralyze":
        print(pokeAttacker.poke["name"]+" is paralyzed and can't move!")
        pokeAttacker.whereIs = "field"
        return ""
    elif accResult == "fail:freeze":
        print(pokeAttacker.poke["name"] + " is frozen and can't move!")
        return "freeze"
    elif accResult == "fail:sky":
        print(pokeAttacker.poke["name"]+" can't hit a Pokemon in the air!")
        # still counts for mirror move
        pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
        return ""
    elif accResult == "fail:underground":
        print(pokeAttacker.poke["name"]+" can't hit a Pokemon underground!")
        pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
        return ""
    # there are so many cases... the simplest first...
    # null = no effect at all, like splash
    if cats[0] == "null":
        print("That move had no effect!")

    elif cats[0] == "counter":
        if accResult == "success":
            if (pokeAttacker.lastDamage[0] != 0) and (pokeAttacker.lastDamage[1] in ["normal","fighting"]):
                damage = min(pokeDefender.HP,2*pokeAttacker.lastDamage[0])
                pokeAttacker.lastDamage[0] = damage
                pokeDefender.activeStats[0] = pokeDefender.HP-damage
                pokeDefender.setStats()
                print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                if pokeDefender.HP == 0:
                    print(pokeDefender.poke["name"]+" has fainted!")
                    return "defender:faint"
            else:
                print("The move failed!")
                pokeAttacker.lastDamage[0] = 0
        else:
            pokeAttacker.lastDamage[0] = 0
            print("The move missed!")

    # status move *only* paralyze/confuse/poison/burn/toxic
    # alters the pokemon's status parameter
    elif cats[0] == 'status':
        # these moves do not change lastDamage, unless it misses I think?
        pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
        # first do an accuracy check
        if accResult == "success":
            if cats[1]!= 'confuse':
                if pokeDefender.status != "none":
                    print("The pokemon is already afflicted by a status condition!")
                else:
                    if move["type"] not in pokeDefender.types:
                        if cats[1] == 'sleep':
                            pokeDefender.turncount["sleep"] = random.randint(1,7)
                            pokeDefender.status = "sleep"
                            print(pokeDefender.poke["name"]+" has been put to sleep!")
                            # if the pokemon is recharging from hyper beam, going to sleep stops that
                            pokeDefender.recharging = False
                        elif (cats[1] == 'freeze'): 
                            if pokeDefender.subbing:
                                print("A substitute cannot be frozen!")
                            else:
                                pokeDefender.status = "freeze"
                                print(pokeDefender.poke["name"]+" has been frozen!")
                        elif (cats[1] == 'poison'):
                            if pokeDefender.subbing:
                                print("A substitute cannot be poisoned!")
                            else:
                                pokeDefender.status = "poison"
                                print(pokeDefender.poke["name"]+" has been poisoned!")
                        elif (cats[1] == 'burn'):
                            if pokeDefender.subbing:
                                print("A substitute cannot be burnt!")
                            else:
                                pokeDefender.status = "burn"
                                print(pokeDefender.poke["name"]+" has been burned!")
                                pokeDefender.statUpdate("+burn",defBadge)
                        elif cats[1] == "paralyze": # for some reason, this affects subbed pokemon
                            pokeDefender.status = "paralyze"
                            print(pokeDefender.poke["name"]+" has been paralyzed!")
                            pokeDefender.statUpdate("+paralyze",defBadge)
                        elif (cats[1] == 'toxic'):
                            if pokeDefender.subbing:
                                print("A substitute cannot be poisoned!")
                            else:
                                pokeDefender.status = "poison"
                                print(pokeDefender.poke["name"]+" has been badly poisoned!")
                                pokeDefender.turncount["toxic"] = 1
                    else:
                        print("The move failed!")
            else:
                if pokeDefender.confused:
                    print(pokeDefender.poke["name"]+" is already confused!")
                else:
                    if pokeDefender.subbing:
                        print("A substitute cannot be confused!")
                    else:
                        pokeDefender.confused = True
                        pokeDefender.turncount["confused"] = random.randint(1,4)
                        print(pokeDefender.poke["name"]+" is now confused!")
        else:
            print("The move failed!")
            pokeDefender.lastDamage[0] = 0

    # there are three walls, and they all can be active at once. 
    # Reflect and Light Screen work for 5 turns, while Mist is active until the pokemon switches out
    elif cats[0] == 'wall':
        # wall moves cant miss, but can fail from par or conf
        wallname = move["name"].casefold()
        if wallname in pokeAttacker.wall:
            print(wallname.capitalize()+" is already up!")
        else:
            pokeAttacker.wall.append(wallname)
            print(pokeAttacker.poke["name"]+" has put up "+wallname)
            # mist lasts until switchout, reflect + light screen last two turns
            if wallname == "reflect" or "light screen":
                pokeAttacker.turncount[wallname] = 5                    
               
    # heal moves simply heal the self by 1/2 total health
    elif cats[0] == 'heal':
        toHeal = min(math.floor(pokeAttacker.maxHP/2),pokeAttacker.maxHP-pokeAttacker.HP)
        if toHeal == 0:
            print(pokeAttacker.poke["name"]+" is already at full health!")
        else:
            pokeAttacker.activeStats[0] = pokeAttacker.HP+toHeal
            pokeAttacker.setStats()
            print(pokeAttacker.poke["name"]+" healed for "+str(toHeal)+" HP!")

    # stat moves alter the self or enemy's stats
    elif cats[0] == 'stat':
        pokeDefender.lastDamage[0] = 0 # resets damage done
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
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
            # enemy stat-ups can miss, fail due to par or conf and miss due to the enemy being in the sky/underground

            if accResult == "success":
                if pokeDefender.subbing:
                    print("A substitute cannot have its stats lowered!")
                elif "mist" in pokeDefender.wall:
                    print(pokeDefender.poke["name"] + " is shrouded in mist!")
                else:
                    pokeDefender.statUpdate("mod:"+cats[2]+":"+cats[3]+":enemy:"+pokeDefender.status,defBadge)
            else:
                print("The move missed!")
                pokeDefender.lastDamage[0] = 0

    # there are many kinds of damage moves. the most simple kinds don't do anything other than damage
    # then some have a chance of causing status or stat , some that cause recoil, some that heal the user,
    # multi-hit moves, two-turn charge-up moves, instakill moves, self-destructing moves
    # and very unique moves which we will handle separately
    elif cats[0] == 'damage':
        # first, check if the move lands.Every damage move can fail due to confusion, paralysis, field effects or accuracy
        # even Swift can miss due to gen 1 miss mechanic!
        
        pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
        
        if accResult == "success":
            # Here's a rundown
            # "damage","damage:effect","damage:sd","damage:recoil" and "damage:heal" all require the same sort of damage calculation first
            # "damage:instakill" simply checks the level and kills the enemy if it hits. cool!
            # "damage:multihit" and "damage:twohit" require slightly more intricate damage calculation
            if cats[1] == "instakill":
                #check type immunity and speed
                if ((move["type"]=="normal") and ("ghost" in pokeAttacker.poke["types"])) or ((move["type"]=="ground") and ("flying" in pokeDefender.poke["types"])) or (pokeDefender.activeStats[4]>pokeAttacker.activeStats[4]):
                    print("The move has no effect!")
                    return ""
                damage = pokeDefender.HP
                pokeDefender.lastDamage[0] = damage
                pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
                if pokeDefender.subbing:
                    pokeDefender.subbing = False
                    pokeDefender.subHP = 0
                    print(pokeDefender.poke["name"] + "'s substitute has immediately broken!")
                else:
                    pokeDefender.activeStats[0] = 0
                    pokeDefender.setStats()
                    print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                    print(pokeDefender.poke["name"]+" has instantly fainted!")
                    return "defender:faint"
            elif cats[1] in ["standard","enemy","heal","recoil","sd"]:
                # These are all of the moves that deal regularly calculated damage once
                subBef = pokeDefender.subbing
                res = processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
                # if the pokemon's substitute was broken, other things happen
                subBroken = subBef and (not pokeDefender.subbing)

                # self-destructing moves can kill either the attacker, a substitute or both the attacker and defender
                if cats[1] == "sd":
                    if subBroken:
                        # for some reason, sd moves dont self-damage after a substitute is broken
                        return ""
                    pokeDefender.activeStats[0] = 0
                    pokeDefender.setStats()
                    print(pokeAttacker.poke["name"]+" has fainted in noble sacrifice!")
                    if pokeDefender.HP == 0:
                        print(pokeDefender.poke["name"]+" has fainted!")
                        return "both:faint"
                    else:
                        return "attacker:faint"
                elif cats[1] == "recoil":
                    selfDamage = min(math.ceil(damage/4),pokeAttacker.HP)
                    pokeAttacker.activeStats[0] = pokeAttacker.HP-selfDamage
                    pokeAttacker.setStats()
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
                    if subBroken:
                        # for some reason drain moves don't drain any HP if you broke a sub
                        return ""
                    pokeAttacker.activeStats[0] = pokeAttacker.HP+selfHeal
                    pokeAttacker.setStats()
                    print(pokeAttacker.poke["name"]+" healed for "+str(selfHeal)+"!")
                # check if defender fainted in other situations
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
                                if move["type"] not in pokeDefender.types:
                                    if pokeDefender.status == "none":
                                        # only actually effects the enemy if they aren't already statused
                                        # paralysis, poison and burn last forever. sleep lasts 1-7 turns.
                                        # subs cannot be poinones, frozen, burnt or flinched
                                        # if the sub is not broken, damage moves can confuse or par
                                        if cats[2] == 'sleep':
                                            if not subBef:
                                                pokeDefender.turncount["sleep"] = random.randint(1,7)
                                                pokeDefender.status = "sleep"
                                                print(pokeDefender.poke["name"]+" has been put to sleep!")
                                            pokeDefender.recharging = False
                                        elif (cats[2] == 'freeze'):
                                            if not subBef:
                                                pokeDefender.status = "freeze"
                                                print(pokeDefender.poke["name"]+" has been frozen!")
                                        elif (cats[2] == 'poison'):
                                            if not subBef:
                                                pokeDefender.status = "poison"
                                                print(pokeDefender.poke["name"]+" has been poisoned!")
                                        elif (cats[2] == 'burn'):
                                            if not subBef:
                                                pokeDefender.status = "burn"
                                                pokeDefender.statUpdate("+burn",defBadge)
                                                print(pokeDefender.poke["name"]+" has been burned!")
                                        elif cats[2] == "paralyze":
                                            if not subBroken:
                                                pokeDefender.status = "paralyze"
                                                pokeDefender.statUpdate("+paralyze",defBadge)
                                                print(pokeDefender.poke["name"]+" has been paralyzed!")
                            elif cats[2] == 'confuse':
                                if not (pokeDefender.confused or subBroken):
                                    #only works if pokemon not already confused, of course
                                    pokeDefender.confused = True
                                    pokeDefender.turncount["confused"] = random.randint(1,4)
                                    print(pokeDefender.poke["name"]+" is now confused!")
                            elif cats[2] == "flinch":
                                if subBef:
                                    return "" # substitutes cannot flinch
                                pokeDefender.flinching = True
                                return "flinch"
                        elif not subBef:
                            # this means the attacks inflicts a stat change
                            enemyChange = pokeDefender.statUpdate("mod:"+cats[2]+":"+cats[3]+":enemy:"+pokeDefender.status,defBadge)
                            if enemyChange == "speed":
                                pokeDefender.activeStats[4] = max(math.floor(pokeDefender.activeStats[4]/4),1)
                                pokeDefender.setStats()
                            elif enemyChange == "attack":
                                pokeDefender.activeStats[1] = max(math.floor(pokeDefender.activeStats[1]/2),1)
                                pokeDefender.setStats()

            else:
                # multihit case. a multihit move deal the same amount of damage n times
                # we also need to consider substitute. multihit stops instantly when it hits a subst
                damage = damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo)
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
                    damage = min(pokeDefender.HP,damage)
                    pokeDefender.lastDamage[0] = damage
                    pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
                    if pokeDefender.subbing:
                        damage = min(pokeDefender.subHP,damage)
                        pokeDefender.subHP = pokeDefender.subHP - damage
                        if pokeDefender.subHP == 0:
                            print("The substitute has broken!")
                            return ""
                    pokeDefender.activeStats[0] = pokeDefender.HP-damage
                    pokeDefender.setStats()
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
                pokeAttacker.activeStats[0] = pokeAttacker.HP-1
                pokeDefender.lastDamage[0] = 1
                pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
                pokeAttacker.setStats()
                print(pokeAttacker.poke["name"]+" hit a wall and took 1 damage!")
                if pokeAttacker.HP == 0:
                    print(pokeAttacker.poke["name"]+" has fainted!")
                    return "attacker:faint"
            else:
                pokeDefender.lastDamage[0] = 0
   
    elif cats[0] == "dreameater":
        if accResult == "success":
            if pokeDefender.status != "sleep":
                print("The move failed!")
            else:
                if not pokeDefender.subbing:
                    damage = min(pokeDefender.HP,damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo))
                    pokeDefender.lastDamage[0] = damage
                    pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
                    pokeDefender.activeStats[0] = pokeDefender.HP-damage
                    pokeDefender.setStats()
                    print(pokeDefender.poke["name"]+" took "+str(damage)+" damage!")
                    toHealTemp = max(1,math.floor(damage/2))
                    toHeal = min(pokeAttacker.maxHP-pokeAttacker.HP,toHealTemp)
                    if pokeAttacker.HP!=pokeAttacker.maxHP:
                        pokeAttacker.activeStats[0] = pokeAttacker.HP+toHeal
                        pokeAttacker.setStats()
                        print(pokeAttacker.poke["name"]+" healed for "+str(toHeal)+" HP!")
                    if pokeDefender.HP == 0:
                        print(pokeDefender.poke["name"]+" has fainted!")
                        return "defender:faint"
                else:
                    damage = min(pokeDefender.subHP,damageCalc(pokeAttacker,pokeDefender,moveAddress,typeInfo))
                    pokeDefender.lastDamage[0] = damage
                    pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
                    pokeDefender.subHP = pokeDefender.subHP-damage
                    if pokeDefender.subHP == 0:
                        pokeDefender.subbing = False
                        print(pokedefender.poke["name"]+"'s Substitute broke!")
                    else:
                        toHealTemp = max(1,math.floor(damage/2))
                        toHeal = min(pokeAttacker.maxHP-pokeAttacker.HP,toHealTemp)
                        if pokeAttacker.HP!=pokeAttacker.maxHP:
                            pokeAttacker.activeStats[0] = pokeAttacker.HP+toHeal
                            pokeAttacker.setStats()
                            print(pokeAttacker.poke["name"]+" healed for "+str(toHeal)+" HP!")
        else:
            print("The move missed!")
            pokeDefender.lastDamage[0] = 0
        
        pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]


    # rest fails if the user is at full HP. Otherwise, it will clear all status conditions (without changing the stat changes they cause!), heal to full and put to sleep for 2 turns.
    # for some reason, it also fails if maxHP-currentHP%256 == 255
    elif cats[0]=="rest":
        toHeal = pokeAttacker.maxHP-pokeAttacker.HP
        if (toHeal==0) or (toHeal%256==255):
            print("Rest failed!")
        else:
            print(pokeAttacker.poke["name"]+" has healed up and fallen asleep!")
            pokeAttacker.activeStats[0] = pokeAttacker.maxHP
            pokeAttacker.setStats()
            pokeAttacker.status = "sleep"
            pokeAttacker.turncount["sleep"] = 2

    # conversion just changes the attacker's types to be those of the opponent
    elif cats[0]=="conversion":
        if accResult == "success":
            pokeAttacker.types = pokeDefender.types
            print(pokeAttacker.poke["name"]+" has changed type to match its opponent!")
        else:
            print("The move missed!")
            pokeDefender.lastDamage[0] = 0
        pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]

    elif cats[0]=="haze":
        # first, haze resets all active stats to out of battle stats (except HP of course)
        pokeAttacker.statReset()
        pokeAttacker.wall = []
        pokeAttacker.leechSeed=False

        pokeDefender.statReset()
        pokeDefender.wall = []
        pokeDefender.leechSeed=False
        if pokeDefender.status in ["sleep","freeze"]:
            print("Various stat effects have been nullified!")
            pokeDefender.status="none"
            return "unable"
        pokeDefender.status="none"
        print("Various stat effects have been nullified!")

    elif cats[0]=="disable":
        pokeDefender.lastDamage[0] = 0

        # for whatever reason, this builds rage
        if pokeDefender.raging != -1:
            enemyChange = pokeAttacker.statUpdate("mod:"+"attack"+":"+"1"+":self:"+pokeDefender.status,attBadge)
            if enemyChange == "speed":
                pokeDefender.activeStats[4] = max(math.floor(pokeDefender.activeStats[4]/4),1)
                pokeDefender.setStats()
            elif enemyChange == "attack":
                pokeDefender.activeStats[1] = max(math.floor(pokeDefender.activeStats[1]/2),1)
                pokeDefender.setStats()


        if pokeDefender.disable != "":
            print(pokeDefender.poke["name"]+" already has a move disabled!")
            return ""
        validMoves = []
        for i in range(len(pokeDefender.moveset)):
            if pokeDefender.PP[i] !=0:
                validMoves.append(pokeDefender.moveset[i]["name"])
        if validMoves == []:
            print("There are no moves to disable!")
        else:
            moveToDisable = random.choice(validMoves)
            pokeDefender.disable = moveToDisable
            pokeDefender.turncount["disable"] = random.randint(1,7)
            print(pokeDefender.poke["name"]+" had its " + moveToDisable+" disabled!")

    elif cats[0]=="leechseed":
        if accResult == "success":
            if "grass" in pokeDefender.types:
                print("Leech Seed does not affect Grass-type Pokemon!")
            else:
                print(pokeDefender.poke["name"] + " is seeded!")
                pokeDefender.leechSeed = True
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
        else:
            print("The move missed!")
            pokeDefender.lastDamage[0] = 0

    elif cats[0]=="twoturn":
        # two cases: this is the first turn (charging will be -1) or the second turn after charging
        if pokeAttacker.charging == -1:
            pokeAttacker.charging = moveAddress
            print(pokeAttacker.poke["name"] + " is charging up!")
        else:
            pokeAttacker.charging = -1
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
            if accResult == "success":
                return processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
            else:
                print("The move missed!")
                pokeDefender.lastDamage[0] = 0


    elif cats[0]=="fly":
        # two cases: this is the first turn (charging will be -1) or the second turn after charging
        if pokeAttacker.charging == -1:
            pokeAttacker.charging = moveAddress
            print(pokeAttacker.poke["name"] + " has flown into the sky!")
            pokeAttacker.whereIs = "sky"
        else:
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
            pokeAttacker.charging = -1
            pokeAttacker.whereIs = "field"
            if accResult == "success":
                return processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
            else:
                print("The move failed!")
                pokeDefender.lastDamage[0] = 0

    elif cats[0]=="dig":
        # two cases: this is the first turn (charging will be -1) or the second turn after charging
        if pokeAttacker.charging == -1:
            pokeAttacker.charging = moveAddress
            print(pokeAttacker.poke["name"] + " has burrowed underground!")
            pokeAttacker.whereIs = "underground"
        else:
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
            pokeAttacker.charging = -1
            pokeAttacker.whereIs = "field"
            if accResult == "success":
                return processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
            else:
                print("The move failed!")
                pokeDefender.lastDamage[0] = 0
    
    elif cats[0] == "hyperbeam":
        # this move is kind of funny. It will try to do damage, of course. if the  move lands and doesn't kill the pokemon or break a substitute, it will enter "recharging". This means the next turn the player cannot take an action. a few things screw up recharging, like bind or freeze. That is handled outside of here.
        if accResult == "success":
            subBef = pokeDefender.subbing
            r = processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
            subBroken = subBef and (not pokeDefender.subbing)
            if not subBroken:
                pokeAttacker.recharging = pokeAttacker.recharging + 1
            return r
        else:
            print("The move failed!")
            pokeDefender.lastDamage[0] = 0

    elif cats[0] == "mimic":
        # this move displays the enemy moveset and lets you pick one of their moves to replace mimic. it maintains the same PP as mimic. it can mimic literally any move.
        if accResult == "success":
            print("Please select one of the Pokemon's moves to copy:")
            M = len(pokeDefender.moveset)
            for m in range(M):
                print("["+str(m+1)+"]"+pokeDefender.moveset[m]["name"])
            valid = False
            while not valid:
                selection = input()
                if not selection.isdigit():
                    print("That is not a valid option")
                elif (int(selection)-1) in range(M):
                    selection = int(selection)-1
                    valid = True
                else:
                    print("That is not a valid option")
            # now copy that move to where mimic was
            pokeAttacker.moveset[moveAddress] = pokeDefender.moveset[selection]
            pokeAttacker.mimic_on = moveAddress
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
            print(pokeAttacker.poke["name"]+" has copied "+pokeAttacker.moveset[moveAddress]["name"]+"!")
        else:
            print("The move failed!")
            pokeDefender.lastDamage[0] = 0

    elif cats[0] == "mirrormove":
        # this should only occur if metronome calls mirror move or mirror move calls mirror move. it should fail in both cases
        print("Mirror Move failed!")
        pokeDefender.lastDamage[0] = 0
        pokeDefender.mirrored = "mirror move"

    elif cats[0] == "rage":
        # the first time rage is used, pokemon.raging will be -1. In this case, we do a simple accuracy check and if anything goes wrong, nothing interesting happens
        if pokeAttacker.raging == -1:
            if accResult != "success":
                print(pokeAttacker.poke["name"] + " missed!")
                pokeDefender.lastDamage[0] = 0
            else:
                # rage begins! the rampage is on!
                pokeAttacker.raging = moveAddress
                print("The rampage begins!")
                enemyChange = pokeAttacker.statUpdate("mod:"+"attack"+":"+"1"+":self:"+pokeDefender.status,attBadge)
                if enemyChange == "speed":
                    pokeDefender.activeStats[4] = max(math.floor(pokeDefender.activeStats[4]/4),1)
                    pokeDefender.setStats()
                elif enemyChange == "attack":
                    pokeDefender.activeStats[1] = max(math.floor(pokeDefender.activeStats[1]/2),1)
                    pokeDefender.setStats()

                return processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
        else:
            # this is the class where rage is already ongoing. The move may hit, in which case it does damage and rage builds. If the move misses due to accuracy/evasion, there is a weird glitch where the accuracy of the move gets fucked up
            if accResult == "success":
                print("The rampage continues!")
                enemyChange = pokeAttacker.statUpdate("mod:"+"attack"+":"+"1"+":self:"+pokeDefender.status,attBadge)
                if enemyChange == "speed":
                    pokeDefender.activeStats[4] = max(math.floor(pokeDefender.activeStats[4]/4),1)
                    pokeDefender.setStats()
                elif enemyChange == "attack":
                    pokeDefender.activeStats[1] = max(math.floor(pokeDefender.activeStats[1]/2),1)
                    pokeDefender.setStats()

                return processStandardDamage(pokeAttacker,pokeDefender,moveAddress,typeInfo)
            else:
                if accResult == "gen1miss_rage":
                    print("Rage missed!")
                else:
                    print("Rage missed! "+pokeAttacker.poke["name"] + " is wobbling around!")
                    pokeAttacker.rageAcc = "lowered"
        return ""

    elif cats[0] == "transform":
        if accResult!="success":
            pokeDefender.lastDamage[0] = 0
            pokeDefender.lastDamage[1] =  pokeAttacker.moveset[moveAddress]["type"].casefold()
            print("Transformed failed!")
        else:
            print(pokeAttacker.poke["name"] + " is transforming into " + pokeDefender.poke["name"] + "!")
            pokeDefender.mirrorable = pokeAttacker.moveset[moveAddress]["name"]
            # transform copies the types, moves, current stats and statmods, and sets all move PP to 5
            # if switched out, the pokemon goes back to its original state.
            # transformBuffer creates a buffer of current PP, moves, types, stats and so on.
            # when the poke faints or switches out, this data is pushed back
            pokeAttacker.transformBuffer()
            # now we change types, stats, moves and PP
            pokeAttacker.types = pokeDefender.types
            pokeAttacker.initMoves = pokeDefender.initMoves
            pokeAttacker.setMoveset(pokeAttacker.initMoves)
            pokeAttacker.PP = []
            for i in range(len(pokeAttacker.initMoves)):
                pokeAttacker.PP.append(5)
            pokeAttacker.modifiers = pokeDefender.modifiers
            # the HP stat doesn't change
            HP = pokeAttacker.activeStats[0]
            pokeAttacker.activeStats = pokeDefender.activeStats[:]
            pokeAttacker.activeStats[0] = HP
            pokeAttacker.setStats()
            pokeAttacker.transformed = True

    if cats[0] == "substitute":
        # substitute only works if the pokemon has more than 25% of its max HP
        if pokeAttackker.subbing:
            print(pokeAttacker.poke["name"]+" already has a substitute out!")
            return ""
        subFloor = math.floor(pokeAttacker.maxHP/4)
        if pokeAttacker.HP < subFloor:
            print(pokeAttacker.poke["name"]+" does not have enough HP to form a substitute!")
            return ""
        # in gen 1, the pokemon just dies if it has exactly 25% HP
        elif pokeAttacker.HP == subFloor:
            print(pokeAttacker.poke["neme"]+" fainted forming a substitute!")
            pokeAttacker.activeStats[0] = 0
            pokeAttacker.setStats()
            return "attacker:faint"
            
        else:
            pokeAttacker.subbing = True
            pokeAttacker.subHP = subFloor+1
            pokeAttacker.activeStats[0] = pokeAttacker.HP-subFloor
            pokeAttacker.setStats()
            print(pokeAttacker.poke["name"]+" has put up a substitute!")

    return ""
