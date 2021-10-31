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

        climateclock_util.load_config("config.ini.template",self)

        self.timer = climateclock_util.get_local_time()
        self.ret_val = ["", 5,True]
        self.curr_frame = 0
        self.position = display_size
        self.text_failed_width = climateclock_util.calculate_text_width(self.text_failed)
        self.status = "counting"

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
    def count(self,display_size):

        #Uhr hoechstens jede Sekunde aktualisieren
        if(not self.text_failed in self.ret_val[0]):

            if(self.timer < climateclock_util.get_local_time()):
                t = self.get_time()

                if(t[0] >= 0 and t[1] >= 0 and t[2] >= 0 and t[3] >= 0 and t[4] >= 0):
                    clock_text = str(t[0]) + "J. " + to_digit2(t[1]) + "T. " + to_digit(t[2]) + ":" + to_digit(t[3]) + ":" + to_digit(t[4])
                    self.ret_val = [clock_text, 5,True]
                    if(int(t[0]) + int(t[1]) + int(t[2]) + int(t[3]) == 0):
                        self.status = "countdown"
                else:
                    self.ret_val = [self.text_failed, display_size,True]
                    self.status = "failed"

            self.timer = climateclock_util.get_local_time()

        return self.ret_val

    # Hauptfunktion display_text fuer die Berechnung der Lauftextanzeige
    def display_text(self,text, text_width, display_size):

        if("$CLOCK$" in text):
            text = text.replace("$CLOCK$","")
            clock_text = self.count(display_size)[0]
            if(self.status == "failed"):
                text_width += self.text_failed_width
                clock_text = self.text_failed

        else:
            clock_text = ""
        #Falls Text durchgelaufen: Reset und Uhr anzeigen
        if(self.curr_frame > text_width + display_size + 28):
            self.curr_frame = 0
            self.position = display_size
            ret_val = [clock_text, self.position,True]

        #Ansonsten: Text um 1 Frame verschieben
        else:
            self.position -= 1
            self.curr_frame += 1
            ret_val = [text + "  " + clock_text, self.position,False]

        return ret_val
