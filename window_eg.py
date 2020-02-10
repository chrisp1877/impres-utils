from easygui import *
import os, sys, glob
from PIL import Image, ImageTk, ImageQt


greeting = """
Welcome to the Impresys ultra-simple image bulk pasting tool.
Would you like to insert many images into a single background image,
or insert a single image into many different images?
"""
greeting_title = "Impresys bulk pasting tool"
greeting_choices = [
    "Wrap many images in larger background (shelling)",
    "Insert smaller image into many larger images"
]
choice = choicebox(greeting, greeting_title, choices=greeting_choices)
assets = diropenbox("Select assets directory (foreground image)")
bg_prompt_msg = """
Please select the image you would like serve as the background
image for the images contained in the assets folder you just selected.
"""
bg_img = fileopenbox("Select background image (background image)")

if choice == "Wrap many images in larger background (shelling)":
    image_msg = """
    Enter the location on the background where the assets should be located (measured from the top left corner),
    and their final dimensions after being resized.
    """
    image_fields=[
        "Assets location (x, pixels):", #where on BG image assets will be placed going right from top left
        "Assets location (y, pixels):", #where on BG image assets will be placed going down from top left
        "Assets final size (width, pixels):", #how wide should asset final size be counting from the x position specified
        "Assets final size (height, pixels):" #how tall should asset final size be counting from the y position specified
    ]
else:
    image_msg = """
    Enter the location on the background where the inserted image should be located on the assets (measured from
    the top left corner) and its final dimension after being resized:
    """
    image_fields=[
        "Inserted image location (x, pixels):",
        "Inserted image location (y, pixels):",
        "Inserted image final size (width, pixels):",
        "Inserted image final size (ehgith, pixels):"
    ]
image_vals = []
image_props = multenterbox(image_msg, title="Enter image data:",  fields = image_fields, values=image_vals)

def bulk_paste(assets_path: str, image_path: str, image_vals: list(int)):
    '''
    Usage: In script folder, open terminal and run python main.py {demo asset folder}
    '''
    path = assets_path
    bg_img = Image.open(image_path)
    bg_img.show()
    new_image_size = (image_vals[2], image_vals[3])
    fg_image_loc = (image_vals[0], image_vals[1])

    for subdir, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.Png'):
                new_path = os.path.join(subdir, file)
                print(new_path)
                
                img = Image.open(new_path)
                bg_copy = bg_img.copy()
                img_resize = img.resize((new_image_size), Image.ANTIALIAS)
                bg_copy.paste(img_resize, fg_image_loc)
                bg_copy.save(new_path, quality=100)
                print("Finished: " + new_path)

        
bulk_paste(assets, bg_img, image_props)

msg_ex = "Do you want to continue?"
title_ex = "Please Confirm"
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