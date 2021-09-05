import re
import os
from datetime import datetime
from time import time
import climateclock_util
from bdflib import reader
from dateutil.relativedelta import relativedelta
# Falls noch nicht vohanden: bei Installation dieser Module herunterladen mit
# pip3 install python-dateutil
# pip3 install bdflib


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
            font_width = 5
            
        text_width += font_width
    return text_width

class Countobject():
    def __init__(self,display_size):
        
        climateclock_util.load_config(self)

        # Timer fuer Infoanzeige
        # Zaehlt unabhaengig von Uhrzeit, da beliebige Intervalle moeglich sein sollen
        self.timer = time()
        self.start_time = time()
        self.mode = "clock"
        self.curr_text_width = calculate_text_width(self.info_text)
        self.curr_frame = 0
        self.position = display_size
        self.daylight = [[0,0,0],[0,0,0]]
        self.d_l_time_updated = 0
        self.light_intensity = self.light_intensity_night
        self.light_color = self.light_color_night.split(",")


        # Fuer Test: Aktuellen Zeitpunkt setzen auf 04.10.2027 11:59:50
        self.test_t0 = datetime.now()
        self.test_t0 = self.test_t0.replace(year=2029)
        self.test_t0 = self.test_t0.replace(month=7)
        self.test_t0 = self.test_t0.replace(day=24)
        self.test_t0 = self.test_t0.replace(hour=11)
        self.test_t0 = self.test_t0.replace(minute=59)
        self.test_t0 = self.test_t0.replace(second=50)

    # Hilfsfunktion fuer Test: Zaehlt Zeit relativ zu Startzeitpunkt sekundenweise herunter
    def count_time_4test(self):

        delta = int(round(time() - self.start_time, 0))
        self.start_time = self.start_time + delta
        if(self.test_t0.second + delta <= 59):
            self.test_t0 = self.test_t0.replace(second=self.test_t0.second+delta)
        else:
            self.test_t0 = self.test_t0.replace(hour=self.test_t0.hour + 1)
            self.test_t0 = self.test_t0.replace(minute=0)
            self.test_t0 = self.test_t0.replace(second=0)

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
        # nur zum Test: Verfehlen simulieren
        t0 = self.test_t0
        t1 = datetime.strptime(self.fail_date,"%Y-%m-%d %H:%M:%S")

        #Zeitunterschied berechnen
        delta = relativedelta(t1,t0)
        days = (t1-t0).days%365
        
        ret_val = ""
        if(int((t1-t0).total_seconds()) > 0):
            ret_val = delta.years, days, delta.hours, delta.minutes, delta.seconds
        else:
            ret_val = False
        
        return(ret_val)

    # Hauptfunktion count fuer die Berechnung der Zeitanzeige
    def count(self):

        ret_val = []
        t = self.get_time()
        if t != False:
            
            # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
            clock_text = str(t[0]) + "J. " + to_digit2(t[1]) + "T. " + to_digit(t[2]) + ":" + to_digit(t[3]) + ":" + to_digit(t[4])
            ret_val = [clock_text, 5,True]

            self.count_time_4test()

        else:
            ret_val = [self.text_failed,9,True]

        return ret_val

    # Hauptfunktion display_text fuer die Berechnung der Lauftextanzeige
    def display_text(self,text, text_width, display_size, current_time):

        if("$CLOCK$" in text):
            text = text.replace("$CLOCK$","")
            clock_text = self.count()[0]
        else:
            clock_text = ""
        #Falls Text durchgelaufen: Reset und Uhr anzeigen
        if(self.curr_frame > text_width + display_size+16):
            self.curr_frame = 0
            self.position = display_size
            ret_val = [clock_text, self.position,True]

        #Ansonsten: Text um 1 Frame verschieben
        else:
            self.position -= 1
            self.curr_frame += 1
            ret_val = [text + "  " + clock_text, self.position,False]
                    
        return ret_val

