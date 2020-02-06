from tkinter import *
import add_image_border as paste

def main():
    root = Root()
    root.mainloop()

class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()

        self.bg_path
        self.fg_path
        self.img_loc
        self.img_size

        self.title("Impresys Bulk Image Edit Utility")
        self.minsize(800, 600)

        self.greeting = Label(self, text= '''
        Welcome to the Impresys bulk image pasting utility.
        To start, select background and foreground image:
        ''')
        self.greeting.grid(column=0, row=0, padx=20, pady=20)

        self.labelFrame = LabelFrame(self, text = "Open File")
        self.labelFrame.grid(column = 0, row = 1, padx = 20, pady = 20)
 
        self.open_bg_btn()
        self.open_fg_btn()
        
        self.submit()

    def open_bg_btn(self):
        pass

    def open_fg_btn(self):
        pass

if __name__ == '__main__':
    main()