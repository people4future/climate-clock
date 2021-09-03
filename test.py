from time import sleep
from time import time
from datetime import datetime
import climateclock_util
from climateclock_counter import Countobject
import json
#from climateclock_counter_simulate import Countobject
#rechnet Sekunden des aktuellen Tages in Lokalzeit aus

class Test():
    def __init__(self):
        #eigenstaendige configs laden
        climateclock_util.load_config(self)

        self.daylight = [[0,0,0],[0,0,0]]
        self.d_l_time_updated = 0
        self.light_intensity = self.light_intensity_night
        self.light_color = self.light_color_night.split(",")
        self.get_daylight_times(datetime.now())
        
        # Unser Zaehlobjekt anlegen
        self.countobject = Countobject(256)
        
        #alle konfigurierten Jobs laden
        # und mit Zeitstempel versehen
        # fuer text: textWidth berechnen
        with open('jobs.json',"r") as f:
            self.jobs = json.load(f)

        for j in self.jobs:
            j["added"] = climateclock_util.get_local_time()
            if(j["type"] == "text"):
                j["text_width"] = climateclock_util.calculate_text_width(j["content"])

        self.job_list = []

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

    def update_job_list(self,current_time):
        for j in self.jobs:
            t = 0
            cron = j["cron"].split(" ")
            if(len(cron) == 3):
                if(cron[0] != "*"):
                    t = int(cron[0])
                if(cron[1] != "*"):
                    t += int(cron[1])*60
                if(cron[2] != "*"):
                    t += int(cron[2])*3600
            if(t > 0 and current_time%t == 0 and j["added"] != current_time):
 
                #Falls jobliste zu voll: nicht hinzufuegen
                if(len(self.job_list) < 20):
                    self.job_list.append(j)
                    j["added"] = current_time
                    
                                
    def run(self):
        curr_sunset = 0
        curr_sundown = 0
        while True:
            
            current_time = climateclock_util.get_local_time()
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

            self.update_job_list(current_time)

            if(len(self.job_list) > 0):
                if(self.job_list[0]["type"] == "text"):
                    display_text = self.countobject.display_text(self.job_list[0]["content"], self.job_list[0]["text_width"], 256, current_time)
                    print(display_text)
                elif(self.job_list[0]["type"] == "img"):
                    #display_text = imageviewer.draw_image(self.matrix,self.job_list[0]["content"]])
                    print(self.job_list[0])
                    display_text = [False]
                #Falls Job beendet oder Zeit abgelaufen: aus Jobliste loeschen
                if(display_text[-1] == True or (self.job_list[0]["duration"] > 0 and self.job_started + self.job_list[0]["duration"] < current_time)):
                    self.job_list.pop(0)
                
            else:
                #Zeit fuer duration fuer naechsten Durchlauf initialisieren
                self.job_started = current_time
                
                # Unser Zaehlobjekt anfragen
                display_text = self.countobject.count()
                print(display_text)
                
            sleep(0.005)

t = Test()
t.run()

while True:
    t.update_job_list(climateclock_util.get_local_time())
    print(t.job_list)
    sleep(1)
