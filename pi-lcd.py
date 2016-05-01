#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import re
import subprocess
import threading
import time
import traceback
import Adafruit_CharLCD as LCD


# Globals
npages = 4                          # Number of different info pages
page = 0                            # Current info page
enable_display = True               # Display on/off
button_changed = True               # Has been any button triggered?
ip_device = 'eth0'                  # Device to show IP
lcd = LCD.Adafruit_CharLCDPlate()   # Object representing LCD Hat
content = {}
info = {}
cfg_parser = ConfigParser.ConfigParser()


# Execute a shell command and return the output
def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = p.communicate()[0]
    return output


# Get internal IP
def getIP(device="eth0"):
    cad_ip = ""
    cad_ip = run_cmd("ip addr show "+device+" | grep \"inet \" | awk '{print $2}' | cut -d/ -f1")[:-1]
    return cad_ip
   
# Get hostname
def getHostname():
    cad_hostname = run_cmd("hostname")
    return cad_hostname
    
# Get uptime
def getUptime():
    cad_uptime = run_cmd("awk '{printf(\"%dd %02dh %02dm\",($1/60/60/24),($1/60/60%24),($1/60%60))}' /proc/uptime")
    return cad_uptime
    
# Get temperature
def getTemp():
    aux_temp = run_cmd("/opt/vc/bin/vcgencmd measure_temp")
    cad_temp = re.match(r'temp=(\d+\.\d+)\'C',aux_temp).group(1)
    return cad_temp

# Get load
def getLoad():
    aux_load = run_cmd("uptime")
    cad_load = ''
    cad_load += re.match(r'(.+)load average\: (\d+\.\d+), (\d+\.\d+), (\d+\.\d+)',aux_load).group(2) + " "
    cad_load += re.match(r'(.+)load average\: (\d+\.\d+), (\d+\.\d+), (\d+\.\d+)',aux_load).group(3) + " "
    cad_load += re.match(r'(.+)load average\: (\d+\.\d+), (\d+\.\d+), (\d+\.\d+)',aux_load).group(4)
    return cad_load
    
# Get RAM
def getRAM():
    aux_ram = run_cmd("free -h -m")
    parsed_ram = re.search(r'Mem: *(\d+M) *(\d+M) *(\d+M).*',aux_ram)
    cad_ram = "RAM: "+str(parsed_ram.group(2))+"/"+str(parsed_ram.group(1))
    return cad_ram
    
# Get Swap
def getSwap():
    aux_swap = run_cmd("free -h -m")
    parsed_swap = re.search(r'Swap: *(\d+[MB]) *(\d+[MB]).*',aux_swap)
    cad_swap = "Swap: "+str(parsed_swap.group(2))+"/"+str(parsed_swap.group(1))
    return cad_swap
    
    
# Data model worker
def dataModelWorker(interval=1):
    global ip_device
    
    while True:
        info["hostname"] = getHostname()
        info["ip"]       = getIP(ip_device)
        info["load"]     = getLoad()
        info["uptime"]   = getUptime()
        info["temp"]     = getTemp()
        info["ram"]      = getRAM()
        info["swap"]     = getSwap()
        time.sleep(interval)
        
    
# Data display worker
def dataDisplayWorker(interval=2):
    global enable_display
    global button_changed
    global page
    global ncols
    
    while True:
        lcd.enable_display(enable_display)
        if button_changed:
            button_changed = False
            lcd.clear()
            
        lcd.set_cursor(0,0)
        lcd.message(info[content['page'+str(page),'line0']])
        lcd.set_cursor(0,1)
        lcd.message(info[content['page'+str(page),'line1']])
        lcd.set_cursor(ncols-1,0)
        lcd.message(str(page))
        time.sleep(interval)

        
# Buttons handler worker        
def buttonsWorker(interval=0.01):
    global page
    global button_changed
    global enable_display
    
    while True:
        if not button_changed:
            if lcd.is_pressed(LCD.SELECT):
                enable_display = not enable_display
                button_changed = True
            if lcd.is_pressed(LCD.UP):
                page = (page - 1)%npages
                button_changed = True
            if lcd.is_pressed(LCD.DOWN):
                page = (page + 1)%npages
                button_changed = True
        time.sleep(interval)
            
            
            
            
try:
    cfg_parser.read('pi-lcd.cfg')
except:
    print "Can't read pi-lcd.cfg"
    quit()
    
try:
    npages           = int(cfg_parser.get('settings', 'npages'))
    nlines           = int(cfg_parser.get('settings', 'nlines'))
    ncols            = int(cfg_parser.get('settings', 'ncols'))
    model_interval   = float(cfg_parser.get('settings', 'model_interval'))
    disp_interval    = float(cfg_parser.get('settings', 'disp_interval'))
    buttons_interval = float(cfg_parser.get('settings', 'buttons_interval'))
    ip_device        = str(cfg_parser.get('settings', 'ip_device'))
    
    for i in range(0,npages):
        key = 'page'+str(i)
        print 'Saving:',key
        content[key,'line0'] = cfg_parser.get(key, 'line0')
        content[key,'line1'] = cfg_parser.get(key, 'line1')
       
except:
    print "Incorrenct config in pi-lcd.cfg"
    traceback.print_exc()
    quit()




# Init and clear display
lcd.set_color(0.0, 0.0, 0.0)    # Turn off RGB Led
lcd.clear()                     # Clear display

# Launch workers as daemons
model     = threading.Thread(target=dataModelWorker, args=(model_interval,), name='Model')
view      = threading.Thread(target=dataDisplayWorker, args=(disp_interval,), name='View')
buttons   = threading.Thread(target=buttonsWorker, args=(buttons_interval,), name='Buttons')

model.setDaemon(True)
view.setDaemon(True)
buttons.setDaemon(True)

model.start()
view.start()
buttons.start()

# Wait loop
while True:
    time.sleep(1)
