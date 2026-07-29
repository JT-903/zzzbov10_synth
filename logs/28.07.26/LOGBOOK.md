# Plan of Action

1) RA and such
2) Prepare solutions for robot use
3) The first synthesis run

## Preparing solutions

Two options:
- Human concentration: creates 67 umol of target (2.3 mm cube at 100% yield).
    - Dissolve 97.01 mg of cobalt nitrate hexahydrate per mL of water (if anhydrous, 60.98 mg)
    - Dissolve 46.00 mg of 1,2,4-triazole per mL of water
    - Dissolve 50.75 mg of ammonium thiocyanate per mL of water
- More concentrated: dissolve twice as much per mL (confirmed by FIHM group to work) to make twice as much product. Dissolving more is also a possibility. For now, twice as concentrated seems like the best option (thanks Maria!).

Make equal volumes of each solution (2.5 mL for 2x concentrated).

Do not forget the antisolvent (ethanol).

Placement in reservoir:
- cobalt solution: A1
- triazole solution: A2
- thiocyanate solution: A3
- antisolvent: A4

## Synthesis

Set up deck as in code.

Make sure to triple check everything, and modify reservoir and plate in code/on deck if necessary.

Failure modes:
- Well bottom clearance for triazole dispensing may be far too high. Be ready to stop the procedure, then edit the code to rerun.
- Pipette cannot reach last bit of liquid in the reservoir. Stop the procedure, then transfer to smaller well reservoir or top up reservoir.
    - Prevention (partially): use 12-well reservoir instead of 4-well reservoir
- Ethanol is a volatile liquid. Volatile liquids have not been tested yet. Be ready to stop the procedure. DO NOT CONTINUE IF HANDLING IS A PROBLEM - more tests will be necessary.

# Results

Concentration used: 0.67 M for cobalt, 1.33 M for others

Setup: 2x concentration used (2.5 mL solutions), position of tiprack and reservoir modified to avoid crashes.

(previously un)known bug: the `distribute` command does not retract the pipette back up between dispenses if it thinks the pipette tip is above the height of the plate. As such, the well bottom clearance for triazole dispensing was in fact too low.

Lessons learned:
- Touch tip to get the last drop
- Create a custom labware for the vial plate
- Reduce cycles to 5 or maybe even 4?
- Add mix steps after addition of ammonium thiocyanate and ethanol
Other recommendation:
- Use tall vials as the reservoirs - no problems with low solution levels

First sample got basically no triazole; second was fine-ish; third was a bit iffy.

A possible idea from the meeting afterwards was to try a different ordering of additions. `methodA_variant.py` has been created, and could be run to test this.

## Blue precipitate?

There is a large amount of blue precipitate and a small amount of red precipitate (the desired product) in the second sample. An attempt will be made to characterise it if it is still present on 30.07.