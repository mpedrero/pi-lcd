# pi-lcd
Program to show misc information with LCD RGB Keypad for RPi

## Usage
Start the program with `./pi-lcd`

Select button turn the screen on and off, Up/Down buttons change the information pages.


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
+ __uptime__: time since Raspberry Pi was powered on
+ __temp__: Temperature in Celsius
+ __ram__: Used and total RAM
+ __swap__: Used and total Swap

This readme will be updated regularly when more values are available.

## Advanced configuration

These values are defined in `settings` group of `pi-lcd.cfg` file.

+ __ip\_device__: device used to show IP (e.g. eth0)

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