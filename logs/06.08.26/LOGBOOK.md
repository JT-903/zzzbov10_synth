# Plan of Action

1) Initial testing to try and fix the bug
2) Synthesis: 0:3 to 5:3 ethanol:water
3) Synthesis 2: 0 - 500 uL dilution of 100 uL cobalt solution

## Initial testing

Failure modes: 
- Pressure error when trying to aspirate ethanol. See below.
- Misalignment of the wellplate offset. Just remove the negative sign and run again.

Possible temporary fixes for the pressure error:
- Call repeated transfers of 100 uL (which didn't cause errors last time)
- Include blow-outs after each dispense

Permanent fix to follow where needed.

## Synthesis

Triple check as always. Don't try and pull out sample 1 before the anti-solvent. Just wait; the blue won't disappear for at least a few minutes.

Failure modes:
- Pressure error. Install temporary fixes, then diagnose afterwards.
- Contamination of the reservoir. Try to stop it before it occurs, then retry with a different dispense clearance.

# Results

No errors on the initial testing for some reason. Vial rack aligned quite well, but drifts slightly forward as it moves through the column due to the spacing between wells being different.

The pipette overpressure error happened multiple times during the variant synthesis while transferring large volumes of ethanol, and is persistent while `transfer_with_liquid_class` is used. Using `transfer` instead prevents this error.

The blue precipitate is almost definitely cobalt hydroxide. See `gotcha.jpg` for proof.

More ethanol means the blue sticks around for longer.

Lessons learned:
- `transfer_with_liquid_class` is terrible and just throws up random errors.
- Sample 1 yielded only 2.2 mg of blue precipitate. It's very difficult to isolate and not worth the effort.

No problems during second synthesis. More dilution does not reduce amount of blue - it just looks less blue.

## Yield

The ethanol samples will be discarded - not a single one showed decently sized crystals.

When cleaning out the ethanol samples, the liquid was discarded. Then acetone was added to the solid that remained, causing a turquoise colour. This only happened on the first wash. No idea what it is, but I think it's cool.

The crystals on the diluted samples are a few hundred um long and roughly cubic.

Yield was hampered heavily by a large amount of pink cobalt hydroxide at the bottom of the diluted runs. Total yield (all six samples combined): 78.5 mg, 64%.