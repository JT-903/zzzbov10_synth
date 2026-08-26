# Plan Of Action

1) Initial testing
2) Camera focusing and exposure - pylon viewer
3) TEST USAGE OF `capycam.pfs`
4) Set off Capy
5) After Capy is done, set off Capycam

# Results

## Initial testing was rough

- Calling repeated move commands is not recommended, especially on non-standard labware, as the pipette doesn't retract far enough up.
    - This isn't usually a problem since most protocols will be a string of aspirates, dispenses, and mixes.
    - Capy broke the A1 pillar of the printed vial rack. Not cool bro.
- Risers work just fine to adjust the labware height.
- NEVER CANCEL CAPY WHILE IT'S HOMING ITS AXES. It won't be able to drop pipette tips until its axes are re-homed.
- The aspirate clearance for the reservoir is 2. Not lower. 2.

## The camera settings were good enough

They will be refined on 27/08 as the footage was quite grainy.

## Synthesis was interesting

B6S1 was probably contaminated, but the stuff that grew around the contamination was probably blue. The blue is back, forming a layer on top of each sample and then snowing down to the bottom over a few hours. It was not present on samples 4 and 5 (75 uL and 100 uL water respectively), and was very patchy on sample 3.

## The timelapse is in the Sun lab *datalab* under batch 7 sample 3

I'll make a new function for the web app to take a "video" (it's actually a timelapse but it returns a video instead of images). The timelapse function will stick around because it might work better with an AI agent.