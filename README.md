# ZZZBOV10 Synthesis using Capybara

Clara's code comes from Capybara's dev branch: `modules/capy_mof_hardcode.py`.

## Features

- JSON file integration: store up to 24 sets of sample parameters (volumes, mixing times) in `sampledata.json` and they will be carried out sequentially.
    - Unfortunately, this won't simply work on the robot, as the JSON file cannot be uploaded to it. [The API documentation implies this is possible, and files (CSV in their example) can be stored on the robot: https://docs.opentrons.com/python-api/runtime-parameters/defining/]
    - A possible workaround to this is to use the Jupyter notebook server running on the robot at port 48888. Note that all files in the notebook are stored on the robot, so there could still be a struggle there.
    - Due to implementation, only the first mixing time and cycle number will be used. However, these quantities must be present for all samples (they can be set to 0 and 1 respectively if desired).
- Heater-shaker module: the implementation is a bit janky for now, but the shake mode can be used to mix the (trz) into the cobalt solution. Alternatively, the hardcode can be edited to disable it.
- Antisolvent is supported, and a volume of it is required (or set it to zero and it will be skipped).
- Mara: The alternative script to `methodA.py` for Mara is `meatball_Maranara.py`, and `initial_testing.py` should be modified slightly for Mara (instructions in the file). As of 24/07/26, the protocols for Mara are up to date.
- The method A script should be used for Mn, Fe, Co, Ni, and Zn; the method B script should be used only for Cu and Zn.
    - In order to yield the beta-Ni phase, the starting solution of nickel nitrate should be acidified with nitric acid.

## Notes and Observations

Modularity:
- When switching pipettes, any command with a `flow_rate` parameter also had to be edited. As such, all of these have been replaced with the `rate` parameter for easier switching of pipettes.
- Issue: Labware and adapters need to be compatible when the heater-shaker is being used, or a LabwareCannotBeStackedError is raised. To not receive this error, see the appendix for known matches or create a custom labware definition (or lie to the robot).
- Warning: JSON files made for method A are not compatible with method B, as the `delay_time` parameter is used very differently, and vice versa.

AI Compatibility:
- Issue: When using a multi-channel pipette in SINGLE nozzle configuration, `pick_up_tip` locations must be specified or the pipette will raise an OutOfTipsError. This does not affect the prewritten scripts in `protocols` as tip tracking is hardcoded in, but if the AI were to write its own script it should be prompted to specify tip locations.
- Issue: see the miscellaneous issue about overflowing wells. The AI may choose a wellplate that overflows, so human review is necessary to choose a wellplate that can hold the volumes required.

Miscellaneous:
- Flow rates in multi-channel pipettes are much slower than single-channel pipettes of the same volume.
- Issue: The API has no idea if a well on the wellplate overflows. The simulation raises no errors. The Opentrons app raises no errors and the UI adds a massive amount of unlabelled fluid to any overflowing wells (for reasons unknown). Robot response pending.
    - The Opentrons app fills non-empty wells that aren't full yet but will overflow later in the procedure with this unlabelled fluid as well. Even when the liquids in the reservoir are unlabelled, the extra unlabelled fluid is still added. The unlabelled fluid amount is independent of the well capacity, but dependent on how much liquid is added to the well.
    - This "issue" could be an advantage, as it is possible to lie to the machine about 3D printed or non-standard plates that have been designed to fit both the heater-shaker and the relevant adapter. This would skip having to create custom labware definitions.

## Obligatory mention of *datalab*

- *datalab* integration: ideally, the sample data could be generated in the *datalab* interface, and robot actions could be relayed back to *datalab*. The sample data would then be injected into the python script due to the JSON file problem above.

## Logs of attempted syntheses

- These can be found in `logs/[date]` as `LOGBOOK.md`.
- 21.07.26: Capy performed initial testing.
- 23.07.26: SMs received, setup options explored. Synthesis delayed to 28.07.

# Appendix

## Complete list of heater-shaker adapters and compatible plates/tube racks

Note that many of the well plates and all tube racks in the labware library are not compatible with any heater-shaker adapter.

Without custom labware definitions, the universal adapter only supports 384-, 96-, and 24-well plates. The type B universal adapter only supports 96-well plates.

Most of this information is not present on the labware library or the API documentation. A small amount is present as retired/deprecated "combination" labware.

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