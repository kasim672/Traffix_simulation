# signals.py Documentation

## File Purpose
Implements the traffic signal controller and draws signal posts/lights.

## Classes And Functions In This File

### class TrafficSignal
State machine for signal timing and manual overrides.

#### __init__()
- Initializes active direction, pending direction, phase, timer, and mode.

#### update(dt)
- Advances signal timer.
- Applies phase transitions (green and yellow-before-green behavior).

#### should_stop(direction)
- Returns whether a vehicle in `direction` must stop.

#### set_green(direction)
- Manual override to request a direction change.

#### set_auto_cycle(enabled)
- Enables or disables auto cycling.

#### time_remaining()
- Returns remaining time for current signal phase.

#### progress()
- Returns normalized phase progress for UI bars.

#### _draw_signal_box(surface, cx, cy, active_color)
- Draws one 3-bulb signal housing with active lamp and glow.

#### draw(surface)
- Draws all approach signal posts around the intersection.

## Computer Graphics Algorithms Used In This File
- Finite State Machine (FSM) for signal phase transitions.
- 2D raster primitive rendering (`rect`, `circle`) for signal hardware.
- Painter-style layering inside each signal element (housing, lamps, glow).
