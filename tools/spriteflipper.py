# All of the original sprites were h-flipped. this file flipped all pngs.
# This file is not needed in final build.

from PIL import Image
import os

# Specify the folder containing the images
folder_path = "sprites_png"

# Loop through the images in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".png"):
        # Load the image
        image_path = os.path.join(folder_path, filename)
        image = Image.open(image_path)

        # Flip the image horizontally
        flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)

        # Overwrite the original image
        flipped_image.save(image_path)

        print(f"Flipped and overwritten {filename}.")

print("Flipping and overwriting complete.")
