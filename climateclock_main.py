#!/usr/bin/env python3
from samplebase import SampleBase
from rgbmatrix import graphics
from time import sleep
import datetime
import climateclock_util
from climateclock_counter import Countobject
import json
from re import match
from PIL import Image, ImageEnhance
import os



class RunClock(SampleBase):

    #Initialize clock-object. Creates a 'samplebase' loading all configs from file rgb-matrix.conf
    def __init__(self, *args, **kwargs):
        super(RunClock, self).__init__(*args, **kwargs)

        #load clock configs (fail date, fonts, colors and brightness)
        climateclock_util.load_config("config.ini",self)

        # Create count object for text-based content
        self.countobject = Countobject(256)

        #Test the final countdown by uncommenting the following line:
        #self.countobject.fail_date = (datetime.datetime.now() + datetime.timedelta(minutes = 1)).strftime("%Y-%m-%d %H:%M:%S")

        #initialize basic instance variables
        self.daylight = [[0,0,0],[0,0,0]]
        self.light_intensity = self.light_intensity_day
        self.light_color = self.light_color_night.split(",")
        self.get_daylight_times(datetime.datetime.now())
        self.font = graphics.Font()
        self.font.LoadFont(self.countobject.font_dir)
        self.vert = 26
        self.sleep_time = 0.015


        # load jobs from file jobs.json
        # attributes origin from json-file
        with open('jobs.json',"r") as f:
            self.jobs = json.load(f)

        job_count = 0 #for error message only
        for j in self.jobs:

            #if content type text: calculate text width (px) initially (time critical!)
            if(j["type"] == "text"):
                j["text_width"] = climateclock_util.calculate_text_width(j["content"],self.font_dir)

            #validate configured intervals
            if(match(r"^((\d\d:)+\d\d)|-1$",j["interval"][0])==None or match(r"^((\d\d:)+\d\d)|-1$",j["interval"][1])==None):
                print("Error in interval detected in job " + str(job_count) + ". Interval entry will be ignored.")
                j["interval"] = ["-1","-1"]
            job_count += 1

        #initialize dynamic job list ('todo list' filled on runtime based on cron-like expression). Works with FIFO
        self.job_list = []
        self.job_list_updated = climateclock_util.get_local_time()

    # reads sunrise and sunset times for the current day based on csv-file
    # ATTENTION: Day and night times may afford a different csv-file corresponding to your geolocation
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


    #update the dynamic job 'todo' list. Interates through all defined jobs and evaluates the cron-like expression
    def update_job_list(self,current_time):

        for j in self.jobs:
            t = 0

            #evaluate cron-like expression
            cron = j["cron"].split(" ")
            if(len(cron) == 3):
                if(cron[0] != "*"):
                    t = int(cron[0])
                if(cron[1] != "*"):
                    t += int(cron[1])*60
                if(cron[2] != "*"):
                    t += int(cron[2])*3600

            #read start and stop values.
            interval = j["interval"]

            if(interval[0] == "-1"):
                interval[0] = "00:00:00"
            if(interval[1] == "-1"):
                interval[1] = "23:59:59"

            #convert clock times to local day time (secs since midnight)
            interval_start = [int(i) for i in interval[0].split(":")]
            interval_stop = [int(i) for i in interval[1].split(":")]

            start_time = interval_start[0]*3600 + interval_start[1]*60 + interval_start[2]
            stop_time = interval_stop[0]*3600 + interval_stop[1]*60 + interval_stop[2]

            # if current time is within specified interval and time fits cron expression: add job to job list
            if(current_time >= start_time and current_time <= stop_time):

                if(t > 0 and (current_time-start_time)%t == 0):

                    #If job list is too full (>20 jobs) or the final countdown is running (final 60 secs)
                    if(len(self.job_list) < 20 and self.countobject.status != "countdown"):
                        self.job_list.append(j)

    # draws a text line on the rgb-matrix (screen refresh) using the graphics module.
    def draw_text(self,pos,text):

        #set text color based on configuration values (config.ini)
        textColor = graphics.Color(int(int(self.light_color[0])*self.light_intensity),int(int(self.light_color[1])*self.light_intensity),int(int(self.light_color[2])*self.light_intensity))

        #refresh screen
        self.offscreen_canvas.Clear()
        graphics.DrawText(self.offscreen_canvas, self.font, pos, self.vert, textColor, text)

        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    # drawing image on the rgb-matrix
    def draw_image(self,img_name, opt_sleep_time):
        image = Image.open(os.path.join(os.getcwd(),img_name))

        # Make image fit our screen.
        image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)

        #set the image brightness according to the current mode (day/night)
        image = ImageEnhance.Brightness(image).enhance(self.light_intensity)

        #matrix.SetImage(image.convert('RGB'))
        self.matrix.SetImage(image)

        #if a sleep_time has been provided: wait until time has passed
        if(opt_sleep_time != None):
           sleep(opt_sleep_time)

        #return false on first pos (=job finished value)
        #time for displaying an image in a job is handled based on job list item
        return([False])

    def run(self):

        #define the offscreen_canvas for frame refreshes. Needs to be created here (after initialization of the samplebase object)
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

        #convert current sunrise and sunset to day time (secs since midnight)
        curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
        curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]

        #'Hello-Screen' displaying clock image on startup
        self.draw_image("img/stripes_Klimauhr6.jpg",10)

        while True:

            #calculate current day time (secs since midnight)
            current_time = climateclock_util.get_local_time()

            #Once a day at midnight: update sunrise and sunset times
            if(current_time == 0):

                self.get_daylight_times(datetime.datetime.now())
                curr_sunset = (self.daylight[0][0] * 3600) +  (self.daylight[0][1] * 60) + self.daylight[0][2]
                curr_sundown = (self.daylight[1][0] * 3600) +  (self.daylight[1][1] * 60) + self.daylight[1][2]

            #set light intensity according to sunrise/sunset time
            if(current_time > curr_sunset and current_time < curr_sundown):
                self.light_intensity = self.light_intensity_day
                self.light_color = self.light_color_day.split(",")
            else:
                self.light_intensity = self.light_intensity_night
                self.light_color = self.light_color_night.split(",")

            #update job list every second
            if(current_time == 0 or current_time > self.job_list_updated):
                self.update_job_list(current_time)
                self.job_list_updated = current_time

            #if job list contains jobs: run first job
            if(len(self.job_list) > 0):

                #run a text based job
                if(self.job_list[0]["type"] == "text"):
                    #decrease sleep time only when needed (run text) for better performance
                    self.sleep_time = 0.015
                    display_text = self.countobject.display_text(self.job_list[0]["content"], self.job_list[0]["text_width"], 256)
                    self.draw_text(display_text[1],display_text[0])

                #run an image based job
                elif(self.job_list[0]["type"] == "img"):
                    display_text = self.draw_image(self.job_list[0]["content"],None)

                #If job has been finsihed or job timer has run out
                if(display_text[-1] == True or (self.job_list[0]["duration"] > 0 and self.job_started + self.job_list[0]["duration"] < current_time)):
                    self.job_list.pop(0)
                    self.job_started = current_time

            #else: display counting clock
            else:
                #if the time has not yet expired: normal counting
                if(self.countobject.status == "counting" or self.countobject.status == "countdown"):
                    self.job_started = current_time
                    self.sleep_time = 0.1 #encrease sleep time for better performance (appr. 6% CPU save on pi3)

                    # Call the countobject for current display text and draw it on screen
                    display_text = self.countobject.count(256)
                    self.draw_text(display_text[1],display_text[0])

                # else if time for climate goal has expired: create a new job for displaying the failed text
                elif(self.countobject.status == "failed"):
                    job_failed = {"type":"text","content":self.countobject.text_failed,"duration":-1,"text_width":self.countobject.text_failed_width}
                    self.job_list.append(job_failed)

            sleep(self.sleep_time)

# Main function
if __name__ == "__main__":
    runner = RunClock()
    if (not runner.process()):
        runner.print_help()
