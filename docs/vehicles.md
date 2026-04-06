# vehicles.py

## Purpose
Defines vehicle entities, movement behavior, spacing logic, and vehicle rendering.

## Global Helper
### _new_id()
Generates unique integer IDs for vehicle instances.

## Core Class
### Vehicle
Represents one moving unit (car or ambulance) in a single travel direction.

## Key Responsibilities
- spawn at direction-specific road entry,
- compute front/rear geometry helpers,
- compute stop-line distance and leader gap,
- update speed and position each frame,
- render itself to the screen.

## Important Methods
### __init__(direction, kind="car")
Initializes identity, type, speed profile, dimensions, and start position.

### update(stop_for_signal, ahead, emergency_stop=False, nearby_same_dir=None)
Main motion routine.

For regular cars:
- stop-line braking when required,
- follow leader speed/gap,
- emergency yielding behavior.

For ambulance:
- evaluate center/left/right offsets,
- choose best forward-gap side path,
- follow side-path leader safely,
- apply overlap safety clamp.

### draw(surface)
Renders body, roof, windshield, and lights.
Ambulance adds stripe and lightbar styling.

## Geometry Helpers
- `_lane_center()`
- `_yield_side_sign()`
- `front()`
- `rear()`
- `dist_to_stop_line()`
- `gap_to_ahead(ahead)`
- `is_off_screen()`

## Techniques Used
- Kinematic speed interpolation with acceleration/deceleration limits.
- Gap-based following for collision avoidance.
- Lateral offset interpolation for smooth side movement.
- Primitive-shape raster rendering for vehicle visuals.
