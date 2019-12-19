
import sys
# Append VLC library location to path
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
import vlc
import time
import RPi.GPIO as GPIO
# Import SmBus for I2C
import smbus
import math

# Configuration for light-sensor (BH1750)
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20

# Folder with the sounds
FOLDER_SOUNDS = "sounds/"
# Dictionary for sounds
SOUNDS = {
    0: "low.mp3",
    1: "low.mp3",
    2: "mid.mp3",
    3: "mid.mp3",
    4: "high.mp3",
    5: "high.mp3"
}

def play(p):
    '''
        Plays the entire music track
        @params
            p - media player instance with set media file
    '''
    p.play() 
    vlc.libvlc_audio_set_volume(p, 100)  # volume 0..100
    time.sleep(1)
    duration = p.get_length() / 1000

    for i in range(int(duration)):
        time.sleep(1)
        print("Playing for ", i, "seconds.")

    return


def set_music(instance, file):
    '''
        Sets the music to play.
        @params
            instance - VLC instance
            file - path to file(mp3, others?try)
        @returns
            media file for instance to play
    '''
    m = instance.media_new(file)

    return m

def detect_movement(INPUT_PIN):
    '''
        @params
            INPUT_PIN - number of pin where RADAR/PIR sensor is on
        @returns
            boolean - if movement is detected
    '''
    # Read the pin and return boolean
    return GPIO.input(INPUT_PIN)

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

def log_lux_scale(lux_value):
    """
        Changes the lux input to log10

        input: lux_value....value between 0 and 65536 -> after log10 yields between 0 and cca 5

        output: integer ranging from 0 to 50, corresponding to song index to play

    """
    if lux_value == 0:
        log_lux = 0
    else:
        log_lux = math.log10(lux_value)

    # For example if we have cca 50 different songs, play one that is on that rank.
    return int(log_lux * 10)

def millis():
    # equivalent to C millis
    return int(round(time.time() * 1000))


if __name__ == "__main__":
    # Init GPIO
    GPIO.setmode(GPIO.BCM) 
    # Radar sensor is on GPIO14
    INPUT_PIN = 14
    GPIO.setup(INPUT_PIN, GPIO.IN)

    # Init smbus and light sensor
    bus = smbus.SMBus(1)
	
    # Init VLC
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()

    # Set the music file to play
    p.set_media(set_music(instance, 'test.mp3')) 


    # infinite loop that plays music when movement is detected
    movement_timeout = 5000
    last_movement = 0
    while True:
        # If movement is detected, update last_movement value
        if detect_movement(INPUT_PIN):
            print("Movement detected")
            last_movement = millis()
        else:
            print("No movement")

        # Read LUX and send to server regardless of movement
        # TODO: send LUX value to some server 
        # (no need to send each value by itself - maybe avg of the last 30 values? or all 30 values at once)
        lux = readLight()

        # If movement was present in the last MOVEMENT_TIMEOUT milliseconds, do something
        if last_movement + movement_timeout > millis():
            
            print(lux, "lux")
            print("LOG10 lux: ", log_lux_scale(lux))

            # Set the media to play next based on LUX value
            # TODO: remove '/10' part. this is just because we only have like 3 tracks
            sound_to_play = SOUNDS[(log_lux_scale() / 10)]
            p.set_media(set_music(instance, FOLDER_SOUNDS + sound_to_play))
            play(p)
        # Nobody inside. No sounds. Sleep for 2 seconds
        else:
            time.sleep(2)

