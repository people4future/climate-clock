import re
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import time
from time import localtime
from bdflib import reader
# Falls noch nicht vohanden: bei Installation dieser Module herunterladen mit
# pip3 install python-dateutil
# pip3 install bdflib

#rechnet Sekunden des aktuellen Tages in Lokalzeit aus
def get_local_time():
    local_time = localtime()
    return (3600*local_time.tm_hour) + (60*local_time.tm_min) + local_time.tm_sec

# Wandelt integer in Zeitziffer-String um
def to_digit(num):
    if(num < 10):
        return("0" + str(num))
    else:
        return str(num)

# Wandelt integer in Zeitziffer-String um
def to_digit2(num):
    if(num < 10):
        return("  " + str(num))
    elif(num < 100):
        return(" " + str(num))
    else:
        return str(num)

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

    return text_width


class Countobject():
    def __init__(self,display_size):

        #config.ini in gleichem Ordner oeffnen und Parameter als Instanzvariablen speichern
        with open("config.ini.template","r",encoding="utf-8") as ini_file:
            arr = ini_file.read().split("\n")
            for line in arr:
                if(line != "" and not line.startswith(";")):
                    tup = line.split("=")
                    tup[0] = tup[0].strip()

                    if(re.match(r"^\d+\.*\d*$",tup[1])):
                        tup[1] = float(tup[1])
                    setattr(self,tup[0],tup[1])
        # Timer fuer Infoanzeige
        # Zaehlt unabhaengig von Uhrzeit, da beliebige Intervalle moeglich sein sollen
        self.timer = get_local_time()
        self.mode = "clock"
        self.curr_text_width = calculate_text_width(self.info_text) + display_size+16
        self.curr_frame = 0
        self.position = display_size
        self.daylight = [[0,0,0],[0,0,0]]
        self.d_l_time_updated = 0
        self.light_intensity = self.light_intensity_night
        self.light_color = self.light_color_night.split(",")
        self.get_daylight_times(datetime.now())

    def get_daylight_times(self,datetime_obj):
        with open("daylight_times.csv","r") as f:
            c = f.read()
        lines = c.split("\n")
        for l in lines:
            values = l.split(";")
            if(str(datetime_obj.month) == values[1] and str(datetime_obj.day) == values[0]):
                self.daylight = []
                self.daylight.append(values[2].split(":"))
                self.daylight.append(values[3].split(":"))

        for i in range(len(self.daylight[0])):
            self.daylight[0][i] = int(self.daylight[0][i])

        for i in range(len(self.daylight[1])):
            self.daylight[1][i] = int(self.daylight[1][i])




    # Fuehrt Zeit-Subtraktion aus.
    # Rueckgabe ist Zeit-Array ([J,T,H,Min,S]) oder False, falls Zeit abgelaufen ist
    def get_time(self):
        t0 = datetime.now()
        t1 = datetime.strptime(self.fail_date,"%Y-%m-%d %H:%M:%S")

        #Zeitunterschied berechnen
        delta = relativedelta(t1,t0)
        days = (t1-t0).days%365

        ret_val = ""
        if(int((t1-t0).total_seconds()) > 0):
            ret_val = delta.years, days, delta.hours, delta.minutes, delta.seconds,(t1-t0).total_seconds()
        else:
            ret_val = False

        return(ret_val)


    # Hauptfunktion der Klasse
    # Startet Berechnung, setzt ggf. Sleeptime und gibt anzuzeigenden Text zureuck
    def count(self):
        current_time = get_local_time()
        # 1x am Tag (um 0 Uhr): Sonnenaufgangs- und -untergangszeit aktualisieren
        #if(current_time == 0 and (time() - self.d_l_time_updated) >= 86400):
        #Fuer Test: alle 10 Sekunden neu einlesen
        if(current_time%10 == 0 and (time() - self.d_l_time_updated) >= 10):
            self.get_daylight_times(datetime.now())
            self.d_l_time_updated = time()

        # Helligkeit auf Basis der Tageszeit berechnen:
        curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
        curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]

        if(current_time > curr_sunset and current_time < curr_sundown):
            self.light_intensity = self.light_intensity_day
            self.light_color = self.light_color_day.split(",")
        else:
            self.light_intensity = self.light_intensity_night
            self.light_color = self.light_color_night.split(",")

        ret_val = ""
        t = self.get_time()
        if t != False:
            
            # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
            clock_text = str(t[0]) + "J. " + to_digit2(t[1]) + "T. " + to_digit(t[2]) + ":" + to_digit(t[3]) + ":" + to_digit(t[4])
            ret_val = [clock_text, 5, self.light_intensity, self.light_color]

            #current_time = time()
            if(self.mode == "info"):

                if(self.curr_frame > self.curr_text_width):
                    self.mode = "clock"
                    self.timer = current_time
                else:
                    self.position -= 1
                    self.curr_frame += 1
                    ret_val = [self.info_text + "  " + clock_text, self.position, self.light_intensity, self.light_color]
            else:
                if(current_time > self.timer + self.clock_duration):
                    self.mode = "info"
                    self.timer = current_time
                    self.position = 256
                    self.curr_frame = 0

        else:
            ret_val = [self.text_failed,9, self.light_intensity, self.light_color]

        return ret_val
