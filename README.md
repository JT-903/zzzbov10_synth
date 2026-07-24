# ZZZBOV10 Synthesis using Capybara

Clara's code comes from Capybara's dev branch: `modules/capy_mof_hardcode.py`.

## Features

- JSON file integration: store up to 24 sets of sample parameters (volumes, mixing times) in `sampledata.json` and they will be carried out sequentially.
    - Unfortunately, this won't simply work on the robot, as the JSON file cannot be uploaded to it. [The API documentation implies this is possible, and files (CSV in their example) can be stored on the robot: https://docs.opentrons.com/python-api/runtime-parameters/defining/]
    - A possible workaround to this is to use the Jupyter notebook server running on the robot at port 48888. Note that all files in the notebook are stored on the robot, so there could still be a struggle there.
    - Due to implementation, only the first mixing time and cycle number will be used. However, these quantities must be present for all samples (they can be set to 0 and 1 respectively if desired).
- Heater-shaker module: the implementation is a bit janky for now, but the shake mode can be used to mix the (trz) into the cobalt solution. Alternatively, the hardcode can be edited to disable it.
- Antisolvent is supported, and a volume of it is required (or set it to zero and it will be skipped).
- Mara: The alternative script to `main.py` for Mara is `meatball_Maranara.py`, and `initial_testing.py` should be modified slightly for Mara (instructions in the file). As of 23/07/26, the protocols for Mara are multiple versions behind.

## Notes and Observations

Modularity:
- When switching pipettes, any command with a `flow_rate` parameter also had to be edited. As such, all of these have been replaced with the `rate` parameter for easier switching of pipettes.
- Issue: labware and adapters need to be compatible when the heater-shaker is being used, or a LabwareCannotBeStackedError is raised. To not receive this error, use known combinations (or lie to the machine).

Miscellaneous:
- Issue: The API has no idea if the well plate overflows. The simulation raises no errors. The Opentrons app raises no errors and the UI adds a massive amount of unlabelled fluid to any full or overflowing wells (for reasons unknown). Robot response pending.

## Obligatory mention of *datalab*

- *datalab* integration: ideally, the sample data could be generated in the *datalab* interface, and robot actions could be relayed back to *datalab*. The sample data would then be injected into the python script due to the JSON file problem above.

## Logs of attempted syntheses

- These can be found in `logs/[date]` as `LOGBOOK.md`.
- 21.07.26: Capy performed initial testing.
- 23.07.26: SMs received, setup options explored. Synthesis delayed to 28.07.

# Appendix

## Complete list of adapters and compatible plates/tube racks

Note that many of the well plates and all tube racks in the labware library are not compatible with any adapter.

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