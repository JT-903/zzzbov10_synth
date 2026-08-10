# ZZZBOV10 Synthesis using Capybara

Clara's code comes from Capybara's dev branch: `modules/capy_mof_hardcode.py`.

## Features

- JSON file integration: store sets of sample parameters (volumes, mixing times) and they will be carried out concurrently.
- Antisolvent, dilution, and acidification are supported, and volumes of them are required (or set it to zero and it will be skipped).
- Variant script: in `methodA_variant.py`, the thiocyanate is added before the triazole. This works well and doesn't require the heater-shaker, so is preferred over method A.
- The method A scripts should be used for Mn, Fe, Co, Ni, and Zn; the method B script should be used only for Cu and Zn.
    - In order to yield the beta-Ni phase, the starting solutions should be made up in nitric acid.

## Retired features

- `methodA.py`, `meatball_Maranara.py`, the custom labware definition, and separate sample data JSON files have been retired as they are no longer necessary.
- Heater-shaker module (method A): the shake mode can be used to mix the triazole into the cobalt solution. Alternatively, the hardcode can be edited to disable it.
    - This has limited effectiveness on tall narrow wells, and should work better on wide wells.
- Mara: The alternative script to `methodA.py` for Mara is `meatball_Maranara.py`, and `initial_testing.py` should be modified for Mara. As of 06/08/26, the protocol for Mara is quite a few versions behind method A.
- Image capture: after any Flex method is run, the robot can capture an image every hour for 48 hours. Currently disabled.

## Notes and Observations

Modularity:
- When switching pipettes, any command with a `flow_rate` parameter also had to be edited. As such, all of these have been replaced with the `rate` parameter for easier switching of pipettes.
- Issue: Labware and adapters need to be compatible when the heater-shaker is being used, or a LabwareCannotBeStackedError is raised. To not receive this error, see the appendix for known matches or create a custom labware definition (or lie to the robot).
- `methodA_variant.py` can be modified to work with additional tip racks to increase sample numbers, but the tip tracking must be rewritten.
- `methodB.py` has not been made fully modular as it has not been tested yet.

AI Compatibility:
- Issue: When using a multi-channel pipette in SINGLE nozzle configuration, `pick_up_tip` locations must be specified or the pipette will raise an OutOfTipsError. This does not affect the prewritten scripts in `protocols` as tip tracking is hardcoded in, but if the AI were to write its own script it should be prompted to specify tip locations.
- Issue: see the miscellaneous issue about overflowing wells. The AI may choose a wellplate that overflows, so human review is necessary to choose a wellplate that can hold the volumes required.

Miscellaneous:
- Flow rates in multi-channel pipettes are much slower than single-channel pipettes of the same volume.
- Issue: The API has no idea if a well on the wellplate overflows. The simulation raises no errors. The Opentrons app raises no errors. The robot raises no errors.
    - This "issue" could be an advantage, as it is possible to lie to the machine about 3D printed or non-standard plates that have been designed to fit both the heater-shaker and the relevant adapter. This would skip having to create custom labware definitions.
- Issue: the pipette will throw out a "pipette overpressure error" during some `transfer_with_liquid_class` commands but not with others. To work around this, don't use `transfer_with_liquid_class` because the normal `transfer` works perfectly fine with ethanol.

### The Current Direction

The SunLab Vial Rack can actually hold up to 1 mL (but maybe don't fill all the way to the top). The vial rack should be modified to 900 uL.

Add nitric acid to the samples to hopefully prevent the cobalt hydroxide crashing out.

## Obligatory mention of *datalab*

- *datalab* integration: ideally, the sample data could be generated in the *datalab* interface, and robot actions could be relayed back to *datalab*. The sample data would then be injected into the python script due to the JSON file problem above.

## Logs of attempted syntheses

- These can be found in `logs/[date]` as `LOGBOOK.md`.
- 21.07.26: Capy performed initial testing.
- 23.07.26: SMs received, setup options explored. Synthesis delayed to 28.07.
- 28.07.26: Capy performed method A synthesis with cobalt, with varied success across the plate. Yield okay (44-60%).
- 04.08.26: Capy performed method A variant synthesis with cobalt. An error occurred at the end, but otherwise successful. Yield good, but only okay for anti-solvent.
- 06.08.26: Capy performed initial testing with no errors, then method A variant synthesis with cobalt. The same error as last time occurred at the anti-solvent transfer, but with a couple of hotfixes the protocol was completed as intended. Capy then performed method A variant synthesis with cobalt, but testing dilution levels. There were no errors.

# Appendix

## Complete list of heater-shaker adapters and compatible plates/tube racks

Note that many of the well plates and all tube racks in the labware library are not compatible with any heater-shaker adapter.

As of writing, loading custom labware onto adapters is not yet supported.

Without custom labware definitions: 
- The universal adapter only supports 384-, 96-, and 24-well plates.
- The type B universal adapter only supports 96-well plates.

Most of this information is not present on the labware library or the API documentation. A small amount is present as retired/deprecated "combination" labware.

These lists were collected by simulating the `adapter_compatibility_tester.py` script. Each adapter should be checked after every API release. More information about simulating this script can be found in the script.

##### opentrons_universal_flat_adapter
- axygen_96_wellplate_500ul
- corning_384_wellplate_112ul_flat
- corning_96_wellplate_360ul_flat
- corning_falcon_384_wellplate_130ul_flat
- greiner_384_wellplate_240ul
- ibidi_96_square_well_plate_300ul
- nest_24_wellplate_10.4ml
##### opentrons_universal_flat_adapter_type_b
- milliplex_r_96_well_microtiter_plate
- thermofisher_nunc_maxisorp_lockwell_elisa
##### opentrons_96_deep_well_adapter
- nest_96_wellplate_2ml_deep
##### opentrons_96_flat_bottom_adapter
- nest_96_wellplate_200ul_flat
##### opentrons_96_pcr_adapter
- biorad_96_wellplate_200ul_pcr
- nest_96_wellplate_100ul_pcr_full_skirt
- opentrons_96_wellplate_200ul_pcr_full_skirt