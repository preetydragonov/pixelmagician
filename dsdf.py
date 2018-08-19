#-*- encoding: utf-8 -*-
import subprocess
import tkinter as tk
from os import *
import os
import time

root = tk.Tk()

def my_function():
    current_query = my_entry.get()
    url_member_1 = "http://www.google.com/search\?q\="+ str(current_query) + "\&source\=lnms\&tbm\=isch"
    url_member_2 = "http://www.google.com/search\?q\=" + str(current_query) + str(current_query) + "\&source\=lnms\&tbm\=isch"
    now = time.localtime()
    s = "%04d-%02d-%02d_%02d:%02d:%02d_" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

    os.system("chrome-cli open "+ url_member_1)
    os.system("chrome-cli open "+ url_member_2)
    time.sleep(3)
    os.system("screencapture ~/Desktop/photo_folder/" + str(s) + current_query + "_1.png " + "~/Desktop/photo_folder/" + str(s) + current_query + "_2.png " + "~/Desktop/photo_folder/" + str(s) + current_query + "_3.png")

photo = tk.PhotoImage(file="googlelogo-ConvertImage.gif")
photo = photo.subsample(2, 2)
r = tk.Label(root, image=photo)
r.place(relx=0.38, rely=0.4)

my_entry = tk.Entry(root, width=50, font = "Helvetica 14")
my_entry.place(relx=0.355, rely=0.54)

my_button = tk.Button(root, text = "Submit", command = my_function)
my_button.place(relx=0.605, rely = 0.54)


root.mainloop()

