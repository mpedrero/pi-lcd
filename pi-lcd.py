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
enable_reboot = False
button_changed = True               # Has been any button triggered?
ip_device = 'eth0'                  # Device to show IP
disk_partition = '/dev/mmcblk0p1'   # Partition to show info
lcd = LCD.Adafruit_CharLCDPlate()   # Object representing LCD Hat
content = {}
info = {}
cfg_parser = ConfigParser.ConfigParser()

# Display custom characters
lcd.create_char(1, [0,4,14,21,4,4,4,0]) # Upload speed
lcd.create_char(2, [0,4,4,4,21,14,4,0]) # Download speed
lcd.create_char(3, [0,4,14,31,0,10,10,4]) # Upload bytes
lcd.create_char(4, [0,31,14,4,0,12,10,12]) # Download bytes
lcd.create_char(5, [0,0,30,21,17,17,31,0]) # Disk

# Execute a shell command and return the output
def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = p.communicate()[0]
    return output

def info_init():
    info["hostname"] = getHostname()
    info["ip"]       = getIP(ip_device)
    info["load"]     = getLoad()
    info["uptime"]   = getUptime()
    info["temp"]     = getTemp()
    info["ram"]      = getRAM()
    info["swap"]     = getSwap()
    info["inetspeed"]= getInetSpeed()
    info["mac"]      = getMAC(ip_device)
    info["inetbytes"]= getInetTransf(ip_device)
    info["cpu"]      = getCPU()
    info["disk"]     = getDiskInfo(disk_partition)
    
# Return suitable unit (B/KB/MB/GB/TB)
def unit(bytes):
    bytes = float(bytes)
    
    if bytes < 1000:
        u = "B"
        b = bytes
    elif bytes < 1000000:
        u = "KB"
        b = bytes/1024
    elif bytes < 1000000000:
        u = "MB"
        b = bytes/1048576
    elif bytes < 1000000000000:
        u = "GB"
        b = bytes/1073741824
    else:
        u = "TB"
        b = bytes/1099511627776
        
    return str(round(b,1))+u
        
    
# Get internal IP
def getIP(device="eth0"):
    cad_ip = "                "
    cad_ip = run_cmd("ip addr show "+device+" | grep \"inet \" | awk '{print $2}' | cut -d/ -f1")[:-1]
    return cad_ip
    
# Get MAC address
def getMAC(device="eth0"):
    cad_mac = "                "
    cad_mac = run_cmd("ifconfig "+device+" | grep HWaddr")[:-1]
    aux_mac = re.search("HWaddr ((\w+:)+\w+)",cad_mac)
    return str("MAC "+aux_mac.group(1).replace(':',''))

# Get connection bytes    
def getInetTransf(device="eth0"):
    cad_transf = run_cmd("ifconfig "+device+" | grep \"RX bytes\"")[:-1]
    aux_transf = re.search(r"RX bytes:(\d+) .+TX bytes:(\d+)",cad_transf)
    rx = unit(aux_transf.group(1))
    tx = unit(aux_transf.group(2))
    return str("\04"+rx.ljust(7)+tx.rjust(7)+"\03")
    
# Get connection speed
def getInetSpeed(device="eth0"):
    aux_speed = run_cmd('ifstat -i '+device+' 1 1 | grep -E \"([0-9]+(\\.[0-9]+)*) +([0-9]+(\\.[0-9]+))\"')[:-1]
    cad_speed = re.search(r"((\d+)(\.\d+)*) +((\d+)(\.\d+)*)",aux_speed)
    download = cad_speed.group(2)
    upload = cad_speed.group(5)
    return str("\x02"+download.ljust(5)+"KB/s"+upload.rjust(5)+"\x01")

# Get disk information
def getDiskInfo(device="/dev/sda1"):
    aux_disk = run_cmd("df "+device+" | grep \""+device+"\"")[:-1]
    cad_disk = re.search(r"(\d+) +(\d+) +(\d+) +(\d+%).*",aux_disk)
    if cad_disk != None:
        used      = cad_disk.group(2)
        available = cad_disk.group(3)
        use       = cad_disk.group(4)
        disk = "\x05 "+unit(int(used)*1024)+"/"+unit(int(available)*1024)
    else:
        disk = "Disk not found"
        
    return disk
    
    
# Get hostname
def getHostname():
    cad_hostname = run_cmd("hostname")
    return cad_hostname

# Get clockspeed
def getCPU():
    cad_cpu = run_cmd("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")[:-1]
    cad_cpu = "CPU: "+str(int(cad_cpu)/1000).rjust(4)+"MHz"
    return cad_cpu
    
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
    
# Are you sure to reboot the system?
def warningReboot():

    # Wait for LEFT to be released
    while lcd.is_pressed(LCD.LEFT):
        pass
        
    lcd.clear()
    lcd.set_cursor(0,0)
    lcd.message("Sure to reboot?")
    lcd.set_cursor(0,1)
    lcd.message("Y: Left, N: Any")
    
    while True:
        if lcd.is_pressed(LCD.LEFT):
            return True
        if lcd.is_pressed(LCD.RIGHT):
            return False
        if lcd.is_pressed(LCD.UP):
            return False
        if lcd.is_pressed(LCD.DOWN):
            return False
        if lcd.is_pressed(LCD.SELECT):
            return False
        time.sleep(0.1)
    
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
        info["inetspeed"]= getInetSpeed()
        info["mac"]      = getMAC(ip_device)
        info["inetbytes"]= getInetTransf(ip_device)
        info["cpu"]      = getCPU()
        info["disk"]     = getDiskInfo(disk_partition)
        time.sleep(interval)
        
    
# Data display worker
def dataDisplayWorker(interval=2):
    global enable_display
    global enable_reboot
    global button_changed
    global page
    global ncols
    
    while True:
        lcd.enable_display(enable_display)
        if button_changed:
            button_changed = False
            lcd.clear()
        if enable_reboot:
            if warningReboot():
                run_cmd("sudo reboot")
            else:
                enable_reboot = False
                lcd.clear()
        lcd.set_cursor(0,0)
        lcd.message(info[content['page'+str(page),'line0']])
        lcd.set_cursor(0,1)
        lcd.message(info[content['page'+str(page),'line1']])

        time.sleep(interval)

        
# Buttons handler worker        
def buttonsWorker(interval=0.01):
    global page
    global button_changed
    global enable_display
    global enable_reboot
    
    while True:
        if not button_changed:
            if lcd.is_pressed(LCD.SELECT):
                enable_display = not enable_display
                button_changed = True
            if lcd.is_pressed(LCD.LEFT):
                enable_reboot = True
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
    disk_partition   = str(cfg_parser.get('settings', 'disk_partition'))
    
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

# Init info dict
info_init()

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
