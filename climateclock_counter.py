from datetime import datetime
from dateutil.relativedelta import relativedelta
import climateclock_util

# if not yet installed: install python-dateutil:
# pip3 install python-dateutil


# Converts a number to a clock digit string
def to_digit(num):
    if(num < 10):
        return("0" + str(num))
    else:
        return str(num)

# Converts a number to a date string (adds spaces)
def to_digit2(num):
    if(num < 10):
        return("  " + str(num))
    elif(num < 100):
        return(" " + str(num))
    else:
        return str(num)

# Countobject class for calculating display text content
class Countobject():
    def __init__(self,display_size):

        #loads an own set of properties from the config.ini
        climateclock_util.load_config("config.ini",self)

        #initialize instance variables when object is created
        self.ret_val = ["", 5,True]
        self.curr_frame = 0
        self.position = display_size
        self.text_failed_width = climateclock_util.calculate_text_width(self.text_failed,self.font_dir)
        self.status = "counting"

    # calculates remaining time until fail date
    # Returns time list [years, days, hours, minutes, seconds, totalseconds]
    def get_time(self):
        t0 = datetime.now()
        t1 = datetime.strptime(self.fail_date,"%Y-%m-%d %H:%M:%S")

        #calculate time delta
        delta = relativedelta(t1,t0)

        #since relativedelta works with mixed years, days and time another datetime object is nedded for calculating absolute days and seconds
        abs_delta = t1-t0

        #calculate remaining days of current year
        if(abs_delta.days > 0):
            days = abs_delta.days%365
        else:
            days = 0

        ret_val = delta.years, days, delta.hours, delta.minutes, delta.seconds,abs_delta.total_seconds()

        return(ret_val)


    # Main function for creating clock display text
    def count(self,display_size):

        #Only recalculate time, if the previous return value does not contain the failed text
        if(not self.text_failed in self.ret_val[0]):

            #custom time calculation: [years, days, hours, minutes, seconds, totalseconds]
            t = self.get_time()

           #Display counting clock if there is time remaining
            if(t[5] > 0):
                clock_text = str(t[0]) + "J. " + to_digit2(t[1]) + "T. " + to_digit(t[2]) + ":" + to_digit(t[3]) + ":" + to_digit(t[4])
                self.ret_val = [clock_text, 5,True]

                #set status to "countdown" in the last 60 seconds (thereby avoiding all other jobs to be scheduled)
                if(t[5] < 60):
                    self.status = "countdown"
            else:
                self.ret_val = [self.text_failed, display_size,True]
                self.status = "failed"

        return self.ret_val

    # Main function for displaying custom run text
    def display_text(self,text, text_width, display_size):

        #if displayed text containes keyword $CLOCK$: replace it with the result of dynamic counting
        if("$CLOCK$" in text):
            text = text.replace("$CLOCK$","")
            clock_text = self.count(display_size)[0]
            if(self.status == "failed"):
                text_width += self.text_failed_width
                clock_text = self.text_failed

        else:
            clock_text = ""

        #if the text has left the left side of screen: reset current frame and show clock on final frame
        #Returning True gives back information "job has been finished"
        #Offset of 28 for stopping movement was found by trial'n'error (minor discrepancy with text length?) 
        if(self.curr_frame > text_width + display_size + 28):
            self.curr_frame = 0
            self.position = display_size
            ret_val = [clock_text, self.position,True]

        #else if the text has not reached the left side: move text position 1px to left, increase frame and mark as "not finished"
        else:
            self.position -= 1
            self.curr_frame += 1
            ret_val = [text + "  " + clock_text, self.position,False]

        return ret_val
