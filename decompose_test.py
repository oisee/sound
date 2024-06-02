import os
import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft
import pandas as pd

def analyze_waveform(file_path):
    # Read the WAV file
    sample_rate, data = wav.read(file_path)
    
    # If stereo, take only one channel
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # Perform FFT
    fft_result = fft(data)
    fft_magnitude = np.abs(fft_result)
    fft_frequencies = np.fft.fftfreq(len(fft_result), d=1/sample_rate)
    
    # Extract the most significant frequency components
    half_len = len(fft_magnitude) // 2
    fft_magnitude = fft_magnitude[:half_len]
    fft_frequencies = fft_frequencies[:half_len]
    
    significant_indices = np.argsort(fft_magnitude)[-10:][::-1]  # Extract top 10 significant frequencies
    significant_frequencies = fft_frequencies[significant_indices]
    significant_amplitudes = fft_magnitude[significant_indices]
    
    return significant_frequencies, significant_amplitudes

def scale_amplitudes(amplitudes):
    # Normalize amplitudes to a range of 0 to 1
    max_amplitude = np.max(amplitudes)
    min_amplitude = np.min(amplitudes)
    normalized_amplitudes = (amplitudes - min_amplitude) / (max_amplitude - min_amplitude)
    
    # Scale to a range of 0 to 15 and convert to integer
    scaled_amplitudes = np.round(normalized_amplitudes * 15).astype(int)
    return scaled_amplitudes

def save_frequencies(frequencies, amplitudes, output_path):
    # Scale the amplitudes
    scaled_amplitudes = scale_amplitudes(amplitudes)
    
    # Save frequencies and scaled amplitudes to a TSV file
    df = pd.DataFrame({'Frequency': frequencies, 'Amplitude': scaled_amplitudes})
    df.to_csv(output_path, sep='\t', index=False)

def analyze_folder(folder_path):
    # Ensure the output directory exists
    output_dir = os.path.join(folder_path, 'tsv')
    os.makedirs(output_dir, exist_ok=True)
    
    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".wav"):
            file_path = os.path.join(folder_path, filename)
            significant_frequencies, significant_amplitudes = analyze_waveform(file_path)
            
            # Save the frequencies and scaled amplitudes with the same name but .tsv extension
            output_filename = f"{os.path.splitext(filename)[0]}.tsv"
            output_path = os.path.join(output_dir, output_filename)
            save_frequencies(significant_frequencies, significant_amplitudes, output_path)
            print(f"Processed {filename}, saved frequencies to {output_filename}")

if __name__ == "__main__":
    folder_path = "./test_wav/"
    analyze_folder(folder_path)
