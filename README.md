# pi-lcd
Program to show misc information with LCD RGB Keypad for RPi

## Screenshots

![Hostname and HDD space](https://dl.dropboxusercontent.com/u/2904420/pi-lcd-photos/pi-lcd1.jpg)
<center>Hostname and HDD space</center>

![CPU clock and temperature](https://dl.dropboxusercontent.com/u/2904420/pi-lcd-photos/pi-lcd2.jpg)
<center>CPU clock and temperature</center>

![RAM and Swap](https://dl.dropboxusercontent.com/u/2904420/pi-lcd-photos/pi-lcd3.jpg)
<center>RAM and Swap</center>

![Network velocity and bytes](https://dl.dropboxusercontent.com/u/2904420/pi-lcd-photos/pi-lcd4.jpg)
<center>Network speed and bytes transferred</center>

![Headless reboot](https://dl.dropboxusercontent.com/u/2904420/pi-lcd-photos/pi-lcd5.jpg)
<center>Headless reboot</center>

## Usage
Start the program with `./pi-lcd`

Select button turns the screen on and off, Up/Down buttons change the information pages.
Left button reboot Raspberry Pi (Must be pressed twice to avoid accidental activation).

`ifstat` package is required to show network speed. It can be installed with:
    
    $> sudo apt install ifstat

To use reboot button without executing `pi-lcd` as root, edit sudoers file with:
	
	$> sudo visudo

And add the following line:

	$> pi ALL=NOPASSWD: /sbin/reboot

If user executing `pi-lcd` **is not** pi, substitute with the correct user.

## Libraries

+ __ConfigParser__ to read the configuration file
+ __re__ to grep information
+ __subprocess__ to execute shell commands
+ __threading__ to handle threads
+ __time__ to handle intervals
+ __traceback__
+ __Adafruit\_CharLCD__ [Available here](https://github.com/adafruit/Adafruit_Python_CharLCD)

## Configuration file

__pi-lcd__ displays misc information in a 16x2 character display. To do this, you can define _pages_, each one with two lines of information. File `pi-lcd.cfg` allows to customize the number of pages and the information showed in each one. To specify the total number of pages, change the parameter `npages` on `settings` group. For each page, a group called `pageX` (being X a number between 0 and npages-1) must be created. Each `pageX` group has exactly two keys:

+ __line0__ to specify what it is shown on the upper line of the display.
+ __line1__ to specify what it is shown on the lower line of the display.

In the current version, possible values for `line0` and `line1` are:

+ __hostname__: displays Raspberry Pi's hostname
+ __ip__: displays IP on specified device
+ __load__: load on the last 1m/5m/15m
+ __cpu__: cpu frequency
+ __uptime__: time since Raspberry Pi was powered on
+ __temp__: temperature in Celsius
+ __ram__: used and total RAM
+ __swap__: used and total Swap
+ __inetspeed__: real time network speed on specified device
+ __inetbytes__: downloaded and uploaded bytes on specified device
+ __mac__: MAC address of specified device
+ __disk__: used and available space on specified partition

This readme will be updated regularly when more values are available.

## Advanced configuration

These values are defined in `settings` group of `pi-lcd.cfg` file.

+ __ip\_device__: device used to show IP (e.g. eth0)
+ __disk\_partition__: partition used to show space (e.g. /dev/sda1)

The update interval of various events can be specified:

+ __model\_interval__: time between info updates.
+ __disp\_interval__: time between display updates.
+ __buttons\_interval__: time between buttons' checks.

All the values are expressed in seconds. Decimal values can be used. Note that lower values increase the CPU requirements for the program.

## Example pi-lcd.cfg file

	[settings]
	npages           = 4
	nlines           = 2
	ncols            = 16
	ip_device        = eth0
	model_interval   = 1
	disp_interval    = 2
	buttons_interval = 0.02
	
	[page0]
	line0     = hostname
	line1     = ip
	
	[page1]
	line0     = hostname
	line1     = load
	
	[page2]
	line0     = hostname
	line1     = uptime
	
	[page3]
	line0     = hostname
	line1     = temp