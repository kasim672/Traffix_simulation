# renderer.py

## Purpose
Handles all frame rendering for the simulation.

This module draws the world, dynamic entities, and UI overlays.

## Core Class
### Renderer

## Render Pipeline
`draw_frame(sim, fps)` draws in this order:
1. prebuilt static road surface,
2. traffic signals,
3. vehicles,
4. HUD panels,
5. pause overlay.

This layering keeps visuals stable and readable.

## Main Methods
### __init__(screen)
Stores output surface, loads fonts, and caches static road artwork.

### _load_fonts()
Initializes HUD and overlay font objects.

### _build_road_surface()
Pre-renders static scene elements once:
- grass texture,
- sidewalks and curbs,
- road strips and intersection,
- lane marks,
- stop lines,
- zebra crossings,
- edge lines,
- direction arrows.

### _draw_arrows(surf)
Places directional hints on each road arm.

### _draw_single_arrow(...)
Draws one polygon arrow primitive.

### _draw_hud(sim, fps)
Draws left information panel:
- signal color/mode status,
- phase progress bar and timer,
- active/passed/time/fps metrics,
- speed multiplier and speed bar.

### _draw_controls_panel(sim)
Draws right controls/help panel and ambulance status.

### _draw_pause_overlay()
Draws translucent pause screen overlay and labels.

## Techniques Used
- Painter-style draw ordering.
- Procedural 2D raster drawing with Pygame primitives.
- Static surface caching for performance.
