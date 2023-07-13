from __future__ import annotations

import numpy as np
import os
import platform
import pygame
import random
import sys

from PIL import Image
from typing import List, Tuple, Union

from pygame.locals import QUIT, MOUSEBUTTONUP, USEREVENT

if platform.system() == "Windows":
    os.environ["SDL_VIDEODRIVER"] = "windib"

Screen = pygame.Surface
UserEvent = int

AGE_HATCH = 128
AGE_MATURE = 796
AGE_DEATHFROMNATURALCAUSES = 8192
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
BTN_BORDER_COLOR = (128, 12, 24)
BTN_CENTER_COLOR = (200, 33, 44)

FPS = 30
SECOND = 1000
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 520


def load_sprite(filename: str) -> np.array:
    image = Image.open(filename)
    image_array = np.array(image)
    return image_array


def load_animation_sprites(sprite_folder: str, num_frames: int) -> List[np.array]:
    sprite_images = []
    for frame in range(num_frames):
        filename = os.path.join(sprite_folder, f"{frame}.png")
        sprite_image = load_sprite(filename)
        sprite_images.append(sprite_image)
    return sprite_images


# SPRITES
# Animations
sprite_folder = "sprites"

# Eggs
egg_folder = os.path.join(sprite_folder, "eggs", "egg1")  # TODO: Add more variants.
IDLE_EGG = load_animation_sprites(egg_folder, 2)

# Babies
baby_folder = os.path.join(sprite_folder, "babies", "baby1")
IDLE_BABY = load_animation_sprites(os.path.join(baby_folder, "sleep"), 2)
SLEEP_BABY = load_animation_sprites(os.path.join(baby_folder, "idle"), 2)

# Children
child_folder = os.path.join(sprite_folder, "children", "child1")
IDLE_CHILD = load_animation_sprites(os.path.join(child_folder, "idle"), 2)
SLEEP_CHILD = load_animation_sprites(os.path.join(child_folder, "sleep"), 2)

# Teen
# ...
# Adult
# ...
# Special
# ...

# Overlays
overlay_folder = os.path.join(sprite_folder, "overlay")
OVERLAY_ZZZ = load_animation_sprites(os.path.join(overlay_folder, "OVERLAY_ZZZ"), 2)
OVERLAY_EAT = load_animation_sprites(os.path.join(overlay_folder, "EAT", "apple"), 6)  # TODO: Add more foods
OVERLAY_STINK = load_animation_sprites(os.path.join(overlay_folder, "OVERLAY_STINK"), 2)
OVERLAY_DEAD = load_animation_sprites(os.path.join(overlay_folder, "OVERLAY_DEAD"), 2)
OVERLAY_EXCLAIM = load_animation_sprites(os.path.join(overlay_folder, "OVERLAY_EXCLAIM"), 2)
OVERLAY_CLEAN = load_sprite(os.path.join(sprite_folder, "OVERLAY", "OVERLAY_CLEAN.png"))

# Components
SELECTOR = load_sprite(os.path.join(sprite_folder, "components", "SELECTOR.png"))
FEED = load_sprite(os.path.join(sprite_folder, "components", "FEED.png"))
FLUSH = load_sprite(os.path.join(sprite_folder, "components", "FLUSH.png"))
HEALTH = load_sprite(os.path.join(sprite_folder, "components", "HEALTH.png"))
ZZZ = load_sprite(os.path.join(sprite_folder, "components", "ZZZ.png"))
DISPLAY_HUNGER = load_sprite(os.path.join(sprite_folder, "components", "DISPLAY_HUNGER.png"))
DISPLAY_ENERGY = load_sprite(os.path.join(sprite_folder, "components", "DISPLAY_ENERGY.png"))
DISPLAY_WASTE = load_sprite(os.path.join(sprite_folder, "components", "DISPLAY_WASTE.png"))
DISPLAY_AGE = load_sprite(os.path.join(sprite_folder, "components", "DISPLAY_AGE.png"))
DISPLAY_BACK = load_sprite(os.path.join(sprite_folder, "components", "DISPLAY_BACK.png"))


def bitor(
    current_frame: Tuple[int, ...], overlay_frame: Tuple[int, ...]
) -> Tuple[int, ...]:
    bit_list: List[int] = []
    for i in range(32):
        bit = current_frame[i] | overlay_frame[i]
        bit_list.append(bit)
    return tuple(bit_list)


def get_bits(number: int, num_bits: int) -> List[int]:
    """Solution from http://stackoverflow.com/questions/16659944/iterate-between-bits-in-a-binary-number"""
    return [(number >> bit) & 1 for bit in range(num_bits - 1, -1, -1)]


def render_display(
    screen: pygame.Surface,
    image_data: np.ndarray,
    fg_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int],
    off=0,
    percv=0,
) -> None:
    # TODO: update to take in bits from images.
    for y in range(32):
        for x in range(off, 32 + off):
            color = bg_color
            if x in range(len(image_data[y])):
                if not image_data[y][x]:
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
            pixels[x][y] = fg_color if not bit else bg_color
    del pixels


def do_random_event(pet: dict) -> None:
    num = random.randint(0, 31)
    if num == 12:
        pet["hunger"] += 1
    elif num == 16:
        pet["energy"] -= 1
    elif num == 18:
        pet["energy"] += 1
    elif num == 20:
        pet["waste"] += 1
    elif num == 7:
        pet["happiness"] += 1
    elif num == 4:
        pet["happiness"] -= 1


def do_cycle(pet: dict) -> None:
    # TODO: hunger/waste/energy shouldn't decrease as egg, should be higher as baby.
    do_random_event(pet)
    pet["hunger"] += 1
    pet["waste"] += 1
    pet["energy"] -= 1
    pet["age"] += 2
    if pet["waste"] >= WASTE_EXPUNGE:
        pet["happiness"] -= 1


def get_offset() -> int:
    return random.randint(-3, 2)


def get_next_frame(animation_frames: List[Tuple[int, ...]], current_frame: int) -> int:
    return (current_frame + 1) % len(animation_frames)


def trigger_death(stage: int) -> Tuple[int, int, bool, bool]:
    if stage == 1:
        current_anim = SLEEP_BABY
    elif stage == 2:
        current_anim = SLEEP_CHILD
    overlay_anim = OVERLAY_DEAD
    return current_anim, overlay_anim, True, True


def trigger_sleep(stage: int) -> Tuple[int, int, bool, bool]:
    if stage == 1:
        current_anim = SLEEP_BABY
    elif stage == 2:
        current_anim = SLEEP_CHILD
    overlay_anim = OVERLAY_ZZZ
    return current_anim, overlay_anim, True, True


def update_page(spid: int) -> int:
    if spid == 0:
        stats_page = DISPLAY_HUNGER
    elif spid == 1:
        stats_page = DISPLAY_AGE
    elif spid == 2:
        stats_page = DISPLAY_WASTE
    elif spid == 3:
        stats_page = DISPLAY_ENERGY
    elif spid == 4:
        stats_page = DISPLAY_BACK
    return stats_page


def get_button_at_pixel(x: int, y: int) -> Union[int, None]:
    if 420 < y < 484:
        button = 0
        for i in range(0, 288, 96):
            if 64 + 1 < x < 128 + 1:
                return button
            else:
                button += 1
    return None


def render_buttons(screen: pygame.Surface, left: int, top: int) -> None:
    for i in range(0, 288, 96):
        pygame.draw.ellipse(screen, BTN_BORDER_COLOR, (left + i, top, 64, 64))
        pygame.draw.ellipse(screen, BTN_CENTER_COLOR, (left + i + 4, top + 4, 56, 56))
        pygame.draw.ellipse(screen, PIXEL_COLOR, (left + i, top, 64, 64), 1)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen: Screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    pygame.display.set_caption("Tamagotchi")
    font = pygame.font.SysFont("Arial", 14)
    selector_img = pygame.Surface((32, 32)).convert_alpha()
    render_component(selector_img, SELECTOR, PIXEL_COLOR, TRANSPARENT_COLOR)
    pygame.time.set_timer(USEREVENT + 1, SECOND)

    # Tamagotchi
    pet: dict[str, int] = {
        "hunger": 0,
        "energy": 256,
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

    current_anim: int = IDLE_EGG
    overlay_anim: int = OVERLAY_ZZZ
    stats_page: int = DISPLAY_HUNGER

    # Game loop
    while True:
        screen.fill(BG_COLOR)
        mousex: int = 0
        mousey: int = 0

        # Event handler
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
            elif event.type == USEREVENT + 1:
                if cleaning:
                    pygame.time.set_timer(USEREVENT + 1, int(SECOND / 10))
                update_game = True

        # Buttons logic
        # TODO: Remove buttons.
        button = get_button_at_pixel(mousex, mousey)
        if button == 0:
            if stats:
                spid -= 1
                if spid <= -1:
                    spid = 4
                stats_page = update_page(spid)
            else:
                selid -= 1
                if selid <= -1:
                    selid = 3
        elif button == 1:
            if stage > 0 or selid == 2:
                if selid == 0:
                    eating = True
                    overlay_anim = OVERLAY_EAT
                    ol_frame = 0
                    has_overlay = True
                elif selid == 1:
                    cleaning = True
                    overlay_anim = OVERLAY_CLEAN
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
        elif button == 2:
            if stats:
                spid += 1
                spid %= 5
                stats_page = update_page(spid)
            else:
                selid += 1
                selid %= 4

        # Game logic
        if update_game:
            if stage == 0 and pet["age"] > AGE_HATCH:
                stage += 1
                current_anim = IDLE_BABY
                has_overlay = False
            if stage == 1 and pet["age"] > AGE_MATURE:
                stage += 1
                current_anim = IDLE_CHILD
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
                        current_anim = IDLE_EGG
                    elif stage == 1:
                        current_anim = IDLE_BABY
                    elif stage == 2:
                        current_anim = IDLE_CHILD
            if cleaning:
                off -= 1
                if off == -33:
                    off = 0
                    # cleanincr = 0  # Never used.
                    cleaning = False
                    has_overlay = False
                    pet["waste"] = 0
                    pygame.time.set_timer(USEREVENT + 1, SECOND)
            else:
                if not dead:
                    frame = get_next_frame(current_anim, frame)
                    off = get_offset()
                    do_cycle(pet)
                    if pet["energy"] < ENERGY_PASSOUT and stage > 0:
                        pet["happiness"] -= 64
                        current_anim, overlay_anim, sleeping, has_overlay = trigger_sleep(stage)

            if not any([sleeping, cleaning, eating, dead]):
                if pet["waste"] >= WASTE_EXPUNGE:
                    overlay_anim = OVERLAY_STINK
                    has_overlay = True
                elif (
                    pet["energy"] <= ENERGY_TIRED
                    or pet["hunger"] >= HUNGER_NEEDSTOEAT
                    or pet["waste"] >= WASTE_EXPUNGE - WASTE_EXPUNGE / 3
                ):
                    overlay_anim = OVERLAY_EXCLAIM
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
        zipped = zip([FEED, FLUSH, HEALTH, ZZZ], [i for i in range(64, 320, 64)])
        z = list(zipped)
        for i in range(len(z)):
            img = pygame.Surface((32, 32))
            render_component(img, z[i][0], PIXEL_COLOR, NONPIXEL_COLOR)
            screen.blit(pygame.transform.flip(img, True, False), (z[i][1], 16))

        # Render selector
        screen.blit(
            pygame.transform.flip(selector_img, True, False), (64 + (selid * 64), 16)
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
                animation = bitor(current_anim[frame], overlay_anim[ol_frame])
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

        # Render buttons
        render_buttons(screen, 64, 420)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
