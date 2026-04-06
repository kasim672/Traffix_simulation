# =============================================================================
#  main.py  –  Entry point: game loop, events, FPS control
# =============================================================================
"""
Real-Time Traffic Simulation
─────────────────────────────
Run:
    python main.py

Controls:
    P          →  Pause / Resume
    A          →  Call emergency ambulance
    N / E / S / W  →  Set GREEN signal to North / East / South / West
    R          →  Resume automatic signal cycle
    + / UP     →  Speed up simulation
    - / DOWN   →  Slow down simulation
    ESC / Q    →  Quit
"""

import sys
import pygame

from constants  import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, NORTH, EAST, SOUTH, WEST
from simulation import Simulation
from renderer   import Renderer


def main():
    # ── Pygame initialisation ────────────────────────────────────────────────
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # Optional: nicer window icon (plain coloured surface fallback)
    icon = pygame.Surface((32, 32))
    icon.fill((50, 52, 60))
    pygame.draw.circle(icon, (45, 215, 80), (16, 16), 10)
    pygame.display.set_icon(icon)

    clock    = pygame.time.Clock()
    sim      = Simulation()
    renderer = Renderer(screen)

    # Smooth FPS average for the HUD display
    fps_smooth = float(FPS)
    fps_alpha  = 0.05   # smoothing factor

    # ── Main loop ────────────────────────────────────────────────────────────
    running = True
    while running:

        # dt is the real elapsed wall-clock time since the last frame (seconds)
        dt = clock.tick(FPS) / 1000.0
        # Clamp dt to prevent huge jumps (e.g. after OS suspend)
        dt = min(dt, 0.05)

        # Smooth FPS counter
        if dt > 0:
            fps_smooth = fps_smooth * (1 - fps_alpha) + (1 / dt) * fps_alpha

        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                key = event.key

                # Quit
                if key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

                # Pause / Resume
                elif key == pygame.K_p:
                    sim.toggle_pause()

                # Emergency ambulance
                elif key == pygame.K_a:
                    sim.trigger_ambulance()

                # Manual signal controls (one direction green)
                elif key == pygame.K_n:
                    sim.set_signal_green(SOUTH)
                elif key == pygame.K_e:
                    sim.set_signal_green(WEST)
                elif key == pygame.K_s:
                    sim.set_signal_green(NORTH)
                elif key == pygame.K_w:
                    sim.set_signal_green(EAST)
                elif key == pygame.K_r:
                    sim.set_signal_auto(True)

                # Speed up
                elif key in (pygame.K_PLUS, pygame.K_EQUALS,
                             pygame.K_KP_PLUS, pygame.K_UP):
                    sim.increase_speed()

                # Speed down
                elif key in (pygame.K_MINUS, pygame.K_KP_MINUS,
                             pygame.K_DOWN):
                    sim.decrease_speed()

        # ── Simulation step ──────────────────────────────────────────────────
        sim.update(dt)

        # ── Render ───────────────────────────────────────────────────────────
        renderer.draw_frame(sim, fps_smooth)
        pygame.display.flip()

    # ── Clean-up ─────────────────────────────────────────────────────────────
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
