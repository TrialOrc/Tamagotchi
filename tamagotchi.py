from __future__ import annotations

import numpy as np
import os
import platform
import pygame
import random
import sys

from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_DOWN, K_RIGHT, USEREVENT

import sprite_handler as sh

from typing import List, Tuple


if platform.system() == "Windows":
    os.environ["SDL_VIDEODRIVER"] = "windib"

Screen = pygame.Surface
UserEvent = int

# Used "y = round((98.3415 * x + 128) / 8) * 8" to plot ages, subject to change for balancing.
AGE_HATCH = 128
AGE_CHILD = 816  # Original: 796. Appx. 7 yo
AGE_TEEN = 1408  # Appx. 13 yo
AGE_ADULT = 2584  # Appx 25 yo
AGE_SPECIAL = 5048  # Appx 50 yo
AGE_DEATHFROMNATURALCAUSES = 8192  # Appx. 82 yo, original number

HUNGER_CANEAT = 32
HUNGER_NEEDSTOEAT = 128
HUNGER_SICKFROMNOTEATING = 256
HUNGER_DEADFROMNOTEATING = 512
ENERGY_CANSLEEP = 150
ENERGY_TIRED = 64
ENERGY_PASSOUT = 8
WASTE_EXPUNGE = 256

BG_COLOR = (160, 178, 129)
PIXEL_COLOR = (10, 12, 6)
NONPIXEL_COLOR = (156, 170, 125)
TRANSPARENT_COLOR = (0, 0, 0, 0)

FPS = 30
SECOND = 1000
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 400


def render_display(
    screen: pygame.Surface,
    image_data: np.ndarray,
    fg_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int],
    off=0,
    percv=0,
) -> None:
    for y in range(32):
        for x in range(off, 32 + off):
            color = bg_color
            if x in range(len(image_data[y])):
                if image_data[y][x] or (percv > 0 and 11 < y < 17 and 2 < x < 3 + percv):
                    color = fg_color
            pygame.draw.rect(screen, color, ((x - off) * 10 + 32, y * 10 + 64, 8, 8))


def render_component(
    surface: Screen,
    image_data: np.ndarray,
    fg_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int] = (255, 255, 255),
) -> None:
    pixels = pygame.PixelArray(surface)
    for y in range(surface.get_height()):
        for x, bit in enumerate(image_data[y]):
            pixels[x][y] = fg_color if bit else bg_color
    del pixels


def do_cycle(pet: dict, stage: int) -> None:
    pet["age"] += 2
    if stage != 0:
        choice = random.choice(["hunger", "energy", "energy", "waste", "happiness", "happiness"])
        if random.randint(0, 31) < 5:
            if choice in ("energy", "happiness"):
                pet[choice] += random.choice([-2, 0])
            else:
                pet[choice] += 2

        if choice != "hunger":
            pet["hunger"] += 1
        if choice != "waste":
            pet["waste"] += 1
        if choice != "energy":
            pet["energy"] -= 1

        if pet["waste"] >= WASTE_EXPUNGE:
            pet["happiness"] -= 1


def get_offset(off: int) -> int:
    if -3 <= off <= 3:
        return random.choice([-1, 0, 1]) + off
    elif off < -3:
        return random.choice([0, 1]) + off
    else:
        return random.choice([-1, 0]) + off


def get_next_frame(animation_frames: List[np.ndarray], current_frame: int) -> int:
    return (current_frame + 1) % len(animation_frames)


def trigger_death(stage: int) -> Tuple[int, int, bool, bool]:
    if stage == 1:
        current_anim = sh.SLEEP_BABY
    elif stage == 2:
        current_anim = sh.SLEEP_CHILD
    overlay_anim = sh.OVERLAY_DEAD
    return current_anim, overlay_anim, True, True


def trigger_sleep(stage: int) -> Tuple[int, int, bool, bool]:
    if stage == 1:
        current_anim = sh.SLEEP_BABY
    elif stage == 2:
        current_anim = sh.SLEEP_CHILD
    overlay_anim = sh.OVERLAY_ZZZ
    return current_anim, overlay_anim, True, True


def update_page(spid: int) -> int:
    if spid == 0:
        stats_page = sh.DISPLAY_HUNGER
    elif spid == 1:
        stats_page = sh.DISPLAY_AGE
    elif spid == 2:
        stats_page = sh.DISPLAY_WASTE
    elif spid == 3:
        stats_page = sh.DISPLAY_ENERGY
    elif spid == 4:
        stats_page = sh.DISPLAY_BACK
    return stats_page


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen: Screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption("Tamagotchi")
    font = pygame.font.SysFont("Arial", 14)
    selector_img = pygame.Surface((32, 32)).convert_alpha()
    render_component(selector_img, sh.SELECTOR, PIXEL_COLOR, TRANSPARENT_COLOR)
    pygame.time.set_timer(USEREVENT + 1, SECOND)

    # Tamagotchi
    pet: dict[str, int] = {
        "hunger": 0,
        "energy": 8,
        "waste": 0,
        "age": 0,
        "happiness": 0,
    }

    # Counters
    # off is the horizontal offset
    off: int = 0
    # selid is the selected button
    selid: int = 0  # TODO: Remove when buttons have been removed.
    # spid is the selected page
    spid: int = 0  # TODO: This will probably need to be modified.
    stage: int = 0
    frame: int = 0
    ol_frame: int = 0

    # Flags
    stats: bool = False
    has_overlay: bool = False
    cleaning: bool = False
    eating: bool = False
    stats: bool = False
    sleeping: bool = False
    dead: bool = False
    update_game: bool = False

    current_anim: int = sh.IDLE_EGG
    overlay_anim: int = sh.OVERLAY_ZZZ
    stats_page: int = sh.DISPLAY_HUNGER

    # Game loop
    while True:
        screen.fill(BG_COLOR)

        # Event handler
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    if stats:
                        spid -= 1
                        if spid <= -1:
                            spid = 4
                        stats_page = update_page(spid)
                    else:
                        selid -= 1
                        if selid <= -1:
                            spid = 4
                        stats_page = update_page(spid)
                elif event.key == K_DOWN:
                    if stage > 0 or selid == 2:
                        if selid == 0:
                            eating = True
                            overlay_anim = sh.OVERLAY_EAT
                            ol_frame = 0
                            has_overlay = True
                        elif selid == 1:
                            cleaning = True
                            overlay_anim = sh.OVERLAY_CLEAN
                            ol_frame = 0
                            has_overlay = True
                        elif selid == 2:
                            stats = not stats
                        elif selid == 3:
                            if pet["energy"] <= ENERGY_CANSLEEP:
                                (
                                    current_anim,
                                    overlay_anim,
                                    sleeping,
                                    has_overlay,
                                ) = trigger_sleep(stage)
                elif event.key == K_RIGHT:
                    if stats:
                        spid += 1
                        spid %= 5
                        stats_page = update_page(spid)
                    else:
                        selid += 1
                        selid %= 4
            elif event.type == USEREVENT + 1:
                if cleaning:
                    pygame.time.set_timer(USEREVENT + 1, int(SECOND / 10))
                update_game = True

        # Game logic
        if update_game:
            if stage == 0 and pet["age"] > AGE_HATCH:
                stage += 1
                current_anim = sh.IDLE_BABY
                has_overlay = False
            if stage == 1 and pet["age"] > AGE_CHILD:
                stage += 1
                current_anim = sh.IDLE_CHILD
            if eating and ol_frame == len(overlay_anim) - 1:
                eating = False
                has_overlay = False
                ol_frame = 0
                pet["hunger"] = 0
            if sleeping:
                pet["energy"] += 8
                if pet["energy"] >= 256:
                    sleeping = False
                    has_overlay = False
                    if stage == 0:
                        current_anim = sh.IDLE_EGG
                    elif stage == 1:
                        current_anim = sh.IDLE_BABY
                    elif stage == 2:
                        current_anim = sh.IDLE_CHILD
            if cleaning:
                off -= 1
                if off == -33:
                    off = 0
                    cleaning = False
                    has_overlay = False
                    pet["waste"] = 0
                    pygame.time.set_timer(USEREVENT + 1, SECOND)
            else:
                if not dead:
                    frame = get_next_frame(current_anim, frame)
                    off = get_offset(off)
                    do_cycle(pet, stage)
                    if pet["energy"] < ENERGY_PASSOUT and stage > 0:
                        pet["happiness"] -= 64
                        current_anim, overlay_anim, sleeping, has_overlay = trigger_sleep(stage)

            if not any([sleeping, cleaning, eating, dead]):
                if pet["waste"] >= WASTE_EXPUNGE:
                    overlay_anim = sh.OVERLAY_STINK
                    has_overlay = True
                elif (
                    pet["energy"] <= ENERGY_TIRED
                    or pet["hunger"] >= HUNGER_NEEDSTOEAT
                    or pet["waste"] >= WASTE_EXPUNGE - WASTE_EXPUNGE / 3
                ):
                    overlay_anim = sh.OVERLAY_EXCLAIM
                    has_overlay = True
                if not dead and (
                        pet["hunger"] >= HUNGER_DEADFROMNOTEATING
                        or pet["age"] >= AGE_DEATHFROMNATURALCAUSES
                ):
                    off = 3
                    current_anim, overlay_anim, dead, has_overlay = trigger_death(stage)

            if has_overlay:
                ol_frame = get_next_frame(overlay_anim, ol_frame)
            update_game = False

        # Render components
        zipped = zip([sh.FEED, sh.FLUSH, sh.HEALTH, sh.ZZZ], [i for i in range(79, 335, 64)])
        z = list(zipped)
        for i in range(len(z)):
            img = pygame.Surface((32, 32))
            render_component(img, z[i][0], PIXEL_COLOR, NONPIXEL_COLOR)
            screen.blit(pygame.transform.flip(img, True, False), (z[i][1], 16))

        # Render selector
        screen.blit(
            pygame.transform.flip(selector_img, True, False), (79 + (selid * 64), 16)
        )

        # Render display
        if stats:
            if spid == 0:
                percv = pet["hunger"] * 27 / HUNGER_NEEDSTOEAT
            elif spid == 1:
                percv = pet["age"] * 27 / AGE_DEATHFROMNATURALCAUSES
            elif spid == 2:
                percv = (pet["waste"] % WASTE_EXPUNGE) * 27 / WASTE_EXPUNGE
            elif spid == 3:
                percv = pet["energy"] * 27 / 256
            elif spid == 4:
                percv = 0
            if percv > 27:
                percv = 27
            render_display(screen, stats_page, PIXEL_COLOR, NONPIXEL_COLOR, 0, percv)
        else:
            if has_overlay:
                animation = np.bitwise_or(current_anim[frame], overlay_anim[ol_frame])
            else:
                animation = current_anim[frame]
            render_display(screen, animation, PIXEL_COLOR, NONPIXEL_COLOR, off)

        # Render debug
        surf = font.render("DEBUG --", True, PIXEL_COLOR)
        screen.blit(surf, (360, 60))
        debug = (
            ("AGE: %s", "HUNGER: %s", "ENERGY: %s", "WASTE: %d", "HAPPINESS: %s"),
            ("age", "hunger", "energy", "waste", "happiness"),
        )
        for pos, y in enumerate(i for i in range(70, 120, 10)):
            surf = font.render(debug[0][pos] % pet[debug[1][pos]], True, PIXEL_COLOR)
            screen.blit(surf, (360, y))

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
