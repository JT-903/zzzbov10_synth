# Plan of Action

1)	Risk assessment
2)	Initial testing
3)	Evaluate tests
4)	Possible synthesis run?

## Initial testing

Preliminary (robot): fill reservoir well A1 with water, empty plate, full tip rack

Preliminary (code): pipette (1 channel or 96 channel single), labware

Note down data either here or in separate excel spreadsheet

Failure modes:
- Crashes – always be ready to press stop, then reconfigure deck layout
- Pipette leakage – since it’s only water, can observe this. Test again to see if air gaps fix this
- (96 channel) Random errors – consult main.py (local) for my fixes, consult Clara for good fixes

## Evaluate tests

Evaluate data gained from initial tests – error bars, standard deviations

Write conclusions to this file

Failure modes:
- Large offset/scaling between code/default and real – this can be coded for, go back to code and adjust
- High deviation/large error bars – do not continue to synthesis, go back to testing. Is there a way to make the robot more consistent?

## Synthesis run

Preliminary (robot): reconfigure deck layout, make up solutions for reservoir, tips in column 1 for use, empty plate again, do we want to do one with an antisolvent?

Preliminary (code): use initial tests as a guide for changes, pipette, labware, do we want to do one with an antisolvent?

Failure modes:
- Crashes – should not be a problem due to initial testing, but always be ready to press stop
- Pipette leakage – should have been seen in testing, immediate stop, back to testing to see if air gaps stop this
- Problems with ethanol (if applicable) – stop, could try creating a custom liquid class for special instructions then go back to testing (with ethanol this time)
In case of success: find a place for sample(s) to sit undisturbed

# Results

Known bug: the robot will pick up any tip it’s positioned over. If start="A1" and it tries to pick up tip A1, it will pick up all tips. Pick up H12 instead and work backwards, or start="H12" and go from start.

Second time was the charm. See initial_testing.py for the final script.

Pipette: 200 ul 96 channel pipette is the best option right now. Waiting on a 1000 ul pipette for The Big Crystal (TM).

## Evaluation

- See excel spreadsheet.
- There is a ~ 0.1 s standard deviation in how long an aspirate/dispense action takes. This deviation could be in flow rates, robot movement, robot computer, etc.
- Aspirates take on average ~ 1.5 s longer than dispenses.

## Conclusions for next run

The default rates for aspirate and dispense functions are 15 ul/s. This is very slow.

Use a vial as the plate. After run, leave it in designated drawer with the message "do not disturb. crystals sleeping"