
def parseItem(turnChar,offturnChar,itemAddress):
    # turn character is who's using the item. their pokemon out is pokeAttacker
    # offturn character is whoever is not using the item. 
    # This only matters because of some weird weird shit with counter and stat changes
    
    pokeAttacker = turnChar.team[0]
    itemUsed = turnChar.items[itemAddress].casefold()
    pokeDefender = offturnChar.team[0]

    # items are strings, which can be one of 27 things. we just cover them in categories
    # there are 6 items that JUST heal
    healItems = ["potion","super potion","hyper potion","max potion","fresh water","lemonade"]
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
            healAmt = pokeAttacker.maxHP-pokeAttacker.activeStats[0]
        toHeal = min(healAmt,pokeAttacker.maxHP-healAmt)
        pokeAttacker.activeStats[0] = pokeAttacker.activeStats[0]+toHeal
        pokeAttacker.setStats()
        print(pokeAttacker.poke["name"]+" healed for "+str(toHeal)+" HP!")
        return ""

    # there are 5 items that apply one-unit modifiers.
    battleItems = ["x attack","x defend","x special","x speed","dire hit"]
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
    if itemUsed == "x accuracy":
        pokeAttacker.xAcc = True
        print(pokeAttacker.poke["name"]+" can no longer miss!")

    # these items heal statuses
    statusItems = ["antidote","burn heal","ice heal","awakening","paralyz heal","full heal"]
    if itemUsed == "antidote":
        if pokeAttacker.status != "poison":
            print("The antidote had no effect!")
        else:
            pokeAttacker.status = "none"
            # i don't know if this also resets N for toxic. We simply must find out!
    elif itemUsed == "burn heal":
        curable = "burn"
    elif itemUsed == "ice heal":
        curable = "freeze"
    elif itemUsed = "awakening":
        curable = "sleep"

    revives = ["revive","max revive"]
    

    print("Item time!")
    return
