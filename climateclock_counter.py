import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import time
# Falls noch nicht vohanden: bei Installation dieses Modul herunterladen mit
# pip install python-dateutil

class Countobject():
    def __init__(self,display_size):

        #config.ini in gleichem Ordner oeffnen und Parameter als Instanzvariablen speichern
        with open("config.ini.template","r",encoding="utf-8") as ini_file:
            arr = ini_file.read().split("\n")
            for line in arr:
                if(line != "" and not line.startswith(";")):
                    tup = line.split("=")
                    tup[0] = tup[0].strip()
                    tup[1] = tup[1].strip()
                    if(re.match(r"^\d+\.*\d*$",tup[1])):
                        tup[1] = float(tup[1])
                    setattr(self,tup[0],tup[1])
        # Timer fuer Infoanzeige
        # Zaehlt unabhaengig von Uhrzeit, da beliebige Intervalle moeglich sein sollen
        self.timer = time()
        self.mode = "clock"
        self.position = display_size
        self.daylight = [[0,0,0],[0,0,0]]
        self.d_l_time_updated = time()
        self.light_intensity = self.light_intensity_night
        
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
        current_time = time()
        
        # 1x am Tag (um 0 Uhr): Sonnenaufgangs- und -untergangszeit aktualisieren
        #if(int(round(current_time,0))%86400 == 0):

        #Fuer Test: alle 10 Sekunden neu einlesen
        if(int(round(current_time,0))%86400 == int(round(self.d_l_time_updated,0)%86400) + 10):

            # Pro Tag nur 1x Datei lesen
            #if((current_time - self.d_l_time_updated) >= 86400):
            
            #Fuer Test: alle 10 Sekunden neu einlesen
            if((current_time - self.d_l_time_updated) >= 10):
                self.get_daylight_times(datetime.now())
                self.d_l_time_updated = time()

        # Helligkeit auf Basis der Tageszeit berechnen:
        curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
        curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]

        if(current_time%86400 > curr_sunset and current_time%86400 < curr_sundown):
            self.light_intensity = self.light_intensity_day
        else:
            self.light_intensity = self.light_intensity_night
        
        ret_val = ""
        t = self.get_time()
        if t != False:
            
            # Info-Text entsprechend der Konfiguration alle x Sekunden fuer y Sekunden einblenden
            clock_text = str(t[0]) + "J. " + self.to_digit2(t[1]) + "T. " + self.to_digit(t[2]) + ":" + self.to_digit(t[3]) + ":" + self.to_digit(t[4])
            ret_val = [clock_text, 5, self.light_intensity]

            #current_time = time()
            if(self.mode == "info"):
                if(current_time > self.timer + self.info_duration):
                    self.mode = "clock"
                    self.timer = current_time
                else:
                    self.position = self.position - 1
                    ret_val = [self.info_text + " " + clock_text, self.position, self.light_intensity]
            else:
                if(current_time > self.timer + self.clock_duration):
                    self.mode = "info"
                    self.timer = current_time
                    self.position = 256

        else:
            ret_val = [self.text_failed,5, self.light_intensity]
            
        return ret_val
