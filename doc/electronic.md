# Electronic Part of the Climate Clock

The **climate clock** consists of a Raspberry Pi 3b or better, 4 panels and the
necessary panel driver. This project is based on

...

## Part List

- Raspberry Pi Zero WH (for a one panel setup)
- Raspberry Pi 3 Model B+ (for multiple panel setups)
- 1 to 4 64x32 RGB LED Matrix panels; they come in different sizes
  - 3 mm pixel diameter (display 191mm x 96mm x 15mm)
    https://www.adafruit.com/product/2279
  - 4 mm pixel diameter (display 255mm x 127mm x 15mm)
    https://www.adafruit.com/product/2278
  - 5 mm pixel diameter (display 318mm x 158mm x 15mm)
    https://www.adafruit.com/product/2277
  - 6 mm pixel diameter (display 385mm x 190mm x 13mm)
    https://www.adafruit.com/product/2276
- Adafruit RGB Matrix Bonnet for Raspberry Pi
  https://www.adafruit.com/product/3211
- 5V 4A (4000mA) power supply (for one panel)
- Micro SD card 32 GB 
- Micro SD card reader/writer (in case your computer does not have such reader
  built in and yo udo not possess such device)

## Set up Raspberry Pi

To be able to test the display, we suggest to install the basic operating
system onto the SD card, insert it into the Pi and set up the Pi following
the software installation guide. This allows to test the panels.

## Assemble

**Connect the Bonnet**

Connect the Bonnet to the Raspberry Pi. To do this, you'll need to line up
the GPIO pins on the Pi with the adapter on the bonnet.

*Don't rush this step. If you push too hard or try to do it too quickly,
you could damage the GPIO pins.*

With the pins lined up, press firmly and evenly across the GPIO pins. Squeeze
the boards together. If you do it correctly, you should see the GPIO pins
entering the adapter evenly all the way across.

**Connect Panel Power Cable**

The bonnet will provide power to both the panel and the Raspberry Pi. The
Raspberry Pi will receive power through the GPIO pins, but we'll need to connect
the panel to the bonnet to provide power to the panel.

Depending on the exact panel you purchase, you will likely need to cut and strip
the red and black wires.

Then on the bonnet:

- Unscrew the small screws at the top of the terminals.
- Slide the exposed copper from the cables into the terminals
- Then tighten the screws to secure them.

**Hint** (This is not yet proof read, use with caution)
In case you are using multiple panels, you need to do this for all panels and
connect them in parallel.

**Connect the Ribbon Cable**

You're ready to connect the panels to the bonnet.

- Connect the ribbon cable from the panel to the bonnet.
- In case you are using multiple displays, you can chain them, i.e., the
  first panel will be connected to the bonnet, the second panel to the first
  and so on. However, for testing purposes, we suggest to connect only one
  panel and test each panel separatel with our test script (see software.md)
- Finally connect the chained displays to the bonnet.
- Connect your power supply to the bonnet.


## References

https://howchoo.com/pi/raspberry-pi-led-matrix-panel

