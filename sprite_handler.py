from __future__ import annotations

import numpy as np

import os

from PIL import Image
from typing import List


def load_sprite(filename: str) -> np.array:
    image = Image.open(filename)
    image_array = np.array(image)
    image_array = np.where(image_array == 255, 0, 1)
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
