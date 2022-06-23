#!/usr/bin/env python

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

    def initStats(self,stats):
        if len(stats) != 5:
            raise Exception("Stats must be in a 5-element list")
        for i in range(len(stats)):
            if (not isinstance(stats[i], int)) or (stats[i]<0):
                raise Exception("Stats must be non-negative integers")
        self.HP = stats[0]
        self.Attack = stats[1]
        self.Defense = stats[2]
        self.Special = stats[3]
        self.Speed = stats[4]
    
    def initPP(self):
        PP = []
        for move in self.moveset:
            PP.append(move["pp"])
        self.PP = PP

    def __init__(self,name,level,stats,moves,pokeList,moveList):
        self.baseStats = stats
        self.setPoke(name,pokeList)
        self.setMoveset(moves,moveList)
        self.initStats(stats)
        self.initPP()
        self.level = level
        self.status = "none"
        self.wall = []
        self.accuracy = 1
        self.evasion = 1
        self.whereIs = "field" #this is "underground" if dig, "air" if fly