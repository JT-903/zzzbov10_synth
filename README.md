# ZZZBOV10 Synthesis using Capybara

Clara's code comes from `dev/modules/capy_mof_hardcode.py`.

## Features

- JSON file integration: store up to 24 sets of sample parameters (volumes, mixing times) in `sampledata.json` and they will be carried out sequentially.
    - Unfortunately, this probably won't work on the robot, as the JSON file cannot be uploaded to it.
- Heater-shaker module: the implementation is a bit janky for now, but the shake can be used to mix the (trz) into the cobalt solution. Alternatively, the hard code can be edited to disable it.
- Volumes up to 1 mL: each solution can be added in volumes of up to 1 mL.
- Antisolvent is supported, and a volume of it is required (or set it to zero and it will be automatically skipped).

## Desired features

- *datalab* integration: ideally, the sample data could be generated in the *datalab* interface, and robot actions could be relayed back to *datalab*. The sample data would then be injected into the python script due to the JSON file problem above.