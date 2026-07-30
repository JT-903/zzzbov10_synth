from opentrons import protocol_api
from opentrons.protocol_api import SINGLE, ROW, COLUMN, ALL
import json

# stealing clara's code but modifying it to fit my script
EXAMPLE_DATA = json.loads("""[
    {"sample_id": 1, "vol_a": 200, "vol_b": 200, "vol_c": 200, "vol_anti": 0, "delay_time": 10, "cycle_n": 4},
    {"sample_id": 2, "vol_a": 200, "vol_b": 200, "vol_c": 200, "vol_anti": 100, "delay_time": 5, "cycle_n": 4},
    {"sample_id": 3, "vol_a": 200, "vol_b": 200, "vol_c": 200, "vol_anti": 200, "delay_time": 0, "cycle_n": 4}
]""") # the datalab integration may have to directly inject the json file into here

def validate_sample_parameters(samples) -> tuple[bool, str]: # max vol 200 ul
    """Validate sample parameters (dict-based version)."""
    max_samples = 47

    if not samples:
        return False, "No samples provided"
    if len(samples) > max_samples:
        return False, f"Too many samples for this protocol: {len(samples)} (max {max_samples})"

    for sample in samples:
        vol_a = sample["vol_a"]
        vol_b = sample["vol_b"]
        vol_c = sample["vol_c"]
        vol_anti = sample["vol_anti"]
        delay_time = sample["delay_time"]
        cycle_n = sample["cycle_n"]
        sid = sample["sample_id"]

        if vol_a < 0 or vol_a > 200:
            return False, f"Sample {sid}: vol_a must be 0-200 µL, got {vol_a}"
        if vol_b < 0 or vol_b > 200:
            return False, f"Sample {sid}: vol_b must be 0-200 µL, got {vol_b}"
        if vol_c < 0 or vol_c > 200:
            return False, f"Sample {sid}: vol_c must be 0-200 µL, got {vol_c}"
        if vol_anti < 0 or vol_anti > 200:
            return False, f"Sample {sid}: vol_anti must be 0-200 µL, got {vol_anti}"
        if delay_time < 0 or delay_time > 60:
            return False, f"Sample {sid}: mixing time must be 0-60 s, got {delay_time}"
        if cycle_n < 1 or not isinstance(cycle_n, int):
            return False, f"Sample {sid}: number of mixing cycles must be a positive integer, got {cycle_n}"

    return True, "All samples valid"

def samples_to_lists(samples) -> tuple[list[float], list[float], list[float], list[float], list[float], list[float]]:
    """Convert dict-based sample parameters to lists."""

    vol_a_list = [s["vol_a"] for s in samples]
    vol_b_list = [s["vol_b"] for s in samples]
    vol_c_list = [s["vol_c"] for s in samples]
    vol_anti_list = [s["vol_anti"] for s in samples]
    delay_time_list = [s["delay_time"] for s in samples]
    cycle_n_list = [s["cycle_n"] for s in samples]

    return vol_a_list, vol_b_list, vol_c_list, vol_anti_list, delay_time_list, cycle_n_list

# Back to my code

# This isn't necessary
metadata = {
    "protocolName": "ZZZBOV10 AutoSynthesis",
    "description": "v0.6b: camera integration, more lessons learned, ready for synthesis, 30/07/26",
    "author": "JT-903"
}

# THIS IS NECESSARY
requirements = {"robotType": "Flex", "apiLevel": "2.27"}

def run(protocol: protocol_api.ProtocolContext):
    # Labware - best configuration? avoids collisions
    protocol.comment("-> Initialising deck")
    tips = protocol.load_labware("opentrons_flex_96_filtertiprack_200ul", "B2")
    reservoir = protocol.load_labware("opentrons_tough_12_reservoir_22ml", "C1")
    #''' # with hs_mod
    hs_mod = protocol.load_module("heaterShakerModuleV1", "D3")
    hs_adapter = hs_mod.load_adapter("opentrons_universal_flat_adapter") # opentrons_universal_flat_adapter is the one we have
    hs_plate = hs_adapter.load_labware("axygen_96_wellplate_500ul") # placeholder - custom labware doesn't fit on adapters yet
    hs_mod.close_labware_latch()
    ''' # no hs_mod - look through and hash out 2 lines
    hs_plate = protocol.load_labware("sunlab_96_vialrack_800ul", "D3")
    #'''

    # Trash
    trash = protocol.load_trash_bin("A3")

    # Instrument
    protocol.comment("-> Initialising instrument")
    #pipette = protocol.load_instrument("flex_1channel_1000", "right", tip_racks=[tips])
    #''' # For multi-channel pipette
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
        volume = 2500,
        liquid = anti_solvent_gen
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
    volA, volB, volC, volAnti, timeDelay, cycleN = samples_to_lists(samples)
    ''' # Default data instead of the file
    samples = ["lol"]
    volA = [1000]
    volB = [1000]
    volC = [1000]
    volAnti = [0]
    timeDelay = [10]
    cycleN = [5]
    #'''

    # -|===> MAIN <===|-
    protocol.home()
    antiClass = protocol.get_liquid_class("ethanol_80") # used for anti-solvent transfer - volatile
    sampleN = len(samples) # used for looping and indexing later
    protocol.comment("-|===> Starting Protocol <===|-")
    ''' Notes for users:
    1) k is the tip tracking index; i is the sample index (which is also used for tip tracking); j is the mixing loop index.
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

    # Add (trz) to wells slowly with mixing
    protocol.comment("-> Transferring 1,2,4-triazole slowly with mixing")
    pipette.well_bottom_clearance.dispense = 30 # KNOWN HARDWARE ISSUE - should go away with custom labware definition
    dist_list = [elem/cycleN[0] for elem in volB]

    pipette.pick_up_tip(tips.wells()[1])
    for j in range(cycleN[0]):
        pipette.distribute(dist_list, reservoir.wells()[2], hs_plate.wells()[:sampleN], new_tip="never", disposal_volume=5, touch_tip=True)
        # pipette can't move while hs_mod is shaking
        hs_mod.set_and_wait_for_shake_speed(1200) # valid range 200-3000 RPM
        protocol.delay(seconds=timeDelay[0])
        hs_mod.deactivate_shaker()
    pipette.drop_tip()

    # Add ammonium thiocyanate to wells
    protocol.comment("-> Transferring ammonium thiocyanate")
    pipette.well_bottom_clearance.dispense = 1 # reset after trz
    for i in range(sampleN):
        pipette.pick_up_tip(tips.wells()[2+i])
        pipette.aspirate(volC[i], reservoir.wells()[4])
        pipette.dispense(volC[i], hs_plate.wells()[i], rate=3.0)
        pipette.dynamic_mix(
            aspirate_start_location=hs_plate.wells()[i].bottom(z=2),
            dispense_start_location=hs_plate.wells()[i].bottom(z=20),
            repetitions=3,
            volume=200,
            rate=3.0
        )
        pipette.drop_tip()

    # Add anti-solvent to wells
    protocol.comment("-> Transferring anti-solvent")
    k = 0
    for i in range(sampleN):
        if volAnti[i] == 0:
            k += 1 # don't waste an unused pipette, and adjust indices for next tip pick-up
        else:
            pipette.pick_up_tip(tips.wells()[2+sampleN+i-k])
            pipette.transfer_with_liquid_class(antiClass, volAnti[i], reservoir.wells()[6], hs_plate.wells()[i], new_tip="never")
            pipette.dynamic_mix(
                aspirate_start_location=hs_plate.wells()[i].bottom(z=2),
                dispense_start_location=hs_plate.wells()[i].bottom(z=20),
                repetitions=3,
                volume=200,
                rate=3.0
            )
            pipette.drop_tip()

    # Finalising
    pipette.home()
    hs_mod.open_labware_latch()
    protocol.comment("<===|- Protocol Complete -|===>")
    ''' Camera integration
    for i in range(48):
        protocol.delay(minutes=60)
        protocol.capture_image(filename=f"snapshot{i}")
    #'''