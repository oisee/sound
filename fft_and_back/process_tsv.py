import os
import numpy as np
import pandas as pd

# Configuration constants
LOWER_FREQ_LIMIT = 80  # Hz
UPPER_FREQ_LIMIT = 14080  # Hz
CENTS_TOLERANCE = 49  # Tolerance in cents (relative to 100 cents per semitone)

def read_tsv(file_path):
    """Reads a TSV file and returns a list of frequency-amplitude pairs."""
    frames = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip() == "":
                frames.append([])
                continue
            values = list(map(float, line.strip().split('\t')))
            frames.append(values)
    return frames

def cents_difference(freq1, freq2):
    """Calculates the difference in cents between two frequencies."""
    return 1200 * np.log2(freq2 / freq1)

def group_and_filter_frequencies(frames):
    """Groups similar frequencies within each frame and filters them."""
    grouped_frames = []
    for frame in frames:
        freqs = np.array(frame[::2])
        amps = np.array(frame[1::2])

        # Filter frequencies outside the specified limits
        valid_indices = (freqs >= LOWER_FREQ_LIMIT) & (freqs <= UPPER_FREQ_LIMIT)
        freqs = freqs[valid_indices]
        amps = amps[valid_indices]

        if len(freqs) == 0:
            # If the frame is empty after filtering, add a silent frame
            grouped_frames.append([0, 0])
            continue

        grouped_freqs = []
        grouped_amps = []

        while len(freqs) > 0:
            ref_freq = freqs[0]
            mask = np.array([cents_difference(ref_freq, f) < CENTS_TOLERANCE for f in freqs])
            group_freqs = freqs[mask]
            group_amps = amps[mask]

            avg_freq = np.mean(group_freqs)
            max_amp = np.max(group_amps)

            grouped_freqs.append(avg_freq)
            grouped_amps.append(max_amp)

            freqs = freqs[~mask]
            amps = amps[~mask]

        grouped_frame = []
        for freq, amp in zip(grouped_freqs, grouped_amps):
            grouped_frame.append(freq)
            grouped_frame.append(amp)

        grouped_frames.append(grouped_frame)
    return grouped_frames

def save_grouped_frequencies(grouped_frames, output_path):
    """Saves grouped and filtered frequencies to a TSV file."""
    with open(output_path, 'w') as f:
        for frame in grouped_frames:
            frame_str = '\t'.join(map(str, frame))
            f.write(frame_str + '\n')

def process_folder(input_folder):
    """Processes all TSV files in the given folder."""
    for filename in os.listdir(input_folder):
        if filename.endswith(".tsv"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(input_folder, filename.replace(".tsv", "_reduced.tsv"))

            frames = read_tsv(input_file)
            grouped_frames = group_and_filter_frequencies(frames)
            save_grouped_frequencies(grouped_frames, output_file)
            print(f"Processed and saved grouped frequencies to {output_file}")

if __name__ == "__main__":
    input_folder = "./in_wav/tsv"
    process_folder(input_folder)
