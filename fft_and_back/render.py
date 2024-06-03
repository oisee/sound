import os
import numpy as np
import scipy.io.wavfile as wav

SAMPLE_RATE = 44100  # 44.1 kHz sample rate
FRAME_DURATION = 1 / 100  # Frame duration is 1/100 of a second
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_DURATION)  # Number of samples per frame

def read_event_tsv(file_path):
    events = []
    with open(file_path, 'r') as f:
        for line in f:
            start_frame, end_frame, freq, amp = map(float, line.strip().split('\t'))
            events.append({
                'start_frame': int(start_frame),
                'end_frame': int(end_frame),
                'frequency': freq,
                'amplitude': amp
            })
    return events

def generate_audio_signal(events, frame_samples=FRAME_SAMPLES, sample_rate=SAMPLE_RATE):
    if not events:
        return np.zeros(0)

    total_duration = (max(event['end_frame'] for event in events) + 1) * FRAME_DURATION
    total_samples = int(total_duration * sample_rate)
    audio_signal = np.zeros(total_samples)

    for event in events:
        start_sample = event['start_frame'] * frame_samples
        end_sample = (event['end_frame'] + 1) * frame_samples  # Include the end frame in the duration
        frequency = event['frequency']
        amplitude = event['amplitude']

        t = np.linspace(start_sample / sample_rate, end_sample / sample_rate, end_sample - start_sample, endpoint=False)
        signal = amplitude * np.sin(2 * np.pi * frequency * t)
        
        audio_signal[start_sample:end_sample] += signal

    # Normalize the audio signal
    max_amplitude = np.max(np.abs(audio_signal))
    if max_amplitude > 0:
        audio_signal = audio_signal / max_amplitude
    
    return audio_signal

def save_audio_signal(audio_signal, output_path, sample_rate=SAMPLE_RATE):
    wav.write(output_path, sample_rate, (audio_signal * 32767).astype(np.int16))

def render_events_to_wav(event_file_path, output_wav_path):
    events = read_event_tsv(event_file_path)
    audio_signal = generate_audio_signal(events)
    save_audio_signal(audio_signal, output_wav_path)
    print(f"Rendered audio saved to {output_wav_path}")

def process_event_folder(input_folder):
    """Processes all _events.tsv files in the given folder and saves the rendered .wav output."""
    output_dir = os.path.join(input_folder, 'rendered_wav')
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith("_events.tsv"):
            event_file_path = os.path.join(input_folder, filename)
            output_wav_filename = f"{os.path.splitext(filename)[0]}.wav"
            output_wav_path = os.path.join(output_dir, output_wav_filename)
            render_events_to_wav(event_file_path, output_wav_path)

if __name__ == "__main__":
    input_folder = "./in_wav/tsv/events/"
    process_event_folder(input_folder)
