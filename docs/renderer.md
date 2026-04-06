# renderer.py Documentation

## File Purpose
Handles all visual rendering: environment, road markings, signals, vehicles, and HUD.

## Classes And Functions In This File

### class Renderer

#### __init__(screen)
- Stores target surface, loads fonts, and prebuilds static road surface.

#### _load_fonts()
- Initializes font resources for HUD and overlays.

#### _build_road_surface()
- Pre-renders static scene layers:
  - grass texture
  - sidewalks/curbs
  - roads/intersection
  - lane dashes
  - stop lines
  - zebra crossings
  - edge lines
  - direction arrows

#### _draw_arrows(surf)
- Places directional arrow hints on road arms.

#### _draw_single_arrow(surf, cx, cy, direction, color, size=10)
- Draws one filled directional arrow polygon.

#### draw_frame(sim, fps)
- Main frame render order:
  - static road
  - signal posts
  - vehicles
  - HUD
  - pause overlay (if paused)

#### _draw_hud(sim, fps)
- Draws simulation information panel, progress bars, metrics, direction counts, and controls list.

#### _draw_pause_overlay()
- Draws translucent pause screen overlay and text.

## Computer Graphics Algorithms Used In This File
- Painter's algorithm (draw order layering).
- Procedural raster geometry using primitive shapes and lines.
- Surface caching optimization (pre-render static road to avoid per-frame recomputation).
