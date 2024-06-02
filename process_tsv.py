import os
import numpy as np
import pandas as pd

# Configuration constants
LOWER_FREQ_LIMIT = 110  # Hz
UPPER_FREQ_LIMIT = 14080  # Hz
FREQUENCY_TOLERANCE = 5  # Hz, tolerance for grouping similar frequencies

def read_tsv(file_path):
    """Reads a TSV file and returns a list of frequency-amplitude pairs."""
    frames = []
    with open(file_path, 'r') as f:
        for line in f:
            values = list(map(float, line.strip().split('\t')))
            frames.append(values)
    return frames

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

def save_grouped_frequencies(grouped_frames, output_path):
    """Saves grouped and filtered frequencies to a TSV file."""
    with open(output_path, 'w') as f:
        for frame in grouped_frames:
            frame_str = '\t'.join(map(str, frame))
            f.write(frame_str + '\n')

if __name__ == "__main__":
    # input_file = "/mnt/data/cosine_440_523.25Hz.tsv"
    # output_file = "/mnt/data/cosine_440_523.25Hz_processed.tsv"
    input_file = "./in_wav/tsv/other.tsv"
    output_file = "./in_wav/tsv/other_processed.tsv"    

    frames = read_tsv(input_file)
    grouped_frames = group_and_filter_frequencies(frames)
    save_grouped_frequencies(grouped_frames, output_file)
    print(f"Processed and saved grouped frequencies to {output_file}")
