import tkinter
from tkinter import *
from tkinter.messagebox import showerror
from PIL import Image

# root window
root = Tk()
root.title('Temperature Converter')
root.geometry('200x150')
root.configure(background = "white")
root.resizable(False, False)


def fahrenheit_to_celsius(f):
    """ Convert fahrenheit to celsius
    """
    return (f - 32) * 5/9


# frame


# field options
options = {'padx': 5, 'pady': 5}

for i in range(2):
    label_stats_e = Label(root,text="BRIAN TIME\n BRIAN "+str(i),background="white")
    label_stats_e.grid(column=0,row=0,sticky='W',**options)

    img_frontsprite = PhotoImage(file="gen1data/sprites/front-1.png")
    label_frontsprite = Label(root,image=img_frontsprite,background="white")
    label_frontsprite.grid(column=1,row=0,**options)

    label_stats_p = Label(root,text="KEVIN TIME\n KEVIN LIFE",background="white")
    label_stats_p.grid(column=1,row=1,sticky='W',**options)

    img_backsprite = PhotoImage(file="gen1data/sprites/back-"+str(i+5)+".png")
    label_backsprite = Label(root,image=img_backsprite,background="white")
    label_backsprite.grid(column=0,row=1,**options)

    input()
