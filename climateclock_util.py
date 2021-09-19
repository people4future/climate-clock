import os
import re
from time import localtime
from bdflib import reader
# Falls noch nicht vohanden: bei Installation dieser Module herunterladen mit
# pip3 install bdflib


#rechnet Sekunden des aktuellen Tages in Lokalzeit aus
def get_local_time():
    local_time = localtime()
    return (3600*local_time.tm_hour) + (60*local_time.tm_min) + local_time.tm_sec


#config.ini in gleichem Ordner oeffnen und Parameter als Instanzvariablen speichern
# besser: auslagern in externes modul
def load_config(target_obj):
    with open("config.ini.template","r",encoding="utf-8") as ini_file:
        arr = ini_file.read().split("\n")
        for line in arr:
            if(line != "" and not line.startswith(";")):
                tup = line.split("=")
                tup[0] = tup[0].strip()

                if(re.match(r"^\d+\.*\d*$",tup[1])):
                    tup[1] = float(tup[1])
                setattr(target_obj,tup[0],tup[1])

def calculate_text_width(text):
    text_width = 0
    fontdir = os.path.join(os.getcwd(),"fonts","texgyreheros-bold-22.bdf")
    with open(fontdir, "rb") as handle:
        font = reader.read_bdf(handle)
    for char in text:
        font_width = font[ord(char)].bbW

        #Notloesung, da Leerzeichen, Tabs, etc nicht korrekt gelesen werden
        if(font_width == 0):
            font_width = 10

        #jeder Buchstabe enthaelt jeweils 1px davor und danach
        font_width +=2
        text_width += font_width

    #Clock-Alias herausrechnen
    if("$CLOCK$" in text and text != "$CLOCK$"):
        text_width -= calculate_text_width("$CLOCK$")
    return text_width
