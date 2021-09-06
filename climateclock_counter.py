import re
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import time
import climateclock_util

# Falls noch nicht vohanden: bei Installation dieser Module herunterladen mit
# pip3 install python-dateutil


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


class Countobject():
    def __init__(self,display_size):

        climateclock_util.load_config(self)
        
        # Timer fuer Infoanzeige
        # Zaehlt unabhaengig von Uhrzeit, da beliebige Intervalle moeglich sein sollen
        self.timer = climateclock_util.get_local_time()
        #self.mode = "clock"
        #self.curr_text_width = calculate_text_width(self.info_text) + display_size+16
        self.curr_frame = 0
        self.position = display_size


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


    # Hauptfunktion count fuer die Berechnung der Zeitanzeige
    def count(self):

        ret_val = []
        t = self.get_time()
        if t != False:
            
            # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
            clock_text = str(t[0]) + "J. " + to_digit2(t[1]) + "T. " + to_digit(t[2]) + ":" + to_digit(t[3]) + ":" + to_digit(t[4])
            ret_val = [clock_text, 5,True]


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
        if(self.curr_frame > text_width + display_size + 27):
            self.curr_frame = 0
            self.position = display_size
            ret_val = [clock_text, self.position,True]

        #Ansonsten: Text um 1 Frame verschieben
        else:
            self.position -= 1
            self.curr_frame += 1
            ret_val = [text + "  " + clock_text, self.position,False]

        return ret_val
