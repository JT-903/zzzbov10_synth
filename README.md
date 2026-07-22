# ZZZBOV10 Synthesis using Capybara

Clara's code comes from Capybara's dev branch: `modules/capy_mof_hardcode.py`.

## Features

- JSON file integration: store up to 24 sets of sample parameters (volumes, mixing times) in `sampledata.json` and they will be carried out sequentially.
    - Unfortunately, this won't simply work on the robot, as the JSON file cannot be uploaded to it. [The API documentation implies this is possible, and files (CSV in their example) can be stored on the robot: https://docs.opentrons.com/python-api/runtime-parameters/defining/]
    - A possible workaround to this is to use the Jupyter notebook server running on the robot at port 48888. Note that all files in the notebook are stored on the robot, so there could still be a struggle there.
- Heater-shaker module: the implementation is a bit janky for now, but the shake mode can be used to mix the (trz) into the cobalt solution. Alternatively, the hard code can be edited to disable it.
- Antisolvent is supported, and a volume of it is required (or set it to zero and it will be automatically skipped).
- Mara: The alternative to `main.py` for Mara is `meatball_Maranara.py`, and `initial_testing.py` should be modified slightly for Mara (instructions in the file). As of 22/07/26, the protocols for Mara are a version behind.

## Notes and Observations

Modularity:
- When switching pipettes, any command with a `flow_rate` parameter also had to be edited. As such, all of these have been replaced with the `rate` parameter for easier switching of pipettes.
- Issue: labware and adapters need to match when the Heater-Shaker is being used, or a LabwareCannotBeStackedError is raised. To not receive this error, use known combinations (or lie to the machine).

## Obligatory mention of *datalab*

- *datalab* integration: ideally, the sample data could be generated in the *datalab* interface, and robot actions could be relayed back to *datalab*. The sample data would then be injected into the python script due to the JSON file problem above.

## Logs of attempted syntheses

- These can be found in `logs/[date]` as `LOGBOOK.md`.