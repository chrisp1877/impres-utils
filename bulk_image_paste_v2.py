from easygui import *
import time
import threading
import os, sys, glob
from PIL import Image, ImageTk, ImageQt
from typing import List\

while 1:
    greeting = """
    Welcome to the Impresys ultra-simple image bulk pasting tool.
    Would you like to insert many images into a single background image,
    or insert a single image into many different images?
    """
    greeting_title = "Impresys bulk pasting tool"
    greeting_choices = [
        "Wrap many images in larger background (shelling)",
        "Insert smaller image into many larger images (insertion)"
    ]
    choice = choicebox(greeting, greeting_title, choices=greeting_choices)
    # choice = variable determinig whether performing shelling or bulk image insertion

    print(choice)
    if choice == greeting_choices[0]: # --> USER SELECTED SHELLING
        image_field_msg = """
            Enter the location of both the asset folder as well as the image used for
            background/shelling. Enter the location on the background where the assets
            should be located (measured from the top left corner), and their final dimensions after being resized.
        """
        image_fields=[
            "Assets folder directory:",
            "Background (shelling) image file location:",
            "Asset image placement (x, pixels):", #where on BG image assets will be placed going right from top left
            "Asset image placement (y, pixels):", #where on BG image assets will be placed going down from top left
            "Assets final size (width, pixels):", #how wide should asset final size be counting from the x position specified
            "Assets final size (height, pixels):" #how tall should asset final size be counting from the y position specified
        ]
    else: # --> USER SELECTED INSERTION
        image_field_msg = """
            Enter the location of both the asset folder as well as the image to be inserted
            onto the assets. Enter the location on the assets where the image to be inserted
            should be located (measured from the top left corner), and its final dimensions after being resized.
        """
        image_fields=[
            "Assets folder directory:",
            "Insertion image file location:",
            "Insert image placement (x, pixels):",
            "Insert image placement (y, pixels):",
            "Insert image final size (width, pixels):",
            "Insert image final size (height, pixels):" 
        ]
    image_vals = []
    image_vals = multenterbox(image_field_msg,  title="Enter image data:",  fields = image_fields, values=image_vals)
    print("Image_vals: ", image_vals)

    def bulk_paste(image_vals: List[int], choice: str):
        '''
        Usage: In script folder, open terminal and run python main.py {demo asset folder}
        '''
        path = image_vals[0]
        img = Image.open(image_vals[1])
        fg_img_size = (int(image_vals[4]), int(image_vals[5]))
        fg_img_loc = (int(image_vals[2]), int(image_vals[3]))
        print("New image size: ", fg_img_size)
        print("fg image loc: ", fg_img_loc)
        for subdir, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.Png'):
                    new_path = os.path.join(subdir, file)
                    asset_img = Image.open(new_path)
                    if choice == greeting_choices[0]:
                        bg_copy = img.copy()
                        asset_img_resize = asset_img.resize((fg_img_size), Image.ANTIALIAS)
                        bg_copy.paste(asset_img_resize, fg_img_loc)
                        bg_copy.save(new_path, quality=100)
                        print("Finished: " + new_path + " shelling.")
                    else:
                        fg_copy = img.copy()
                        fg_img_resize = fg_copy.resize((fg_img_size), Image.ANTIALIAS)
                        asset_img.paste(fg_img_resize, fg_img_loc)
                        asset_img.save(new_path, quality=100)
                        print("Finished: " + new_path + " insertion.")

            
    bulk_paste(image_vals, choice)

    msg_ex = "Do you want to perform more actions? (Cancel to quit)"
    title_ex = "Continue or cancel"
    if ccbox(msg_ex, title_ex):     # show a Continue/Cancel dialog
        pass  # user chose Continue
    else:
        sys.exit(0)           # user chose Cancel

# from tkinter import *

# Location of the image to be 'bordered' in the background tablet/phone shell
# IMAGE_LOC[0] is horizontal x distance, IMAGE_LOC[1] is the vertical y distance,
# with the uppermost leftmost point of the image as the origin
"""
IMAGE_LOC = (240, 96)
IMAGE_RES = (1920, 1080)
SCREEN_NEW_SIZE = (1438, 894) #size of screen after resize

# File locations i


"""