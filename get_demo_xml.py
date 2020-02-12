#------------------------------------------------------#
#                  get_demo_demo.py                    #
#      gets step and demo metadata and stores          #
#      in dict for later usage in bulk edits           #
#------------------------------------------------------#

import xml.etree.ElementTree as ET

demo_LOC = r"C:\Users\impresys\Documents\Projects\impresys-utils-demo\cfs_final_backup.demo"


def get_demo_meta(path):
    demo = ET.parse(path)
    root = demo.getroot()
    for chapters in root.findall('Chapters'):
        print(dir(chapters))

        '''
        for chapter in chapters.findall('Chapter'):
            print(len(chapter))
            for step in chapter.findall('Step'):
                print(len(step))
        '''

def get_sections_with_tag(tag):
    pass

if __name__ == '__main__':
    get_demo_meta(demo_LOC)
