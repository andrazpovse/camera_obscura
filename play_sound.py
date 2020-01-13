from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

import random
import threading
import time


click = AudioSegment.from_wav("sounds/geiger/single_click.wav")

double_crackle = AudioSegment.from_wav("sounds/geiger/double_crackle.wav")
crackle_faster = AudioSegment.from_wav("sounds/geiger/single_crackle_faster.wav")
crackle_slower = AudioSegment.from_wav("sounds/geiger/single_crackle_slower.wav")
# List of all crackles.
crackles = [double_crackle, crackle_faster, crackle_slower]



def play(sound):
    '''
        Play sound in a thread
    '''
    play_obj = _play_with_simpleaudio(sound)


def sound_generation_limits(lux):
    '''
        input: lux = log10(LUX)*100...ranging from 0 to about 500

        output: 
            - lower_silence_limit: lower limit for silence sound parts (in MS)
            - upper_silence_limit: upper limit for silence sound parts (in MS)
            - crackle_limit: percent chance of crackle playing
    '''
    print("Log10(LUX) * 100  = ", lux)
    # Very dark, approaching night
    if lux < 150:
        crackle_limit = (lux / 30)
        upper_silence_limit = 1000 - lux
        lower_silence_limit = upper_silence_limit / 2
    # Cloudy, very overcast day is less than 250
    elif lux < 250:
        crackle_limit = (lux / 20)
        upper_silence_limit = 750 - lux
        lower_silence_limit = upper_silence_limit / 3
    elif lux < 350:
        crackle_limit = (lux / 15)
        upper_silence_limit = 650 - lux
        lower_silence_limit = upper_silence_limit / 4
    # More than 350 is full daylight higher values reaching direct sun
    elif lux < 450:
        upper_silence_limit = 600 - lux
        lower_silence_limit = upper_silence_limit / 5
        crackle_limit = (lux / 10)
    # Direct daylight sunlight values reaching up to 500
    else:
        upper_silence_limit = 550 - lux
        lower_silence_limit = upper_silence_limit / 10
        crackle_limit = (lux / 7)
    # Safety check in case lux is 0
    if crackle_limit <= 0:
        crackle_limit = 1
    print('upper_silence_limit: ', upper_silence_limit)
    print('lower_silence_limit: ', lower_silence_limit)
    print('crackle_limit: ', crackle_limit)

    return int(lower_silence_limit), int(upper_silence_limit), int(crackle_limit)

def make_sound(lux):
    '''
        input: lux = log10(LUX)*100...ranging from 0 to about 485

        output: generated sound to play
    '''
    # get limits for max,min length of silence and crackle sound percentage chance
    lower_silence_limit, upper_silence_limit, crackle_limit = sound_generation_limits(lux)
    
    # Make each sound sample last around 3 seconds
    approx_sample_length = 3*1000
    # Start sound with 10ms of silence (not neccessary)
    sound_to_play = AudioSegment.silent(duration=10)
    # Append silences, clicks and crackles untill we reach wanted length
    while len(sound_to_play) < approx_sample_length:
        # Append random silence to the sound within the limits
        s = random.randint(lower_silence_limit,upper_silence_limit)
        sound_to_play += AudioSegment.silent(duration=s)
        # Append a random crackle if we are within crackle limit
        if random.randint(1,100) < crackle_limit:
            sound_to_play += random.choice(crackles)
        # Else append a click
        else:
            sound_to_play += click

    return sound_to_play

def play_sound(lux):
    '''
        input: log10 of LUX value
    '''
    # Multiply the log10LUX with 100, so we get a nicer range
    sound_to_play = make_sound(lux * 100)
    # Play sound in a thread so it can overlap while it loads a new file to play
    t1 = threading.Thread(target=play,args=(sound_to_play,))
    t1.start()
    # RPI takes cca 2 seconds to play a new file)
    time.sleep(sound_to_play.duration_seconds - 2)



if __name__ == "__main__":
    # log10luxes and idx used for testing only
    log10luxes = [2.176, 3.4771, 4.431, 4.65]
    idx = 0
    # Infinite loop across luxes
    while True:
        lux = log10luxes[idx]
        idx += 1
        idx = idx % len(log10luxes)    
        play_sound(lux)