import os
import numpy as np

# Configuration constants
WINDOW_SIZE = 8  # Sliding window size (in number of frames)
GAP_TOLERANCE = 2  # Maximum allowed gap in frames
CENTS_TOLERANCE = 49  # Tolerance in cents (relative to 100 cents per semitone)

def read_tsv(file_path):
    """Reads a TSV file and returns a list of frequency-amplitude pairs."""
    frames = []
    with open(file_path, 'r') as f:
        for line in f:
            values = list(map(float, line.strip().split('\t')))
            frames.append(values)
    return frames

def cents_difference(freq1, freq2):
    """Calculates the difference in cents between two frequencies."""
    return 1200 * np.log2(freq2 / freq1)

def sliding_window_average(frames, window_size, gap_tolerance):
    """Applies a sliding window to average similar frequency groups across frames."""
    num_frames = len(frames)
    max_pairs = max(len(frame) // 2 for frame in frames)
    windowed_frames = []

    for i in range(num_frames):
        window = frames[max(0, i - window_size + 1):i + 1]
        averaged_frame = []

        for j in range(max_pairs):
            group_freqs = []
            group_amps = []
            for k in range(len(window)):
                if 2 * j < len(window[k]):
                    freq = window[k][2 * j]
                    amp = window[k][2 * j + 1]
                    if freq > 0 and amp > 0:
                        group_freqs.append(freq)
                        group_amps.append(amp)

            if len(group_freqs) > 0:
                avg_freq = np.mean(group_freqs)
                avg_amp = np.mean(group_amps)
                averaged_frame.extend([avg_freq, avg_amp])
            else:
                averaged_frame.extend([0, 0])

        windowed_frames.append(averaged_frame)

    return windowed_frames

def save_grouped_frequencies(grouped_frames, output_path):
    """Saves grouped and filtered frequencies to a TSV file."""
    with open(output_path, 'w') as f:
        for frame in grouped_frames:
            frame_str = '\t'.join(map(str, frame))
            f.write(frame_str + '\n')

def process_folder(input_folder):
    """Processes all _reduced.tsv files in the given folder and saves the smoothed output."""
    for filename in os.listdir(input_folder):
        if filename.endswith("_reduced.tsv"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(input_folder, filename.replace("_reduced.tsv", "_smooth.tsv"))

            frames = read_tsv(input_file)
            smoothed_frames = sliding_window_average(frames, WINDOW_SIZE, GAP_TOLERANCE)
            save_grouped_frequencies(smoothed_frames, output_file)
            print(f"Processed and saved smoothed frequencies to {output_file}")

if __name__ == "__main__":
    input_folder = "./in_wav/tsv"
    process_folder(input_folder)
