#!/usr/bin/env python3
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
from time import sleep
from time import time
from datetime import datetime
import climateclock_util
from climateclock_counter import Countobject
import json
from re import match
# oder zum Test 'Final Countdown':
#from climateclock_counter_simulate import Countobject
import imageviewer

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        #eigenstaendige configs laden
        climateclock_util.load_config("config.ini.template",self)

        self.daylight = [[0,0,0],[0,0,0]]
        self.light_intensity = self.light_intensity_day
        self.light_color = self.light_color_night.split(",")
        self.get_daylight_times(datetime.now())
        self.debug = True

        # Unser Zaehlobjekt anlegen
        self.countobject = Countobject(256)


        #alle konfigurierten Jobs laden
        # und mit Zeitstempel versehen
        with open('jobs.json',"r") as f:
            self.jobs = json.load(f)

        job_count = 0
        for j in self.jobs:
            j["added"] = climateclock_util.get_local_time()
            if(j["type"] == "text"):
                j["text_width"] = climateclock_util.calculate_text_width(j["content"])

            if(match(r"^((\d\d:)+\d\d)|-1$",j["interval"][0])==None or match(r"^((\d\d:)+\d\d)|-1$",j["interval"][1])==None):
                print("Error in interval detected in job " + str(job_count) + ". Interval entry will be ignored.")
                j["interval"] = ["-1","-1"]
            job_count += 1


        self.job_list = []
        self.job_list_updated = climateclock_util.get_local_time()
        self.job_started = climateclock_util.get_local_time()

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

            interval = j["interval"]

            if(interval[0] == "-1"):
                interval[0] = "00:00:00"
            if(interval[1] == "-1"):
                interval[1] = "23:59:59"

            interval_start = [int(i) for i in interval[0].split(":")]
            interval_stop = [int(i) for i in interval[1].split(":")]

            start_time = interval_start[0]*3600 + interval_start[1]*60 + interval_start[2]
            stop_time = interval_stop[0]*3600 + interval_stop[1]*60 + interval_stop[2]

            if(current_time >= start_time and current_time <= stop_time):

                if(t > 0 and (current_time-start_time)%t == 0 and j["added"] != current_time):

                    #Falls jobliste zu voll oder der finale countdown laeuft: nicht hinzufuegen
                    if(len(self.job_list) < 20 and self.countobject.status != "countdown"):
                        self.job_list.append(j)
                        j["added"] = current_time

    def draw_text(self,pos,text):
        textColor = graphics.Color(int(int(self.light_color[0])*self.light_intensity),int(int(self.light_color[1])*self.light_intensity),int(int(self.light_color[2])*self.light_intensity))
        self.offscreen_canvas.Clear()
        graphics.DrawText(self.offscreen_canvas, self.font, pos, self.vert, textColor, text)

        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)


    def run(self):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()
        self.font.LoadFont(self.countobject.font)
        self.vert = 26
        self.sleep_time = 0.015

        curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
        curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]


        imageviewer.draw_image(self.matrix,"img/stripes_Klimauhr6.jpg",self.light_intensity,10)
        #imageviewer.draw_image(self.matrix,"img/logo_kiel3.jpg",20)
        #imageviewer.draw_image(self.matrix,"img/256 x 32.jpg",20)

        while True:

            current_time = climateclock_util.get_local_time()

            # 1x am Tag (um 0 Uhr): Sonnenaufgangs- und -untergangszeit aktualisieren
            if(current_time == 0):
            #Fuer Test: alle 10 Sekunden neu einlesen
            #if(current_time%10 == 0):
                self.get_daylight_times(datetime.now())

                # Helligkeit auf Basis der Tageszeit berechnen:
                curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
                curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]

            if(current_time > curr_sunset and current_time < curr_sundown):
                self.light_intensity = self.light_intensity_day
                self.light_color = self.light_color_day.split(",")
            else:
                self.light_intensity = self.light_intensity_night
                self.light_color = self.light_color_night.split(",")

            #nur hoechstens jede neue sekunde joblist updaten
            if(current_time == 0 or current_time > self.job_list_updated):
                self.update_job_list(current_time)
                self.job_list_updated = current_time

            #falls jobliste nicht leer:
            if(len(self.job_list) > 0):
                self.sleep_time = 0.015
                if(self.job_list[0]["type"] == "text"):
                    display_text = self.countobject.display_text(self.job_list[0]["content"], self.job_list[0]["text_width"], 256)
                    self.draw_text(display_text[1],display_text[0])

                elif(self.job_list[0]["type"] == "img"):
                    display_text = imageviewer.draw_image(self.matrix,self.job_list[0]["content"],self.light_intensity,None)

                #Falls Job beendet oder Zeit abgelaufen: Job aus Jobliste loeschen
                if(display_text[-1] == True or (self.job_list[0]["duration"] > 0 and self.job_started + self.job_list[0]["duration"] < current_time)):
                    self.job_list.pop(0)
                    self.job_started = current_time

            else:
                if(self.countobject.status == "counting" or self.countobject.status == "countdown"):
                    #Zeit fuer duration fuer naechsten Durchlauf initialisieren
                    self.job_started = current_time
                    self.sleep_time = 0.15
                    # Unser Zaehlobjekt anfragen
                    display_text = self.countobject.count(256)
                    self.draw_text(display_text[1],display_text[0])

                elif(self.countobject.status == "failed"):
                    job_failed = {"type":"text","content":self.countobject.text_failed,"duration":-1,"text_width":self.countobject.text_failed_width}
                    self.job_list.append(job_failed)

            sleep(self.sleep_time)


        self.draw_text(display_text[1],display_text[0])

# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
