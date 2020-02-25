#------------------------------------------------------#
#                  get_demo_demo.py                    #
#      gets step and demo metadata and stores          #
#      in dict for later usage in bulk edits           #
#------------------------------------------------------#

import xml.etree.ElementTree as ET
from PIL import Image
import sys


def image_paste(demo_path, image_path, img_loc, img_size, typ='shell', sect='All'):



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
                asset_dir =  step.find("StartPicture").find("AssetsDirectory").text
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
                        print("SHIFTED: "+str(cloc, cby, cbx)+" to "+str(cloc_n, cby_n, cbx_n))
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
 
    demo.write(demo_dir + '\\' + 'test1.demo')
    sys.exit(0)
