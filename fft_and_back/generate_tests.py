import numpy as np
import scipy.io.wavfile as wav
import os

# Output directory
OUTPUT_DIR = "./test_wav/"
# Sampling rate
SAMPLE_RATE = 44100

# Duration of the sound file in seconds
DURATION = 3

# Frequencies to generate
FREQUENCIES = [
    440,  # A4
    523.25,  # C5
    587.33,  # D5
    659.25,  # E5
    698.46,  # F5
    783.99,  # G5
    880  # A5
]

# Waveform generators
def generate_cosine(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.cos(2 * np.pi * frequency * t)

def generate_pulse(frequency, duty_cycle, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.where((t * frequency % 1) < duty_cycle, 1.0, -1.0)

def generate_triangle(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 2 * np.abs(2 * (t * frequency % 1) - 1) - 1

def generate_sawtooth_up(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 2 * (t * frequency % 1) - 1

def generate_sawtooth_down(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 1 - 2 * (t * frequency % 1)

def generate_sliding_cosine(start_freq, end_freq, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    frequencies = np.linspace(start_freq, end_freq, int(sample_rate * duration))
    waveform = np.cos(2 * np.pi * frequencies * t)
    return waveform

# Save waveform to a .wav file
def save_waveform(waveform, filename, directory=OUTPUT_DIR):
    # Normalize waveform to 16-bit range
    waveform_integers = np.int16(waveform * 32767)
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    # Save the file in the output directory
    wav.write(os.path.join(OUTPUT_DIR, filename), SAMPLE_RATE, waveform_integers)

# Generate waveforms and save them to files
def generate_waveforms():
    waveforms = {
        "cosine": generate_cosine,
        "pulse_50": lambda f, d, s: generate_pulse(f, 0.5, d, s),
        "pulse_70": lambda f, d, s: generate_pulse(f, 0.7, d, s),
        "triangle": generate_triangle,
        "saw_up": generate_sawtooth_up,
        "saw_down": generate_sawtooth_down,
        "sliding_cosine": lambda f, d, s: generate_sliding_cosine(1760, 440, d, s)
    }

    for name, generator in waveforms.items():
        if name == "sliding_cosine":
            waveform = generator(0, DURATION, SAMPLE_RATE)  # Frequencies are hardcoded for sliding_cosine
            filename = f"{name}_1760_to_440Hz.wav"
            save_waveform(waveform, filename)
        else:
            for freq in FREQUENCIES:
                waveform = generator(freq, DURATION, SAMPLE_RATE)
                filename = f"{name}_{freq}Hz.wav"
                save_waveform(waveform, filename)
            
            for i in range(len(FREQUENCIES)):
                for j in range(i + 1, len(FREQUENCIES)):
                    combined_freqs = [FREQUENCIES[i], FREQUENCIES[j]]
                    waveform = sum(generator(f, DURATION, SAMPLE_RATE) for f in combined_freqs) / len(combined_freqs)
                    filename = f"{name}_{'_'.join(map(str, sorted(combined_freqs)))}Hz.wav"
                    save_waveform(waveform, filename)

if __name__ == "__main__":
    generate_waveforms()
