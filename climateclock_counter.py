
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import time
# Falls noch nicht vohanden: bei Installation dieses Modul herunterladen mit
# pip install python-dateutil

class Countobject():
    def __init__(self,display_size):

        # Timer fuer Infoanzeige
        # Zaehlt unabhaengig von Uhrzeit, da beliebige Intervalle moeglich sein sollen
        self.timer = time()
        self.mode = "clock"
        self.position = display_size
        
        #config.ini in gleichem Ordner oeffnen und Parameter als Instanzvariablen speichern
        with open("config.ini","r",encoding="utf-8") as ini_file:
            arr = ini_file.read().split("\n")
            for line in arr:
                if(line != "" and not line.startswith(";")):
                    tup = line.split("=")
                    tup[0] = tup[0].strip()
                    tup[1] = tup[1].strip()
                    if(tup[1].isdigit()):
                        tup[1] = int(tup[1])
                    setattr(self,tup[0],tup[1])        
        

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

    # Wandelt integer in Zeitziffer-String um
    def to_digit(self,num):
        if(num < 10):
            return("0" + str(num))
        else:
            return str(num)

    # Wandelt integer in Zeitziffer-String um
    def to_digit2(self,num):
        if(num < 10):
            return("00" + str(num))
        elif(num < 100):
            return("0" + str(num))
        else:
            return str(num)

    # Hauptfunktion der Klasse
    # Startet Berechnung, setzt ggf. Sleeptime und gibt anzuzeigenden Text zureuck
    def count(self):
        ret_text = ""
        t = self.get_time()
        if t != False:
            
            # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
            ret_text = [str(t[0]) + "J. " + self.to_digit2(t[1]) + "T. " + self.to_digit(t[2]) + ":" + self.to_digit(t[3]) + ":" + self.to_digit(t[4]),0]

            current_time = time()
            if(self.mode == "info"):
                if(current_time > self.timer + self.info_duration):
                    self.mode = "clock"
                    self.timer = current_time
                else:
                    self.position = self.position - 1
                    ret_text = [self.info_text, self.position]
            else:
                if(current_time > self.timer + self.clock_duration):
                    self.mode = "info"
                    self.timer = current_time
                    self.position = 256

            # Exakte Sleeptime errechnen (Startzeit + 1 Sek. abzgl. Rechenzeit)
            #self.nexttime += 1
            #self.sleeptime = self.nexttime - time()

        else:
            ret_text = self.text_failed
            self.sleeptime = self.sleeptime_exp
            
        return ret_text
