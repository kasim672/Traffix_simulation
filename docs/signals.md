# signals.py

## Purpose
Defines the traffic signal controller and signal rendering.

This module is responsible for both signal state transitions and drawing the signal posts/lights on screen.

## Core Class
### TrafficSignal
A finite state machine that keeps one active approach at a time.

## State Model
- `active_direction`: currently green direction.
- `pending_direction`: next direction to become green.
- `phase`: either `GREEN` or `YELLOW_BEFORE_GREEN`.
- `timer`: elapsed time in current phase.
- `auto_cycle`: whether automatic cycling is enabled.

## Key Methods
### update(dt)
Advances signal timing and performs phase transitions.

### should_stop(direction)
Returns whether a vehicle in that direction should stop.

### set_green(direction)
Manual request for next green direction.

### set_auto_cycle(enabled)
Enables or disables automatic cycling.

### time_remaining()
Returns remaining phase time for UI display.

### progress()
Returns normalized phase progress for progress bar rendering.

### _draw_signal_box(surface, cx, cy, active_color)
Draws one traffic-light housing with 3 lamps.

### draw(surface)
Draws the four signal posts around intersection approaches.

## Techniques Used
- Finite state machine for transition logic.
- Primitive raster rendering with Pygame shapes.
- Per-lamp glow layering for active light feedback.
