#!/usr/bin/env python
##############################################################################
# Copyright (c) 2012 Hajime Nakagami<nakagami@gmail.com>
# All rights reserved.
# Licensed under the New BSD License
# (http://www.freebsd.org/copyright/freebsd-license.html)
#
# A image viewer. Require Pillow ( https://pypi.python.org/pypi/Pillow/ ).
##################################]############################################
import PIL.Image

try:
    from tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog
import PIL.ImageTk
from typing import List, Set, Tuple

class App(Frame):
    def chg_image(self):
        if self.im.mode == "1": # bitmap image
            self.img = PIL.ImageTk.BitmapImage(self.im, foreground="white")
        else:              # photox image
            self.img = PIL.ImageTk.PhotoImage(self.im)
        self.la.config(image=self.img, bg="#000000",
            width=self.img.width(), height=self.img.height())

    def open_file(self):
        filename = filedialog.askopenfilename()
        if filename != "":
            self.imgdf_path = filename

    def open_directory(self):
        directory = filedialog.askdirectory()
        if directory != "":
            self.asset_path = directory

    def seek_prev(self):
        self.num_page=self.num_page-1
        if self.num_page < 0:
            self.num_page = 0
        self.img.seek(self.num_page)
        self.chg_image()
        self.num_page_tv.set(str(self.num_page+1))

    def seek_next(self):
        try:
            self.im.seek(self.num_page)
        except:
            self.num_page=self.num_page-1
        self.chg_image()
        self.num_page_tv.set(str(self.num_page+1))

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Image Viewer')

        self.num_page=0
        self.num_page_tv = StringVar()
        self.image_path = StringVar()  #--> absolute(must be raw) path to 'shelling' image
        self.asset_path = StringVar()   #--> absolute(also raw) path to directory containing assets
        self.image_newsize = Tuple[int, int]
        self.imag_location = Tuple[int, int]

            
        #-----------------------> Set the frame -----------------------------------------
        fram = Frame(self) 

        # ----------------- Set the components in the frame ------------------------------

        Label(fram, text="Welcome to the Impresys bulk image pasting tooL!").pack(side=LEFT)
        Button(fram, text="Open File", command=self.open_file).pack(side=LEFT)
        Button(fram, text="Open Assets", command=self.open_directory).pack(side=LEFT)
        Button(fram, text="Prev", command=self.seek_prev).pack(side=LEFT)
        Button(fram, text="Next", command=self.seek_next).pack(side=LEFT)
        Label(fram, textvariable=self.num_page_tv).pack(side=LEFT)
        Label(fram, textvariable=self.img_path).pack(side=RIGHT)
        Label(fram, textvariable=self.asset_path).pack(side=RIGHT)
        fram.pack(side=TOP, fill=BOTH)


        self.la = Label(self)
        self.la.pack()

        self.pack()

if __name__ == "__main__":
    root = Tk()
    root.minsize(800, 600)
    app = App()
    app.mainloop()