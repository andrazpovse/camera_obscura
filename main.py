
import sys
# Append VLC library location to path
sys.path.append('/home/pi/.local/lib/python3.7/site-packages')
import vlc
import time
import RPi.GPIO as GPIO
# Import SmBus for I2C
import smbus

# Configuration for light-sensor (BH1750)
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20

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
        # Change volume based on light. Can also break the loop if a certain threshold
        # is reached.
        if i > 5:
            pass
            # vlc.libvlc_audio_set_volume(p, 50)
        
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
    # Read the pin
    if (GPIO.input(INPUT_PIN) == True): 
        print('MOVEMENT')
        return True
    else:
        print('NO movement')
        return False

def convertToNumber(data):
    # Simple function to convert 2 bytes of data
    # into a decimal number
    return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE):
    data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
    return convertToNumber(data)    

def light_status():
    # TODO
    # Returns some value correlated to brightness
	lightStatus = readLight()
	return lightStatus

if __name__ == "__main__":
    # Init GPIO
    GPIO.setmode(GPIO.BCM) 
    # Radar sensor is on GPIO14
    INPUT_PIN = 14
    GPIO.setup(INPUT_PIN, GPIO.IN)
    # detect_movement(INPUT_PIN)        

    # Init smbus and light sensor
    bus = smbus.SMBus(1)
	
    # Init VLC
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()

    # Set the music file
    p.set_media(set_music(instance, 'test.mp3')) 


    # infinite loop that plays music when movement is detected
    while True:
        # TODO Trigger play upon movement detected by sensor
        play(p)
        # Set the media to play next...can be based on current light
        p.set_media(set_music(instance, 'test.mp3'))
        print(light_status(), "lux")
        time.sleep(1)

