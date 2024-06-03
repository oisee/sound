import os
import numpy as np

SLICE_DURATION = 1 / 100  # Duration of each slice in seconds
SAMPLE_RATE = 44100
FRAME_SAMPLES = int(SAMPLE_RATE * SLICE_DURATION)  # Number of samples per frame

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

def detect_frequency_events(frames, cents_tolerance=70):
    events = []
    current_events = {}

    def frequency_key(freq):
        return round(1200 * np.log2(freq / 440.0))  # Relative to A4

    for frame_index, frame in enumerate(frames):
        frame_events = []
        for i in range(0, len(frame), 2):
            freq = frame[i]
            amp = frame[i + 1]
            if freq > 0 and amp > 0:
                key = frequency_key(freq)
                # Look for similar frequencies in previous and next frames
                match_found = False
                for offset in [-1, 0, 1]:
                    if 0 <= frame_index + offset < len(frames):
                        adjacent_frame = frames[frame_index + offset]
                        for j in range(0, len(adjacent_frame), 2):
                            adjacent_freq = adjacent_frame[j]
                            adjacent_amp = adjacent_frame[j + 1]
                            if adjacent_freq > 0 and adjacent_amp > 0:
                                if abs(cents_difference(freq, adjacent_freq)) <= cents_tolerance:
                                    #print(f"Matched {freq} Hz with {adjacent_freq} Hz")
                                    key = frequency_key(adjacent_freq)
                                    match_found = True
                                    break
                        if match_found:
                            break

                if key in current_events:
                    # Update the end frame and amplitude (average over time)
                    event = current_events[key]
                    event['end_frame'] = frame_index
                    event['amplitudes'].append(amp)
                    event['frequency'] = (event['frequency'] * (len(event['amplitudes']) - 1) + freq) / len(event['amplitudes'])
                else:
                    # Start a new event
                    current_events[key] = {
                        'start_frame': frame_index,
                        'end_frame': frame_index,
                        'frequency': freq,
                        'amplitudes': [amp]
                    }
                frame_events.append(key)

        # Check for ended events
        ended_keys = [key for key in current_events if key not in frame_events]
        for key in ended_keys:
            event = current_events[key]
            event['amplitude'] = np.mean(event['amplitudes'])
            events.append(event)
            del current_events[key]

    # Append remaining ongoing events
    for key in current_events:
        event = current_events[key]
        event['amplitude'] = np.mean(event['amplitudes'])
        events.append(event)

    return events

def save_events(events, output_path):
    """Saves frequency events to a TSV file."""
    with open(output_path, 'w') as f:
        for event in events:
            line = f"{event['start_frame']}\t{event['end_frame']}\t{event['frequency']}\t{event['amplitude']}\n"
            f.write(line)

def process_folder(input_folder):
    """Processes all TSV files in the given folder and saves the event-based output."""
    output_dir = os.path.join(input_folder, 'events')
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith("reduced.tsv") or filename.endswith("smooth.tsv"):
            file_path = os.path.join(input_folder, filename)
            frames = read_tsv(file_path)
            events = detect_frequency_events(frames)
            
            output_filename = f"{os.path.splitext(filename)[0]}_events.tsv"
            output_path = os.path.join(output_dir, output_filename)
            save_events(events, output_path)
            print(f"Processed {filename}, saved events to {output_filename}")

if __name__ == "__main__":
    input_folder = "./in_wav/tsv"
    process_folder(input_folder)
