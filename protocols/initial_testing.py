from opentrons import protocol_api
from opentrons.protocol_api import SINGLE, ALL

# i feel obligated
metadata = {
    "protocolName": "Capy's trial by alcohol poisoning",
    "description": "why did the last run raise an error? 05/08/26",
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
    hs_plate.set_offset(x=-1, y=0, z=0) # because we're using sunlab_96_vialrack_800ul
    #'''

    # Trash
    trash = protocol.load_trash_bin("D1")

    # Instrument
    protocol.comment("-> Initialising instrument")
    pipette = protocol.load_instrument("flex_96channel_200", "left", tip_racks=[tips])
    pipette.configure_nozzle_layout(style=SINGLE, start="H12")
    
    # -|===> MAIN <===|-
    protocol.home()
    antiClass = protocol.get_liquid_class("ethanol_80")
    pipette.well_bottom_clearance.aspirate = 2 # labware difference
    pipette.well_bottom_clearance.dispense = 2 # for safety
    protocol.comment("-|===> Starting Protocol <===|-")

    # Capy drinks and spits out 1000 uL of ethanol
    pipette.pick_up_tip(tips.wells()[0])
    pipette.transfer_with_liquid_class(antiClass, 300, reservoir.wells()[6], reservoir.wells()[11], new_tip="never")
    pipette.transfer_with_liquid_class(antiClass, 200, reservoir.wells()[6], reservoir.wells()[11], new_tip="never")
    pipette.transfer_with_liquid_class(antiClass, 500, reservoir.wells()[6], reservoir.wells()[11], new_tip="never")
    pipette.drop_tip()

    # Finalising
    pipette.home()
    protocol.comment("<===|- Protocol Complete -|===>")