from opentrons import protocol_api
import json

# stealing clara's code but modifying it to fit my script
EXAMPLE_DATA = json.loads("""[
    {"sample_id": 1, "vol_a": 1000, "vol_b": 1000, "vol_c": 1000, "vol_anti": 0, "delay_time": 15},
    {"sample_id": 2, "vol_a": 1000, "vol_b": 1000, "vol_c": 1000, "vol_anti": 500, "delay_time": 10}
]""") # pls don't change me if you want to use a real file - change line 133 instead

def validate_sample_parameters(samples) -> tuple[bool, str]:
    """Validate sample parameters (dict-based version)."""
    max_samples = 24

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
        sid = sample["sample_id"]

        if vol_a < 0 or vol_a > 1000:
            return False, f"Sample {sid}: vol_a must be 0-1000 µL, got {vol_a}"
        if vol_b < 0 or vol_b > 1000:
            return False, f"Sample {sid}: vol_b must be 0-1000 µL, got {vol_b}"
        if vol_c < 0 or vol_c > 1000:
            return False, f"Sample {sid}: vol_c must be 0-1000 µL, got {vol_c}"
        if vol_anti < 0 or vol_anti > 1000:
            return False, f"Sample {sid}: vol_anti must be 0-1000 µL, got {vol_anti}"
        if delay_time < 0 or delay_time > 300:
            return False, f"Sample {sid}: mixing time must be 0-300s, got {delay_time}"

    return True, "All samples valid"
    return True, "All samples valid" # duplicate?

def samples_to_lists(samples) -> tuple[list[float], list[float], list[float], list[float], list[float]]:
    """Convert dict-based sample parameters to lists."""

    vol_a_list = [s["vol_a"] for s in samples]
    vol_b_list = [s["vol_b"] for s in samples]
    vol_c_list = [s["vol_c"] for s in samples]
    vol_anti_list = [s["vol_anti"] for s in samples]
    delay_time_list = [s["delay_time"] for s in samples]

    return vol_a_list, vol_b_list, vol_c_list, vol_anti_list, delay_time_list

# Back to my code

# This isn't necessary
metadata = {
    "protocolName": "ZZZBOV10 AutoSynthesis",
    "description": "v0.4c: half measures, heater-shaker hardcode option, json loader, proof of concept, hi matt 16/07/26",
    "author": "JT-903"
}

# THIS IS NECESSARY
requirements = {"robotType": "Flex", "apiLevel": "2.27"}

def run(protocol: protocol_api.ProtocolContext):
    # Labware
    protocol.comment("-> Initialising deck")
    tips = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "D1")
    reservoir = protocol.load_labware("opentrons_tough_4_reservoir_72ml", "D2")
    #''' # with hs_mod
    hs_mod = protocol.load_module("heaterShakerModuleV1", "D3")
    hs_adapter = hs_mod.load_adapter("opentrons_universal_flat_adapter")
    hs_plate = hs_adapter.load_labware("nest_24_wellplate_10.4ml")
    hs_mod.close_labware_latch()
    ''' # no hs_mod - look through and hash out 2 lines
    hs_plate = protocol.load_labware("nest_24_wellplate_10.4ml", "D3")
    '''

    # Trash
    trash = protocol.load_trash_bin("A3")

    # Instrument
    protocol.comment("-> Initialising instrument")
    pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=[tips])

    # Define liquids in reservoir - I don't think this is necessary and I can't see what it changes
    cobalt_nitrate = protocol.define_liquid(
        name = "Cobalt(II) nitrate",
        description = "solution in water, x M",
        display_color = "#FF0000"
    )
    trz_ligand = protocol.define_liquid(
        name = "1,2,4-triazole",
        description = "solution in water, y M",
        display_color = "#67718A"
    )
    ammonium_thiocyanate = protocol.define_liquid(
        name = "Ammonium thiocyanate",
        description = "solution in water, z M",
        display_color = "#88FF99"
    )
    anti_solvent_gen = protocol.define_liquid(
        name = "Anti-solvent",
        description = "[your info here]",
        display_color = "#FFFFFF"
    )

    reservoir.load_liquid(
        wells = ["A1"],
        volume = 12000,
        liquid = cobalt_nitrate
    )
    reservoir.load_liquid(
        wells = ["A2"],
        volume = 12000,
        liquid = trz_ligand
    )
    reservoir.load_liquid(
        wells = ["A3"],
        volume = 12000,
        liquid = ammonium_thiocyanate
    )
    reservoir.load_liquid(
        wells = ["A4"],
        volume = 12000,
        liquid = anti_solvent_gen
    )

    # Task file integration
    protocol.comment("-> Loading sample parameters")
    try:
        samples = EXAMPLE_DATA # change for an actual json file when ready eg:
        #with open("sampledata.json", "r") as f:
            #samples = json.load(f)
        is_valid, msg = validate_sample_parameters(samples)
        if not is_valid:
            raise ValueError(msg)
        protocol.comment(f"Loaded {len(samples)} samples from JSON")
    except Exception as e:
        protocol.comment(f"ERROR: Failed to load samples: {str(e)}")
        raise
    
    #''' Data from the file
    volA, volB, volC, volAnti, timeDelay = samples_to_lists(samples)
    ''' # Default data instead of the file
    samples = ["lol"]
    volA = [1000]
    volB = [1000]
    volC = [1000]
    volAnti = [0]
    timeDelay = [15]
    '''

    # -|===> MAIN <===|-
    protocol.home()
    antiClass = protocol.get_liquid_class("ethanol_80") # used for anti-solvent transfer - volatile
    protocol.comment("-|===> Starting Protocol <===|-")
    ''' Notes to self:
    0) no manual review so far on the code procedure
    1) mild error checking is here!!
    2) the .json file data can be imported successfully!
    '''
    
    for i in range(len(samples)):
        protocol.comment(f"-|=> Sample {i+1}")

        # Add cobalt nitrate to well
        protocol.comment("-> Transferring cobalt nitrate")
        pipette.pick_up_tip()
        pipette.transfer(volA[i], reservoir.wells()[0], hs_plate.wells()[i], new_tip="never")
        pipette.drop_tip()

        # Add (trz) to well slowly with mixing - after testing put this in a function?
        protocol.comment("-> Transferring trz slowly with mixing")
        pipette.well_bottom_clearance.dispense = 21 # don't dip pipette in sample? probs not necessary
        pipette.pick_up_tip()
        pipette.aspirate(volB[i], reservoir.wells()[1])
        # So the 'with mixing' bit is a bit ad hoc - pipette can't move while hs_mod is shaking
        for j in range(10):
            pipette.dispense(volB[i]/10, hs_plate.wells()[i], flow_rate=100)
            hs_mod.set_and_wait_for_shake_speed(200) # valid range 200-3000 RPM
            protocol.delay(seconds=timeDelay[i])
            hs_mod.deactivate_shaker()
        pipette.drop_tip()

        # Add ammonium cyanate to well
        protocol.comment("-> Transferring ammonium thiocyanate")
        pipette.well_bottom_clearance.dispense = 1 # see trz above if this is necessary
        pipette.pick_up_tip()
        pipette.aspirate(volC[i], reservoir.wells()[2])
        pipette.dispense(volC[i], hs_plate.wells()[i], rate=3.0)
        pipette.drop_tip()

        # Add anti-solvent to well (volume 0 is skipped by Capy)
        protocol.comment(f"-> Transferring{" no" if volAnti[i] == 0 else ""} anti-solvent")
        pipette.transfer_with_liquid_class(antiClass, volAnti[i], reservoir.wells()[3], hs_plate.wells()[i])

    # Finalising
    protocol.comment("<===|- Protocol Complete -|===>")

    # playground - delete me when publishing
    '''
    pipette.default_speed = 100 # default is 300-350 - DO NOT GO FASTER! also doesn't show a protocol comment - GANTRY speed
    pipette.flow_rate.aspirate = 716 # also can set .dispense and .blow_out and they are all independent
    pipette.transfer(2000, reservoir["A1"], plate["D6"], new_tip="once") # yes this works - transfer does refills
    # transfer does breakdown comments, transfer_with_liquid_class does not
    pipette.configure_for_volume(4) # generates a protocol comment, only useful for 50ul pipette, 1-5 or 5-50 possible
    pipette.well_bottom_clearance.dispense = 1 # does not generate protocol comment - useful so no contamination
    ''' # hi matt