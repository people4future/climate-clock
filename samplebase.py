import argparse
import time
import sys
import os
import climateclock_util

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class SampleBase(object):
    def __init__(self, *args, **kwargs):

        self.parser = argparse.ArgumentParser()

    def process(self):
        climateclock_util.load_config("rgb_configs.ini",self)

        options = RGBMatrixOptions()

        if self.led_gpio_mapping != "":
          options.hardware_mapping = self.led_gpio_mapping
        options.rows = self.led_rows
        options.cols = self.led_cols
        options.chain_length = self.led_chain
        options.parallel = self.led_parallel
        options.row_address_type = self.led_row_addr_type
        options.multiplexing = self.led_multiplexing
        options.pwm_bits = self.led_pwm_bits
        options.brightness = self.led_brightness
        options.pwm_lsb_nanoseconds = self.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = self.led_rgb_sequence
        options.pixel_mapper_config = self.led_pixel_mapper
        options.panel_type = self.led_panel_type
        options.drop_privileges=True
        options.pwm_dither_bits = self.led_pwm_dither_bits
        options.limit_refresh_rate_hz = self.led_limit_refresh_rate_hz

        if self.led_show_refresh == "True" or self.led_show_refresh == 1:
          options.show_refresh_rate = 1

        if self.led_slowdown_gpio != "":
            options.gpio_slowdown = self.led_slowdown_gpio
        if self.led_no_hardware_pulse == "True" or self.led_no_hardware_pulse == 1:
          options.disable_hardware_pulsing = True
        if self.led_no_drop_privs == "False" or self.led_no_drop_privs == 0:
          options.drop_privileges=False

        self.matrix =  RGBMatrix(options = options)

        try:
            # Start loop
            print("Press CTRL-C to stop clock.")
            self.run()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        return True


