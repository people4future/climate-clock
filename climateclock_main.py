#!/usr/bin/env python3
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
from time import sleep
from climateclock_counter import Countobject
# oder zum Test 'Final Countdown':
#from climateclock_counter_simulate import Countobject

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        # Unser Zaehlobjekt anlegen
        self.countobject = Countobject(256)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(self.countobject.font)
        textColor = graphics.Color(200, 200, 0)
        pos = 0
        vert = 30

        while True:
            # Unser Zaehlobjekt anfragen
            display_text = self.countobject.count()
            
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, display_text[1], vert, textColor, display_text[0])

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

            # Sleeptime aus Zaehlobjekt anfragen (damit Zeit nach Verfehlen des Ziel veraendert werden kann)
            #sleep(self.countobject.sleeptime)
            sleep(0.01)

        offscreen_canvas.Clear()
        len = graphics.DrawText(offscreen_canvas, font, pos, vert, textColor, display_text)
        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
