#!/usr/bin/env python
import math

from Stage2Mult import stage2Mult
class Pokemon:

    def setPoke(self,name,pokeList):
        pokeValid = False
        for i in range(len(pokeList["pokemon"])):
            if name.casefold() == pokeList["pokemon"][i]["name"].casefold():
                pokeValid = True
                self.poke = pokeList["pokemon"][i]
                break
        if not pokeValid:
            raise Exception("That is not a valid Pokemon name!")
        
    def setMoveset(self,moves,moveList):
        moveset = []
        if (len(moves)<0) or (len(moves)>4):
            raise Exception("Each Pokemon can only have 1-4 moves")
        for i in range(len(moves)):
            move2Check = moves[i]
            moveValid = False
            for j in range(len(moveList["moves"])):
                if move2Check.casefold() == moveList["moves"][j]["name"].casefold():
                    moveValid = True
                    moveset.append(moveList["moves"][j])    
                    break
            if not moveValid:
                raise Exception("The move "+move2Check+" does not exist in the move list")
        self.moveset = moveset      

    def setStats(self):
        stats = self.activeStats
        # two ways of accessing stats: through activeStats and nicely named stats like HP, attack, ...
        # these should always be the same
        if len(stats) != 5:
            raise Exception("Stats must be in a 5-element list")
        for i in range(len(stats)):
            if (not isinstance(stats[i], int)) or (stats[i]<0):
                raise Exception("Stats must be non-negative integers")
        self.HP = stats[0]
        self.attack = stats[1]
        self.defense = stats[2]
        self.special = stats[3]
        self.speed = stats[4]

    def statUpdate(self,reason,badges):
        # https://www.dragonflycave.com/mechanics/gen-i-stat-modification
        # badges = 4-element list, Attack (Brock), Def (Surge), Speed (Koga), Special (Blaine)
        # reason the stat update is occurring. Could be 3 things: 
        # 1) sending poke out, 2) status change, 3) move modified the value
        # because of strange nonsense that happens in case 3, we need an output that will tell if the enemy needs to change its speed or attack stat
        enemyChange = ""
        if reason == "send":
            self.activeStats = self.outOfBattleStats
            # sending out is as intended
            # sets active stats to out of battle stats, then checks for status + badge boosts
            self.setStats()
            if self.status == "paralyze":
                # paralysis quarters speed
                self.activeStats[4] = max(1,math.floor(self.speed/4))
            if self.status == "burn":
                # burn halves attack
                self.activeStats[1] = max(1,math.floor(self.attack/2))
            #badge boosts give 12.5% boosts initially
            if badges[0] == 1:
                self.activeStats[1] = min(999,math.floor(self.attack*1.125))
            if badges[1] == 1:
                self.activeStats[2] = min(999,math.floor(self.defense*1.125))
            if badges[2] == 1:
                self.activeStats[4] = min(999,math.floor(self.speed*1.125))
            if badges[3] == 1:
                self.activeStats[3] = min(999,math.floor(self.special*1.125))
            
            # also when we send in a pokemon its types are set back to normal (conversion is why this is necessary)
            self.types = self.poke["types"]

        elif reason == "+paralysis":
            # pokemon getting paralyzed functions as expected
            self.activeStats[4] = max(1,math.floor(self.speed/4))
        elif reason == "+burn":
            # similar for burn
            self.activeStats[1] = max(1,math.floor(self.attack/2))

        elif reason[0:2] == "-p":
            # the case of removing a stat condition is horribly confusing and depends on the item or method being used to do so.
            # I WILL ADD THIS LATER
            return
        elif reason[0:2] == "-b":
            # the case of removing a stat condition is horribly confusing and depends on the item or method being used to do so.
            # I WILL ADD THIS LATER
            return
        
        elif reason[0:3] == "mod":
            # parse the string. It will be of the form "mod:stat:stage:self/enemy employing stat change:enemy status"
                reasonSplit = str.split(reason,":")
                ind = ["attack","defense","special","speed","accuracy","evasion","crit"].index(reasonSplit[1])
                modNum = int(reasonSplit[2])
                preMod = self.modifiers[ind]
                if ind !=6: 
                    # this means a stat that can range from +/-6 is updated, NOT crit
                    # first check if the mod can happen
                    if  (modNum>0) and (preMod == 6):
                        print("This stat is already too high!")
                    elif (modNum<0) and (preMod == -6):
                        print("This stat is already too low!")
                    else:
                        # here we will just check if the stat is already 1 or 999
                        if (ind<4) and (modNum>0) and (self.activeStats[ind+1]==999): # add 1 because of HP not being in the mod list
                            print("This stat is already too high!")
                        elif (ind<4) and (modNum<0) and (self.activeStats[ind+1]==1): # add 1 because of HP not being in the mod list
                            print("This stat is already too low!")
                        # in this case the stat change goes through. This is where things get totally absurd
                        # 1) The stat stage itself is raised or lowered according to the move's effect.
                        # simple enough
                        elif modNum<0:
                            self.modifiers[ind] = max(-6,self.modifiers[ind]+modNum)
                            if modNum == -1:
                                print("The Pokemon's " + reasonSplit[1] + " was decreased!")
                            if modNum == -2:
                                print("The Pokemon's " + reasonSplit[1] + " was greatly decreased!")
                        else:
                            self.modifiers[ind] = min(6,self.modifiers[ind]+modNum)
                            if modNum == 1:
                                print("The Pokemon's " + reasonSplit[1] + " was increased!")
                            if modNum == 2:
                                print("The Pokemon's " + reasonSplit[1] + " was greatly increased!")    
                        # 2) The stat is recalculated as the original out-of-battle stat multiplied by the ratio corresponding to the new stat stage. If we're raising the stat, it's capped at 999; if we're lowering the stat, it's bumped up to 1 if it ends up at zero. So far, so good.
                        # note that we don't take paralysis or burn into account yet.
                        if ind<4:
                            self.activeStats[ind+1] = min(999,max(1,math.floor(self.outOfBattleStats[ind+1]*stage2Mult(self.modifiers[ind]))))
                        # 3) If the stat being modified is the player's Pokémon's, the badge boost is applied to all of its stats that you have the corresponding badge for, capped at 999. This is not as expected. It means your other stats get re-boosted if you have the right badge.
                        # in our mod, we will allow both enemies and the player to get badge boosts, so we do not check the condition here
                        if badges[0] == 1:
                            self.activeStats[1] = min(999,math.floor(self.activeStats[1]*1.125))
                        if badges[1] == 1:
                            self.activeStats[2] = min(999,math.floor(self.activeStats[2]*1.125))
                        if badges[2] == 1:
                            self.activeStats[4] = min(999,math.floor(self.activeStats[4]*1.125))
                        if badges[3] == 1:
                            self.activeStats[3] = min(999,math.floor(self.activeStats[3]*1.125))
                        # 4) If the Pokémon whose turn it is not is paralyzed, its Speed is quartered. This means if one of your other stats is lowered, your Speed will get quartered again if you're paralyzed. This is obviously not the intended effect. Worse still, because this applies to the Pokémon whose turn it is not, this will happen to the opponent when you raise one of your own stats, and vice versa.
                        # 5) If the Pokémon whose turn it is not is burned, its Attack is halved. As above.
                        # this is tricky to implement. We have to return a value here to see if the enemy's pokemon also needs to update its stats. not that bad but why is this in the game lmao
                        if reasonSplit[3] == "self":
                            # if this value is "self", we will lower the *enemy's* stat based on status
                            if reasonSplit[4] == "paralyze":
                                enemyChange = "speed"
                            elif reasonSplit[4] == "burn":
                                enemyChange = "attack"
                        elif reasonSplit[3] == "enemy":
                            # if this value is "enemy", we will lower this pokemon's stat based on status
                            if self.status == "paralyze":
                                self.activeStats[4] = max(1,math.floor(self.activeStats[4]/4))
                            elif self.status == "burn":
                                self.activeStats[1] = max(1,math.floor(self.activeStats[1]/2))
                        else:
                            print("You made a mistake Brian! check the reason input to statUpdate")

                else:
                    if preMod !=0:
                        print("This stat is already too high!")
                    else:
                        self.modifiers[6] = -1

                        
        else:
            print("You messed up, Brian!!! Check the reason input to statUpdate")
            print(reason[0:3])
        # finally, update the nice-named stats
        self.setStats()
        return enemyChange

    def statReset(self):
        self.modifiers = [0,0,0,0,0,0,0]
        self.confused = False
        self.activeStats[1:] = self.outOfBattleStats[1:]
        self.setStats()
        self.turncount["toxic"]=0
        self.turncount["confused"]=0
        if "mist" in self.wall:
            self.wall.remove("mist")

    def __init__(self,name,level,stats,maxHP,moves,maxPP,PP,pokeList,moveList):
        self.setPoke(name,pokeList)
        
        # need to set the types separately because they can be modified by the move conversion
        self.types = self.poke["types"]

        self.setMoveset(moves,moveList)
        self.wall = []
        # when the pokemon gets sent out, no matter what, it starts with out of battle stats
        self.outOfBattleStats = stats
        # active stats, affected by modifiers and status, are what are actually used. 
        # These have readable names set in setstats, and have standard indexed names in activeStats
        self.activeStats = stats
        self.setStats()
        
        self.maxHP = maxHP
        self.PP = PP
        self.maxPP = maxPP
        self.level = level
        
        # Status conditions and confusion can coexist
        self.status = "none"
        self.confused = False
        self.flinching = False

        self.leechSeed= False
        self.modifiers = [0,0,0,0,0,0,0] # attack, defense, special, speed, accuracy, evasion, crit chance in stages
        self.whereIs = "field" # this is "underground" if dig, "air" if fly, "faint" if dead before turn ends
        self.turncount = {"toxic":0,"sleep":0,"confused":0}
