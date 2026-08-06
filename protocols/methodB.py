from opentrons import protocol_api
from opentrons.protocol_api import SINGLE, ROW, COLUMN, ALL
import json

# stealing clara's code but modifying it to fit my script
EXAMPLE_DATA = json.loads("""[
    {"sample_id": 1, "vol_a": 200, "vol_b": 80, "delay_time": 60},
    {"sample_id": 2, "vol_a": 200, "vol_b": 80, "delay_time": 120},
    {"sample_id": 3, "vol_a": 200, "vol_b": 80, "delay_time": 180}
]""") # vol_a, vol_b, delay_time are the only values used as the protocol is very simple

def validate_sample_parameters(samples) -> tuple[bool, str]: # max vol 200 ul
    """Validate sample parameters (dict-based version)."""
    max_samples = 95

    if not samples:
        return False, "No samples provided"
    if len(samples) > max_samples:
        return False, f"Too many samples for this protocol: {len(samples)} (max {max_samples})"

    for sample in samples:
        vol_a = sample["vol_a"]
        vol_b = sample["vol_b"]
        delay_time = sample["delay_time"]
        sid = sample["sample_id"]

        if vol_a < 0 or vol_a > 200:
            return False, f"Sample {sid}: vol_a must be 0-200 µL, got {vol_a}"
        if vol_b < 0 or vol_b > 200:
            return False, f"Sample {sid}: vol_b must be 0-200 µL, got {vol_b}"
        if delay_time < 0 or delay_time > 600:
            return False, f"Sample {sid}: mixing time must be 0-600 s, got {delay_time}"
        # Overflow clause - modify where necessary
        if vol_a + vol_b + vol_c + vol_anti > 900:
            return False, f"Sample {sid}: total volume exceeds well volume: {vol_a+vol_b+vol_c+vol_anti} µL (max 900 µL)"

    return True, "All samples valid"

def samples_to_lists(samples) -> tuple[list[float], list[float], list[float]]:
    """Convert dict-based sample parameters to lists."""

    vol_a_list = [s["vol_a"] for s in samples]
    vol_b_list = [s["vol_b"] for s in samples]
    delay_time_list = [s["delay_time"] for s in samples]

    return vol_a_list, vol_b_list, delay_time_list

# Back to my code

# This isn't necessary
metadata = {
    "protocolName": "Cu/Zn analogue AutoSynthesis",
    "description": "v0.6a: removed volatile liquid class,  06/08/26",
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
    hs_plate.set_offset(x=-1, y=0, z=0) # because we're using sunlab_96_vialrack_800ul
    hs_mod.close_labware_latch()
    ''' # no hs_mod - look through and hash out 2 lines
    hs_plate = protocol.load_labware("axygen_96_wellplate_500ul", "D3")
    hs_plate.set_offset(x=-1, y=0, z=0) # because we're using sunlab_96_vialrack_800ul
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
    copper_thiocyanate = protocol.define_liquid(
        name = "Metal(II) thiocyanate",
        description = "dilute solution in acetone, x M",
        display_color = "#FF0000"
    )
    trz_ligand = protocol.define_liquid(
        name = "1,2,4-triazole",
        description = "solution in acetone, 5x M",
        display_color = "#67718A"
    )

    reservoir.load_liquid(
        wells = ["A1"],
        volume = 2500,
        liquid = copper_thiocyanate
    )
    reservoir.load_liquid(
        wells = ["A3"],
        volume = 2500,
        liquid = trz_ligand
    )

    # Task file integration
    protocol.comment("-> Loading sample parameters")
    try:
        samples = EXAMPLE_DATA # the hashed-out code below is probably not useful
        #with open("sampledataB.json", "r") as f:
            #samples = json.load(f)
        is_valid, msg = validate_sample_parameters(samples)
        if not is_valid:
            raise ValueError(msg)
        protocol.comment(f"Loaded {len(samples)} samples from JSON")
    except Exception as e:
        protocol.comment(f"ERROR: Failed to load samples: {str(e)}")
        raise
    
    #''' Data from the file
    volA, volB, timeDelay = samples_to_lists(samples)
    ''' # Default data instead of the file
    samples = ["lol"]
    volA = [200]
    volB = [200]
    timeDelay = [10]
    #'''

    # -|===> MAIN <===|-
    protocol.home()
    protocol.comment("-|===> Starting Protocol <===|-")
    
    # Add metal thiocyanate to wells
    protocol.comment("-> Transferring metal thiocyanate")
    #pipette.well_bottom_clearance.aspirate = 2 # labware difference
    pipette.pick_up_tip(tips.wells()[0])
    for i in range(len(samples)):
        pipette.transfer(volA[i], reservoir.wells()[0], hs_plate.wells()[i], new_tip="never")
    pipette.drop_tip()

    # Add (trz) to wells
    protocol.comment("-> Transferring 1,2,4-triazole")
    for i in range(len(samples)):
        pipette.pick_up_tip(tips.wells()[1+i])
        pipette.transfer(volB[i], reservoir.wells()[2], hs_plate.wells()[i], new_tip="never")
        pipette.drop_tip()

    # Stirring and concentrating
    protocol.comment("-> Mixing and concentrating")
    concTask = hs_mod.set_target_temperature(55) # DO NOT GO ABOVE 56
    hs_mod.set_and_wait_for_shake_speed(1200)
    protocol.wait_for_tasks([concTask])
    protocol.delay(seconds=timeDelay[0])
    hs_mod.deactivate_heater()
    hs_mod.deactivate_shaker()

    # Finalising
    pipette.home()
    hs_mod.open_labware_latch()
    protocol.comment("<===|- Protocol Complete -|===>")
    ''' Camera integration
    for i in range(48):
        protocol.delay(minutes=60)
        protocol.capture_image(filename=f"snapshot{i}")
    #'''