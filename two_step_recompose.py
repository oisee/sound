import numpy as np
import pandas as pd
from scipy.io import wavfile
import os

# Constants
INPUT_DIR = './in_wav/tsv/'
OUTPUT_DIR = './in_wav/tsv/wav/'
FREQ_TOLERANCE_CENTS = 49
FREQ_MIN = 110
FREQ_MAX = 14080
SAMPLE_RATE = 44100

# Function to convert cents to frequency ratio
def cents_to_ratio(cents):
    return 2 ** (cents / 1200)

# Function to group frequencies within a tolerance
def group_frequencies(frequencies, amplitudes, tolerance):
    grouped_freqs = []
    grouped_amps = []
    for freq, amp in zip(frequencies, amplitudes):
        if FREQ_MIN <= freq <= FREQ_MAX:
            for i, (gf, ga) in enumerate(zip(grouped_freqs, grouped_amps)):
                if abs(np.log2(gf / freq)) <= np.log2(cents_to_ratio(tolerance)):
                    if amp > ga:
                        grouped_freqs[i] = freq
                        grouped_amps[i] = amp
                    break
            else:
                grouped_freqs.append(freq)
                grouped_amps.append(amp)
    return grouped_freqs, grouped_amps

# Process TSV files
def process_tsv_file(input_file, output_file):
    df = pd.read_csv(input_file, sep='\t', header=None)
    processed_data = []
    for _, row in df.iterrows():
        frequencies = row[::2].values
        amplitudes = row[1::2].values
        if np.all(frequencies == 0) and np.all(amplitudes == 0):
            processed_data.append([0, 0])
        else:
            grouped_freqs, grouped_amps = group_frequencies(frequencies, amplitudes, FREQ_TOLERANCE_CENTS)
            processed_row = []
            for gf, ga in zip(grouped_freqs, grouped_amps):
                processed_row.extend([gf, ga])
            processed_data.append(processed_row)
    pd.DataFrame(processed_data).to_csv(output_file, sep='\t', index=False, header=False)

# Generate WAV file from processed TSV
def generate_wav_file(tsv_file, wav_file):
    df = pd.read_csv(tsv_file, sep='\t', header=None)
    audio_data = []
    for _, row in df.iterrows():
        frame_data = []
        for freq, amp in zip(row[::2], row[1::2]):
            if freq == 0 and amp == 0:
                frame_data.append(np.zeros(SAMPLE_RATE // 100))
            else:
                t = np.linspace(0, 0.01, SAMPLE_RATE // 100, endpoint=False)
                frame_data.append(amp * np.cos(2 * np.pi * freq * t))
        audio_data.extend(np.sum(frame_data, axis=0))
    wavfile.write(wav_file, SAMPLE_RATE, np.int16(audio_data))

# Main processing
if __name__ == '__main__':
    for file_name in os.listdir(INPUT_DIR):
        if file_name.endswith('.tsv'):
            input_file = os.path.join(INPUT_DIR, file_name)
            output_tsv_file = os.path.join(OUTPUT_DIR, file_name.replace('.tsv', '_processed.tsv'))
            process_tsv_file(input_file, output_tsv_file)
            output_wav_file = os.path.join(OUTPUT_DIR, file_name.replace('.tsv', '_reconstructed.wav'))
            generate_wav_file(output_tsv_file, output_wav_file)
