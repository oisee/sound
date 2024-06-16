import struct
import argparse

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
    current_frame = [0] * 14
    i = 0
    while i < len(data):
        value = data[i]
        if value == 0xFF:  # End of frame marker
            frames.append(current_frame.copy())
        elif value == 0xFE:  # Skipping multiple frames
            skip_frames = data[i + 1] * 4
            frames.extend([current_frame.copy()] * skip_frames)
            i += 1
        elif value == 0xFD:  # End of PSG data (not standard but mentioned in some docs)
            break
        else:
            register = value & 0x0F
            value = data[i + 1]
            if register < 14:  # Valid AY register
                current_frame[register] = value
            i += 1
        i += 1
    return frames

def write_register_dump(frames, output_filename):
    with open(output_filename, 'w') as file:
        previous_frame = [None] * 14
        for frame in frames:
            output_frame = []
            for i, value in enumerate(frame):
                if value == previous_frame[i]:
                    output_frame.append('_')
                    #output_frame.append(' ')
                else:
                    output_frame.append(str(value))
            file.write('\t'.join(output_frame) + '\n')
            previous_frame = frame.copy()

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
