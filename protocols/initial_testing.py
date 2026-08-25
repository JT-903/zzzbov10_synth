from opentrons import protocol_api
from opentrons.protocol_api import SINGLE, ALL

# i feel obligated
metadata = {
    "protocolName": "The Big One 2026",
    "description": "it's literally just a calibration test 25/08/26",
    "author": "JT-903"
}

requirements = {"robotType": "Flex", "apiLevel": "2.27"}

def run(protocol: protocol_api.ProtocolContext):
    # Labware
    protocol.comment("-> Initialising deck")
    tips = protocol.load_labware("opentrons_flex_96_filtertiprack_200ul", "B2")
    reservoir = protocol.load_labware("opentrons_tough_12_reservoir_22ml", "C1")
    ''' with hs_mod
    hs_mod = protocol.load_module("heaterShakerModuleV1", "D3")
    hs_adapter = hs_mod.load_adapter("opentrons_universal_flat_adapter")
    hs_plate = hs_adapter.load_labware("axygen_96_wellplate_500ul")
    hs_mod.close_labware_latch()
    ''' # no hs_mod
    hs_plate = protocol.load_labware("axygen_96_wellplate_500ul", "D3")
    hs_plate.set_offset(x=-1, y=0.5, z=12) # because we're using sunlab_96_printedrack_900ul
    #'''

    # Trash
    trash = protocol.load_trash_bin("D1")

    # Instrument
    protocol.comment("-> Initialising instrument")
    pipette = protocol.load_instrument("flex_96channel_200", "left", tip_racks=[tips])
    pipette.configure_nozzle_layout(style=SINGLE, start="H12")
    
    # -|===> MAIN <===|-
    protocol.home()
    pipette.well_bottom_clearance.aspirate = 1.5 # let's see
    protocol.comment("-|===> Starting Protocol <===|-")

    # Part 1: calibration test
    pipette.pick_up_tip(tips.wells()[0])
    pipette.move_to(hs_plate.wells()[0].bottom(z=1))
    pipette.move_to(hs_plate.wells()[7].bottom(z=1))
    pipette.move_to(hs_plate.wells()[-8].bottom(z=1))
    pipette.move_to(hs_plate.wells()[-5].bottom(z=1))
    pipette.move_to(hs_plate.wells()[-1].bottom(z=1))

    # Part 2: can the aspirate get lower?
    pipette.well_bottom_clearance.dispense = 1.5
    pipette.aspirate(200, reservoir.wells()[6])
    pipette.dispense(200, reservoir.wells()[6])
    pipette.drop_tip()

    # Finalising
    pipette.home()
    protocol.comment("<===|- Protocol Complete -|===>")