from tkinter import *
import add_image_border as paste

def main():
    window = Tk()
    window.title("Impresys Bulk Image Edit Utility")
    window.geometry('800x600')

    greeting = Label(window, text= '''
        Welcome to the Impresys bulk image pasting utility.
        To start, select background and foreground image:
    ''')
    greeting.grid(column=0, row=0)

    ### ---

    ### ---

    def submit():
        submit_btn.configure(text="Submitting...")

    submit_btn = Button(window, text="Click Me", command=submit)
    submit_btn.grid(column=1, row=0)

    window.mainloop()

if __name__ == '__main__':
    main()