import os
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft
import pandas as pd

SLICE_DURATION = 1 / 100  # Duration of each slice in seconds
SAMPLE_RATE = 44100

def analyze_waveform(file_path):
    sample_rate, data = wav.read(file_path)
    
    if len(data.shape) > 1:
        data = data[:, 0]
    
    slice_samples = int(SAMPLE_RATE * SLICE_DURATION)
    num_slices = int(len(data) / slice_samples)
    
    results = []
    
    for i in range(num_slices):
        start = i * slice_samples
        end = start + slice_samples
        slice_data = data[start:end]
        
        padding_before = np.zeros(slice_samples * 49)
        padding_after = np.zeros(slice_samples * 49)
        padded_slice = np.concatenate((padding_before, slice_data, padding_after))
        
        fft_result = fft(padded_slice)
        fft_magnitude = np.abs(fft_result)
        fft_frequencies = np.fft.fftfreq(len(fft_result), d=1/sample_rate)
        
        half_len = len(fft_magnitude) // 2
        fft_magnitude = fft_magnitude[:half_len]
        fft_frequencies = fft_frequencies[:half_len]
        
        nonzero_indices = fft_frequencies != 0
        fft_magnitude = fft_magnitude[nonzero_indices]
        fft_frequencies = fft_frequencies[nonzero_indices]
        
        # Determine a dynamic threshold
        threshold = np.mean(fft_magnitude) + 2 * np.std(fft_magnitude)
        significant_indices = np.where(fft_magnitude > threshold)[0]
        
        # If the number of significant frequencies exceeds 100, limit it to the top 100
        if len(significant_indices) > 1000:
            significant_indices = significant_indices[np.argsort(fft_magnitude[significant_indices])[-1000:]]
        
        significant_frequencies = fft_frequencies[significant_indices]
        significant_amplitudes = fft_magnitude[significant_indices]
        
        scaled_amplitudes = scale_amplitudes(significant_amplitudes)
        
        frame_data = []
        for freq, amp in zip(significant_frequencies, scaled_amplitudes):
            frame_data.append(freq)
            frame_data.append(amp)
        
        results.append(frame_data)
    
    return results

def scale_amplitudes(amplitudes):
    if len(amplitudes) == 0:
        return amplitudes
    max_amplitude = np.max(amplitudes)
    min_amplitude = np.min(amplitudes)
    
    if max_amplitude == min_amplitude:
        normalized_amplitudes = np.zeros_like(amplitudes)
    else:
        normalized_amplitudes = (amplitudes - min_amplitude) / (max_amplitude - min_amplitude)
    
    scaled_amplitudes = np.round(normalized_amplitudes * 15).astype(int)
    return scaled_amplitudes

def save_frequencies_over_time(results, output_path):
    with open(output_path, 'w') as f:
        for frame_data in results:
            line = '\t'.join(map(str, frame_data))
            f.write(line + '\n')

def analyze_folder(folder_path):
    output_dir = os.path.join(folder_path, 'tsv')
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(folder_path):
        if filename.endswith("m.wav"):
            file_path = os.path.join(folder_path, filename)
            results = analyze_waveform(file_path)
            
            output_filename = f"{os.path.splitext(filename)[0]}_imp.tsv"
            output_path = os.path.join(output_dir, output_filename)
            save_frequencies_over_time(results, output_path)
            print(f"Processed {filename}, saved frequencies to {output_filename}")

if __name__ == "__main__":
    folder_path = "./in_wav/"
    analyze_folder(folder_path)
