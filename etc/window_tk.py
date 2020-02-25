from tkinter import *
from PIL import Image, ImageTk
import glob

class Window:
    def __init__(self, win):
        self.greeting = Label(win, text='''
        Welcome to the Impresys bulk image pasting utility.
        To start, select background and foreground image:
        ''')
        self.greeting.grid(column=0, row=0)

        self.asset_dir = filedialog.askopenfilename(initialdir=r"C:\", title="Select File",)
        self.lbl1=Label(win, text='First number')
        self.lbl2=Label(win, text='Second number')
        self.lbl3=Label(win, text='Result')
        self.t1=Entry(bd=3)
        self.t2=Entry()
        self.t3=Entry()
        self.btn1 = Button(win, text='Add')
        self.btn2=Button(win, text='Subtract')
        self.lbl1.grid(column=0, row = 1)
        self.t1.grid(column=0, row=2)
        self.lbl2.grid(column=0, row=3)
        self.t2.grid(column=0, row=4)
        self.b1=Button(win, text='Add', command=self.add)
        self.b2=Button(win, text='Subtract')
        self.b2.bind('<Button-1>', self.sub)
        self.b1.grid(column=0, row =5)
        self.b2.grid(column=0, row=6)
        self.lbl3.grid(column=0, row=7)
        self.t3.grid(column=0, row=8)

        self.preview=Canvas(win)
        self.preview.grid(column=2, row=0)

        self.submit=Button(win, text="Submit", command=self.submit)
        self.submit.grid(column=2, row=8)

    def add(self):
        self.t3.delete(0, 'end')
        num1=int(self.t1.get())
        num2=int(self.t2.get())
        result=num1+num2
        self.t3.insert(END, str(result))

    def sub(self, event):
        self.t3.delete(0, 'end')
        num1=int(self.t1.get())
        num2=int(self.t2.get())
        result=num1-num2
        self.t3.insert(END, str(result))
    
    def submit(self, event):
        self.t3.delete(0, 'end')
        num1=int(self.t1.get())
        num2=int(self.t2.get())
        result=num1-num2
        self.t3.insert(END, str(result))
    
    '''
    def list_images(self) -> list(str):
        labels = []
        for png in glob.glob("C:/Users/Public/Pictures/Sample Pictures/*.jpg")[:5]:
            im = Image.open(jpeg)
            im.thumbnail((96, 170), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(im)
            label = tk.Label(root, image=photo)
            label.pack()    
            label.img = photo # *   
            labels.append(label)
    '''

def main():
    window=Tk()
    mywin=Window(window)
    window.title('Impresys Bulk Image Pasting Utility')
    window.geometry("800x600+10+10")
    window.mainloop()

if __name__ == '__main__':
    main()