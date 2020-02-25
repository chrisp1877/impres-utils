import os, sys, glob
from PIL import Image
from typing import List
# from tkinter import *

# Location of the image to be 'bordered' in the background tablet/phone shell
# IMAGE_LOC[0] is horizontal x distance, IMAGE_LOC[1] is the vertical y distance,
# with the uppermost leftmost point of the image as the origin
IMAGE_LOC = (240, 96)
IMAGE_RES = (1920, 1080)
SCREEN_NEW_SIZE = (1438, 894) #size of screen after resize

# File locations i
ASSET_PATH = r"C:\Users\impresys\Documents\Projects\impresys-utils\demo\cfs_final.demo_Assets"
BG_IMAGE_PATH = r"C:\Users\impresys\Documents\py_scripts\200205tablet\assets\tablet_bg.png"


def main(take_path_input=False, in_demo_folder=False):
    '''
    Usage: In script folder, open terminal and run python main.py {demo asset folder}
    '''
    if take_path_input: 
        os.chdir(sys.argv[1]) # --> python add_image_border.py {path\to\asset\folder}
    elif in_demo_folder:
        path = os.getcwd() # --> if place script in folder containing asset folder 
    else:
        path = ASSET_PATH

    bg_img = Image.open(BG_IMAGE_PATH)
    bg_img.show()

    for subdir, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.Png'):
                new_path = os.path.join(subdir, file)
                print(new_path)
                
                img = Image.open(new_path)
                bg_copy = bg_img.copy()
                img_resize = img.resize((SCREEN_NEW_SIZE), Image.ANTIALIAS)
                bg_copy.paste(img_resize, IMAGE_LOC)
                bg_copy.save(new_path, quality=100)
                print("Finished: " + new_path)


if __name__ == '__main__':
    main()
