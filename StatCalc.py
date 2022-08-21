import math
def statCalc(baseStats,DVs,statXP,level):
    # all are lists of of 5 numbers in order: [HP,ATT,DEF,SPEC,SPEED]
    # DVs are from 0 to 15, statXP is from 0 to 65535
    stats = [0,0,0,0,0]
    for i in range(5):
        E = math.floor(min(255, math.ceil(math.sqrt(statXP[i]))) / 4)
        if i == 0:
            stats[i] = math.floor(10+level+(((2*(baseStats[i]+DVs[i])+E)*level)/100))
        else:
            stats[i] = math.floor(5+(((2*(baseStats[i]+DVs[i])+E)*level)/100))
    return stats