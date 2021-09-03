
#!/usr/bin/env python
import time
import sys
#from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import os

# Configuration for the matrix
#options = RGBMatrixOptions()
#options.rows = 32
#options.chain_length = 1
#options.parallel = 1
#options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

#matrix = RGBMatrix(options = options)

def draw_image(matrix,img_name,opt_sleep_time):
    image = Image.open(os.path.join(os.getcwd(),img_name))

    # Make image fit our screen.
    image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)

    matrix.SetImage(image.convert('RGB'))
    if(opt_sleep_time != None):
        time.sleep(opt_sleep_time)
    return([False])
