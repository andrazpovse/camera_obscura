from pydub import AudioSegment
from pydub.playback import play
import random


click = AudioSegment.from_wav("sounds/geiger/single_click.wav")

double_crackle = AudioSegment.from_wav("sounds/geiger/double_crackle.wav")
crackle_faster = AudioSegment.from_wav("sounds/geiger/single_crackle_faster.wav")
crackle_slower = AudioSegment.from_wav("sounds/geiger/single_crackle_slower.wav")
# List of all crackles.
crackles = [double_crackle, crackle_faster, crackle_slower]


def make_sound(lux):
    '''
        input: lux = log10(LUX)*100

        output: generated sound to play
    '''
    # Check lux value and assign correct lower and upper limit for silence length (in milliseconds)
    # and crackle limit (percent chance that a crackle will occur instead of click)
    if lux < 100:
        lower = 100
        upper = 500
        crackle_limit = 5
    elif lux < 500:
        lower = 50
        upper = 400
        crackle_limit = 10
    elif lux < 800:
        lower = 25
        upper = 200
        crackle_limit = 25
    else:
        lower = 10
        upper = 150
        crackle_limit = 40
    # TODO: change n based on lux (loger silences yield longer sound_to_play
    # and should therefore have less clicks & crackles to maintain simillar length
    # TODO: n could also always be the same (same for certain lux values)
    n = random.randint(4,15)
    
    # Start sound with 10ms of silence (not neccessary)
    sound_to_play = AudioSegment.silent(duration=10)
    for i in range(n):
        s = random.randint(lower,upper)
        # Append random silence to the sound
        sound_to_play += AudioSegment.silent(duration=s)
        # Append a random crackle if we are within crackle limit
        if random.randint(1,100) < crackle_limit:
            sound_to_play += random.choice(crackles)
        # Else append a click
        else:
            sound_to_play += click
        # Append random silence to the sound (same 's' as above)
        sound_to_play += AudioSegment.silent(duration=s)

    return sound_to_play

def play_sound(lux):
    '''
        input: log10 of LUX value
    '''
    # Multiply the log10LUX with 100, so we get a nicer range
    sound_to_play = make_sound(lux * 100)
    play(sound_to_play)



if __name__ == "__main__":
    # luxes and idx used for testing only
    luxes = [10, 400, 900]
    idx = 0
    # Infinite loop across luxes
    while True:
        lux = luxes[idx]
        idx += 1
        idx = idx % len(luxes)    
        print("Current lux value: ", lux)
        play(make_sound(lux))