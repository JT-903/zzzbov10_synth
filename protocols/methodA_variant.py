from opentrons import protocol_api
from opentrons.protocol_api import SINGLE, ROW, COLUMN, ALL
import json

# stealing clara's code but modifying it to fit my script
EXAMPLE_DATA = json.loads("""[
    {"sample_id": 1, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 0, "delay_time": 0, "cycle_n": 2},
    {"sample_id": 2, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 100, "delay_time": 0, "cycle_n": 2},
    {"sample_id": 3, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 200, "delay_time": 0, "cycle_n": 2},
    {"sample_id": 4, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 300, "delay_time": 0, "cycle_n": 2},
    {"sample_id": 5, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 400, "delay_time": 0, "cycle_n": 2},
    {"sample_id": 6, "vol_a": 100, "vol_b": 100, "vol_c": 100, "vol_anti": 500, "delay_time": 0, "cycle_n": 2}
]""") # the datalab integration may have to directly inject the json file into here

def validate_sample_parameters(samples) -> tuple[bool, str]: # max vol 200 ul
    """Validate sample parameters (dict-based version)."""
    max_samples = 31

    if not samples:
        return False, "No samples provided"
    if len(samples) > max_samples:
        return False, f"Too many samples for this protocol: {len(samples)} (max {max_samples})"

    for sample in samples:
        vol_a = sample["vol_a"]
        vol_b = sample["vol_b"]
        vol_c = sample["vol_c"]
        vol_anti = sample["vol_anti"]
        cycle_n = sample["cycle_n"]
        sid = sample["sample_id"]

        if vol_a < 0 or vol_a > 200:
            return False, f"Sample {sid}: vol_a must be 0-200 µL, got {vol_a}"
        if vol_b < 0 or vol_b > 200:
            return False, f"Sample {sid}: vol_b must be 0-200 µL, got {vol_b}"
        if vol_c < 0 or vol_c > 200:
            return False, f"Sample {sid}: vol_c must be 0-200 µL, got {vol_c}"
        if cycle_n < 1 or not isinstance(cycle_n, int):
            return False, f"Sample {sid}: cycle number must be a positive integer, got {cycle_n}"
        # Overflow clause - modify where necessary
        if vol_a + vol_b + vol_c + vol_anti > 900:
            return False, f"Sample {sid}: total volume exceeds well volume: {vol_a+vol_b+vol_c+vol_anti} µL (max 900 µL)"

    return True, "All samples valid"

def samples_to_lists(samples) -> tuple[list[float], list[float], list[float], list[float], list[float]]:
    """Convert dict-based sample parameters to lists."""

    vol_a_list = [s["vol_a"] for s in samples]
    vol_b_list = [s["vol_b"] for s in samples]
    vol_c_list = [s["vol_c"] for s in samples]
    vol_anti_list = [s["vol_anti"] for s in samples]
    cycle_n_list = [s["cycle_n"] for s in samples]

    return vol_a_list, vol_b_list, vol_c_list, vol_anti_list, cycle_n_list

# Back to my code

# This isn't necessary
metadata = {
    "protocolName": "ZZZBOV10 Variant Synthesis",
    "description": "v0.7b: also nitric acid option, about to break everything, 07/08/26",
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
    hs_mod.close_labware_latch()
    ''' # no hs_mod
    hs_plate = protocol.load_labware("axygen_96_wellplate_500ul", "D3")
    hs_plate.set_offset(x=-1, y=0, z=0) # because we're using sunlab_96_vialrack_800ul
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
        display_color = "#FCFC00"
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
        samples = EXAMPLE_DATA # the hashed-out code below is probably not useful
        #with open("sampledataA.json", "r") as f:
            #samples = json.load(f)
        is_valid, msg = validate_sample_parameters(samples)
        if not is_valid:
            raise ValueError(msg)
        protocol.comment(f"Loaded {len(samples)} samples from JSON")
    except Exception as e:
        protocol.comment(f"ERROR: Failed to load samples: {str(e)}")
        raise
    
    #''' Data from the file
    volA, volB, volC, volAnti, cycleN = samples_to_lists(samples)
    ''' # Default data instead of the file
    samples = ["lol"]
    volA = [200]
    volB = [200]
    volC = [200]
    volAnti = [0]
    cycleN = [4]
    #'''

    # -|===> MAIN <===|-
    protocol.home()
    sampleN = len(samples) # used for looping and indexing later
    protocol.comment("-|===> Starting Protocol <===|-")
    ''' Notes for users:
    1) k is the tip tracking index; i is the sample index (which is also used for tip tracking).
        - Please do not try to redefine them. I don't know how spectacularly the rest of the program will break.
    2) There is no built-in concentrating step for the Mn and Zn analogues. This must be done separately.
    '''
    
    # Add metal nitrate to wells
    protocol.comment("-> Transferring metal nitrate")
    pipette.well_bottom_clearance.aspirate = 2 # labware difference
    pipette.pick_up_tip(tips.wells()[0])
    for i in range(sampleN):
        pipette.transfer(volA[i], reservoir.wells()[0], hs_plate.wells()[i], new_tip="never")
    pipette.drop_tip()

    # Add anti-solvent to wells
    protocol.comment("-> Transferring anti-solvent")
    k = 0
    pipette.well_bottom_clearance.dispense = 28 # don't contaminate the reservoir
    for i in range(sampleN):
        if volAnti[i] == 0:
            k += 1 # don't waste an unused pipette, and adjust indices for next tip pick-up
        else:
            pipette.pick_up_tip(tips.wells()[1+i-k])
            #pipette.home() # just in case the overpressure error somehow persists
            pipette.transfer(volAnti[i], reservoir.wells()[8], hs_plate.wells()[i], new_tip="never")
            pipette.dynamic_mix(
                aspirate_start_location=hs_plate.wells()[i].bottom(z=2),
                dispense_start_location=hs_plate.wells()[i].bottom(z=20),
                repetitions=cycleN[i],
                volume=150,
                rate=3.0
            ) # this could cause precipitation of product - modify for big crystal
            pipette.blow_out()
            pipette.drop_tip()

    # Add ammonium thiocyanate to wells
    protocol.comment("-> Transferring ammonium thiocyanate")
    pipette.well_bottom_clearance.dispense = 1 # back to default
    for i in range(sampleN):
        pipette.pick_up_tip(tips.wells()[1+sampleN+i-k])
        pipette.aspirate(volC[i], reservoir.wells()[4])
        pipette.dispense(volC[i], hs_plate.wells()[i])
        pipette.dynamic_mix(
            aspirate_start_location=hs_plate.wells()[i].bottom(z=2),
            dispense_start_location=hs_plate.wells()[i].bottom(z=20),
            repetitions=cycleN[i],
            volume=200,
            rate=3.0
        )
        pipette.blow_out(hs_plate.wells()[i])
        pipette.drop_tip()

    # Add (trz) to wells rapidly
    protocol.comment("-> Transferring 1,2,4-triazole")
    for i in range(sampleN):
        pipette.pick_up_tip(tips.wells()[1+2*sampleN+i-k])
        pipette.aspirate(volB[i], reservoir.wells()[2])
        pipette.dispense(volB[i], hs_plate.wells()[i], rate=3.0)
        pipette.dynamic_mix(
            aspirate_start_location=hs_plate.wells()[i].bottom(z=2),
            dispense_start_location=hs_plate.wells()[i].bottom(z=20),
            repetitions=cycleN[i],
            volume=200,
            rate=3.0
        ) # this causes precipitation of blue - modify for big crystal
        pipette.blow_out()
        pipette.drop_tip()

    # Finalising
    pipette.home()
    protocol.comment("<===|- Protocol Complete -|===>")