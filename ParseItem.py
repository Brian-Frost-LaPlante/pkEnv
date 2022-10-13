import math

def parseItem(turnChar,offturnChar,itemAddress):
    # turn character is who's using the item. their pokemon out is pokeAttacker
    # offturn character is whoever is not using the item. 
    # This only matters because of some weird weird shit with counter and stat changes
    
    pokeAttacker = turnChar.team[0]
    itemUsed = turnChar.items[itemAddress].casefold()
    pokeDefender = offturnChar.team[0]

    healItems = ["potion","super potion","hyper potion","max potion","fresh water","soda pop","lemonade"]
    battleItems = ["x attack","x defend","x special","x speed","dire hit"]
    statusItems = ["antidote","burn heal","ice heal","awakening","paralyz heal","full heal","full restore"]
    revives = ["revive","max revive"]
    ethers = ['ether','max ether','elixer','max elixer']
    misc = ["x accuracy","guard spec","poke flute"]
    
    
    # X items can only be used on pokemon who are currently out (pokeAttacker). Others can only be used on ANY pokemon
    # pokeUsed is the pokemon this is used on
    
    if (itemUsed not in battleItems) and (itemUsed not in misc):
        # determine which poke was used
        goodAnswer = False
        while not goodAnswer:
            for i in range(len(turnChar.team)):
                print("["+str(i+1)+"] " +turnChar.team[i].poke["name"]+":\t\t"+turnChar.team[i].status)
                print("Pick a Pokemon to use the item on: ")
                option = input()
                if not option.isdigit():
                    print("Please input a valid answer.")
                elif (int(option)-1) not in range(len(turnChar.team)):
                    print("Please input a valid answer.")
                else:
                    PPAnswer = True
                    index = int(option)-1
                    goodAnswer = True   
                    pokeUsed = turnChar.team[index]
                    isOut = (index==0)
    else:
        pokeUsed = pokeAttacker
        isOut = True
    
    # items are strings, which can be one of 27 things. we just cover them in categories
    # there are 6 items that JUST heal
    if itemUsed in healItems:
        # we heal for some amount called healAmt
        if itemUsed == "potion":
            healAmt = 20
        elif itemUsed in ["super potion","fresh water"]:
            healAmt = 50
        elif itemUsed == "soda pop":
            healAmt = 60
        elif itemUsed == "lemonade":
            healAmt = 80
        elif itemUsed == "hyper potion":
            healAmt = 200
        elif itemUsed == "max potion":
            healAmt = pokeUsed.maxHP-pokeUsed.activeStats[0]
        toHeal = min(healAmt,pokeUsed.maxHP-healAmt)
        pokeUsed.activeStats[0] = pokeAttacker.activeStats[0]+toHeal
        pokeUsed.setStats()
        print(pokeUsed.poke["name"]+" healed for "+str(toHeal)+" HP!")
        return ""

    # there are 5 items that apply one-unit modifiers.
    if itemUsed in battleItems:
        # we up some stat statToUp
        if itemUsed == "x attack":
            statToUp = "attack"
        elif itemUsed == "x defend":
            statToUp = "defend"
        elif itemUsed == "x special":
            statToUp = "special"
        elif itemUsed == "x speed":
            statToUp = "speed"
        elif itemUsed == "dire hit":
            statToUp = "crit:"
        # now raise this stat by one unit. Recall that when this happens, we have to worry about the possibility of reapplying enemy status debuffs.
        enemyChange = pokeAttacker.statUpdate("mod:"+statToUp+":+1:self:"+pokeDefender.status,turnChar.badges)
        if enemyChange == "speed":
            pokeDefender.activeStats[4] = max(math.floor(pokeDefender.activeStats[4]/4),1)
            pokeDefender.setStats()
        elif enemyChange == "attack":
            pokeDefender.activeStats[1] = max(math.floor(pokeDefender.activeStats[1]/2),1)
        pokeDefender.setStats()
        return ""

    # x accuracy is different from other x items -- it just makes pokemon ignore all acc checks.
    # c acc and guard spec are the "misc" items from above that only affect the poke currently out.
    if itemUsed == "x accuracy":
        pokeAttacker.xAcc = True
        print(pokeAttacker.poke["name"]+" can no longer miss!")

    if itemUsed == "guard spec":
        if "mist" in pokeAttacker.wall:
            print("The Guard Spec had no effect!")
        else:
            pokeAttacker.wall.append("mist")
            print(pokeAttacker.poke["name"]+" has put up mist!")

    # these items heal statuses
    if itemUsed == "antidote":
        if pokeUsed.status != "poison":
            print("The Antidote had no effect!")
        else:
            pokeUsed.status = "none"
            print("The Pokemon is no longer poisoned!")
            if isOut:
                enemyChange = pokeAttacker.statUpdate("item",turnChar.badges)
            # i don't know if this also resets N for toxic. We simply must find out!
    if itemUsed == "burn heal":
        if pokeUsed.status != "burn":
            print("The Burn Heal had no effect!")
        else:
            pokeUsed.status = "none"
            print("The Pokemon is no longer burning!")
            if isOut:
                enemyChange = pokeAttacker.statUpdate("item",turnChar.badges)
                # i don't know if this also resets N for toxic. We simply must find out!
    if itemUsed == "ice heal":
        if pokeUsed.status != "freeze":
            print("The Ice Heal had no effect!")
        else:
            print("The Pokemon thawed out!")
            pokeUsed.status = "none"
            if isOut:
                enemyChange = pokeAttacker.statUpdate("item",turnChar.badges)
    if itemUsed == "awakening":
        if pokeUsed.status != "sleep":
            print("The Awakening had no effect!")
            goodAnswer = False
        else:
            print("The Pokemon woke up!")
            pokeUsed.status = "none"
            if isOut:
                enemyChange = pokeAttacker.statUpdate("item",turnChar.badges)
    
    if itemUsed == "poke flute":
        if  (pokeAttacker.status != "sleep") and (pokeDefender.status != "sleep"):
            print("Nothing happened!")
        else:
            print("Everyone woke up!")
            if pokeAttacker.status == "sleep":
                pokeAttacker.status = "none"
            if pokeDefender.status == "sleep":
                pokeDefender.status = "none"
        return ""
    
    if itemUsed == "paralyz heal":
        if pokeUsed.status != "paralyze":
            print("The Paralyz Heal had no effect!")
        else:
            pokeUsed.status = "none"
            print("The Pokemon is no longer paralyzed!")
            if isOut:
                enemyChange = pokeAttacker.statUpdate("item",turnChar.badges)
    if itemUsed == "full heal":
        if pokeUsed.status == "none":
            print("The Full Heal had no effect!")
        else:
            print("The Pokemon's status condition has been healed!")
            if isOut:
                enemyChange = pokeAttacker.statUpdate("item",turnChar.badges)
            pokeUsed.status = "none"
    if itemUsed == "full restore":
        if (pokeUsed.status == "none") and (pokeUsed.HP == pokeUsed.maxHP):
            print("The Full Restore had no effect!")
        else:
            print("The Pokemon's status condition has been healed and its health has been restored to maximum!")
            if (isOut):
                if pokeAttacker.HP == pokeAttacker.maxHP:
                    enemyChange = pokeAttacker.statUpdate("item",turnChar.badges)
            pokeUsed.status = "none"
            pokeUsed.activeStats[0] = pokeUsed.maxHP
            pokeUsed.setStats()

    if itemUsed in revives:
        if pokeUsed.status != "faint":
            print("The item had no effect!!")
        else:
            pokeUsed.status = ""
            if itemUsed == "max revive":
                pokeUsed.activeStats[0] = maxHP
                pokeUsed.setStats()
            elif itemUsed == "revive":
                pokeUsed.activeStats[0] = math.floor(maxHP/2)
                pokeUsed.setStats()

    if itemUsed in ethers:
        if itemUsed == "max elixer":
            pokeUsed.PP  = pokeUsed.maxPP
            print("All moves have been restored to max PP!")
        elif itemUsed == "elixer":
            for i in range(len(pokeUsed.maxPP)):
                pokeUsed.PP = min(pokeUsed.PP[i]+10,pokeUsed.maxPP[i])
            print("All moves have had some PP restored!")
        else:
            PPAnswer = False
            while not PPAnswer:
                for i in range(len(pokeUsed.moveset)):
                    print("["+str(i+1)+"] " +pokeUsed.moveset[i]["name"]+":\t\t"+str(pokeUsed.PP[i])+"/"+str(pokeUsed.maxPP[i]))
                print("Pick a move: ")
                option = input()
                if not option.isdigit():
                    print("Please input a valid answer.")
                elif int(option) not in (range(len(pokeUsed.moveSet))+1):
                    print("Please input a valid answer.")
                else:
                    PPAnswer = True
                    index = int(option)-1
            if itemUsed == "max ether":
                pokeUsed.PP[i] = pokeUsed.maxPP[i]
                print("The Pokemon's move has had its PP entirely restored!")
            if itemUsed == "ether":
                pokeUsed.PP[i] = min(pokeUsed.maxPP[i],pokeUsed.PP[i]+10)
                print("The Pokemon's move has had some of its PP restored!")

    return
