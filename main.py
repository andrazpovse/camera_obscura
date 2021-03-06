
import sys
# Append library locations to path
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
import time
import RPi.GPIO as GPIO
# Import SmBus for I2C
import smbus
import math
import requests
# Other python file that takes care of generating and playing sound
from play_sound import play_sound


# Configuration for light-sensor (BH1750)
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20

#Configuration for sending DATA
API_KEY = "DBD15MS5LSQUNJL6"
API_URL = "http://vitez.si:8086/write?db=ioi"
DEVICE_NAME = "dev01"



def detect_movement(INPUT_PINS):
    '''
        @params
            INPUT_PINS - numbers of pins where RADAR/PIR sensor is on
        @returns
            boolean - if movement is detected
    '''
    # Check list of inputs for movement. If any of them is true, return true
    for ip in INPUT_PINS:
        if GPIO.input(ip):
            return True
    # else return false
    return False

def convertToNumber(data):
    # Simple function to convert 2 bytes of data
    # into a decimal number
    return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE):
    """
        LUX scale:

        0.05–0.3	Full moon on a clear night
        3.4	Dark limit of civil twilight under a clear sky
        20–50	Public areas with dark surroundings
        50	Family living room lights
        80	Office building hallway/toilet lighting
        100	Very dark overcast day
        150	Train station platforms
        320–500	Office lighting
        400	Sunrise or sunset on a clear day.
        1000	Overcast day; typical TV studio lighting
        10,000–25,000	Full daylight (not direct sun)
        32,000–100,000	Direct sunlight
    """
    data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
    return int(convertToNumber(data)) 

def sendLightToServer(value):
    print("Sending light value to:", API_URL)
    try:
        r = requests.post(url = API_URL, data = 'lightIntensity,machine='+DEVICE_NAME+' intensity='+str(value),
            timeout=2)
        print(r)

        return True
    except Exception as e:
        print("Failed to connect to server")
        print(e)

        return False

def sendMovementToServer(value):
    print("Sending movement value to:", API_URL)
    try:
        r = requests.post(url = API_URL, data = 'movement,machine='+DEVICE_NAME+' movement='+str(value),
            timeout=2)
        print(r)

        return True
    except Exception as e:
        print("Failed to connect to server")
        print(e)

        return False

def log_lux_scale(lux_value):
    """
        Changes the lux input to log10

        input: lux_value....value between 0 and 65536 -> after log10 yields between 0 and cca 5

        output: log10 of lux value

    """
    if lux_value == 0:
        log_lux = 0
    else:
        log_lux = math.log10(lux_value)

    return log_lux

def millis():
    # equivalent to C millis
    return int(round(time.time() * 1000))



if __name__ == "__main__":
    # Init GPIO
    GPIO.setmode(GPIO.BCM) 
    # Radar sensor is on GPIO14. List of movement detector input pins.
    INPUT_PINS = [14]
    for ip in INPUT_PINS:
        GPIO.setup(ip, GPIO.IN)

    # Init smbus and light sensor
    bus = smbus.SMBus(1)

    # How long to play after last movement was detected - in millis
    # Set to 60 seconds
    movement_timeout = 60 * 1000
    last_movement = 0

    # If we fail to connect to server, this will tell us after how many iterations
    # we try again
    try_connect_to_server = 0
    while True:
        # If movement is detected, update last_movement value
        movement_status = 0
        if detect_movement(INPUT_PINS):
            print("Movement detected")
            last_movement = millis()
            movement_status = 1
        else:
            print("No movement")
            movement_status = 0

        # Read LUX and send to server regardless of movement
        lux = readLight()

        # Only connect to server if previous attempts were ok, or certain iterations passed
        if try_connect_to_server == 0:
            # TODO: if we have no internet connection, timeout will not work
            # TODO: fix issue when we have no internet connection (takes too long to drop)
            # Send movement status to server
            status1 = sendMovementToServer(movement_status)
            # Send light status to server
            status2 = sendLightToServer(lux)
            
            # If any of them is false, stop connecting for 20 iterations
            if status1 and status2:
                try_connect_to_server = 20
        else:
            # Reduce remaining iterations untill another connection to server
            try_connect_to_server -= 1
        print("Current light level:", lux, "lux")
        # If movement was present in the last MOVEMENT_TIMEOUT milliseconds, do something
        if last_movement + movement_timeout > millis():
            
            print(lux, "lux")
            log10lux = log_lux_scale(lux)
            print("LOG10 lux: ", log10lux)
            # Play sound based on log10 lux value
            play_sound(log10lux)
        # Nobody inside. No sounds. Sleep for 1 second
        else:
            time.sleep(1)
