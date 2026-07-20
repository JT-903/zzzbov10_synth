from opentrons import protocol_api

# i feel obligated
metadata = {
    "protocolName": "Basic testing and verifying for both robots",
    "description": "what is the rate parameter? is the flow rate accurate? and other questions from matt 20/07/26",
    "author": "JT-903"
}

# There are only 4 lines that need changing for switching from Capy to Mara

# ONLY ONE ACTIVE pls
#requirements = {"robotType": "OT-2", "apiLevel": "2.27"} # Mara
requirements = {"robotType": "Flex", "apiLevel": "2.27"} # Capy

# this is designed to run on both (but please read through the bit before MAIN)
def run(protocol: protocol_api.ProtocolContext):
    # Labware
    protocol.comment("-> Initialising deck")
    # ONLY ONE tips ACTIVE pls
    #tips = protocol.load_labware("opentrons_96_filtertiprack_1000ul", 4) # Mara
    tips = protocol.load_labware("opentrons_flex_96_filtertiprack_1000ul", "C1") # Capy
    reservoir = protocol.load_labware("opentrons_tough_4_reservoir_72ml", 5)
    ''' with hs_mod - needs to be lonely on OT-2
    hs_mod = protocol.load_module("heaterShakerModuleV1", 3)
    hs_adapter = hs_mod.load_adapter("opentrons_universal_flat_adapter")
    hs_plate = hs_adapter.load_labware("nest_24_wellplate_10.4ml")
    hs_mod.close_labware_latch()
    ''' # no hs_mod
    hs_plate = protocol.load_labware("nest_24_wellplate_10.4ml", 6)
    #'''

    # Trash - leave blank for Mara
    trash = protocol.load_trash_bin("A3") # Capy

    # Instrument - ONLY ONE ACTIVE pls
    protocol.comment("-> Initialising instrument")
    #pipette = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[tips]) # Mara
    pipette = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=[tips]) # Capy

    # -|===> MAIN <===|-
    protocol.home()
    protocol.comment("-|===> Starting Protocol <===|-")
    pipette.pick_up_tip()

    # information
    default_aspirate = pipette.flow_rate.aspirate
    default_dispense = pipette.flow_rate.dispense
    default_blow_out = pipette.flow_rate.blow_out
    protocol.comment(f"The default aspirate rate is {default_aspirate} ul/s.")
    protocol.comment(f"The default dispense rate is {default_dispense} ul/s.")
    protocol.comment(f"The default blow-out rate is {default_blow_out} ul/s.")

    # test 1: is the flow rate accurate?
    protocol.comment("-> This liquid aspirate should take 10 seconds")
    pipette.aspirate(1000, reservoir.wells()[0], flow_rate=100)
    protocol.comment("-> This liquid dispense should take 5 seconds")
    pipette.dispense(1000, hs_plate.wells()[0], flow_rate=200)

    # test 2: what is the rate parameter?
    pipette.flow_rate.aspirate = 200
    pipette.flow_rate.dispense = 200
    protocol.comment("-> Time this aspirate - it should be 10 seconds")
    pipette.aspirate(1000, reservoir.wells()[0], rate=0.5)
    protocol.comment("-> Time this dispense - it should be 2.5 seconds")
    pipette.dispense(1000, hs_plate.wells()[1], rate=2.0)

    pipette.drop_tip()
    protocol.comment("<===|- Protocol Complete -|===>")