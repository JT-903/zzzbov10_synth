# Plan of Action

1) Initial testing to try and fix the bug
2) Synthesis: 0:3 to 5:3 ethanol:water

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

No errors on the initial testing. Wellplate aligned well.

The pipette overpressure error is persistent while `transfer_with_liquid_class` is used. Not using it prevents this error.

The blue precipitate is cobalt hydroxide. See `gotcha.jpg` for proof.

Lessons learned:
- `transfer_with_liquid_class` is terrible and just throws up random errors.