from logging import BufferingFormatter
import random
import math
from AccuracyCheck import accuracyCheck
from ParseAttack import parseAttack
from Stage2Mult import stage2Mult
import tkinter
from tkinter import *
from tkinter.messagebox import showerror
from PIL import Image


class Battle:

    def options(self,trainer):
        team = trainer.team
        moveset = team[0].moveset
        pp = team[0].PP
        availableMoves = []
        moveAddresses = []
        movePP = []
        for i in range(len(pp)):
            if pp[i]>0:
                availableMoves.append(moveset[i])
                moveAddresses.append(i)
                movePP.append(pp[i])
        availableSwaps = []
        swapAddresses = []
        for p in range(len(team)-1):
            if team[p+1].HP>0:
                availableSwaps.append(team[p+1])
                swapAddresses.append(p+1)
        availableActions = {
            "pokeOut":team[0],
            "moves":availableMoves,
            "pp":movePP,
            "swaps":availableSwaps,
            "swapAddresses":swapAddresses,
            "items":trainer.items
        }
        return availableActions

    def useItem(self,trainer,itemAddress):
        item = trainer.items[itemAddress]
        return

    def disableCheck(self,pokeChar):
        if (pokeChar.disable != ""):
            pokeChar.turncount["disable"] = pokeChar.turncount["disable"]-1
            if pokeChar.turncount["disable"] == 0:
                print(pokeChar.poke["name"]+"'s "+pokeChar.disable+" is no longer disabled!")
                pokeChar.disable = ""

    def metronome(self,pokeAttacker,pokeDefender,moveAddress,attacker,defender):
        # metronome will do something strange -- it will pick a random move (other than metronome) and then execute that move. To use the parse attack function as written, we first switch out the move in its own moveset, then change it back to metronome after the attack is carried out.

        # if a twoturn move was used by metronome
        if pokeAttacker.buffer != "":
            for i in range(len(self.moveInfo["moves"])):
                if self.moveInfo["moves"][i]["name"].casefold()=="metronome":
                    metronomeMove = self.moveInfo["moves"][i]
            moveToUse = pokeAttacker.buffer
            print(pokeAttacker.poke["name"]+ " is attacking with "+ moveToUse["name"]+"!")
            pokeAttacker.moveset[moveAddress] = moveToUse #briefly make the move different
            result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
            pokeAttacker.moveset[moveAddress] = metronomeMove
            pokeAttacker.buffer = ""
            return result

        moveList = []
        for i in range(len(self.moveInfo["moves"])):
            if self.moveInfo["moves"][i]["name"]!="Metronome":
                moveList.append(self.moveInfo["moves"][i])
            else:
                metronomeMove = self.moveInfo["moves"][i]
        moveToUse = random.sample(moveList,1)[0]
        pokeAttacker.moveset[moveAddress] = moveToUse #briefly make the move different
        print("Metronome landed on "+moveToUse["name"]+"!")
        # must handle counter and twoturn moves differently
        if moveToUse["name"] == "Counter":
            print("The move did nothing!")
            return ""
        elif moveToUse["category"] == "twoturn":
            pokeAttacker.buffer = moveToUse
            result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
            pokeAttacker.moveset[moveAddress] = metronomeMove
        else:
            result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
            # now bring metronome back
            pokeAttacker.moveset[moveAddress] = metronomeMove
            if result not in ["fail:confuse","fail:paralyze"]:
                pokeDefender.mirrorable = "metronome"
            return result

    def mirrormove(self,pokeAttacker,pokeDefender,moveAddress,attacker,defender):
        # mirror move will do something strange -- it will try to use  and then execute that move. To use the parse attack function as written, we first switch out the move in its own moveset, then change it back to metronome after the attack is carried out.
 
        # if a twoturn move was used by mirror move
        if pokeAttacker.buffer != "":
            for i in range(len(self.moveInfo["moves"])):
                if self.moveInfo["moves"][i]["name"].casefold()=="mirror move":
                    mirrormoveMove = self.moveInfo["moves"][i]
            moveToUse = pokeAttacker.buffer
            print(pokeAttacker.poke["name"]+ " is attacking with "+ moveToUse["name"]+"!")
            pokeAttacker.moveset[moveAddress] = moveToUse #briefly make the move different
            result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
            pokeAttacker.moveset[moveAddress] = mirrormoveMove
            pokeAttacker.buffer = ""
            return result       
        
        for i in range(len(self.moveInfo["moves"])):
            if self.moveInfo["moves"][i]["name"].casefold()==pokeAttacker.mirrorable.casefold():
                moveToUse = self.moveInfo["moves"][i]
            if self.moveInfo["moves"][i]["name"].casefold()=="mirror move":
                mirrormoveMove = self.moveInfo["moves"][i]
        if pokeAttacker.mirrorable == "":
            moveToUse = mirrormoveMove
        pokeAttacker.moveset[moveAddress] = moveToUse #briefly make the move different
        
        if moveToUse["name"].casefold() == "metronome":
            result = self.metronome(pokeAttacker,pokeDefender,moveAddress,attacker,defender)
            pokeAttacker.moveset[moveAddress] = mirrormoveMove
            return result

        elif moveToUse["category"] == "twoturn":
            pokeAttacker.buffer = moveToUse
            result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
            pokeAttacker.moveset[moveAddress] = mirrormoveMove
            return result

        if moveToUse["name"].casefold() != "mirror move":
            print(pokeAttacker.poke["name"] + " is trying to mirror "+moveToUse["name"]+"!")
        
        result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
        # now bring mirror move back, so long as charging is over
        pokeAttacker.moveset[moveAddress] = mirrormoveMove
        if result not in ["fail:confuse","fail:paralyze"]:
            pokeDefender.mirrorable = "mirror move"

 
        return result



    def statusCheck(self,character,pokeChar,pokeNot):
        loss = False
        toSwitch = False
        # burn, poison and toxic all do damage based on the toxic counter, which is bizarre but true!
        if pokeChar.status == "burn":
            burnDamage = min(pokeChar.HP,max(math.ceil(pokeChar.maxHP/16),pokeChar.turncount["toxic"]*math.ceil(pokeChar.maxHP/16)))
            pokeChar.activeStats[0] = pokeChar.HP-burnDamage
            pokeChar.setStats()
            print(pokeChar.poke["name"] + " took "+str(burnDamage)+ " damage from its burn!")
        elif pokeChar.status == "poison":
            poisonDamage = min(pokeChar.HP,max(math.ceil(pokeChar.maxHP/16),pokeChar.turncount["toxic"]*math.ceil(pokeChar.maxHP/16)))
            pokeChar.activeStats[0] = pokeChar.HP-poisonDamage
            pokeChar.setStats()
            print(pokeChar.poke["name"] + " took "+str(poisonDamage)+ " damage from poison!")
        if (pokeChar.HP!=0) and pokeChar.leechSeed:
            leechDamage = min(pokeChar.HP,max(math.ceil(pokeChar.maxHP/16),pokeChar.turncount["toxic"]*math.ceil(pokeChar.maxHP/16)))
            pokeChar.activeStats[0] = pokeChar.HP-leechDamage
            pokeChar.setStats()
            print(pokeChar.poke["name"] + " took "+str(leechDamage)+ " damage from Leech Seed!")
            leechHeal = min(leechDamage,pokeNot.maxHP-pokeNot.HP)
            if leechHeal!=0:
                pokeNot.activeStats[0] = pokeNot.HP+leechHeal
                pokeNot.setStats()
                print(pokeNot.poke["name"] + " healed "+str(leechHeal)+ " from Leech Seed!")
            
        if pokeChar.HP == 0:
            pokeChar.status = "faint"
            print(pokeChar.poke["name"]+" has fainted!")
            options = []
            for i in range(len(character.team)):
                if character.team[i].status != "faint":
                    options.append(i)
            if options == []:
                print(character.name + " has no Pokemon left to battle.")
                print(character.name + " has lost the battle!")
                loss = True
            else:
                toSwitch = True

        # the pokeCharmon hasn't fainted
        if pokeChar.turncount["toxic"]!=0:
            pokeChar.turncount["toxic"] = pokeChar.turncount["toxic"]+1        
        return [loss,toSwitch]


    def attackPhase(self,optionPlayer,optionEnemy):
        # a strange turn will occur if one of the characters is recharging.
        # bools for which player is attacking.
        # handled differently if one or both attack.
        playerIs = optionPlayer[0]=="attack"
        enemyIs = optionEnemy[0]=="attack"
        firstToSwitch = False
        secondToSwitch = False
        # if only one player tried an attack, the process is easier
        if not (playerIs and enemyIs):
            if playerIs:
                # only player is attacking
                attacker=self.player
                moveAddress = optionPlayer[1]
                defender=self.enemy
                first = "player"
                second = "enemy"
            else:
                # only enemy is attacking
                attacker=self.enemy
                moveAddress = optionEnemy[1]
                defender=self.player
                first = "enemy"
                second = "player"
            pokeAttacker=attacker.team[0]
            pokeDefender=defender.team[0]
            # check if attack will land
            if pokeAttacker.status not in ["sleep","freeze"]:
                print(pokeAttacker.poke["name"]+ " is attacking "+ pokeDefender.poke["name"]+ " with " + pokeAttacker.moveset[moveAddress]["name"])
            if pokeAttacker.moveset[moveAddress]["name"] not in ["Mirror Move","Metronome"]:
                result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
            elif pokeAttacker.moveset[moveAddress]["name"] == "Metronome":
                result = self.metronome(pokeAttacker,pokeDefender,moveAddress,attacker,defender)
            elif pokeAttacker.moveset[moveAddress]["name"] == "Mirror Move":
                result = self.mirrormove(pokeAttacker,pokeDefender,moveAddress,attacker,defender)
            #handle the case where either player's pokemon has fainted
            [firstToSwitch,secondToSwitch,lossAttacker,lossDefender]=self.checkResult(result,attacker,defender)
            if lossAttacker:
                if lossDefender:
                    return "loss:both"
                else:
                    return "loss:"+first
            elif lossDefender:
                return "loss:"+second

            # poison and burn damage apply if neither player's pokemon fainted, take status damage and check again
            if not (firstToSwitch or secondToSwitch):
                [lossAttacker,firstToSwitch] = self.statusCheck(attacker,pokeAttacker,pokeDefender)
                if lossAttacker:
                    return "loss:"+first
            # this is the case where only one pokemon attacked, which means the defender has swapped/used an item. 
            # This means they will take status damage at the end of the turn, i.e. here, so long as nobody fainted
            if not (firstToSwitch or secondToSwitch):
                [lossDefender,secondToSwitch] = self.statusCheck(defender,pokeDefender,pokeAttacker)
                if lossDefender:
                    return "loss:"+second            

        else:
            # this is the case where both players attacked! We need to 
            # 1) determine whose move goes first by checking priority and speed. In gen 1 there are only two priority moves:
            # Quick Attack, which goes first, and Counter, which goes second. 
            # 2) check if the first move goes through
            # 3) if yes, determine the effect of the first move
            # 4) check if the second move goes through, which includes the possibility that either pokemon has died
            #    or that a status (wrap, sleep, etc.) has been incurred
            # 5) if yes, determine the effect of the second move
            firstStatusChecked = False
            playerMove = self.player.team[0].moveset[optionPlayer[1]]
            enemyMove  = self.enemy.team[0].moveset[optionPlayer[1]]
            prio = [0,0]
            if (playerMove["name"] == "Quick Attack"):
                prio[0] = 1
            if (enemyMove["name"] == "Quick Attack"):
                prio[1] = 1
            if (playerMove["name"] == "Counter"):
                prio[0] = -1
            if (enemyMove["name"] == "Counter"):
                prio[1] = -1
            if prio[0]>prio[1]:
                first="player"
            elif prio[1]>prio[0]:
                first="enemy"
            else:
                # check speed if there is a priority tie
                # implement speed stat stages and paralysis here
                playerSpeed = self.player.team[0].speed
                enemySpeed = self.enemy.team[0].speed
                
                if playerSpeed == enemySpeed:
                    # speed tie case. coin toss
                    speedRoll = random.randint(0,1)
                    if speedRoll==0:
                        first = "player"
                    else:
                        first = "enemy"
                elif playerSpeed>enemySpeed:
                    first="player"
                else:
                    first="enemy"
            # now we know who went first, so we have to process the first attack
            if first == "player":
                second = "enemy"
                # player is attacking
                attacker=self.player
                moveAddress = optionPlayer[1]
                defender=self.enemy
            else:
                second = "player"
                # enemy is attacking
                attacker=self.enemy
                moveAddress = optionEnemy[1]
                defender=self.player
            pokeAttacker=attacker.team[0]
            pokeDefender=defender.team[0]
            if pokeAttacker.status not in ["sleep","freeze"]:
                print(pokeAttacker.poke["name"]+ " is attacking "+ pokeDefender.poke["name"]+ " with " + pokeAttacker.moveset[moveAddress]["name"])

            if (playerMove["name"] == "Counter") and (enemyMove["name"] == "Counter"):
                print("Counter failed!")
                pokeAttacker.lastDamage[0] = 0
                result = ""  
            elif pokeAttacker.moveset[moveAddress]["name"] not in ["Mirror Move","Metronome"]:
                result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
            elif pokeAttacker.moveset[moveAddress]["name"] == "Metronome":
                result = self.metronome(pokeAttacker,pokeDefender,moveAddress,attacker,defender)
            elif pokeAttacker.moveset[moveAddress]["name"] == "Mirror Move":
                result = self.mirrormove(pokeAttacker,pokeDefender,moveAddress,attacker,defender)

# check for possible losses or deaths
            [firstToSwitch,secondToSwitch,lossAttacker,lossDefender]=self.checkResult(result,attacker,defender)
            if lossAttacker:
                if lossDefender:
                    return "loss:both"
                else:
                    return "loss:"+first
            elif lossDefender:
                return "loss:"+second
            # poison and burn damage apply if neither player's pokemon fainted, take status damage and check again
            if (not (firstToSwitch or secondToSwitch)) and (pokeAttacker.status in ["poison","burn"]):
                [lossAttacker,firstToSwitch] = self.statusCheck(attacker,pokeAttacker,pokeDefender)
                firstStatusChecked = True # if not, we have to check at the end of the turn
                if lossAttacker:
                    return "loss:"+first

            # now the first attack is over. many things can happen as a result of the first attack.
            # the defender may have died, the attack may have been disabled, they might have been statused
            # the attacker also may have died due to recoil, confusion, poison, burn or explosion/selfdestruct
            
            # this is the case that the defender is still alive after the turn
            if result not in ["defender:faint","both:faint","unable"]:
                if first == "player":
                    # enemy is attacking now
                    attacker=self.enemy
                    moveAddress = optionEnemy[1]
                    defender=self.player
                else:
                    # player is attacking
                    attacker=self.player
                    moveAddress = optionPlayer[1]
                    defender=self.enemy
                pokeAttacker=attacker.team[0]
                pokeDefender=defender.team[0]
                if not pokeAttacker.flinching:
                    if pokeAttacker.status not in ["sleep","freeze"]:
                        print(pokeAttacker.poke["name"]+ " is attacking "+ pokeDefender.poke["name"]+ " with " + pokeAttacker.moveset[moveAddress]["name"])
                    if (playerMove["name"] == "Counter") and (enemyMove["name"] == "Counter"):
                        print("Counter failed!")
                        pokeAttacker.lastDamage[0] = 0
                        result = ""  
                    elif pokeAttacker.moveset[moveAddress]["name"] not in ["Mirror Move", "Metronome"]:
                        result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,self.moveInfo,attacker.badges,defender.badges)
                    elif pokeAttacker.moveset[moveAddress]["name"] == "Metronome":
                        result = self.metronome(pokeAttacker,pokeDefender,moveAddress,attacker,defender)
                    elif pokeAttacker.moveset[moveAddress]["name"] == "Mirror Move":
                        result = self.mirrormove(pokeAttacker,pokeDefender,moveAddress,attacker,defender)

                    [firstToSwitch,secondToSwitch,lossAttacker,lossDefender]=self.checkResult(result,attacker,defender)
                    if lossAttacker:
                        if lossDefender:
                            return "loss:both"
                        else:
                            return "loss:"+second
                    elif lossDefender:
                        return "loss:first"
                else:
                    print(pokeAttacker.poke["name"] + " flinched!")
                    pokeAttacker.flinching=False

                # status gets checked here so long as the pokemon didn't faint or knock out its opponent
                if not (secondToSwitch or (result == "defender:faint")):
                    if result not in ["sleep","freeze","flinch"]:
                        self.disableCheck(pokeAttacker)
                    [lossAttacker,secondToSwitch] = self.statusCheck(attacker,pokeAttacker,pokeDefender)
                    if lossAttacker:
                        return "loss:"+second
                if not firstStatusChecked:
                    [lossDefender,firstToSwitch] = self.statusCheck(defender,pokeDefender,pokeAttacker)
                    if lossDefender:
                        return "loss:"+first                    

            # one niche possibility is that the first pokemon used Haze while the second was asleep/frozen. In this case, the second pokemon should be unable to attack. in this case, result is "unable", and we skip to status check
        if result == "unable":
            if first == "player":
                # enemy is attacking now
                attacker=self.enemy
                moveAddress = optionEnemy[1]
                defender=self.player
            else:
                # player is attacking
                attacker=self.player
                moveAddress = optionPlayer[1]
                defender=self.enemy

            [lossAttacker,secondToSwitch] = self.statusCheck(attacker,pokeAttacker,pokeDefender)
            if lossAttacker:
                return "loss:"+second
            if not firstStatusChecked:
                [lossDefender,firstToSwitch] = self.statusCheck(defender,pokeDefender,pokeAttacker)
                if lossDefender:
                    return "loss:"+first       



        if firstToSwitch:
            if first == "player":
                print(self.player.name+" needs to swap in a Pokemon.")
                self.swapIn(self.player,self.enemy)
            else:
                print(self.enemy.name+" needs to swap in a Pokemon.")
                self.swapIn(self.enemy,self.player)
        if secondToSwitch:
            if second == "player":
                print(self.player.name+" needs to swap in a Pokemon.")
                self.swapIn(self.player,self.enemy)
            else:
                print(self.enemy.name+" needs to swap in a Pokemon.")
                self.swapIn(self.enemy,self.player)
        return ""

    def checkResult(self,result,attacker,defender):
        firstToSwitch = False
        secondToSwitch = False
        lossDefender = False
        lossAttacker = False
        if result == "defender:faint":
            defender.team[0].status = "faint"
            options = []
            for i in range(len(defender.team)):
                if defender.team[i].status != "faint":
                    options.append(i)
            if options == []:
                print(defender.name + " has no Pokemon left to battle.")
                print(defender.name + " has lost the battle!")
                lossDefender = True
            else:
                secondToSwitch = True
        if result == "attacker:faint":
            attacker.team[0].status = "faint"
            options = []
            for i in range(len(attacker.team)):
                if attacker.team[i].status != "faint":
                    options.append(i)
            if options == []:
                print(attacker.name + " has no Pokemon left to battle.")
                print(attacker.name + " has lost the battle!")
                lossAttacker = True
            else:
                firstToSwitch = True
        if result == "both:faint":
            defender.team[0].status = "faint"
            attacker.team[0].status = "faint"
            options = []
            for i in range(len(defender.team)):
                if defender.team[i].status != "faint":
                    options.append(i)
            if options == []:
                print(defender.name + " has no Pokemon left to battle.")
                lossDefender = True
            else:
                secondToSwitch = True
            options = []
            for i in range(len(attacker.team)):
                if attacker.team[i].status != "faint":
                    options.append(i)
            if options == []:
                print(attacker.name + " has no Pokemon left to battle.")
                lossAttacker = True
            else:
                firstToSwitch = True
            if lossAttacker:
                if lossDefender:
                    # a draw
                    print("Both players have lost the battle!")
                else:
                    print(attacker.name+" has lost the battle!")

            elif lossDefender:
                print(defender.name+" has lost the battle!")
        return [firstToSwitch,secondToSwitch,lossAttacker,lossDefender]

    def swapIn(self,character,opposite):
        options = []
        for i in range(len(character.team)):
            if character.team[i].status != "faint":
                options.append(i)
        for i in range(len(options)):
            print("["+str(options[i])+"]     " + character.team[options[i]].poke["name"]+" ["+character.team[options[i]].status+"]   Level "+str(character.team[options[i]].level))
        print("Which pokemon do you want to switch to?")
        badAnswer = True
        while badAnswer:
            option = input()
            if option.isdigit():
                option = int(option)
                if option in options:
                    badAnswer = False
                else:
                    print("That isn't a valid answer!")
            else:
                print("That isn't a valid answer!")
        
        print(character.name+" is sending in "+character.team[option].poke["name"])
        character.team[0].statReset()
        character.team[0].mirrored=""
        opposite.team[0].mirrored=""
        character.team[0].bideDamage = 0
        character.team[0].turncount["bide"] = -1

        character.team[0], character.team[option] = character.team[option], character.team[0]
        character.team[0].statUpdate("send",character.badges)
        return ""

    def pickOptions(self,character):
        validChoice = False
        if (character.team[0].charging == -1) and (not character.team[0].recharging):
            while not validChoice:
                print(character.name+"'s Options")
                print("[1] ATTACK     [2] ITEM     [3] SWAP")
                macroOption = input()
                if macroOption not in ['1','2','3']:
                    print("That is not a valid choice!")
                elif macroOption == '1':
                    # if the pokemon is using bide, we continue using bide
                    attacks = character.team[0].moveset

                    if character.team[0].turncount["bide"] != -1:
                        for a in range(len(attacks)):
                            if attacks[a]["name"].casefold() == "bide":
                                return ["attack",a]
                    
                    
                    for i in range(len(attacks)):
                        print("["+str(i+1)+"]     "+attacks[i]["name"])
                    option = input()   
                    if option != '0':
                        if (not option.isdigit()):                            
                            print("That is not a valid choice!")
                        elif (int(option)>(len(attacks))) or (int(option)<1):
                            print("That is not a valid choice!")
                        elif attacks[int(option)-1]["name"] == character.team[0].disable:
                            print("That move is disabled!")
                        elif character.team[0].PP[int(option)-1] == 0:
                            print("That move has no PP!")
                        else:
                            return ["attack",int(option)-1]
                    elif macroOption == '2':
                        items = character.items
                        if len(items) == 0:
                            print("You have no items!")
                        else:
                            for i in range(len(items)):
                                print("["+str(i+1)+"]     "+items[i].name)
                            print("Which item do you want to use? (0 to choose another option)")
                            option = input()
                            if (not option.isdigit()):
                                print("That is not a valid choice!")
                            elif (int(option)>(len(items))) or (int(option)<1):
                                print("That is not a valid choice!")
                            elif option != '0':
                                return ["item",int(option)-1]
                    elif macroOption == '3':
                        options = []
                        for i in range(len(character.team)):
                            if character.team[i].status != "faint":
                                options.append(i)
                        if options == []:
                            print("You don't have Pokemon to switch to!")
                            print("")
                        else:
                            for i in range(len(options)):
                                print("["+str(options[i])+"]     " + character.team[options[i]].poke["name"]+" ["+character.team[options[i]].status+"]   Level "+str(character.team[options[i]].level))
                            print("Which pokemon do you want to switch to? (0 to choose another option)")
                            option = input()
                            if (not option.isdigit()):
                                print("That is not a valid choice!")
                            elif int(option) not in options:
                                print("That is not a valid choice!")
                            elif int(option) != 0:
                                return ["swap",int(option)]
        elif character.team[0].charging != -1:
            return ["attack",character.team[0].charging]
        elif character.team[0].recharging:
            return ["recharge"]
        return

    def turn(self,optionPlayer,optionEnemy):
        moveInfo = self.moveInfo
        isOver = ""
        # option is a list of form [move/swap/item,address]
        optionTypePlayer = optionPlayer[0]
        optionTypeEnemy = optionEnemy[0]
        # swap happpens first always
        if optionTypePlayer == "swap":
            print(self.player.name+" is swapping out "+self.player.team[0].poke["name"]+" and is sending in "+self.player.team[optionPlayer[1]].poke["name"])
            self.player.team[0].statReset()
            if self.player.team[0].mimic_on != -1:
                for i in len(moveInfo["moves"]):
                    if moveInfo["moves"][i]["name"] == "Mimic":
                        mimic = moveInfo["moves"][i]
                self.player.team[0].moveset[self.player.team[0].mimic_on] = mimic
                self.player.team[0].mimic_on = -1

            self.player.team[0], self.player.team[optionPlayer[1]] = self.player.team[optionPlayer[1]], self.player.team[0]
            self.player.team[0].statUpdate("send",self.player.badges)
            self.guiUpdate()
        if optionTypeEnemy == "swap":
            print(self.enemy.name+" is swapping out "+self.enemy.team[0].poke["name"]+" and is sending in "+self.enemy.team[optionEnemy[1]].poke["name"])
            self.enemy.team[0].statReset()
            if self.enemy.team[0].mimic_on != -1:
                for i in len(moveInfo["moves"]):
                    if moveInfo["moves"][i]["name"] == "Mimic":
                        mimic = moveInfo["moves"][i]
                self.enemy.team[0].moveset[self.player.team[0].mimic_on] = mimic
                self.enemy.team[0].mimic_on = -1
            self.enemy.team[0], self.enemy.team[optionEnemy[1]] = self.enemy.team[optionEnemy[1]], self.enemy.team[0]
            self.enemy.team[0].statUpdate("send",self.enemy.badges)
            self.guiUpdate()
        # item happens next
        if optionTypePlayer == "item":
            self.useItem(self.player,optionPlayer[1])
            self.guiUpdate()
        if optionTypeEnemy == "item":
            self.useItem(self.enemy,optionEnemy[1])
            self.guiUpdate()
        # attacks happen next
        if optionTypeEnemy == "attack" or optionTypePlayer == "attack":
            isOver = self.attackPhase(optionPlayer,optionEnemy)
            if (optionTypeEnemy == "recharge") and (self.enemy.team[0].recharging>0) and (self.enemy.team[0].HP !=0):
                self.enemy.team[0].recharging = self.enemy.team[0].recharging - 1
                if self.enemy.team[0].recharging == 0:
                    print(self.enemy.team[0].poke["name"]+" is recharging from its Hyper Beam!")
            if (optionTypePlayer == "recharge") and (self.player.team[0].recharging>0) and (self.player.team[0].HP !=0):
                self.player.team[0].recharging = self.player.team[0].recharging - 1
                if self.player.team[0].recharging == 0:
                    print(self.player.team[0].poke["name"]+" is recharging from its Hyper Beam!")
            self.guiUpdate()
        # recharging will occur after the turn if necessary
        else:
            #in this case, we have to check status conditions separatelyif (optionTypeEnemy == "recharge") and (self.enemy.team[0].recharging>0) and (self.enemy.team[0].HP !=0):
            if (optionTypeEnemy == "recharge") and (self.enemy.team[0].recharging>0) and (self.enemy.team[0].HP !=0):
                self.enemy.team[0].recharging = self.enemy.team[0].recharging - 1
                if self.enemy.team[0].recharging == 0:
                    print(self.enemy.team[0].poke["name"]+" is recharging from its Hyper Beam!")
            if (optionTypePlayer == "recharge") and (self.player.team[0].recharging>0) and (self.player.team[0].HP !=0):
                self.player.team[0].recharging = self.player.team[0].recharging - 1
                if self.player.team[0].recharging == 0:
                    print(self.player.team[0].poke["name"]+" is recharging from its Hyper Beam!")
            self.guiUpdate()

            [lossPlayer,playerToSwitch] = self.statusCheck(self.player,self.player.team[0],self.enemy.team[0])
            [lossEnemy,enemyToSwitch] = self.statusCheck(self.enemy,self.enemy.team[0],self.player.team[0])
            self.guiUpdate()
            if lossPlayer:
                if lossEnemy:
                    print("Both players have lost the battle!")
                    return "loss:both"
                else:
                    print(self.player.name+" has lost the battle!")
                    return "loss:player"
            elif lossEnemy:
                print(self.enemy.name+ " has lost the battle!")
                return "loss:enemy"
            
            if playerToSwitch:
                print(self.player.name+" needs to swap in a Pokemon.")
                self.swapIn(self.player,self.enemy)
            if enemyToSwitch:
                print(self.enemy.name+" needs to swap in a Pokemon.")
                self.swapIn(self.enemy,self.player)
        return isOver

    def guiUpdate(self): 
        enemypoke = self.enemy.team[0]
        playerpoke = self.player.team[0]

        self.label_stats_e1.configure(text=enemypoke.poke["name"]+"\nStatus: "+str(enemypoke.status).casefold()+"\nHP: "+str(enemypoke.HP)+"\nPP: "+str(enemypoke.PP),background="white")
        self.label_stats_e2.configure(text="ATT:  "+str(enemypoke.attack)+"\nDEF:  "+str(enemypoke.defense)+"\nSPEC: "+str(enemypoke.special)+"\nSPD:  "+str(enemypoke.speed),background="white", font=('Helvetica 8'), justify= LEFT)


        img_frontsprite = PhotoImage(file="gen1data/sprites/front-"+str(enemypoke.poke["number"])+".png")
        self.label_frontsprite.configure(image=img_frontsprite)
        self.label_frontsprite.image=img_frontsprite

        img_backsprite = PhotoImage(file="gen1data/sprites/back-"+str(playerpoke.poke["number"])+".png")
        self.label_backsprite.configure(image=img_backsprite)
        self.label_backsprite.image = img_backsprite

        self.label_stats_p1.configure(text=playerpoke.poke["name"]+"\nStatus: "+str(playerpoke.status).casefold()+"\nHP: "+str(playerpoke.HP)+"\nPP: "+str(playerpoke.PP),background="white", font=('Helvetica 8'), justify= LEFT)
        self.label_stats_p2.configure(text="ATT:  "+str(playerpoke.attack)+"\nDEF:  "+str(playerpoke.defense)+"\nSPEC: "+str(playerpoke.special)+"\nSPD:  "+str(playerpoke.speed),background="white", font=('Helvetica 8'), justify= LEFT)


    def __init__(self,player,enemy,typeInfo,moveInfo):
        self.typeInfo = typeInfo
        self.moveInfo = moveInfo
        self.player = player
        self.enemy = enemy

        ### GUI INITIALIZATION
        root = Tk()
        root.title('Battle')
        root.geometry('450x200')
        root.configure(background = "white")
        root.resizable(False, False)
        options = {'padx': 5, 'pady': 5}

        # grab enemy pokemon details
        enemypoke = self.enemy.team[0]
        playerpoke = self.player.team[0]

        self.label_stats_e1 = Label(root,text=enemypoke.poke["name"]+"\nStatus: "+str(enemypoke.status).casefold()+"\nHP: "+str(enemypoke.HP)+"\nPP: "+str(enemypoke.PP),background="white", font=('Helvetica 8'), justify= LEFT)
        self.label_stats_e1.grid(column=0,row=0,sticky='W',**options)
        self.label_stats_e2 = Label(root,text="ATT:  "+str(enemypoke.attack)+"\nDEF:  "+str(enemypoke.defense)+"\nSPEC: "+str(enemypoke.special)+"\nSPD:  "+str(enemypoke.speed),background="white", font=('Helvetica 8'), justify= LEFT)
        self.label_stats_e2.grid(column=1,row=0,sticky='W',**options)

        img_frontsprite = PhotoImage(file="gen1data/sprites/front-"+str(enemypoke.poke["number"])+".png")
        self.label_frontsprite = Label(root,image=img_frontsprite,background="white")
        self.label_frontsprite.grid(column=2,row=0,**options)

        self.label_stats_p1 = Label(root,text=playerpoke.poke["name"]+"\nStatus: "+str(playerpoke.status).casefold()+"\nHP: "+str(playerpoke.HP)+"\nPP: "+str(playerpoke.PP),background="white", font=('Helvetica 8'), justify= LEFT)
        self.label_stats_p1.grid(column=1,row=1,sticky='W',**options)
        self.label_stats_p2 = Label(root,text="ATT:  "+str(playerpoke.attack)+"\nDEF:  "+str(playerpoke.defense)+"\nSPEC: "+str(playerpoke.special)+"\nSPD:  "+str(playerpoke.speed),background="white", font=('Helvetica 8'), justify= LEFT)
        self.label_stats_p2.grid(column=2,row=1,sticky='W',**options)
        
        img_backsprite = PhotoImage(file="gen1data/sprites/back-"+str(playerpoke.poke["number"])+".png")
        self.label_backsprite = Label(root,image=img_backsprite,background="white")
        self.label_backsprite.grid(column=0,row=1,**options)
        ###


        print(self.player.name+" sends out "+self.player.team[0].poke["name"]+"!")
        self.player.team[0].statUpdate("send",self.player.badges)
        print(self.enemy.name+" sends out "+self.enemy.team[0].poke["name"]+"!")
        self.enemy.team[0].statUpdate("send",self.enemy.badges)

        isOver = ""
        while isOver == "":
            self.guiUpdate()
            print("")
            optionPlayer = self.pickOptions(self.player)
            print("")
            optionEnemy = self.pickOptions(self.enemy) 
            isOver = self.turn(optionPlayer,optionEnemy)

        input()    
