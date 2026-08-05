# TildularSequencer
A Tildagon badge app (for the 2026 Spaceagon) that works with the Thawney/Jarkman Tildular Sequencer hexpansion. 

It generates 2 channels of CV (1V/octave) and gate/envelope signals to work with other Tildular modules and regular Eurorack (CV in the range 0-3.3V or so, other input voltages are safe but ignored)

Features include 2 channels of
- Sequencer
- Keyboard
- Tilt-to-CV
- 6-step envelope
- Quantiser

Editing generally uses the touch buttons on the Spaceagon, sometimes in conjunction with the first knob on the hexpansion.

It's not done yet. 

TODO

- move sequencer round 1/2 note to line up with the LEDs
- add a start/stop with the unusued buttons?
- add note nums to keyboard
- make clock adjustment nicer
- Make quantiser search outside the home octave for the closest permitted note
- Give quantiser some pre-set scales (maybe choose with joystick up/down)
- Give quantiser an informative display of some sort about what note it is bending
- Make a Turing-alike generator
- fix keyboard latency
- Save and restore all settings
- Flash the EEPROM and have it start when the module is plugged in
- Extend sequencer to multiple screens, navigating with the joystick
- Handle clock and reset inputs
- Add some euclidean clock business to the clock or the sequencer
- Improve the display all over


