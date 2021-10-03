import multiprocessing
from time import sleep
from time import time
from datetime import datetime
import climateclock_util
import json
from climateclock_counter import Countobject
#from climateclock_counter_simulate import Countobject


class ScreenUpdater():
    def __init__(self):
        #eigenstaendige configs laden
        climateclock_util.load_config(self)
        
        #self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        #self.font = graphics.Font()
        #self.font.LoadFont(self.countobject.font)
        
        print(self.font)
        self.vert = 26
        

    def draw_text(self,pos,text,light_color, light_intensity):
        #textColor = graphics.Color(int(int(self.light_color[0])*self.light_intensity),int(int(self.light_color[1])*self.light_intensity),int(int(self.light_color[2])*self.light_intensity))
        #self.offscreen_canvas.Clear()
        #graphics.DrawText(self.offscreen_canvas, self.font, pos, self.vert, textColor, text)

        #self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
        if(climateclock_util.get_local_time() > self.t_old):
            print(text + ", " + str(pos) + ", " + str(light_color) + ", " + str(light_intensity))
            self.t_old = climateclock_util.get_local_time()

    def run(self,queue):
        # content: text/img-src, position; config: [[r,b,g],intensity]
        display_content = {"type":"text","content":["", 0], "config":[[255,255,255],1]}

        #konstruktion mit t_old ist nur fuer test hier (realistischere zeiten)
        self.t_old = climateclock_util.get_local_time()

        #imageviewer.draw_image(self.matrix,"img/stripes_Klimauhr6.jpg",10)
        #imageviewer.draw_image(self.matrix,"img/logo_kiel3.jpg",20)
        
        while True:
            current_time = climateclock_util.get_local_time()
            """try:
                display_content = queue.get(False)
            except:
                pass"""
            if(not queue.empty()):
                display_content = queue.get(False)

            if(display_content["type"] == "text"):
                self.draw_text(display_content["content"][1],display_content["content"][0], display_content["config"][0], display_content["config"][1])
                
            elif(display_content["type"] == "img"):
                #imageviewer.draw_image(self.matrix,display_content["content"],None)

                if(current_time > self.t_old):
                    print(display_content["content"])
                    self.t_old = current_time
            
            sleep(0.015)
    

class Calculator():
    def __init__(self):
        #eigenstaendige configs laden
        climateclock_util.load_config(self)

        self.daylight = [[0,0,0],[0,0,0]]
        self.d_l_time_updated = 0
        #self.light_intensity = self.light_intensity_night
        #self.light_color = self.light_color_night.split(",")
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
            if(t > 0 and current_time%t == 0 and j["added"] != current_time):
 
                #Falls jobliste zu voll: nicht hinzufuegen
                if(len(self.job_list) < 20):
                    self.job_list.append(j)
                    j["added"] = current_time
                
    def run(self,queue):

        curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
        curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]

        queue_message = {"type":"text","content":["",0],"config":[[0,0,0],0]}

        while True:
            current_time = climateclock_util.get_local_time()

            # 1x am Tag (um 0 Uhr): Sonnenaufgangs- und -untergangszeit aktualisieren
            if(current_time == 0):
                self.get_daylight_times(datetime.now())

                # Helligkeit auf Basis der Tageszeit berechnen:
                curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
                curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]

            if(current_time > curr_sunset and current_time < curr_sundown):
                #self.light_intensity = self.light_intensity_day
                #self.light_color = self.light_color_day.split(",")
                queue_message["config"][0] = self.light_color_day.split(",")
                queue_message["config"][1] = self.light_intensity_day
            else:
                #self.light_intensity = self.light_intensity_night
                #self.light_color = self.light_color_night.split(",")
                queue_message["config"][0] = self.light_color_night.split(",")
                queue_message["config"][1] = self.light_intensity_night

            #nur hoechstens jede neue sekunde joblist updaten
            if(current_time > self.job_list_updated):
                self.update_job_list(current_time)
                self.job_list_updated = current_time

            #falls jobliste nicht leer:
            if(len(self.job_list) > 0):
                if(self.job_list[0]["type"] == "text"):
                    display_text = self.countobject.display_text(self.job_list[0]["content"], self.job_list[0]["text_width"], 256, current_time)
                    queue_message["type"] = "text"
                    queue_message["content"] = [display_text[0], display_text[1]]
                    
                    
                elif(self.job_list[0]["type"] == "img"):
                    queue_message["type"] = "img"
                    queue_message["content"] = self.job_list[0]["content"]
                    display_text[-1] = False # wichtig, damit Bild entsprechend seiner konfigurierten Zeit angezeigt wird

                #Falls Job beendet oder Zeit abgelaufen: Job aus Jobliste loeschen
                if(display_text[-1] == True or (self.job_list[0]["duration"] > 0 and self.job_started + self.job_list[0]["duration"] < current_time)):
                    self.job_list.pop(0)
                    self.job_started = current_time
                
            else:
                #Zeit fuer duration fuer naechsten Durchlauf initialisieren
                self.job_started = current_time
                
                # Unser Zaehlobjekt anfragen
                display_text = self.countobject.count(256,"display")
                queue_message["type"] = "text"
                queue_message["content"] = [display_text[0], display_text[1]]
            
            queue.put(queue_message, block=False)
            sleep(0.015)
        


# Main function
if __name__ == "__main__":
    queue = multiprocessing.Queue()

    calculator = Calculator()
    screenupdater = ScreenUpdater()
    
    calculation_process = multiprocessing.Process(target=calculator.run, args=(queue,))
    refresh_process = multiprocessing.Process(target=screenupdater.run, args=(queue,))

    calculation_process.start()
    refresh_process.start()

    calculation_process.join()
    refresh_process.join()
 
