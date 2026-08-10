from opentrons import protocol_api
from opentrons.protocol_api import SINGLE, ROW, COLUMN, ALL
import json

# The order in which things are added
# 1 vol_a; 2 vol_b; 3 vol_c; 4 vol_anti; 5 dil_vol; 6 vol_ha
ordering = [1, 5, 6, 3, 2, 4] # [1, 5, 6, 2, 3, 4] is recommended; 6 first is a bad idea
# the datalab integration could inject the ordering into here

# thanks for the code clara but it's pretty unrecognisable now
EXAMPLE_DATA = json.loads("""[
    {"sample_id": 1, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 0, "dil_vol": 0, "vol_ha": 100, "cycle_n": 2},
    {"sample_id": 2, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 0, "dil_vol": 0, "vol_ha": 200, "cycle_n": 2},
    {"sample_id": 3, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 0, "dil_vol": 100, "vol_ha": 100, "cycle_n": 2},
    {"sample_id": 4, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 0, "dil_vol": 200, "vol_ha": 100, "cycle_n": 2},
    {"sample_id": 5, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 100, "dil_vol": 0, "vol_ha": 100, "cycle_n": 2},
    {"sample_id": 6, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 200, "dil_vol": 0, "vol_ha": 100, "cycle_n": 2},
    {"sample_id": 7, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 300, "dil_vol": 0, "vol_ha": 100, "cycle_n": 2}
]""") # the datalab integration could inject the json file into here

def validate_sample_parameters(samples) -> tuple[bool, str]:
    """Validate sample parameters (dict-based version)."""
    max_samples = 95 # 96 per tip rack, minus 1 for first substance transfer

    if not samples:
        return False, "No samples provided"

    for sample in samples:
        vol_a = sample["vol_a"]
        vol_b = sample["vol_b"]
        vol_c = sample["vol_c"]
        vol_anti = sample["vol_anti"]
        dil_vol = sample["dil_vol"]
        vol_ha = sample["vol_ha"]
        cycle_n = sample["cycle_n"]
        sid = sample["sample_id"]

        # Big check
        if vol_a < 0:
            return False, f"Sample {sid}: vol_a must be non-negative, got {vol_a}"
        if vol_b < 0:
            return False, f"Sample {sid}: vol_b must be non-negative, got {vol_b}"
        if vol_c < 0:
            return False, f"Sample {sid}: vol_c must be non-negative, got {vol_c}"
        if vol_anti < 0:
            return False, f"Sample {sid}: vol_anti must be non-negative, got {vol_anti}"
        if dil_vol < 0:
            return False, f"Sample {sid}: dil_vol must be non-negative, got {dil_vol}"
        if vol_ha < 0:
            return False, f"Sample {sid}: vol_ha must be non-negative, got {vol_ha}"
        if cycle_n < 1 or not isinstance(cycle_n, int):
            return False, f"Sample {sid}: cycle number must be a positive integer, got {cycle_n}"

        # Overflow clause
        total_vol = vol_a + vol_b + vol_c + vol_anti + dil_vol + vol_ha
        if total_vol > 900:
            return False, f"Sample {sid}: total volume exceeds well volume: {total_vol} µL (max 900 µL)"
        
        # Max sample checking - implicit assumption that vol_a is added first
        if vol_b != 0:
            max_samples = max_samples - 1
        if vol_c != 0:
            max_samples = max_samples - 1
        if vol_anti != 0:
            max_samples = max_samples - 1
        if dil_vol != 0:
            max_samples = max_samples - 1
        if vol_ha != 0:
            max_samples = max_samples - 1
        
    if max_samples < 0:
        return False, f"Too many samples for this protocol: {-max_samples} liquid transfers over maximum"

    return True, "All samples valid"

def samples_to_lists(samples):
    """Convert dict-based sample parameters to a list of lists."""

    vol_a_list = [s["vol_a"] for s in samples]
    vol_b_list = [s["vol_b"] for s in samples]
    vol_c_list = [s["vol_c"] for s in samples]
    vol_anti_list = [s["vol_anti"] for s in samples]
    dil_vol_list = [s["dil_vol"] for s in samples]
    vol_ha_list = [s["vol_ha"] for s in samples]
    cycle_n_list = [s["cycle_n"] for s in samples]

    return [vol_a_list, vol_b_list, vol_c_list, vol_anti_list, dil_vol_list, vol_ha_list, cycle_n_list]

# Back to my code

def orderingToName(n):
    names = ["metal nitrate", "1,2,4-triazole", "ammonium thiocyanate", "anti-solvent", "diluent", "acid"]
    return names[n-1]

# This isn't necessary
metadata = {
    "protocolName": "ZZZBOV10 Variant Synthesis",
    "description": "vBeta: total modularity, hopefully I haven't broken everything, 10/08/26",
    "author": "JT-903"
}

# THIS IS NECESSARY
requirements = {"robotType": "Flex", "apiLevel": "2.27"}

def run(protocol: protocol_api.ProtocolContext):
    # Labware - best configuration? avoids collisions
    protocol.comment("-> Initialising deck")
    tips = protocol.load_labware("opentrons_flex_96_filtertiprack_200ul", "B2")
    reservoir = protocol.load_labware("opentrons_tough_12_reservoir_22ml", "C1")
    ''' with hs_mod
    hs_mod = protocol.load_module("heaterShakerModuleV1", "D3")
    hs_adapter = hs_mod.load_adapter("opentrons_universal_flat_adapter") # opentrons_universal_flat_adapter is the one we have
    hs_plate = hs_adapter.load_labware("axygen_96_wellplate_500ul") # placeholder - custom labware doesn't fit on adapters yet
    hs_plate.set_offset(x=-1, y=0.5, z=0) # because we're using sunlab_96_vialrack_900ul
    hs_mod.close_labware_latch()
    ''' # no hs_mod
    hs_plate = protocol.load_labware("axygen_96_wellplate_500ul", "D3")
    hs_plate.set_offset(x=-1, y=0.5, z=0) # because we're using sunlab_96_vialrack_900ul
    #'''

    # Trash has moved
    trash = protocol.load_trash_bin("D1")

    # Instrument
    protocol.comment("-> Initialising instrument")
    #pipette = protocol.load_instrument("flex_1channel_1000", "right", tip_racks=[tips])
    #''' For multi-channel pipette
    pipette = protocol.load_instrument("flex_96channel_200", tip_racks=[tips])
    pipette.configure_nozzle_layout(style=SINGLE, start="H12") # lessons were learned
    #'''

    # Define liquids in reservoir - makes it pretty in the opentrons app
    cobalt_nitrate = protocol.define_liquid(
        name = "Metal(II) nitrate",
        description = "solution in water, 0.67 M",
        display_color = "#FF0000"
    )
    trz_ligand = protocol.define_liquid(
        name = "1,2,4-triazole",
        description = "solution in water, 1.33 M",
        display_color = "#67718A"
    )
    ammonium_thiocyanate = protocol.define_liquid(
        name = "Ammonium thiocyanate",
        description = "solution in water, 1.33 M",
        display_color = "#88FF99"
    )
    anti_solvent_gen = protocol.define_liquid(
        name = "Anti-solvent",
        description = "probably neat ethanol",
        display_color = "#FFFFFF"
    )
    water_liquid = protocol.define_liquid(
        name = "Water",
        description = "water",
        display_color = "#0000FF"
    )
    nitric_acid = protocol.define_liquid(
        name = "Nitric acid",
        description = "solution in water, 1 M",
        display_color = "#FFFF00"
    )

    reservoir.load_liquid(
        wells = ["A1"],
        volume = 2500,
        liquid = cobalt_nitrate
    )
    reservoir.load_liquid(
        wells = ["A3"],
        volume = 2500,
        liquid = trz_ligand
    )
    reservoir.load_liquid(
        wells = ["A5"],
        volume = 2500,
        liquid = ammonium_thiocyanate
    )
    reservoir.load_liquid(
        wells = ["A7"],
        volume = 5000,
        liquid = anti_solvent_gen
    )
    reservoir.load_liquid(
        wells = ["A9"],
        volume = 5000,
        liquid = water_liquid
    )
    reservoir.load_liquid(
        wells = ["A11"],
        volume = 2500,
        liquid = nitric_acid
    )

    # Task file integration
    protocol.comment("-> Loading sample parameters")
    try:
        samples = EXAMPLE_DATA
        is_valid, msg = validate_sample_parameters(samples)
        if not is_valid:
            raise ValueError(msg)
        protocol.comment(f"Loaded {len(samples)} samples from JSON")
    except Exception as e:
        protocol.comment(f"ERROR: Failed to load samples: {str(e)}")
        raise
    
    #''' Data from the file
    theMasterList = samples_to_lists(samples)
    ''' # Default data instead of the file
    samples = ["lol"]
    theMasterList = [[100], [100], [100], [0], [0], [100], [2]]
    #'''

    # The Modularity Functions - the reason I rewrote everything
    def firstThingsFirst(n):
        resIndex = 2*n - 2
        protocol.comment(f"-> Transferring {orderingToName(n)}")
        pipette.pick_up_tip(tips.wells()[0])
        for i in range(sampleN):
            pipette.transfer(theMasterList[n-1][i], reservoir.wells()[resIndex], hs_plate.wells()[i], new_tip="never")
        pipette.drop_tip()
    
    def addSubstance(n, m, c):
        resIndex = 2*n - 2
        protocol.comment(f"-> Transferring {orderingToName(n)}")
        for i in range(sampleN):
            if theMasterList[n-1][i] == 0:
                c += 1 # don't waste an unused pipette, and adjust indices for next tip pick-up
            else:
                pipette.pick_up_tip(tips.wells()[1+m*sampleN+i-c])
                #pipette.home() # just in case the overpressure error somehow persists
                pipette.transfer(theMasterList[n-1][i], reservoir.wells()[resIndex], hs_plate.wells()[i], new_tip="never")
                pipette.dynamic_mix(
                    aspirate_start_location=hs_plate.wells()[i].bottom(z=2),
                    dispense_start_location=hs_plate.wells()[i].bottom(z=20),
                    repetitions=theMasterList[6][i],
                    volume=150,
                    rate=3.0,
                    final_push_out=20
                ) # this could cause precipitation of product - modify for big crystal
                pipette.blow_out()
                pipette.drop_tip()
        return c

    # -|===> MAIN <===|-
    protocol.home()
    sampleN = len(samples) # used for looping and indexing later
    pipette.well_bottom_clearance.aspirate = 2 # labware difference
    k = 0
    protocol.comment("-|===> Starting Protocol <===|-")

    ''' Notes for users:
    1) k/c is the tip tracking index; i is the sample index (which is also used for tip tracking); j is the looping index.
        - Please do not try to redefine them. I don't know how spectacularly the rest of the program will break.
    2) There is no built-in concentrating step for the Mn and Zn analogues. This must be done separately.
    '''
    
    # Full modularity is so cool
    firstThingsFirst(ordering.pop(0))

    pipette.well_bottom_clearance.dispense = 28 # don't contaminate the reservoirs

    for j in range(len(ordering)):
        k = addSubstance(ordering[j], j, k)

    # Finalising
    pipette.home()
    protocol.comment("<===|- Protocol Complete -|===>")