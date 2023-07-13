# I used this file to convert the CSVs generated in byte_converter.py into png images.
# This file is not needed in final build.

from PIL import Image
import numpy as np
import os


def convert_csv_to_png(csv_file, png_file):
    # Load the CSV file as a NumPy array
    sprite_array = np.loadtxt(csv_file, delimiter=",", dtype=int)

    # Create a PIL image from the sprite array
    image_data = np.uint8(np.where(sprite_array == 1, 0, 255))
    image = Image.fromarray(image_data, mode='L')

    # Save the image as PNG
    image.save(png_file)


# Directory where the CSV files are located
csv_directory = "sprites_csv"

# Directory where the PNG files will be saved
png_directory = "sprites_png"

# Create the PNG directory if it doesn't exist
os.makedirs(png_directory, exist_ok=True)

# Iterate over CSV files and convert them to PNG
for filename in os.listdir(csv_directory):
    if filename.endswith(".csv"):
        csv_file = os.path.join(csv_directory, filename)
        png_file = os.path.join(png_directory, filename[:-4] + ".png")
        convert_csv_to_png(csv_file, png_file)
        print(f"Converted {csv_file} to {png_file}")
