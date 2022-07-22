from Stage2Mult import stage2Mult
import math
import random
def confuseCalc(poke,enemyWall):
    attMod = stage2Mult(poke.modifiers[0])
    defMod = stage2Mult(poke.modifiers[1])
    power = 40
    status = poke.status
    level = poke.level
    if status == "burn":
        burnLoss = 2
    else:
        burnLoss = 1
    if "reflect" in enemyWall:
        wallGain = 2
    else:
        wallGain = 1
    
    attStat = math.floor(math.floor(poke.attack*attMod)/burnLoss)
    defStat = math.floor(poke.defense*defMod)*wallGain

    if (attStat > 255) or (defStat > 255):
        attStat = math.floor(attStat / 4) % 256
        defStat = math.floor(defStat / 4) % 256
    
    baseDamage = math.floor(math.floor((math.floor((2*level)/5 + 2)*max(1,attStat)*power)/max(1,defStat))/50)
    threshDamage = min(baseDamage,997)+2
    roll = random.randint(217,255)
    damage = math.floor(threshDamage*roll/255)
    return damage