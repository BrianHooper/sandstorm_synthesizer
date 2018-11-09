# Brian Hooper
# November 8th, 2018

import numpy as np
import wave
import sys
import commands
import os

KEYS = {'C': 174, 'F': 232, 'G': 261, 'A': 293, 'B': 329, 'D': 391, 'E': 439}
max_amplitude = 2 ** 15 - 1  # Taken from scitools.sound module


def play(soundfile):
    """
    Taken from scitools.sound module

    Play a file with name soundfile or an array soundfile.
    (The array is first written to file using the write function
    so the data type can be arbitrary.)
    The player is chosen by the programs 'open' on Mac and 'start'
    on Windows. On Linux, try different open programs for various
    distributions. If keyword argument 'player' is given, only this spesific
    commands is run.
    """
    tmpfile = 'tmp.wav'
    if isinstance(soundfile, np.ndarray):
        write(soundfile, tmpfile)
    elif isinstance(soundfile, str):
        tmpfile = soundfile

    if sys.platform[:5] == 'linux':
        status = 0
        open_commands = ['gnome-open', 'kmfclient exec', 'exo-open', 'xdg-open', 'open']
        for cmd in open_commands:
            status, output = commands.getstatusoutput('%s %s' % (cmd, tmpfile))
            if status == 0:
                break
        if status != 0:
            raise OSError('Unable to open sound file, try to set player keyword argument.')
    elif sys.platform == 'darwin':
        commands.getstatusoutput('open %s' % tmpfile)
    else:
        # assume windows
        os.system('start %s' % tmpfile)
    os.remove(tmpfile)


def write(data, filename, channels=1, sample_width=2, sample_rate=44100):
    """
    Taken from scitools.sound module

    Writes the array data to the specified file.
    The array data type can be arbitrary as it will be
    converted to numpy.int16 in this function.
    """
    ofile = wave.open(filename, 'w')
    ofile.setnchannels(channels)
    ofile.setsampwidth(sample_width)
    ofile.setframerate(sample_rate)
    ofile.writeframesraw(data.astype(np.int16).tostring())
    ofile.close()


def karplus_strong(wavetable, n_samples=44100):
    """
    Converts a wavetable to a musical note using karplus_strong
    :param wavetable: wavetable to convert
    :param n_samples: number of samples
    :return: karplus-strong note
    """
    samples = []
    current_sample = 0
    previous_value = wavetable[0]
    while len(samples) < n_samples:
        wavetable[current_sample] = 0.5 * (wavetable[current_sample] + previous_value)
        samples.append(wavetable[current_sample])
        previous_value = samples[-1]
        current_sample += 1
        current_sample = current_sample % wavetable.size
    return np.array(samples)


def create_random_wavetable(frequency, length, samples=44100):
    """
    Creates a wavetable of randomized values
    between -1.0 and 1.0
    :param frequency: frequency of note
    :param length: length in seconds
    :param samples: number of seconds
    :return: wavetable
    """
    length = int((samples // frequency) * length)
    wavetable = np.random.uniform(-1.0, 1.0, length)
    wavetable = wavetable.astype(np.float)
    return wavetable


def create_note(wavetable, length, samples=44100):
    """
    Converts a wavetable to a note using karplus_strong
    :param wavetable: wavetable to be converted
    :param length: length in seconds
    :param samples: number of samples
    :return: modified wavetable
    """
    x1 = karplus_strong(wavetable, samples * length)
    return list(x1)


def amplify(note):
    """
    Amplifies a waveform and converts it to an np array
    :param note: waveform
    :return: amplified waveform
    """
    return np.array(list(map(lambda i: i * max_amplitude, note)))


def create_sound(frequency, length=0.5):
    """
    Creates a single note
    :param frequency: note frequency
    :param length: length in seconds
    :return: note
    """
    wavetable = create_random_wavetable(frequency * length, length)
    note = create_note(wavetable, length)
    return note


def play_song(notes, bpm):
    """
    Plays a song based on a string of notes
    :param notes: string of notes
    :param bpm: song bpm
    :return: None
    """
    note_length = 16.0 / bpm
    song = []
    for i in range(0, len(notes)):
        note = notes[i]

        if note != '-':
            length = 1
            index = i + 1
            while index < len(notes):
                next_note = notes[index]
                if next_note == '-':
                    length += 1
                    index += 1
                else:
                    break

            song += create_sound(KEYS[note], note_length * length)
    song = amplify(song)
    play(song)
    return song


if __name__ == "__main__":
    sandstorm = "BBBBB-BBBBBBB-EEEEEEE-DDDDDDD-AABBBBB-BBBBBBB-EEBBBBB-BBBBBBB---"
    music = play_song(sandstorm, 136.0)
    # write(music, "sandstorm.wav")
