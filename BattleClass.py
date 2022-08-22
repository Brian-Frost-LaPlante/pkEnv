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

    def statusCheck(self,character,pokeChar):
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
            if pokeAttacker.status != "sleep":
                print(pokeAttacker.poke["name"]+ " is attacking "+ pokeDefender.poke["name"]+ " with " + pokeAttacker.moveset[moveAddress]["name"])
            result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,attacker.badges,defender.badges)
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
                [lossAttacker,firstToSwitch] = self.statusCheck(attacker,pokeAttacker)
                if lossAttacker:
                    return "loss:"+first
            # this is the case where only one pokemon attacked, which means the defender has swapped/used an item. 
            # This means they will take status damage at the end of the turn, i.e. here, so long as nobody fainted
            if not (firstToSwitch or secondToSwitch):
                [lossDefender,secondToSwitch] = self.statusCheck(defender,pokeDefender)
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
            if pokeAttacker.status != "sleep":
                print(pokeAttacker.poke["name"]+ " is attacking "+ pokeDefender.poke["name"]+ " with " + pokeAttacker.moveset[moveAddress]["name"])
            result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,attacker.badges,defender.badges)

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
                [lossAttacker,firstToSwitch] = self.statusCheck(attacker,pokeAttacker)
                firstStatusChecked = True # if not, we have to check at the end of the turn
                if lossAttacker:
                    return "loss:"+first

            # now the first attack is over. many things can happen as a result of the first attack.
            # the defender may have died, the attack may have been disabled, they might have been statused
            # the attacker also may have died due to recoil, confusion, poison, burn or explosion/selfdestruct
            
            # this is the case that the defender is still alive after the turn
            if result not in ["defender:faint","both:faint"]:
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
                    if pokeAttacker.status != "sleep":
                        print(pokeAttacker.poke["name"]+ " is attacking "+ pokeDefender.poke["name"]+ " with " + pokeAttacker.moveset[moveAddress]["name"])
                    result = parseAttack(pokeAttacker,pokeDefender,moveAddress,self.typeInfo,attacker.badges,defender.badges)
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
                    [lossAttacker,secondToSwitch] = self.statusCheck(attacker,pokeAttacker)
                    if lossAttacker:
                        return "loss:"+second
                if not firstStatusChecked:
                    [lossDefender,firstToSwitch] = self.statusCheck(defender,pokeDefender)
                    if lossDefender:
                        return "loss:"+first                    

        if firstToSwitch:
            if first == "player":
                print(self.player.name+" needs to swap in a Pokemon.")
                self.swapIn(self.player)
            else:
                print(self.enemy.name+" needs to swap in a Pokemon.")
                self.swapIn(self.enemy)
        if secondToSwitch:
            if second == "player":
                print(self.player.name+" needs to swap in a Pokemon.")
                self.swapIn(self.player)
            else:
                print(self.enemy.name+" needs to swap in a Pokemon.")
                self.swapIn(self.enemy)
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

    def swapIn(self,character):
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
        character.team[0], character.team[option] = character.team[option], character.team[0]
        character.team[0].statUpdate("send",character.badges)
        return ""

    def pickOptions(self,character):
        validChoice = False
        while not validChoice:
            print(character.name+"'s Options")
            print("[1] ATTACK     [2] ITEM     [3] SWAP")
            macroOption = input()
            if macroOption not in ['1','2','3']:
                print("That is not a valid choice!")
            elif macroOption == '1':
                attacks = character.team[0].moveset
                for i in range(len(attacks)):
                    print("["+str(i+1)+"]     "+attacks[i]["name"])
                option = input()   
                if option != '0':
                    if (not option.isdigit()):
                        print("That is not a valid choice!")
                    elif (int(option)>(len(attacks))) or (int(option)<1):
                        print("That is not a valid choice!")
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
        return

    def turn(self,optionPlayer,optionEnemy):
        
        isOver = ""
        # option is a list of form [move/swap/item,address]
        optionTypePlayer = optionPlayer[0]
        optionTypeEnemy = optionEnemy[0]
        # swap happpens first always
        if optionTypePlayer == "swap":
            print(self.player.name+" is swapping out "+self.player.team[0].poke["name"]+" and is sending in "+self.player.team[optionPlayer[1]].poke["name"])
            self.player.team[0].statReset()
            self.player.team[0], self.player.team[optionPlayer[1]] = self.player.team[optionPlayer[1]], self.player.team[0]
            self.player.team[0].statUpdate("send",self.player.badges)
            self.guiUpdate()
        if optionTypeEnemy == "swap":
            print(self.enemy.name+" is swapping out "+self.enemy.team[0].poke["name"]+" and is sending in "+self.enemy.team[optionEnemy[1]].poke["name"])
            self.enemy.team[0].statReset()
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
            self.guiUpdate()
        else:
            #in this case, we have to check status conditions separately
            [lossPlayer,playerToSwitch] = self.statusCheck(self.player,self.player.team[0])
            [lossEnemy,enemyToSwitch] = self.statusCheck(self.enemy,self.enemy.team[0])
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
                self.swapIn(self.player)
            if enemyToSwitch:
                print(self.enemy.name+" needs to swap in a Pokemon.")
                self.swapIn(self.enemy)
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


    def __init__(self,player,enemy,typeInfo):
        self.typeInfo = typeInfo
        self.player = player
        self.enemy = enemy

        ### GUI INITIALIZATION
        root = Tk()
        root.title('Battle')
        root.geometry('250x150')
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
