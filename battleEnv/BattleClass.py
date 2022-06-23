import random
import math

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

    def tryAttack(self,pokeAttacker,pokeDefender,moveAddress):
        moveResult = "success"
        accRoll = random.randint(0,255)
        moveAcc = math.floor(pokeAttacker.moveset[moveAddress]["acc"]*255/100)
        acc = math.floor(moveAcc*pokeAttacker.accuracy*pokeDefender.evasion)
        if pokeDefender.whereIs != "field":
            moveResult = "fail:"+pokeDefender.whereIs 
        elif acc<=accRoll:
            moveResult = "fail:miss"
        else:
            if pokeAttacker.status == "paralysis":
                paralysisRoll = random.randint(0,255)
                if paralysisRoll < 64:
                    moveResult = "fail:paralysis"
        return moveResult

    def useItem(self,trainer,itemAddress):
        item = trainer.items[itemAddress]
        return

    def attackPhase(self,optionPlayer,optionEnemy):
        # bools for which player is attacking.
        # handled differently if one or both attack.
        playerIs = optionPlayer[0]=="attack"
        enemyIs = optionEnemy[0]=="attack"
        # if only one player tried an attack, the process is easier
        if not (playerIs and enemyIs):
            if playerIs:
                # only player is attacking
                attacker=self.player
                moveAddress = optionPlayer[1]
                defender=self.enemy
            else:
                # only enemy is attacking
                attacker=self.enemy
                moveAddress = optionEnemy[1]
                defender=self.player
            pokeAttacker=attacker.team[0]
            pokeDefender=defender.team[0]
            # check if attack will land
            moveResult = self.tryAttack(pokeAttacker,pokeDefender,moveAddress)
            if moveResult != "success":
                # the one attacker's move didn't land, so the turn is over
                print(moveResult)
                return
            else:
                # the one attacker's move did land, so we have to determine its effect
                print(moveResult)
                # self.parseAttack(pokeAttacker,pokeDefender,moveAddress)
                return
        else:
            # this is the case where both players attacked! We need to 
            # 1) determine whose move goes first by checking priority and speed. In gen 1 there are only two priority moves:
            # Quick Attack, which goes first, and Counter, which goes second. 
            # 2) check if the first move goes through
            # 3) if yes, determine the effect of the first move
            # 4) check if the second move goes through, which includes the possibility that either pokemon has died
            #    or that a status (wrap, sleep, etc.) has been incurred
            # 5) if yes, determine the effect of the second move
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
                playerSpeed = self.player.team[0].Speed
                enemySpeed = self.enemy.team[0].Speed
                if playerSpeed == enemySpeed:
                    # speed tie case. RNG 0-255, if 0-127 player first
                    speedRoll = random.randint(0,255)
                    if speedRoll<128:
                        first = "player"
                    else:
                        first = "enemy"
                elif playerSpeed>enemySpeed:
                    first="player"
                else:
                    first="enemy"
            # now we know who went first, so we have to process the first attack
            if first == "player":
                # only player is attacking
                attacker=self.player
                moveAddress = optionPlayer[1]
                defender=self.enemy
            else:
                # only enemy is attacking
                attacker=self.enemy
                moveAddress = optionEnemy[1]
                defender=self.player
            pokeAttacker=attacker.team[0]
            pokeDefender=defender.team[0]
            moveResult = self.tryAttack(pokeAttacker,pokeDefender,moveAddress)
            if moveResult != "success":
                # the one attacker's move didn't land, so the turn is over
                print(moveResult)
                return
            else:
                # the one attacker's move did land, so we have to determine its effect
                # self.parseAttack(pokeAttacker,pokeDefender,moveAddress)
                print(moveResult)
                return
            # now the first attack is over. many things can happen as a result of the first attack.
            # the defender may have died, the attack may have been disabled, they might have been statused
            # the attacker also may have died due to recoil or explosion/selfdestruct
            # We will check these one by one
        return

    def turn(self,optionPlayer,optionEnemy):
        # option is a list of form [move/swap/item,address]
        optionTypePlayer = optionPlayer[0]
        optionTypeEnemy = optionEnemy[0]
        # swap happpens first always
        if optionTypePlayer == "swap":
            self.player.team[0], self.player.team[optionPlayer[1]] = self.player.team[optionPlayer[1]], self.player.team[0]
        if optionTypeEnemy == "swap":
            self.enemy.team[0], self.enemy.team[optionEnemy[1]] = self.enemy.team[optionEnemy[1]], self.enemy.team[0]
        # item happens next
        if optionTypePlayer == "item":
            self.useItem(self.player,optionPlayer[1])
        if optionTypeEnemy == "item":
            self.useItem(self.enemy,optionEnemy[1])
        # attacks happen next
        if optionTypeEnemy == "attack" or optionTypePlayer == "attack":
            self.attackPhase(optionPlayer,optionEnemy)

    def __init__(self,player,enemy):
        self.player = player
        self.enemy = enemy
        self.turnCount = 0