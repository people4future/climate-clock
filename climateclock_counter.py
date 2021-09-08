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
        
        self.timer = climateclock_util.get_local_time()
        self.ret_val = ["", 5,True]
        self.curr_frame = 0
        self.position = display_size
        self.text_failed_width = climateclock_util.calculate_text_width(self.text_failed)


    # Fuehrt Zeit-Subtraktion aus.
    # Rueckgabe ist Zeit-Array ([J,T,H,Min,S]) oder False, falls Zeit abgelaufen ist
    def get_time(self):
        t0 = datetime.now()
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
    def count(self,display_size,mode):

        #Uhr hoechstens jede Sekunde aktualisieren
        if(not self.text_failed in self.ret_val[0]):
            
            if(self.timer < climateclock_util.get_local_time()):
                t = self.get_time()
                if(t[0] > 0 and t[1] > 0 and t[2] > 0 and t[3] > 0 and t[4] > 0):
                    # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
                    clock_text = str(t[0]) + "J. " + to_digit2(t[1]) + "T. " + to_digit(t[2]) + ":" + to_digit(t[3]) + ":" + to_digit(t[4])
                    self.ret_val = [clock_text, 5,True]
                else:
                    self.ret_val = [self.text_failed, 5,True]
                
            self.timer = climateclock_util.get_local_time()

        else:
            if(mode == "text"):
                self.ret_val = [self.text_failed,9,True]
            elif(mode == "display"):
                self.ret_val =  self.display_text(self.text_failed, self.text_failed_width, display_size, climateclock_util.get_local_time())
 
        return self.ret_val

    # Hauptfunktion display_text fuer die Berechnung der Lauftextanzeige
    def display_text(self,text, text_width, display_size, current_time):

        if("$CLOCK$" in text):
            text = text.replace("$CLOCK$","")
            clock_text = self.count(display_size,"text")[0]
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
