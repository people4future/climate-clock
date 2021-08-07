#!/bin/bash

SOURCE_PATH=/home/pi/climate-clock

cd $SOURCE_PATH

sudo python3 climateclock_main.py --led-gpio-mapping=adafruit-hat-pwm --led-cols 64 --led-rows 32 -c 4 --led-pwm-bits=3 -b 54

# end

