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
        
        climateclock_util.load_config("config.ini.template",self)

        self.start_time = time()
        self.timer = climateclock_util.get_local_time()
        self.ret_val = ["", 5,True]
        self.curr_frame = 0
        self.position = display_size
        self.text_failed_width = climateclock_util.calculate_text_width(self.text_failed)
        self.status = "counting"


        # Fuer Test: Aktuellen Zeitpunkt setzen auf 04.10.2027 11:59:50
        self.test_t0 = datetime.now()
        self.test_t0 = self.test_t0.replace(year=2029)
        self.test_t0 = self.test_t0.replace(month=7)
        self.test_t0 = self.test_t0.replace(day=24)
        self.test_t0 = self.test_t0.replace(hour=11)
        self.test_t0 = self.test_t0.replace(minute=59)
        self.test_t0 = self.test_t0.replace(second=40)

    # Hilfsfunktion fuer Test: Zaehlt Zeit relativ zu Startzeitpunkt sekundenweise herunter
    def count_time_4test(self):

        delta = int(round(time() - self.start_time, 0))
        self.start_time = self.start_time + delta
        if(self.test_t0.second + delta <= 59):
            self.test_t0 = self.test_t0.replace(second=self.test_t0.second+delta)

        else:
            self.test_t0 = self.test_t0.replace(year=2029)
            self.test_t0 = self.test_t0.replace(month=7)
            self.test_t0 = self.test_t0.replace(day=24)
            self.test_t0 = self.test_t0.replace(hour=self.test_t0.hour + 1)
            self.test_t0 = self.test_t0.replace(minute=0)
            self.test_t0 = self.test_t0.replace(second=0)


    # Fuehrt Zeit-Subtraktion aus.
    # Rueckgabe ist Zeit-Array ([J,T,H,Min,S]) oder False, falls Zeit abgelaufen ist
    def get_time(self):
        t0 = datetime.now()
        # nur zum Test: Verfehlen simulieren
        t0 = self.test_t0
        t1 = datetime.strptime(self.fail_date,"%Y-%m-%d %H:%M:%S")

        #Zeitunterschiede berechnen
        delta = relativedelta(t1,t0)
        if((t1-t0).days > 0):
            days = (t1-t0).days%365
        else:
            days = 0

        ret_val = delta.years, days, delta.hours, delta.minutes, delta.seconds,(t1-t0).total_seconds()

        return(ret_val)

    # Hauptfunktion count fuer die Berechnung der Zeitanzeige
    def count(self,display_size):

        #Uhr hoechstens jede Sekunde aktualisieren
        if(not self.text_failed in self.ret_val[0]):
            if(self.timer < climateclock_util.get_local_time()):
                t = self.get_time()
                if(t[0] > 0 or t[1] > 0 or t[2] > 0 or t[3] > 0 or t[4] > 0):
                    # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
                    clock_text = str(t[0]) + "J. " + to_digit2(t[1]) + "T. " + to_digit(t[2]) + ":" + to_digit(t[3]) + ":" + to_digit(t[4])
                    self.ret_val = [clock_text, 5,True]
                else:
                    self.ret_val = [self.text_failed, display_size,True]
                    self.status = "failed"

                
            self.timer = climateclock_util.get_local_time()

        """else:
            if(mode == "text"):
                self.ret_val = [self.text_failed,9,True]
            elif(mode == "display"):
                self.ret_val =  self.display_text(self.text_failed, self.text_failed_width, display_size, climateclock_util.get_local_time())
        """
        self.count_time_4test()

        return self.ret_val

    # Hauptfunktion display_text fuer die Berechnung der Lauftextanzeige
    def display_text(self,text, text_width, display_size, current_time):

        if("$CLOCK$" in text):
            text = text.replace("$CLOCK$","")
            clock_text = self.count(display_size)[0]
            if(self.status == "failed"):
                text_width += self.text_failed_width
                clock_text = self.text_failed
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

