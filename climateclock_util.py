import os
import re
from time import localtime
from bdflib import reader
# install module bdflib before your first run with:
# pip3 install bdflib


# Calculates seconds of the current day since midnight using the computer's local time
def get_local_time():
    local_time = localtime()
    return (3600*local_time.tm_hour) + (60*local_time.tm_min) + local_time.tm_sec


#loads ini-files and adds every non-comment into a python inctance variable
# numeric values are automatically converted to float
def load_config(file,target_obj):
    with open(file,"r",encoding="utf-8") as ini_file:
        arr = ini_file.read().split("\n")
        for line in arr:
            if(line != "" and not line.startswith(";")):
                tup = line.split("=")
                tup[0] = tup[0].strip()

                if(re.match(r"^\d+\.*\d*$",tup[1])):
                    tup[1] = float(tup[1])
                setattr(target_obj,tup[0],tup[1])

# Calculates the width (pixels) for a custom string "text" using the bdflib module
def calculate_text_width(text,font_dir):
    text_width = 0
    #fontdir = os.path.join(os.getcwd(),"fonts","texgyreheros-bold-22.bdf")
    fontdir = os.path.join(os.getcwd(),font_dir)
    with open(fontdir, "rb") as handle:
        font = reader.read_bdf(handle)
    for char in text:
        font_width = font[ord(char)].bbW

        #stopgap, because space characters are not read correctly
        if(font_width == 0):
            font_width = 10

        #every character needs another pixel in front and behind
        font_width +=2
        text_width += font_width

    #subtract clock-Alias width
    if("$CLOCK$" in text and text != "$CLOCK$"):
        text_width -= calculate_text_width("$CLOCK$",font_dir)
    return text_width

