import struct
import argparse

REG_NUM = 14

def read_psg_file(filename):
    with open(filename, 'rb') as file:
        header = file.read(4)
        if header[:3] != b'PSG' or header[3] != 0x1A:
            raise ValueError("Not a valid PSG file")
        
        version = struct.unpack('B', file.read(1))[0]
        file.read(11)  # skip reserved bytes and unknown bytes
        data = file.read()
        return data

def parse_psg_data(data):
    frames = []
    current_frame = [None] * REG_NUM  # Initialize with None to denote uninitialized values
    i = 0
    while i < len(data):
        value = data[i]
        if value == 0xFF:  # Start of frame marker
            if any(v is not None for v in current_frame):  # Only append frames with data
                frames.append(current_frame.copy())
            current_frame = [None] * REG_NUM  # Reset for next frame
        elif value == 0xFE:  # Skipping multiple frames
            skip_frames = data[i + 1] * 4
            for _ in range(skip_frames):
                frames.append([None] * REG_NUM)
            i += 1
        elif value == 0xFD:  # End of PSG data (not standard but mentioned in some docs)
            break
        else:
            register = value & 0x0F
            value = data[i + 1]
            if register < REG_NUM:  # Valid AY register
                current_frame[register] = value
            i += 1
        i += 1
    if any(v is not None for v in current_frame):  # Append the last frame if it has data
        frames.append(current_frame.copy())
    return frames

def write_register_dump(frames, output_filename):
    with open(output_filename, 'w') as file:
        for frame in frames:
            output_frame = []
            for value in frame:
                if value is None:
                    output_frame.append('_')
                else:
                    output_frame.append(str(value))
            if any(value != '_' for value in output_frame):  # Skip lines with all '_'
                file.write('\t'.join(output_frame) + '\n')

def main(input_filename):
    output_filename = input_filename + '.aydump'
    psg_data = read_psg_file(input_filename)
    frames = parse_psg_data(psg_data)
    write_register_dump(frames, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a PSG file to an AY register dump.')
    parser.add_argument('input_filename', nargs='?', default='sync.psg', help='The input PSG file (default: sync.psg)')
    args = parser.parse_args()
    main(args.input_filename)
