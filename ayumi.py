import numpy as np
import wave
import os

class Ayumi:
    def __init__(self, dac_type='AY', panning=(1.0, 1.0), sample_rate=44100, clock_frequency=1750000):
        self.dac_table = AY_DAC_TABLE if dac_type == 'AY' else YM_DAC_TABLE
        self.channels = [self.create_channel() for _ in range(3)]
        self.panning = panning
        self.sample_rate = sample_rate
        self.clock_frequency = clock_frequency  # Clock frequency in Hz
        self.noise_register = 0x01FFFF  # 17-bit LFSR
        self.envelope_counter = 0
        self.envelope_step = 0
        self.envelope_shape = 0
        self.envelope_period = 0

    def create_channel(self):
        return {
            'tone_period': 0,
            'tone_counter': 0,
            'tone_output': 0,
            'volume': 0.1,  # Default volume
        }

    def set_tone(self, channel_index, period):
        self.channels[channel_index]['tone_period'] = period

    def set_noise(self, period):
        self.noise_period = period

    def set_envelope(self, shape, period):
        self.envelope_shape = shape
        self.envelope_period = period
        self.envelope_counter = 0
        self.envelope_step = 0

    def update_tone(self):
        for ch in self.channels:
            if ch['tone_period'] > 0:
                increment = self.clock_frequency / (16 * ch['tone_period'] * self.sample_rate)
                ch['tone_counter'] += increment
                if ch['tone_counter'] >= 1:
                    ch['tone_counter'] -= 1
                    ch['tone_output'] = 1 - ch['tone_output']

    def update_noise(self):
        bit0 = self.noise_register & 1
        bit14 = (self.noise_register >> 14) & 1
        feedback = bit0 ^ bit14
        self.noise_register = (self.noise_register >> 1) | (feedback << 16)

    def update_envelope(self):
        self.envelope_counter += 1
        if self.envelope_counter >= self.envelope_period:
            self.envelope_counter = 0
            self.envelope_step = (self.envelope_step + 1) % 32  # Adjust according to shape specifics

    def process_sound(self):
        self.update_tone()
        self.update_noise()
        self.update_envelope()

        left_output = np.array([0.0])
        right_output = np.array([0.0])
        for ch in self.channels:
            volume_index = int(ch['volume'] * (len(self.dac_table) - 1))
            if volume_index >= len(self.dac_table):
                volume_index = len(self.dac_table) - 1
            elif volume_index < 0:
                volume_index = 0
            dac_output = self.dac_table[volume_index] * ch['tone_output']
            left_output += dac_output * self.panning[0]
            right_output += dac_output * self.panning[1]
        return np.stack((left_output, right_output), axis=-1).flatten().astype(np.float32)

    def generate_sound(self, duration_seconds):
        num_samples = int(self.sample_rate * duration_seconds)
        all_samples = np.zeros((num_samples, 2), dtype=np.float32)

        for i in range(num_samples):
            all_samples[i] = self.process_sound()

        return all_samples

    def save_to_wav(self, filename, duration_seconds):
        # Ensure the directory exists
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        samples = self.generate_sound(duration_seconds)
        try:
            with wave.open(filename, 'w') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes((samples * 32767).astype(np.int16).tobytes())
            print(f"Successfully saved to {filename}")
        except Exception as e:
            print(f"Failed to save the WAV file: {e}")

# Define DAC tables with realistic data from hardware specifications
# AY_DAC_TABLE = [0.0, 0.5, 1.0]  # Simplified DAC values
# YM_DAC_TABLE = [0.0, 0.75, 1.0]  # Simplified DAC values
AY_DAC_TABLE = [
    0.0, 0.0,
    0.00999465934234, 0.00999465934234,
    0.0144502937362, 0.0144502937362,
    0.0210574502174, 0.0210574502174,
    0.0307011520562, 0.0307011520562,
    0.0455481803616, 0.0455481803616,
    0.0644998855573, 0.0644998855573,
    0.107362478065, 0.107362478065,
    0.126588845655, 0.126588845655,
    0.20498970016, 0.20498970016,
    0.292210269322, 0.292210269322,
    0.372838941024, 0.372838941024,
    0.492530708782, 0.492530708782,
    0.635324635691, 0.635324635691,
    0.805584802014, 0.805584802014,
    1.0, 1.0
]
YM_DAC_TABLE = [
    0.0, 0.0,
    0.00465400167849, 0.00772106507973,
    0.0109559777218, 0.0139620050355,
    0.0169985503929, 0.0200198367285,
    0.024368657969, 0.029694056611,
    0.0350652323186, 0.0403906309606,
    0.0485389486534, 0.0583352407111,
    0.0680552376593, 0.0777752346075,
    0.0925154497597, 0.111085679408,
    0.129747463188, 0.148485542077,
    0.17666895552, 0.211551079576,
    0.246387426566, 0.281101701381,
    0.333730067903, 0.400427252613,
    0.467383840696, 0.53443198291,
    0.635172045472, 0.75800717174,
    0.879926756695, 1.0
]

# Example usage
if __name__ == "__main__":
    ayumi = Ayumi(dac_type='AY', panning=(0.5, 0.5), sample_rate=44100, clock_frequency=1750000)
    ayumi.set_tone(0, 512)  # Set tone frequency for channel 0
    ayumi.set_envelope(14, 32)  # Set tone frequency for channel 0
    output_path = "./output.wav"  # Adjusted to a likely valid path
    ayumi.save_to_wav(output_path, 5)  # Generate a 5 second WAV file