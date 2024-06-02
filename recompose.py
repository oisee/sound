import os
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
from scipy.signal import square

# Configuration constants
SAMPLE_RATE = 44100  # Hz
SLICE_DURATION = 1 / 100  # seconds
SLICE_SAMPLES = int(SAMPLE_RATE * SLICE_DURATION)
FREQUENCY_TOLERANCE = 0.5  # Hz, tolerance for grouping similar frequencies
LOWER_LIMIT = 110  # Hz, lower limit for frequencies
UPPER_LIMIT = 14080  # Hz, upper limit for frequencies

def read_tsv(file_path):
    """Reads a TSV file and returns a list of frequency-amplitude pairs."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
        frames = []
        for line in lines:
            values = list(map(float, line.strip().split('\t')))
            frames.append(values)
    return frames

def group_frequencies(frames):
    """Groups similar frequencies within each frame."""
    grouped_frames = []
    for frame in frames:
        freqs = np.array(frame[::2])
        amps = np.array(frame[1::2])
        
        valid_mask = (freqs >= LOWER_LIMIT) & (freqs <= UPPER_LIMIT)
        freqs = freqs[valid_mask]
        amps = amps[valid_mask]
        
        grouped_freqs = []
        grouped_amps = []
        
        while len(freqs) > 0:
            ref_freq = freqs[0]
            mask = (np.abs(freqs - ref_freq) < FREQUENCY_TOLERANCE)
            group_freqs = freqs[mask]
            group_amps = amps[mask]
            
            avg_freq = np.mean(group_freqs)
            avg_amp = np.mean(group_amps)
            
            grouped_freqs.append(avg_freq)
            grouped_amps.append(avg_amp)
            
            freqs = freqs[~mask]
            amps = amps[~mask]
        
        grouped_frame = []
        for freq, amp in zip(grouped_freqs, grouped_amps):
            grouped_frame.append(freq)
            grouped_frame.append(amp)
        
        grouped_frames.append(grouped_frame)
    return grouped_frames

def generate_audio_frame(frame, waveform='cosine', duty=0.5):
    """Generates an audio frame for the given frequency-amplitude pairs."""
    t = np.linspace(0, SLICE_DURATION, SLICE_SAMPLES, endpoint=False)
    audio_frame = np.zeros(SLICE_SAMPLES)
    
    if not frame:
        return audio_frame  # Return silent frame if no valid frequencies
    
    for i in range(0, len(frame), 2):
        freq = frame[i]
        amp = frame[i + 1] / 15.0  # Convert amplitude to a scale of 0 to 1
        if waveform == 'cosine':
            audio_frame += amp * np.cos(2 * np.pi * freq * t)
        elif waveform == 'pulse':
            audio_frame += amp * square(2 * np.pi * freq * t, duty=duty)
    
    audio_frame = np.clip(audio_frame, -1, 1)  # Clipping to avoid overflow
    return audio_frame

def reconstruct_wav(input_folder, output_folder, waveform='cosine', duty=0.5):
    """Reconstructs the WAV file from the grouped frequencies."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".tsv"):
            file_path = os.path.join(input_folder, filename)
            frames = read_tsv(file_path)
            grouped_frames = group_frequencies(frames)
            
            all_audio = []
            for frame in grouped_frames:
                audio_frame = generate_audio_frame(frame, waveform, duty)
                all_audio.append(audio_frame)
            
            all_audio = np.concatenate(all_audio)
            all_audio = (all_audio * 32767).astype(np.int16)  # Convert to 16-bit PCM
            
            output_filename = f"{os.path.splitext(filename)[0]}_reconstructed.wav"
            output_file_path = os.path.join(output_folder, output_filename)
            wav.write(output_file_path, SAMPLE_RATE, all_audio)
            print(f"Reconstructed WAV file saved to {output_file_path}")

if __name__ == "__main__":
    input_folder = "./in_wav/tsv/"
    output_folder = "./in_wav/rec2/"
    # input_folder = "./test_wav/tsv/"
    # output_folder = "./test_wav/rec2/"
    waveform = 'cosine'  # or 'pulse'
    duty = 0.5  # Duty cycle for pulse waveform
    
    reconstruct_wav(input_folder, output_folder, waveform, duty)
