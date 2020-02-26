#------------------------------------------------------#
#                  get_demo_demo.py                    #
#      gets step and demo metadata and stores          #
#      in dict for later usage in bulk edits           #
#------------------------------------------------------#

import lxml.etree as ET
from PIL import Image
from typing import List, Tuple
import sys, os
#@TODO Include top <?xml version="1.0" encoding="utf-8"?> also doesn't include all
# Demo tag attributes
# need to edit mouse coordinates nested under StartPicture -> Hotspots -> Hotspot -> Mouse
# EnterPicture -> MouseCoordinate, not just top level mousecoordinates

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
    parser = ET.XMLParser(strip_cdata=False)
    demo = ET.parse(demo_path, parser)
    root = demo.getroot()
    demo_dir = demo_path.rsplit('\\', 1)[0]
    
    for chapter in list(root.iter('Chapter')):
        section = chapter.find('XmlName').find('Name').text
        if (sect == 'All') or (sect in section):
            steps = list(chapter.iter('Step'))
            for i, step in enumerate(steps):
                asset_dir =  step.find("StartPicture").find("AssetsDirectory").text
                assetpath = demo_dir + '\\' + asset_dir

                hspot = step.find("StartPicture").find("Hotspots").find("Hotspot")
                mouse = step.find("StartPicture").find("MouseCoordinates")
                if (hspot.find("MouseEnterPicture") is not None):
                    h_mouse = hspot.find("MouseEnterPicture").find("MouseCoordinates")
                else:
                    h_mouse = None
                
                if typ == "shell":
                    ry = float(fg_img_size[1] / bg_img_size[1])
                    rx = float(fg_img_size[0] / bg_img_size[0])
                    def transform(coords: List[float]) -> List[str]: #-> [top, bottom, left, right]
                        out = []
                        if len(coords) > 2: # if BOX coordinates (T, B, L, R)
                            for i in range(4):
                                if i < 2: out.append(str(coords[i] * ry + fg_img_loc[1]))
                                else: out.append(str(coords[i] * rx + fg_img_loc[0]))
                        elif len(coords) <= 2: # if CLICK coordinates (X, Y)
                            out.append(str(coords[0] * rx + fg_img_loc[0]))
                            out.append(str(coords[1] * ry + fg_img_loc[1]))
                        return out

                    def get_set_mouse(mouse_path) -> Tuple[List[float], List[float]]:
                        old = [float(mouse_path.find(c).text) for c in ['X', 'Y']]
                        new = transform(old)
                        for i, c in enumerate(['X', 'Y']):
                            mouse_path.find(c).text = str(new[i])
                        return new, old
                            
                    def get_set_box(box_type: str) -> Tuple[List[float], List[float]]:
                        dirs = ['Top', 'Bottom', 'Left', 'Right']
                        cbox = step.find("StartPicture").find(box_type)
                        old = [float(cbox.find(box_type[:-1]).find(d).text) for d in dirs]
                        new = transform(old)
                        for i, d in enumerate(dirs):
                            cbox.find(box_type[:-1]).find(d).text = str(new[i])
                        if box_type == 'VideoRects':
                            video = cbox.find('VideoRect').find('Video')
                            video.find('VideoHeight').text = str(ry*float(video.find('VideoHeight').text))
                            video.find('VideoWidth').text = str(rx*float(video.find('VideoWidth').text))
                        return new, old
            
                    cloc_new, cloc_old = get_set_mouse(mouse)
                    
                    if (h_mouse is not None):
                        hcloc_new, hcloc_old = get_set_mouse(h_mouse) # -> or this one?
                        other_rects = ["Hotspots", "VideoRects", "JumpRects", "TextRects", "HighlightRects"]
                        coords = dict.fromkeys(other_rects)
                        for box in other_rects:
                            if len(list(step.find("StartPicture").find(box))) != 0:
                                new, old = get_set_box(box)
                                coords[box] = [new, old]
                        print("SHIFTED:  "+str(hcloc_old)+" to "+str(hcloc_new))
                        
                for filename in os.listdir(assetpath):
                    if filename.endswith('.Png'):
                        impath = assetpath+filename
                        asset_img = Image.open(impath)
                        new_img = img.copy()
                        if typ == 'shell':
                            asset_img_resize = asset_img.resize((fg_img_size), Image.ANTIALIAS)
                            new_img.paste(asset_img_resize, fg_img_loc)
                            new_img.save(impath, quality=100)
                            print("SHELLED: Section: "+section+", Step: "+str(i)+", image: "+filename)
                        else:
                            fg_img_resize = new_img.resize((fg_img_size), Image.ANTIALIAS)
                            asset_img.paste(fg_img_resize, fg_img_loc)
                            asset_img.save(impath, quality=100)
                            print("INSERTED: Section: "+section+", Step: "+str(i)+", image: "+"t")
 
    demo.write(demo_path, xml_declaration=True, encoding='utf-8')
    sys.exit(0)

def main():
    demo_path = r"C:\Users\impresys\Documents\Projects\impresys-utils\demos\Manage Licenses Across Multiple AWS Accounts [R1-V5].demo"
    nimg_path = r"C:\Users\impresys\Pictures\bg.png"
    loc = (240,96)
    size = (1438, 894)
    typ = 'shell'
    sect = 'Section'
    image_paste(demo_path, nimg_path, loc, size, typ, sect)



if __name__ == '__main__':
    main()
