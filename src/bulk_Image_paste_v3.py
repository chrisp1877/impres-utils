#------------------------------------------------------#
#                  get_demo_demo.py                    #
#      gets step and demo metadata and stores          #
#      in dict for later usage in bulk edits           #
#------------------------------------------------------#

import xml.etree.ElementTree as ET
from PIL import Image
from easygui import *
import sys

def image_paste(demo_path, image_path, img_loc, img_size, typ='shell', sect='All'):
    #with open(path, mode="w", encoding="utf-8") as demo_file:
    # demo_path = vals[0]
    # img = Image.open(vals[1])
    # fg_img_size = (int(vals[4]), int(vals[5]))
    # fg_img_loc = (int(vals[2]), int(vals[3]))
    bg_img_size = (1920, 1080)
    fg_img_loc = img_loc
    fg_img_size = img_size
    if (fg_img_size[0]+fg_img_loc[0]>bg_img_size[0] or
        fg_img_size[1]+fg_img_loc[1]>bg_img_size[1]):
        raise Exception("Resized and relocated image beyond original boundaries")
    img = Image.open(image_path)
    demo = ET.parse(demo_path)
    demo_dir = demo_path.rsplit('\\', 1)[0]
    root = demo.getroot()
    for chapter in list(root.iter('Chapter')):
        section = chapter.find('XmlName').find('Name').text
        if (sect == 'All') or (section.contains(sect)):
            steps = list(chapter.iter('Step'))
            for i, step in enumerate(steps):
                asset = step.find("ID").text
                pfile = step.find("StartPicture").find("PictureFile").text
                asset_dir = step.find("StartPicture").find("AssetsDirectory").text
                impath = demo_dir + '\\' + asset_dir + pfile
                asset_img = Image.open(impath)
                new_img = img.copy()
                if typ == "shell":
                    mouse = step.find("StartPicture").find("MouseCoordinates")
                    cloc = (float(mouse.find("X").text), float(mouse.find("Y").text))
                    hspot = step.find("StartPicture").find("Hotspots").find("Hotspot")
                    cby = (float(hspot.find("Top").text), float(hspot.find("Bottom").text))
                    cbx = (float(hspot.find("Left").text), float(hspot.find("Right").text))
                    if not (cbx[1]-cbx[0]==bg_img_size[0] and cby[1]-cby[0]==bg_img_size[1]):
                        rx = float(fg_img_size[0] / bg_img_size[0])
                        ry = float(fg_img_size[1] / bg_img_size[1])
                        cloc_n = (str(cloc[0]*rx+fg_img_loc[0]), str(cloc[1]*ry+fg_img_loc[1]))
                        cby_n = (str(cby[0]*ry+fg_img_loc[1]), str(cby[1]*ry+fg_img_loc[1]))
                        cbx_n = (str(cbx[0]*rx+fg_img_loc[0]), str(cbx[1]*ry+fg_img_loc[0]))
                        step.find("StartPicture").find("MouseCoordinates").find("X").text = cloc_n[0]
                        step.find("StartPicture").find("MouseCoordinates").find("Y").text = cloc_n[1]
                        step.find("StartPicture").find("Hotspots").find("Hotspot").find("Top").text = cby_n[0]
                        step.find("StartPicture").find("Hotspots").find("Hotspot").find("Bottom").text = cby_n[1]
                        step.find("StartPicture").find("Hotspots").find("Hotspot").find("Left").text = cbx_n[0]
                        step.find("StartPicture").find("Hotspots").find("Hotspot").find("Left").text = cbx_n[1]
                    else:
                        cbx_n, cby_n = cbx, cby
                        cloc_n = cloc
                    asset_img_resize = new_img.resize((fg_img_size), Image.ANTIALIAS)
                    new_img.paste(asset_img_resize, fg_img_loc)
                    new_img.save(impath, quality=100)
                    print("SHELLED: Section: "+section+", Step: "+str(i)+", image: "+impath)
                else: #if type is insertion
                    fg_img_resize = img.resize((fg_img_size), Image.ANTIALIAS)
                    asset_img.paste(fg_img_resize, fg_img_loc)
                    asset_img.save(impath, quality=100)
                    print("INSERTED: Section: "+section+", Step: "+str(i)+", image: "+impath)
 
    demo.write(demo_path)
    sys.exit(0)

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
    choice = 'shell' if choice==greeting_choices[0] else 'insert'
    print(choice)
    if choice == 'shell': # --> USER SELECTED SHELLING
        image_field_msg = """
            Enter the location of the .demo file as well as the image used for
            background/shelling. Enter the location on the background where the assets
            should be located (measured from the top left corner), and their final dimensions after being resized.
        """
        image_fields=[
            ".demo file location:",
            "Background (shelling) image file location:",
            "Asset image placement (x, pixels):", #where on BG image assets will be placed going right from top left
            "Asset image placement (y, pixels):", #where on BG image assets will be placed going down from top left
            "Assets final size (width, pixels):", #how wide should asset final size be counting from the x position specified
            "Assets final size (height, pixels):", #how tall should asset final size be counting from the y position specified
            "Apply to sections with title containing: (leave blank for all sections)",
        ]
    else: # --> USER SELECTED INSERTION
        image_field_msg = """
            Enter the location of both the .demo file as well as the image to be inserted
            onto the assets. Enter the location on the assets where the image to be inserted
            should be located (measured from the top left corner), and its final dimensions after being resized.
        """
        image_fields=[
            ".demo file location:",
            "Insertion image file location:",
            "Insert image placement (x, pixels):",
            "Insert image placement (y, pixels):",
            "Insert image final size (width, pixels):",
            "Insert image final size (height, pixels):",
            "Apply to sections with title containing: ('All' for all sections)"
        ]
    vals = [None, None, None, None, None, None, "All"]
    vals = multenterbox(image_field_msg,  title="Enter image data:",  fields = image_fields, values=vals)
    image_paste(vals[0], vals[1], (int(vals[2]), int(vals[3])), (int(vals[4]), int(vals[5])), choice, vals[6])

# type = "shell" or "insert"


