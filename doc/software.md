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

Before we can install the clock service, here are some dependencies and
prerequsites to be installed and configured before.

Things to do:
- Set up clock
- Install python development tools
- Install LED-matrix library

For these steps, we better switch to super user mode.

**Note:** Lines prefixed with `$` or `#` indicate command line
commands, to be typed in the terminal without the prefix. `$` 
indicates normal terminal/command line mode and `#` super user
mode.

`$ sudo -s` 

### Set up the system clock

Check the current date on the Pi with

`# date`

If it is not the correct date and time, you must change it with using
the correct date and time.

`# date -s '16 May 2023 09:28'`

To avoid future issues with updates, set a time server. Usually, this
is already set up correctly. However, in some local networks, it might be
that public time servers are not reachable or you want to use a different
one than the defaults. In that case:

Deactivate the time server with
`# timedatectl set-ntp false`
Add your time server to the configuration file
`# nano /etc/systemd/timesyncd.conf`
- Add a line with `FallbackNTP=` followed by your time servers.
  for example: `FallbackNTP=my.time.server1 my.time.server2`
- Save the file with Ctrl-O
- Exit the editor with Ctrl-X
Activate the time server again with
`# timedatectl set-ntp true`
Check the status
`# timedatectl status`
The result should look like:
```
               Local time: Tue 2023-05-16 09:40:33 CEST
           Universal time: Tue 2023-05-16 07:40:33 UTC
                 RTC time: n/a
                Time zone: Europe/Berlin (CEST, +0200)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

### Install Python development packages

Update the package information on the Pi.

`# apt-get update` 

Now we are able to install updates and new software.

`# apt-get install python3-dev python3-pillow -y`

### Install LED library

The LED library does not have an installable package, but
it is relatively easy to compile and install it yourself.

Make sure git is installed with
`# apt install git`
`# exit`

Get the library form its repository (clone it): 
`$ git clone https://github.com/hzeller/rpi-rgb-led-matrix.git`

Switch to the directory with
`$ cd rpi-rgb-led-matrix`
and build the library
`$ make`
Now enter the Python bindings directory so it can be used
from within Python.
`$ cd bindings/python`

Build and install the Python stuff with
`$ make build-python PYTHON=$(command -v python3)`
`$ sudo -s`
`# make install-python PYTHON=$(command -v python3)`

## Testing Panels (Display)

To test your panels, you have to connect them to the Pi. For this documentation
we assume you already did this following instructions to set up the hardware.

In the checked out repository `rpi-rgb-led-matrix` you find a `README.md`
containing detailed information to test your setup and play around with the
panels. In addition there are examples in the `bindings/python` subdirectory.
It helps to play around with them too, just to see that all installed parts
work together properly.

## Installing the clock program

Lets assume you are logged in as normal user. In case you are not, you can leave
with
`# exit`

Switch back to your home directory
`$ cd`

Clone the clock repository with
`$ git clone https://github.com/people4future/climate-clock`
Switch to the directory
`$ cd climate-clock`

## Test the clock program

how to test run the clock

## Make the clock start automatically

In this directory, you find a scripted called `climate-clock` which is a proper
init.d start and stop script for the clock. Copy the script to `/etc/init.d`.
`$ sudo -s`
`# cp climate-clock /etc/init.d/`
Make sure the clock is started in the right run levels with
`# cd ../rc3.d`
`# ln -s ../init.d/climate-clock S02climate-clock`
`# cd ../rc6.d`
`# ln -s ../init.d/climate-clock K01climate-clock`

## Configure the clock program

todo

## Playing with fonts

explain how we created the font

## References

- Library for running the RGB matrix panels on the Raspberry Pi 
  https://github.com/hzeller/rpi-rgb-led-matrix/tree/84e1465e9ea5ed000011d05369c5287eaa361ad7
- Raspberry Pi OS
  https://www.raspberrypi.com/software/operating-systems/

