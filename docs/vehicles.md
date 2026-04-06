# vehicles.py Documentation

## File Purpose
Defines vehicle geometry, movement rules, emergency behavior, collision spacing, and vehicle drawing.

## Functions And Classes In This File

### _new_id()
- Generates unique vehicle IDs.

### class Vehicle

#### __init__(direction, kind="car")
- Initializes vehicle type, speed profile, dimensions, and spawn position.

#### _lane_center()
- Returns lane center coordinate for current direction.

#### _yield_side_sign()
- Returns preferred lateral offset side for emergency yielding.

#### front()
- Leading-edge coordinate in travel direction.

#### rear()
- Trailing-edge coordinate in travel direction.

#### dist_to_stop_line()
- Signed distance from vehicle front to stop line.

#### gap_to_ahead(ahead)
- Bumper-to-bumper gap to leader vehicle.

#### is_off_screen()
- Checks whether vehicle has fully exited view.

#### update(stop_for_signal, ahead, emergency_stop=False, nearby_same_dir=None)
- Main motion update:
  - signal braking
  - car-following speed adaptation
  - emergency yielding behavior
  - ambulance side-path selection (left/center/right)
  - anti-overlap clamp
  - smooth speed and lateral interpolation

#### draw(surface)
- Draws vehicle body details.
- Ambulance receives special styling (stripe and lightbar).

## Computer Graphics Algorithms Used In This File
- Kinematic update with constrained acceleration/deceleration.
- Gap-based car-following heuristic.
- Lateral interpolation for smooth side shifts.
- 2D procedural vehicle rendering via raster primitives (`rect`, `circle`).
