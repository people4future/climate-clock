
from datetime import datetime
from time import time
from dateutil.relativedelta import relativedelta
# Falls noch nicht vohanden: bei Installation dieses Modul herunterladen mit
# pip install python-dateutil

class Countobject():
    def __init__(self,display_size):
        
        # Timer fuer Infoanzeige
        # Zaehlt unabhaengig von Uhrzeit, da beliebige Intervalle moeglich sein sollen
        self.timer = time()
        self.start_time = time()
        self.mode = "clock"
        self.position = display_size
        
        #config.ini in gleichem Ordner oeffnen und Parameter als Instanzvariablen speichern
        with open("config.ini.template","r",encoding="utf-8") as ini_file:
            arr = ini_file.read().split("\n")
            for line in arr:
                if(line != "" and not line.startswith(";")):
                    tup = line.split("=")
                    tup[0] = tup[0].strip()
                    tup[1] = tup[1].strip()
                    if(tup[1].isdigit()):
                        tup[1] = int(tup[1])
                    setattr(self,tup[0],tup[1])

        # Fuer Test: Aktuellen Zeitpunkt setzen auf 04.10.2027 11:59:50
        self.test_t0 = datetime.now()
        self.test_t0 = self.test_t0.replace(year=2027)
        self.test_t0 = self.test_t0.replace(month=10)
        self.test_t0 = self.test_t0.replace(day=4)
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

    # Wandelt integer in Zeitziffer-String um
    def to_digit(self,num):
        if(num < 10):
            return("0" + str(num))
        else:
            return str(num)

    # Wandelt integer in Zeitziffer-String um
    def to_digit2(self,num):
        if(num < 10):
            return("  " + str(num))
        elif(num < 100):
            return(" " + str(num))
        else:
            return str(num)
        
    # Hauptfunktion der Klasse
    # Startet Berechnung, setzt ggf. Sleeptime und gibt anzuzeigenden Text zureuck
    def count(self):
        ret_text = ""
        # nur zum Test: Verfehlen simulieren
        t = self.get_time()
        if t != False:

            # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
            clock_text = str(t[0]) + "J. " + self.to_digit2(t[1]) + "T. " + self.to_digit(t[2]) + ":" + self.to_digit(t[3]) + ":" + self.to_digit(t[4])
            ret_text = [clock_text, 5]

            current_time = time()
            if(self.mode == "info"):
                if(current_time > self.timer + self.info_duration):
                    self.mode = "clock"
                    self.timer = current_time
                else:
                    self.position = self.position - 1
                    ret_text = [self.info_text + " " + clock_text, self.position]
            else:
                if(current_time > self.timer + self.clock_duration):
                    self.mode = "info"
                    self.timer = current_time
                    self.position = 256
            self.count_time_4test()

            
        else:
            ret_text = [self.text_failed,5]

        return ret_text
