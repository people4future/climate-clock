# Software Part of the Climate Clock


## Prerequisites

- Raspberry Pi Imager
  https://www.raspberrypi.com/software/
- Your WIFI password and SSID
- Micro SD card reader/writer (some PCs and Laptops have them built in,
  other need an external adapter)

## Installing software on the micro CD card

- Download and install the Raspberry Pi Imager.
- Start the rpi-imager
- Select as operating system
  - Click on "Choose OS"
  - Click on "Raspberry Pi OS (other)"
  - Select "Raspberry Pi OS Lite (32-BIT)" (you can select any other OS, but
    this is the one we used and we really do not need graphical UI)
- Insert the micro SD card
- Click on "Choose Stoarge"
- Select the micro SD card
- Click on "Write" this will transfer the operating system onto the micro SD
  card.
- When the imager has completed its task, end the program and in some cases
  it is helpful to safely remove the micro SD card or eject or unmount the 
  micro SD card
- Remove the card (this is all done to ensure a save state, in many cases your
  operating system automatically mounts the freshly written micro SD card)

## Configuring the SD card

We configure the operating on the SD card in a way that the system will connect
to your WIFI after boot and allows you to remotely setup the Raspberry Pi.
This can be skipped when you do not intent to run the **climate clock** in a
place where you can always connect a keyboard and monitor to the device.
However, we found this feature quite helpful for our clock.

Insert the micro SD card back into the reader.

In case you are a Linux user, the micro SD card will be mounted and the volumes
will be accessible to you. In case you are using Windows or MacOS your
computer might not be able to read the SD card content correctly. In this case
you have to connect a monitor and keyboard to the Raspberry Pi and continue with
*Running the Pie for the first time (with monitor)*.

As Linux user you should be able to read the micro SD card and mount it.
Open the corresponding device with your file manager or use a terminal and
switch to the corresponding device directory, e.g., `/media/$USERNAME/$CARD`.

## Running the Pi for the first time

To be able to run the Pi and connect to it without having a monitor and keyboard
connected to the Pi, need a remote login to connect to the Pi and administer it.
Therefore, you need to set up
- WIFI
- ssh service

Mount the micro SD card and put the following file named `wpa_supplicant.conf` to
the main directory (this is `/media/$USERNAME/$CARD`) on the Pi
(https://raspberrytips.com/raspberry-pi-wifi-setup/).

```
country=DE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
  ssid="YOURSSID"
  scan_ssid=1
  psk="YOURPASSWORD"
  key_mgmt=WPA-PSK
}
```

**Note:**
- YOURSSID must be the **SSID** of the WIFI network you intend to use
- YOURPASSWORD must be the **passphrase** of your WIFI

To activate **ssh**, create an empty file ssh in the same directory.

Now unmount and eject the micro SD card and insert it in the Pi for the first time.
Connect the Pi to a charger or other power source. It will start up and automaticall
connect to your WIFI. This may take some time.

Most router will provide a random IP-address to the Pi. To find out which IP-address
this is, consult your router.

Now you cann log in to the Pi with:
- Linux/Mac `ssh pi@THE_IP_ADDRESS`
- Windows you might want to use the `putty` client

The system will ask for a password. Usually this is **raspberry**.

After log in, you can continue with **installing dependencies** below.

## Running the Pi for the first time (with monitor)

Connect a monitor, a keyboard and a power supply to your Pi.
After it has booted successfully, log in with 
- Login **pi**
- Password **raspberry**

Now you should be on command line of the Pi and able to install dependencies.

## Installing dependencies



## Testing Panels (Display)

## Installing the clock program

## Configure the clock program

## Playing with fonts

## Test the clock program

## Make the clock program start automatically

## References

- Library for running the RGB matrix panels on the Raspberry Pi 
  https://github.com/hzeller/rpi-rgb-led-matrix/tree/84e1465e9ea5ed000011d05369c5287eaa361ad7
- Raspberry Pi OS
  https://www.raspberrypi.com/software/operating-systems/

