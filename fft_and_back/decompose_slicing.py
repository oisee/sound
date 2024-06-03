import os
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft
import pandas as pd

SLICE_DURATION = 1 / 100  # Duration of each slice in seconds
SAMPLE_RATE = 44100

def analyze_waveform(file_path):
    # Read the WAV file
    sample_rate, data = wav.read(file_path)
    
    # If stereo, take only one channel
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # Calculate the number of samples per slice
    slice_samples = int(SAMPLE_RATE * SLICE_DURATION)
    
    # Calculate the number of slices
    num_slices = int(len(data) / slice_samples)
    
    results = []
    
    for i in range(num_slices):
        # Extract the slice
        start = i * slice_samples
        end = start + slice_samples
        slice_data = data[start:end]
        
        # Pad the slice with silence
        padding_before = np.zeros(slice_samples * 49)
        padding_after = np.zeros(slice_samples * 49)
        padded_slice = np.concatenate((padding_before, slice_data, padding_after))
        
        # Perform FFT
        fft_result = fft(padded_slice)
        fft_magnitude = np.abs(fft_result)
        fft_frequencies = np.fft.fftfreq(len(fft_result), d=1/sample_rate)
        
        # Extract the most significant frequency components
        half_len = len(fft_magnitude) // 2
        fft_magnitude = fft_magnitude[:half_len]
        fft_frequencies = fft_frequencies[:half_len]
        
        # Filter out the zero-frequency component (DC component)
        nonzero_indices = fft_frequencies != 0
        fft_magnitude = fft_magnitude[nonzero_indices]
        fft_frequencies = fft_frequencies[nonzero_indices]
        
        significant_indices = np.argsort(fft_magnitude)[-1000:][::-1]  # Extract top 10 significant frequencies
        significant_frequencies = fft_frequencies[significant_indices]
        significant_amplitudes = fft_magnitude[significant_indices]
        
        # Scale amplitudes
        scaled_amplitudes = scale_amplitudes(significant_amplitudes)
        
        # Filter out frequencies with scaled amplitude lower than the threshold
        threshold = 4
        filtered_indices = scaled_amplitudes > threshold
        filtered_frequencies = significant_frequencies[filtered_indices]
        filtered_amplitudes = scaled_amplitudes[filtered_indices]
        
        # Combine frequencies and amplitudes into pairs
        frame_data = []
        for freq, amp in zip(filtered_frequencies, filtered_amplitudes):
            frame_data.append(freq)
            frame_data.append(amp)
        
        results.append(frame_data)
    
    return results

def scale_amplitudes(amplitudes):
    # Normalize amplitudes to a range of 0 to 1
    if len(amplitudes) == 0:
        return amplitudes
    max_amplitude = np.max(amplitudes)
    min_amplitude = np.min(amplitudes)
    
    # Avoid division by zero if max_amplitude equals min_amplitude
    if max_amplitude == min_amplitude:
        normalized_amplitudes = np.zeros_like(amplitudes)
    else:
        normalized_amplitudes = (amplitudes - min_amplitude) / (max_amplitude - min_amplitude)
    
    # Scale to a range of 0 to 15 and convert to integer
    scaled_amplitudes = np.round(normalized_amplitudes * 15).astype(int)
    return scaled_amplitudes

def save_frequencies_over_time(results, output_path):
    # Save frequencies and amplitudes over time to a TSV file
    with open(output_path, 'w') as f:
        for frame_data in results:
            line = '\t'.join(map(str, frame_data))
            f.write(line + '\n')

def analyze_folder(folder_path):
    # Ensure the output directory exists
    output_dir = os.path.join(folder_path, 'tsv')
    os.makedirs(output_dir, exist_ok=True)
    
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith("m.wav"):
            file_path = os.path.join(folder_path, filename)
            results = analyze_waveform(file_path)
            
            # Save the frequencies and amplitudes over time with the same name but .tsv extension
            output_filename = f"{os.path.splitext(filename)[0]}.tsv"
            output_path = os.path.join(output_dir, output_filename)
            save_frequencies_over_time(results, output_path)
            print(f"Processed {filename}, saved frequencies to {output_filename}")

if __name__ == "__main__":
    folder_path = "./in_wav/"
    analyze_folder(folder_path)
