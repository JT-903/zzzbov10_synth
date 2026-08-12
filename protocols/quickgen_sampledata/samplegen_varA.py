import json
import numpy as np

def orderingToName(n):
    names = ["metal nitrate", "1,2,4-triazole", "ammonium thiocyanate", "anti-solvent", "diluent", "acid"]
    return names[n-1]

def coordMap(n):
    ''' Returns a list of sample parameters for one species '''
    m = orderingToName(n)
    lowerLimit = int(input(f"\nLower bound for {m}: "))
    upperLimit = int(input(f"Upper bound for {m}: "))
    stepNum = int(input(f"Number of steps for {m}: "))

    map_n = np.linspace(lowerLimit, upperLimit, stepNum)
    return map_n.tolist()

'''
The lower bound is the lowest volume, in uL, that you want.
The upper bound is the highest volume, in uL, that you want.
The number of steps evenly divides the bound interval into that many equally spaced integer values.

E.g. lower bound 100; upper bound 300; number of steps 5:
    [100, 150, 200, 250, 300]

Note: for a fixed amount for every sample, set lower bound [x]; upper bound [x]; number of steps 1.

WARNING: there are no checks to see if the volume of a given sample is too high, or if there are too many samples.
'''

# Create a list of lists of composition space to be sampled
bigList = []
for i in range(6):
    bigList.append(coordMap(i+1))

# Turn the list of lists into a long list of sample parameters
# Theoretically this can represent a full 6D tensor of composition space that can be sampled
k = 0
sampleDictList = []
for a in bigList[0]:
    for b in bigList[1]:
        for c in bigList[2]:
            for d in bigList[3]:
                for e in bigList[4]:
                    for f in bigList[5]:
                        k += 1
                        sampleDictList.append({
                            "sample_id": k,
                            "vol_a": int(round(a)),
                            "vol_b": int(round(b)),
                            "vol_c": int(round(c)),
                            "vol_anti": int(round(d)),
                            "dil_vol": int(round(e)),
                            "vol_ha": int(round(f)),
                            "cycle_n": 2
                        })

# Write sample parameters to tempdata.json
''' Ugly version
with open("tempdata.json", "w") as f:
    json.dump(sampleDictList, f)
#''' # More pretty version
with open("tempdata.json", "w") as f:
    f.write("[")
with open("tempdata.json", "a") as f:
    for elem in sampleDictList:
        f.write("\n    ")
        json.dump(elem, f)
        if elem != sampleDictList[-1]:
            f.write(",")
    f.write("\n]")
#'''
print("\nData written to tempdata.json")