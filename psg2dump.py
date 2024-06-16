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
        b = data[i]
        if b == 0xff:  # Start of frame marker
            frames.append(current_frame.copy())
            current_frame = [None] * REG_NUM  # Reset for next frame
        elif b == 0xfe:  # Skipping multiple frames
            skip_frames = data[i + 1] * 4
            for _ in range(skip_frames):
                frames.append([None] * REG_NUM)
            i += 1
        elif b == 0xfd:  # End of PSG data
            frames.append(current_frame.copy())
            break
        elif b >= 0x00 and b <= 0x0d:  # AY register
            reg = b
            i += 1
            value = data[i]
            current_frame[reg] = value
        i += 1

    # Ensure the last frame is appended if it contains any data
    if any(v is not None for v in current_frame):
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
