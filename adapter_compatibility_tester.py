from opentrons import protocol_api

# This isn't necessary
metadata = {
    "protocolName": "How to lie to the code",
    "description": "every time the api changes, might be good to check, latest checked: 2.29",
    "author": "JT-903"
}

# THIS IS NECESSARY
requirements = {"robotType": "Flex", "apiLevel": "2.27"}

def run(protocol: protocol_api.ProtocolContext):
    # change the adapter, add to the list
    adapter_name = "opentrons_universal_flat_adapter"
    plate_list = [
        "appliedbiosystemsmicroamp_384_wellplate_40ul",
        "axygen_96_wellplate_500ul",
        "biorad_384_wellplate_50ul",
        "biorad_96_wellplate_200ul_pcr",
        "corning_12_wellplate_6.9ml_flat",
        "corning_24_wellplate_3.4ml_flat",
        "corning_384_wellplate_112ul_flat",
        "corning_48_wellplate_1.6ml_flat",
        "corning_6_wellplate_16.8ml_flat",
        "corning_96_wellplate_330ul",
        "corning_96_wellplate_360ul_flat",
        "corning_falcon_384_wellplate_130ul_flat",
        "costar_96_wellplate_2.2ml",
        "eppendorf_384_wellplate_45ul",
        "eppendorf_96_wellplate_1000ul",
        "eppendorf_96_wellplate_150ul",
        "eppendorf_96_wellplate_2000ul",
        "eppendorf_96_wellplate_2000ul_lobind",
        "eppendorf_96_wellplate_350ul_lobind",
        "eppendorf_96_wellplate_500ul",
        "eppendorf_96_wellplate_500ul_lobind",
        "greiner_384_wellplate_240ul",
        "greiner_96_wellplate_323ul",
        "greiner_96_wellplate_340ul_chimney",
        "greiner_96_wellplate_382ul",
        "ibidi_96_square_well_plate_300ul",
        "milliplex_r_96_well_microtiter_plate",
        "nest_24_wellplate_10.4ml",
        "nest_96_wellplate_100ul_pcr_full_skirt",
        "nest_96_wellplate_200ul_flat",
        "nest_96_wellplate_2ml_deep",
        "nunc_384_wellplate_100ul",
        "nunc_96_wellplate_450ul",
        "opentrons_96_wellplate_200ul_pcr_full_skirt",
        "smc_384_read_plate",
        "thermofisher_nunc_maxisorp_lockwell_elisa",
        "thermoscientific_96_wellplate_800ul",
        "thermoscientific_abgene_96_wellplate_1.2ml",
        "thermoscientificnunc_96_wellplate_1300ul",
        "thermoscientificnunc_96_wellplate_2000ul",
        "usascientific_96_wellplate_2.4ml_deep",
        "opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical",
        "opentrons_10_tuberack_nest_4x50ml_6x15ml_conical",
        "opentrons_15_tuberack_eppendorf_15ml_conical",
        "opentrons_15_tuberack_falcon_15ml_conical",
        "opentrons_15_tuberack_nest_15ml_conical",
        "opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap",
        "opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap",
        "opentrons_24_tuberack_generic_2ml_screwcap",
        "opentrons_24_tuberack_nest_0.5ml_screwcap",
        "opentrons_24_tuberack_nest_1.5ml_screwcap",
        "opentrons_24_tuberack_nest_1.5ml_snapcap",
        "opentrons_24_tuberack_nest_2ml_screwcap",
        "opentrons_24_tuberack_nest_2ml_snapcap",
        "opentrons_6_tuberack_falcon_50ml_conical",
        "opentrons_6_tuberack_nest_50ml_conical"
    ]

    tips = protocol.load_labware("opentrons_flex_96_filtertiprack_200ul", "C2")
    reservoir = protocol.load_labware("opentrons_tough_12_reservoir_22ml", "B1")
    hs_mod = protocol.load_module("heaterShakerModuleV1", "D1")
    hs_adapter = hs_mod.load_adapter(adapter_name) # opentrons_universal_flat_adapter is the one we have
    hs_mod.open_labware_latch() # NECESSARY for this script to run

    trash = protocol.load_trash_bin("A3")

    pipette = protocol.load_instrument("flex_96channel_200", tip_racks=[tips])
    
    for item in plate_list:
        try:
            hs_plate = hs_adapter.load_labware(item)
            protocol.move_labware(hs_plate, protocol_api.OFF_DECK)
            protocol.comment(f"Success: {item}")
        except Exception:
            continue
    # Anything that says Success: is good
    # The moving to off-deck step may raise a lot of warnings - ignore them