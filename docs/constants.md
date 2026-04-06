# constants.py

## Purpose
Central configuration source for the entire project.

All modules import values from this file so geometry, timing, and behavior stay consistent.

## What It Defines
- Window settings: width, height, title, FPS.
- Direction identifiers: EAST, WEST, SOUTH, NORTH.
- Color palette: world, UI, traffic lights, ambulance colors.
- Road/intersection geometry and lane center coordinates.
- Vehicle physics parameters:
	- base speed,
	- braking distance,
	- minimum gap,
	- acceleration and deceleration rates.
- Signal timing values:
	- green duration,
	- yellow duration.
- Spawning and speed-control settings:
	- spawn interval/probability,
	- min/max speed multiplier,
	- speed step.

## Design Notes
- No functions or classes are implemented here.
- This module is configuration-only.
- Changing values here affects behavior globally without changing program flow.
